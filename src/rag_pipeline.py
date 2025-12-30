import os
import sys
from pathlib import Path
from collections import defaultdict
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from embed import Embedder
from src.markdown_writer import MarkdownWriter
from src.symbols_ast import index_repo_ast
from store_qdrant import QdrantStore

# --- 1. Konfiguration ---
LLM_API_BASE = "http://localhost:11434/v1"
LLM_MODEL_NAME = "qwen3:4b"
LLM_API_KEY = "ollama"
DOCS_ROOT = Path("../sample_project/docs")

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


# --- 4. Retrieval & Generation (Standard RAG) ---

def generate_with_rag(llm, code_segment, embedder, store, current_symbol_name):
    """
    Führt den klassischen RAG-Schritt aus:
    Query -> Vektor-Suche -> Kontext -> LLM Generierung
    """

    # Retrieve the 5 most similar symbols form the vector db
    # Only 4 will be used as context, as one hte the symbol itself
    query_vec = embedder.encode([current_symbol_name])
    results = store.search(query_vec, k=5)

    # Create the context with the similar symbols
    context_lines = []
    for res in results:
        if res['qualname'] != current_symbol_name:
            context_lines.append(f"- {res['qualname']} ({res['kind']}) from {res['file']}")

    context_str = "\n".join(context_lines) if context_lines else "No related context found."
    print(f"    [RAG Context]: {len(context_lines)} items found.")

    # LLM like before
    analyze_chain = CODE_EXPERT_PROMPT | llm | StrOutputParser()
    analysis = analyze_chain.invoke({
        "code": code_segment,
        "context": context_str
    })
    docs_chain = DOCS_EXPERT_PROMPT | llm | StrOutputParser()
    markdown = docs_chain.invoke({
        "analysis": analysis,
        "existing_docs": ""
    })
    return markdown


# --- 5. Main Evaluation Loop ---

def evaluate_rag(root_dir: str, llm):
    print("\n--- Standard RAG Evaluation (No Agent) ---")

    embedder = Embedder(device="cpu")

    store = QdrantStore(index_path=Path("../sample_project/qdrant_data"), collection_name="eval_repo")

    writer = MarkdownWriter(DOCS_ROOT)

    # Index repository
    all_symbols = run_indexing(root_dir, embedder, store)

    symbols_by_file = defaultdict(list)
    for sym in all_symbols:
        if sym.kind in ("class", "function", "method"):
            symbols_by_file[sym.file].append(sym)

    for file_path, file_symbols in symbols_by_file.items():
        if "core.py" not in str(file_path):
            continue

        # Generaste the MD file name
        # The name will be all directories and the final file joined with "_"
        # So all MD files can be found in the top level of the DOCS_ROOT
        # ONLY THE FILES WITHIN THE SRC FOLDER WILL BE DOCUMENTED
        src_index = file_path.rfind("src")
        file_path_split = file_path[src_index:].split(os.sep)
        md_file_name = "_".join(file_path_split[1:]).replace(".py", ".md")
        md_file_path = Path(DOCS_ROOT, md_file_name)

        base_name = Path(file_path).stem

        print(f"\nProcessing {base_name} with Standard RAG...")

        file_symbols.sort(key=lambda s: s.start)

        for sym in file_symbols:
            print(f"  > Symbol: {sym.qualname}")

            try:
                full_lines = Path(sym.file).read_text(encoding="utf-8").splitlines()
                code_segment = "\n".join(full_lines[sym.start - 1:sym.end])
            except Exception as e:
                print(f"    Fehler beim Lesen: {e}")
                continue

            # Call RAG pipeline
            docs = generate_with_rag(llm, code_segment, embedder, store, sym.qualname)
            # Write using the markdown writer
            writer.write_section(file_path=md_file_path, symbol_id=sym.symbol_id,content=docs)


    store.close()


if __name__ == "__main__":
    llm = APILLM(base_url=LLM_API_BASE, api_key=LLM_API_KEY, model_name=LLM_MODEL_NAME, temperature=0)

    target_dir = "../sample_project"
    if not Path(target_dir).exists():
        print(f"Fehler: Ordner '{target_dir}' nicht gefunden.")
        sys.exit(1)

    evaluate_rag(target_dir, llm)