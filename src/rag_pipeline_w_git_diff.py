import os
import sys
from collections import defaultdict
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# Import deiner bestehenden Module
from src.embed import Embedder
from src.markdown_writer import MarkdownWriter
from src.util import run_indexing, git_commit_and_push_changes, get_doc_for_symbol
from src.store_qdrant import QdrantStore

# --- 1. Konfiguration ---
LLM_API_BASE = "http://localhost:11434/v1"
LLM_MODEL_NAME = "qwen3:4b"
LLM_API_KEY = "ollama"
DOCS_ROOT = Path("./sample_project/docs")
REPO_ROOT = Path("./sample_project")
QDRANT_DATA_PATH = Path("./sample_project/qdrant_data")

# --- 2. Prompts ---
from src.prompts import CODE_EXPERT_PROMPT, DOCS_EXPERT_PROMPT


class APILLM(ChatOpenAI):
    def __init__(self, base_url: str, api_key: str, model_name: str, **kwargs):
        super().__init__(base_url=base_url, api_key=api_key, model=model_name, **kwargs)




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
        "analysis": analysis
    })
    return markdown



def process_pipeline(llm):
    embedder = Embedder()
    store = QdrantStore(index_path=Path(QDRANT_DATA_PATH), collection_name="eval_repo")
    writer = MarkdownWriter(DOCS_ROOT)

    # Index repository
    all_symbols, changed_symbols = run_indexing(REPO_ROOT, embedder, store)

    changed_symbols_by_file = defaultdict(list)
    all_symbols_by_file = defaultdict(list)
    for sym in changed_symbols:
        changed_symbols_by_file[sym.file].append(sym)

    for sym in all_symbols:
        all_symbols_by_file[sym.file].append(sym)

    for file_path, changed_file_symbols in changed_symbols_by_file.items():
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

        changed_file_symbols.sort(key=lambda s: s.start)

        for sym in changed_file_symbols:
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
            writer.write_section(file_path=md_file_path, symbol_id=sym.symbol_id, content=docs)

        # Reorder the sections after all updates are done
        all_file_symbols = all_symbols_by_file[file_path]
        all_file_symbols.sort(key=lambda s: s.start)
        writer.reorder_sections(file_path=md_file_path, ordered_symbol_ids=[s.symbol_id for s in all_file_symbols])

    store.close()
    # git_commit_and_push_changes()


if __name__ == "__main__":
    llm = APILLM(base_url=LLM_API_BASE, api_key=LLM_API_KEY, model_name=LLM_MODEL_NAME, temperature=0)

    if not Path(REPO_ROOT).exists():
        print(f"Fehler: Ordner '{REPO_ROOT}' nicht gefunden.")
        sys.exit(1)

    process_pipeline(llm)
