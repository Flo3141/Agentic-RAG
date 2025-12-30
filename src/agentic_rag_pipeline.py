import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI

# Import deiner bestehenden Module
import symbols_ast
from embed import Embedder
from store_qdrant import QdrantStore
from markdown_writer import MarkdownWriter

from prompts import CODE_EXPERT_PROMPT, DOCS_EXPERT_PROMPT, DOCS_REVIEW_PROMPT

# --- 1. Konfiguration ---
LLM_API_BASE = "http://localhost:11434/v1"
LLM_MODEL_NAME = "qwen3:4b"
LLM_API_KEY = "ollama"
DOCS_ROOT = Path("./sample_project/docs")
REPO_ROOT = Path("./sample_project")
QDRANT_DATA_PATH = Path("./sample_project/qdrant_data")


class APILLM(ChatOpenAI):
    def __init__(self, base_url: str, api_key: str, model_name: str, **kwargs):
        super().__init__(base_url=base_url, api_key=api_key, model=model_name, **kwargs)


def run_indexing(root_dir: str, embedder, store):
    """
    Liest den Code, erstellt Embeddings und speichert sie in Qdrant.
    """
    print("\n--- STEP 1: Indexing Repository (Knowledge Base) ---")

    # 1. Find changed files
    changed_files = get_git_diff_files()
    if not changed_files:
        print("Keine Python-Dateien geändert.")
        return

    print(f"Verarbeite Änderungen in: {changed_files}")

    # 1. Code parsen
    current_symbols = symbols_ast.index_repo_ast(root_dir, changed_files)

    # Create lookup map of all symbol_ids with corresponding hashes from the Qdrant DB
    existing_hashes = {}

    try:
        # Get all entries of the db, get only the payload, not the vectors --> the payload contains the symbol_id and the hash
        # We should do this in a loop when the repo is big, but this will suffice for now
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
    changed_symbols = []
    to_embed = []
    skipped_count = 0

    for sym in current_symbols:
        if sym.symbol_id in existing_hashes and existing_hashes[sym.symbol_id] == sym.hash:
            skipped_count += 1
            continue
        # Index and document only relevant symbols (Classes, functions, methods)
        if sym.kind in ("class", "function", "method"):
            changed_symbols.append(sym)
            to_embed.append(sym)

    print(f"{skipped_count} symbols not changed")
    print(f"Update necessary for {len(to_embed)} symbols.")

    if not to_embed:
        return current_symbols, changed_symbols

    # Only embed the changed symbols
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

    return current_symbols, changed_symbols


def find_usages(symbol_name: str, root_dir: Path) -> str:
    """Suche nach Verwendungen des Symbols im Code (einfaches Grep)."""
    usages = []
    try:
        # Wir suchen rekursiv nach dem String
        cmd = ["grep", "-r", symbol_name, str(root_dir)]
        # Grep kann Fehler werfen (exit code 1), wenn nichts gefunden wird, daher try/except
        try:
            result = subprocess.check_output(cmd, text=True).strip()
            lines = result.splitlines()
            # Begrenze auf die ersten 10 Treffer, um Context kurz zu halten
            usages = lines[:10]
        except subprocess.CalledProcessError:
            pass
    except Exception as e:
        print(f"Warning: Could not search usages: {e}")
    
    return "\n".join(usages) if usages else "No direct usages found."


def generate_with_agentic_loop(llm, code_segment, embedder, store, current_symbol_name):
    """
    Agentic RAG Pipeline mit Review-Loop.
    Code Expert -> Docs Expert -> Reviewer (Agent) -> Feedback -> Code Expert ...
    """

    # 1. Retrieve RAG Context
    query_vec = embedder.encode([current_symbol_name])
    results = store.search(query_vec, k=5)

    # Create the context with the similar symbols
    context_lines = []
    for res in results:
        if res['qualname'] != current_symbol_name:
            context_lines.append(f"- {res['qualname']} ({res['kind']}) from {res['file']}")

    context_str = "\n".join(context_lines) if context_lines else "No related context found."
    print(f"    [RAG Context]: {len(context_lines)} items found.")

    # 2. Find Usages (Impact Analysis)
    usage_context = find_usages(current_symbol_name, REPO_ROOT)
    
    current_feedback = ""
    current_docs = ""
    
    max_retries = 5
    for i in range(max_retries):
        print(f"    [Agent Loop] Iteration {i+1}/{max_retries}...")
        
        # A. Code Expert (Analysis)
        analyze_chain = CODE_EXPERT_PROMPT | llm | StrOutputParser()
        analysis = analyze_chain.invoke({
            "code": code_segment,
            "context": context_str,
            "feedback": current_feedback
        })
        
        # B. Docs Expert (Markdown Generation)
        docs_chain = DOCS_EXPERT_PROMPT | llm | StrOutputParser()
        current_docs = docs_chain.invoke({
            "analysis": analysis
        })
        
        # C. Reviewer (Reasoning Agent)
        review_chain = DOCS_REVIEW_PROMPT | llm | JsonOutputParser()
        try:
            review_result = review_chain.invoke({
                "code": code_segment,
                "current_docs": current_docs,
                "usage_context": usage_context
            })
            
            status = review_result.get("status", "REVISION_NEEDED")
            feedback = review_result.get("feedback", "")
            reasoning = review_result.get("reasoning", "No reasoning provided.")
            
            print(f"      [Reviewer] Status: {status}")
            
            if status == "APPROVED":
                print(f"      [Reviewer] Approved! Reasoning: {reasoning}")
                return current_docs
            
            # If not approved, update feedback for next loop
            print(f"      [Reviewer] Feedback: {feedback}")
            current_feedback = f"Previous attempt was rejected. Reviewer feedback: {feedback}. Reviewer Reasoning: {reasoning}"
            
        except Exception as e:
            print(f"      [Reviewer] Error parsing JSON or executing: {e}. Retrying loop...")
            current_feedback = f"Previous answer caused a JSON error or execution fault: {e}. Please fix."

    # If we fall through here, we failed to get approval
    print(f"    [Agent Loop] Failed to get approval after {max_retries} iterations.")
    
    # Log failure
    failure_log = Path("docs_review_failures.log")
    with open(failure_log, "a", encoding="utf-8") as f:
        f.write(f"\n--- Symbol: {current_symbol_name} ---\n")
        f.write(f"Final Docs:\n{current_docs}\n")
        f.write(f"Last Feedback:\n{current_feedback}\n")
        f.write("-------------------------------------\n")
        
    return current_docs # Return best effort


def get_git_diff_files():
    """Holt alle geänderten .py Dateien im Vergleich zum vorherigen Stand."""
    # AKTUELL NOCH TEST MODUS
    print("TEST-MODUS: Simuliere Änderung in core.py")
    # Hier gibst du den Pfad an, den du testen möchtest
    test_file = Path("./sample_project/src/calculator/core.py")
    return [test_file]

    try:
        # Vergleicht den aktuellen Stand mit dem vorherigen Commit
        cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        result = subprocess.check_output(cmd, text=True).strip()
        return [Path(f) for f in result.splitlines() if f.endswith(".py") and Path(f).exists()]
    except Exception as e:
        print(f"Git Diff Fehler (vielleicht erster Commit?): {e}")
        return []


def get_current_branch():
    """Ermittelt den Namen des aktuell ausgecheckten Git-Branches."""
    try:
        # Führt den Befehl aus und gibt den Branch-Namen als String zurück
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True
        ).strip()
        return branch
    except subprocess.CalledProcessError:
        # Fallback auf 'main', falls etwas schiefgeht
        return "main"


def git_commit_and_push_changes():
    """
    Staged die Doku und die Vektor-DB, committet sie und führt einen Push aus.
    """
    print("\nStaging changes (Docs & Vector DB)...")
    # Branch ermitteln
    current_branch = get_current_branch()
    print(f"Detektierter Branch: {current_branch}")
    try:
        # 1. Dateien hinzufügen (Doku-Ordner und Vektor-Daten)
        # Wir fügen explizit diese Pfade hinzu
        subprocess.run(["git", "add", DOCS_ROOT, QDRANT_DATA_PATH], check=True)

        # 2. Prüfen, ob es überhaupt Änderungen gibt
        status = subprocess.check_output(["git", "status", "--porcelain", DOCS_ROOT, QDRANT_DATA_PATH], text=True)
        print(status)
        if not status.strip():
            print("Keine Änderungen an Doku oder DB erkannt. Alles aktuell.")
            return

        print("Committing automated documentation updates...")
        # 3. Automatischer Commit
        subprocess.run(["git", "commit", "-m", "docs: auto-update documentation and vector DB via RAG pipeline"],
                       check=True)

        print(f"Pushing updates to origin {current_branch}...")
        # 4. Push ausführen.
        # WICHTIG: --no-verify verhindert, dass der Hook sich selbst endlos aufruft!
        subprocess.run(["git", "push", "origin", current_branch, "--no-verify"], check=True)
        print("All changes (Code, Docs, DB) successfully pushed.")
    except subprocess.CalledProcessError as e:
        print(f"Git-Fehler: {e}")


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

        changed_file_symbols.sort(key=lambda s: s.start)

        for sym in changed_file_symbols:
            print(f"  > Symbol: {sym.qualname}")

            try:
                full_lines = Path(sym.file).read_text(encoding="utf-8").splitlines()
                code_segment = "\n".join(full_lines[sym.start - 1:sym.end])
            except Exception as e:
                print(f"    Fehler beim Lesen: {e}")
                continue

            # Call Agentic RAG pipeline
            docs = generate_with_agentic_loop(llm, code_segment, embedder, store, sym.qualname)
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
