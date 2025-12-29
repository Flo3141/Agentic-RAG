import subprocess
import sys
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# Import deiner bestehenden Module
import symbols_ast
from embed import Embedder
from store_qdrant import QdrantStore
from markdown_writer import MarkdownWriter

# --- 1. Konfiguration ---
LLM_API_BASE = "http://localhost:11434/v1"
LLM_MODEL_NAME = "qwen3:4b"
LLM_API_KEY = "ollama"
DOCS_ROOT = Path("../sample_project/docs")
REPO_ROOT = Path("../sample_project")
QDRANT_DATA_PATH = Path("../sample_project/qdrant_data")

# --- 2. Prompts ---
CODE_EXPERT_PROMPT = PromptTemplate(
    input_variables=["code", "context"],
    template="""You are a Senior Python Engineer (Code Expert).
Your task is to analyze the following Python code and its context to understand its behavior, parameters, return values, and potential exceptions.

Context (related symbols):
{context}

Code to Analyze:
```python
{code}
```

Provide a detailed technical analysis including:
1. Summary of functionality.
2. Parameters (name, type, description).
3. Return value (type, description).
4. Exceptions raised.
5. Usage examples.
"""
)

DOCS_EXPERT_PROMPT = PromptTemplate(
    input_variables=["analysis", "existing_docs"],
    template="""You are a Technical Writer (Documentation Expert).
Your task is to generate high-quality Markdown API documentation based on the technical analysis provided by the Code Expert.

Technical Analysis:
{analysis}

Existing Documentation (if any):
{existing_docs}

Generate the Markdown documentation following this structure:
### `SymbolName`

**Summary**
...

**Parameters**
- `name` (type): description

**Returns**
- (type): description

**Raises**
- `Exception`: description

**Examples**
```python
...
```

**See also**
...

CRITICAL INSTRUCTIONS:
1. Output ONLY the Markdown content.
2. DO NOT output any "thinking" process, reasoning, or internal monologue.
3. DO NOT output any conversational text like "Here is the documentation".
4. DO NOT wrap the output in markdown code blocks (e.g. ```markdown ... ```). Just output the raw markdown.
"""
)


class APILLM(ChatOpenAI):
    def __init__(self, base_url: str, api_key: str, model_name: str, **kwargs):
        super().__init__(base_url=base_url, api_key=api_key, model=model_name, **kwargs)


def run_indexing(root_dir: str, embedder, store):
    """
    Liest den Code, erstellt Embeddings und speichert sie in Qdrant.
    """
    print("\n--- STEP 1: Indexing Repository (Knowledge Base) ---")

    # 1. Code parsen
    current_symbols = index_repo_ast(root_dir)

    # Index only relevant symbols (Klassen, Funktionen)
    indexable_symbols = [s for s in current_symbols if s.kind in ("class", "function", "method")]

    # Create lookup map of all symbol_ids with corresponding hashes from the Qdrant DB
    existing_hashes = {}

    try:
        # Get all entries of the db, get only the payload, not the vectors --> the payload contains the symbol_id and the hash
        # You should do this in a loop when the repo is big, but this will suffice for now
        res = store.client.scroll(
            collection_name=store.collection_name,
            limit=10000,
            with_payload=True,
            with_vectors=False
        )[0]

        for point in res:
            payload = point.payload
            if "symbol_id" in payload and "hash" in payload:
                existing_hashes[payload["symbol_id"]] = payload["hash"]

    except Exception as e:
        print(f"Could not read db {e}")

    # Get differences
    to_embed = []
    skipped_count = 0

    for sym in indexable_symbols:
        # Does the symbol exist and is the hash the same? --> If yes, no need to embedd it again
        if sym.symbol_id in existing_hashes and existing_hashes[sym.symbol_id] == sym.hash:
            skipped_count += 1
            continue
        to_embed.append(sym)

    print(f"{skipped_count} symbols not changed")
    print(f"Update necessary for {len(to_embed)} symbols.")

    if not to_embed:
        return current_symbols

    # Only embedd the changed symbols
    texts = [f"{s.qualname}: {s.docstring}" for s in to_embed]
    vectors = embedder.encode(texts)

    metadatas = []
    for s in to_embed:
        metadatas.append({
            "symbol_id": s.symbol_id,
            "qualname": s.qualname,
            "file": s.file,
            "kind": s.kind,
            "hash": s.hash
        })

    store.add(vectors, metadatas)

    return current_symbols


def get_git_diff_files():
    """Holt alle geänderten .py Dateien im Vergleich zum vorherigen Stand."""
    try:
        # Vergleicht den aktuellen Stand mit dem vorherigen Commit
        cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        result = subprocess.check_output(cmd, text=True).strip()
        return [f for f in result.splitlines() if f.endswith(".py") and Path(f).exists()]
    except Exception as e:
        print(f"⚠️ Git Diff Fehler (vielleicht erster Commit?): {e}")
        return []


def process_pipeline(llm):
    # 1. Setup Komponenten
    embedder = Embedder()
    store = QdrantStore(index_path=Path(QDRANT_DATA_PATH), collection_name="eval_repo")
    writer = MarkdownWriter(DOCS_ROOT)

    # 2. Geänderte Dateien finden
    changed_files = get_git_diff_files()
    if not changed_files:
        print("✅ Keine Python-Dateien geändert.")
        return

    print(f"🔍 Verarbeite Änderungen in: {changed_files}")

    for file_path in changed_files:
        # 3. Symbole der geänderten Datei parsen
        symbols = symbols_ast.parse_symbols_file(Path(file_path), REPO_ROOT)

        for sym in symbols:
            if sym.kind not in ("class", "method", "function"):
                continue

            # 4. Inkrementelles Indexing (Optional: Hier Hash-Check einbauen)
            # Wir erstellen das Embedding neu für das geänderte Symbol
            text_to_embed = f"{sym.qualname}: {sym.docstring}"
            vector = embedder.encode([text_to_embed])

            store.add(vector, [{
                "symbol_id": sym.symbol_id,
                "qualname": sym.qualname,
                "file": sym.file,
                "kind": sym.kind,
                "docstring": sym.docstring
            }])

            # 5. RAG-Dokumentation generieren
            print(f"  📝 Generiere Doku für: {sym.qualname}")

            # Context Retrieval
            results = store.search(embedder.encode([sym.qualname]), k=5)
            context = "\n".join([f"- {r['qualname']}: {r.get('docstring', '')[:100]}" for r in results if
                                 r['qualname'] != sym.qualname])

            # LLM Call (vereinfacht)
            prompt = f"Context:\n{context}\n\nCode:\n{sym.qualname}\n\nGenerate Documentation:"
            markdown_content = llm.predict(prompt)

            # 6. Markdown Update mit deinen Markern
            module_name = sym.parent.split('.')[0] if '.' in sym.parent else sym.parent
            target_md = DOCS_ROOT / f"{module_name}.md"

            writer.write_section(
                file_path=target_md,
                symbol_id=sym.symbol_id,
                content=markdown_content
            )

    print("🚀 Pipeline erfolgreich abgeschlossen.")


if __name__ == "__main__":
    llm = APILLM(base_url=LLM_API_BASE, api_key=LLM_API_KEY, model_name=LLM_MODEL_NAME, temperature=0)

    if not Path(REPO_ROOT).exists():
        print(f"Fehler: Ordner '{REPO_ROOT}' nicht gefunden.")
        sys.exit(1)

    process_pipeline(llm)
