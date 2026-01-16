import subprocess
import hashlib
import uuid

from pathlib import Path

from src.config import DOCS_ROOT, QDRANT_DATA_PATH
from src.symbols_ast import index_repo_ast


def get_doc_for_symbol(symbol_id: str) -> str:
    """Retrieve the existing Markdown documentation for a specific symbol.

    Args:
        symbol_id: The unique identifier of the symbol (e.g., 'calculator.core.CalculatorError').
    """
    import re

    if not DOCS_ROOT.exists():
        return "Error: Documentation root not found."

    start_marker = f"<!-- BEGIN: auto:{symbol_id} -->"
    end_marker = f"<!-- END: auto:{symbol_id} -->"

    # Iterate over all MD files in docs root
    for file_path in DOCS_ROOT.glob("*.md"):
        try:
            content = file_path.read_text(encoding="utf-8")
            pattern = re.compile(
                rf"{re.escape(start_marker)}(.*?){re.escape(end_marker)}",
                re.DOTALL
            )
            match = pattern.search(content)
            if match:
                return match.group(0)  # Return the whole block including markers
        except Exception as e:
            continue

    return f"No documentation found for symbol: {symbol_id}"


def run_indexing(root_dir: str, embedder, store):
    """
    Reads the code, creates the embeddings and saves them to qdrant
    """
    print("\n--- STEP 1: Indexing Repository (Knowledge Base) ---")

    # 1. Find changed files
    changed_files = get_git_diff_files()
    if not changed_files:
        print("No python files changed.")
        return [], [], []

    print(f"Process change in: {changed_files}")

    # 1. Code parsen
    current_symbols = index_repo_ast(root_dir, changed_files)
    # Helper: Map file path -> set of current symbol_ids
    current_symbols_by_file = {}
    for sym in current_symbols:
        s_file = str(Path(sym.file))
        if s_file not in current_symbols_by_file:
            current_symbols_by_file[s_file] = set()
        current_symbols_by_file[s_file].add(sym.symbol_id)

    # Create lookup map of all symbol_ids with corresponding hashes from the Qdrant DB
    existing_hashes = {}
    existing_symbols_by_file = {}

    try:
        # Get all entries of the db, get only the payload
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
                
                # Organize by file to detect deletions
                if "file" in payload:
                    p_file = str(Path(payload["file"]))
                    if p_file not in existing_symbols_by_file:
                        existing_symbols_by_file[p_file] = set()
                    existing_symbols_by_file[p_file].add(payload["symbol_id"])
    except Exception as e:
        print(f"Could not read db {e}")

    # --- Detect and Delete Removed Symbols ---
    deleted_ids_all = []
    for c_file_path in changed_files:
        c_file_str = str(c_file_path)
        
        curr_ids = current_symbols_by_file.get(c_file_str, set())
        db_ids = existing_symbols_by_file.get(c_file_str, set())
        
        # Deleted = in DB but not in Current
        deleted_ids = db_ids - curr_ids
        if deleted_ids:
            print(f"Detected {len(deleted_ids)} deleted symbols in {c_file_str}: {list(deleted_ids)}")
            deleted_ids_all.extend(list(deleted_ids))

    if deleted_ids_all:
        point_ids_to_delete = []
        for sid in deleted_ids_all:
            # Reconstruct point ID from symbol ID hash
            hash_val = hashlib.md5(sid.encode("utf-8")).hexdigest()
            point_id = str(uuid.UUID(hex=hash_val))
            point_ids_to_delete.append(point_id)
            
        print(f"Deleting {len(point_ids_to_delete)} symbols from Vector DB...")
        store.delete(point_ids_to_delete)

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
        return current_symbols, changed_symbols, changed_files

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

    return current_symbols, changed_symbols, changed_files


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


