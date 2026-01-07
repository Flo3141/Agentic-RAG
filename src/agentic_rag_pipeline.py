import os
import json
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

from prompts import RESEARCH_LOOP_PROMPT, DOCS_EXPERT_PROMPT, IMPACT_LOOP_PROMPT
from tools import search_code, get_doc_for_symbol

# --- 1. Konfiguration ---
from config import LLM_API_BASE, LLM_MODEL_NAME, LLM_API_KEY, DOCS_ROOT, REPO_ROOT, QDRANT_DATA_PATH

# Tool Mapping
AVAILABLE_TOOLS = {
    "search_code": search_code,
}

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


def get_tools_description():
    """Generates a string description of all available tools."""
    desc = "Available Tools:\n"
    for name, func in AVAILABLE_TOOLS.items():
        desc += f"- {name}: {func.__doc__.strip() if func.__doc__ else 'No description'}\n"
    return desc


def execute_tool(name: str, args: dict) -> str:
    """Executes a tool by name with arguments."""
    if name not in AVAILABLE_TOOLS:
        return f"Error: Tool {name} not found."

    tool_func = AVAILABLE_TOOLS[name]
    try:
        # Invoke langchain tool
        return tool_func.invoke(args)
    except Exception as e:
        return f"Error executing tool '{name}': {e}"


def run_agent_loop(llm, prompt_template, initial_vars, max_steps=5):
    """
    Generic loop for an agent that uses tools.
    """
    history = []
    log_file = Path("agent_history.log")

    for i in range(max_steps):
        print(f"      [Step {i + 1}] Thinking...")

        # Prepare context (history needs to be a string)
        history_str = "\n".join(history)

        # Invoke LLM
        chain = prompt_template | llm | StrOutputParser()
        vars_with_history = {**initial_vars, "history": history_str}

        try:
            response = chain.invoke(vars_with_history)

            # Basic JSON cleaning
            cleaned = response.strip()
            if cleaned.startswith("```json"): cleaned = cleaned[7:]
            if cleaned.startswith("```"): cleaned = cleaned[3:]
            if cleaned.endswith("```"): cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            action = data.get("action")

            if action == "FINISH":
                # Log Finish
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n[Step {i + 1}] FINISHED\n")
                return data

            if action in AVAILABLE_TOOLS:
                print(f"      [Tool] Calling {action} with {data.get('args')}")
                tool_out = execute_tool(action, data.get("args", {}))

                # Truncate tool output if too long
                if len(str(tool_out)) > 1000:
                    tool_out_hist = str(tool_out)[:1000] + "...(truncated)"
                else:
                    tool_out_hist = str(tool_out)

                # Log Step
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n[Step {i + 1}] Action: {action}\n")
                    f.write(f"Args: {data.get('args')}\n")
                    f.write(f"Result: {tool_out_hist}\n")

                history.append(f"Action: {action}\nArgs: {data.get('args')}\nResult: {tool_out_hist}\n")
            else:
                history.append(f"Error: Unknown action {action}")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n[Step {i + 1}] Error: Unknown action {action}\n")

        except json.JSONDecodeError:
            print(f"      [Error] Invalid JSON from LLM: {response[:50]}...")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n[Error] Invalid JSON received: {response}\n")
            history.append(f"System: You produced invalid JSON. Please correct it.")
        except Exception as e:
            print(f"      [Error] {e}")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n[Error] Exception: {e}\n")
            history.append(f"System: Error occurred: {e}")

    # --- FALLBACK: Max steps reached ---
    print(f"      [System] Max steps ({max_steps}) reached. Forcing final analysis.")
    history.append("System: You have reached the maximum number of tool calls. You MUST now produce the final technical analysis based on the information you have. Do not call any more tools. Output the final JSON with action='FINISH'.")

    # One last chance to produce the answer
    history_str = "\n".join(history)
    vars_with_history = {**initial_vars, "history": history_str}
    
    try:
        response = chain.invoke(vars_with_history)
        cleaned = response.strip()
        if cleaned.startswith("```json"): cleaned = cleaned[7:]
        if cleaned.startswith("```"): cleaned = cleaned[3:]
        if cleaned.endswith("```"): cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        
        # If the agent still tries to call a tool, we just return the raw text as analysis
        if data.get("action") == "FINISH":
             return data
        else:
             # It tried to call a tool again or something else
             return {"action": "FINISH", "analysis": str(data)}

    except Exception as e:
        # If it fails to produce JSON, we return the raw text
        return {"action": "FINISH", "analysis": str(response)}


def run_research_phase(llm, code, context):
    print("    [Phase 1] Researching...")

    tools_desc = get_tools_description()

    result = run_agent_loop(
        llm,
        RESEARCH_LOOP_PROMPT,
        {
            "code": code,
            "context": context,
            "tools_info": tools_desc
        },
        max_steps=5
    )
    return result.get("analysis", "No analysis produced.")


def run_impact_phase(llm, symbol_id, code, analysis):
    print("    [Phase 3] Analyzing Impact...")

    tools_desc = get_tools_description()

    result = run_agent_loop(
        llm,
        IMPACT_LOOP_PROMPT,
        {
            "symbol_id": symbol_id,
            "code": code,
            "analysis": analysis,
            "tools_info": tools_desc
        },
        max_steps=5
    )
    return result.get("impact_instructions", [])


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

        print(f"\nProcessing {base_name} with Agentic Research Pipeline...")

        changed_file_symbols.sort(key=lambda s: s.start)

        for sym in changed_file_symbols:
            print(f"  > Symbol: {sym.qualname}")

            try:
                full_lines = Path(sym.file).read_text(encoding="utf-8").splitlines()
                code_segment = "\n".join(full_lines[sym.start - 1:sym.end])
            except Exception as e:
                print(f"    Fehler beim Lesen: {e}")
                continue

            # 1. Pipeline: RESEARCH
            # Get basic RAG context first
            query_vec = embedder.encode([sym.qualname])
            results = store.search(query_vec, k=5)
            context_lines = [f"- {res['qualname']} ({res['kind']}) from {res['file']}" for res in results if
                             res['qualname'] != sym.qualname]
            context_str = "\n".join(context_lines) if context_lines else "No related context found."

            analysis = run_research_phase(llm, code_segment, context_str)

            # 2. Pipeline: DOCS GENERATION
            print("    [Phase 2] Generating Docs...")
            docs_chain = DOCS_EXPERT_PROMPT | llm | StrOutputParser()
            docs = docs_chain.invoke({"analysis": analysis, "existing_docs": ""})

            # Write Docs
            writer.write_section(file_path=md_file_path, symbol_id=sym.symbol_id, content=docs)

            # 3. Pipeline: IMPACT ANALYSIS
            impact_instructions = run_impact_phase(llm, sym.symbol_id, code_segment, analysis)

            if impact_instructions:
                print(f"    [Impact] Found {len(impact_instructions)} dependent symbols to update.")
                for instr in impact_instructions:
                    target_symbol_id = instr.get("symbol_id")
                    print(f"      -> Updating {target_symbol_id}")

                    # Generate update for dependent symbol
                    # We treat the instructions as the "analysis" for the docs expert
                    # And specifically pass the original docs to guide the edit
                    update_docs = docs_chain.invoke({
                        "analysis": f"UPDATE INSTRUCTION: {instr.get('update_instructions')}",
                        "existing_docs": instr.get('original_docs')
                    })

                    # We need to find the correct file for this symbol. 
                    # For simplicty, we scan our writer knowledge or look it up.
                    # HERE: We assume the impact agent might have given us a hint, or we search?
                    # Ideally we have a symbol->file mapping. 'all_symbols' has it.
                    # Find file for target_symbol_id
                    target_file = None
                    for s in all_symbols:
                        if s.symbol_id == target_symbol_id:
                            target_file = s.file
                            break

                    if target_file:
                        # Construct MD path for target
                        src_index_t = target_file.rfind("src")
                        file_path_split_t = target_file[src_index_t:].split(os.sep)
                        md_file_name_t = "_".join(file_path_split_t[1:]).replace(".py", ".md")
                        md_file_path_t = Path(DOCS_ROOT, md_file_name_t)

                        writer.write_section(file_path=md_file_path_t, symbol_id=target_symbol_id, content=update_docs)
                        writer.reorder_sections(md_file_path_t, [s.symbol_id for s in all_symbols_by_file[target_file]])
                    else:
                        print(f"      [Warning] Could not find file for symbol {target_symbol_id}")

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
