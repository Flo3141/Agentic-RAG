import os
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI

from src.embed import Embedder
from src.store_qdrant import QdrantStore
from src.markdown_writer import MarkdownWriter

from src.prompts import RESEARCH_LOOP_PROMPT, DOCS_EXPERT_PROMPT
from src.tools import search_code
from src.util import get_doc_for_symbol, run_indexing, git_commit_and_push_changes
from src.config import LLM_API_BASE, LLM_MODEL_NAME, LLM_API_KEY, DOCS_ROOT, REPO_ROOT, QDRANT_DATA_PATH

# Tool Mapping
AVAILABLE_TOOLS = {
    "search_code": search_code,
}

class APILLM(ChatOpenAI):
    def __init__(self, base_url: str, api_key: str, model_name: str, **kwargs):
        super().__init__(base_url=base_url, api_key=api_key, model=model_name, **kwargs)


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
            thought = data.get("thought", "No reasoning provided.")

            if action == "FINISH":
                # Log Finish
                analysis = data.get("analysis", "No analysis provided.")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n[Step {i + 1}] Reasoning: {thought}\n")
                    f.write(f"[Step {i + 1}] Analysis: {analysis}\n")

                    f.write(f"[Step {i + 1}] FINISHED\n")
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
                    f.write(f"\n[Step {i + 1}] Reasoning: {thought}\n")
                    f.write(f"[Step {i + 1}] Action: {action}\n")
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


def process_pipeline(llm, test_run=False):
    embedder = Embedder()
    store = QdrantStore(index_path=Path(QDRANT_DATA_PATH), collection_name="eval_repo")
    writer = MarkdownWriter(DOCS_ROOT)

    # Index repository
    all_symbols, changed_symbols, changed_files_list = run_indexing(REPO_ROOT, embedder, store, test_run)

    changed_symbols_by_file = defaultdict(list)
    all_symbols_by_file = defaultdict(list)
    for sym in changed_symbols:
        changed_symbols_by_file[sym.file].append(sym)

    for sym in all_symbols:
        all_symbols_by_file[sym.file].append(sym)

    # Iterate over actual changed files (including deletions)
    for file_path_path in changed_files_list:
        file_path = str(file_path_path)
        
        # Generates the MD file name
        # The name will be all directories and the final file joined with "_"
        # So all MD files can be found in the top level of the DOCS_ROOT
        # ONLY THE FILES WITHIN THE SRC FOLDER OF THE REPO_ROOT WILL BE DOCUMENTED
        if "src" not in file_path:
            continue

        src_index = file_path.rfind("src")
        file_path_split = file_path[src_index:].split(os.sep)
        md_file_name = "_".join(file_path_split[1:]).replace(".py", ".md")
        md_file_path = Path(DOCS_ROOT, md_file_name)

        base_name = Path(file_path).stem

        print(f"\nProcessing {base_name} with Agentic Research Pipeline...")

        changed_file_symbols = changed_symbols_by_file.get(file_path, [])
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
            docs = docs_chain.invoke({"analysis": analysis})

            # Write Docs
            writer.write_section(file_path=md_file_path, symbol_id=sym.symbol_id, content=docs)

        # Reorder the sections after all updates are done
        all_file_symbols = all_symbols_by_file.get(file_path, [])
        all_file_symbols.sort(key=lambda s: s.start)
        writer.reorder_sections(file_path=md_file_path, ordered_symbol_ids=[s.symbol_id for s in all_file_symbols])

    store.close()
    if not test_run:
        git_commit_and_push_changes()


if __name__ == "__main__":
    llm = APILLM(base_url=LLM_API_BASE, api_key=LLM_API_KEY, model_name=LLM_MODEL_NAME, temperature=0)

    if not Path(REPO_ROOT).exists():
        print(f"Fehler: Ordner '{REPO_ROOT}' nicht gefunden.")
        sys.exit(1)

    process_pipeline(llm)
