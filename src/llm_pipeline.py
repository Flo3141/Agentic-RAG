import sys
from collections import defaultdict
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from src.symbols_ast import index_repo_ast
from src.symbols_raw import index_repo_raw

# --- 1. LLM & Prompt Konfiguration ---
LLM_API_BASE = "http://localhost:11434/v1"
LLM_MODEL_NAME = "qwen3:4b"
LLM_API_KEY = "ollama"


class APILLM(ChatOpenAI):
    def __init__(self, base_url: str, api_key: str, model_name: str, **kwargs):
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            model=model_name,
            **kwargs
        )


# --- PROMPTS ---
from src.prompts import CODE_EXPERT_PROMPT, DOCS_EXPERT_PROMPT
def generate_docs_no_context(llm, code_segment: str):
    # Analyse with empty context
    analyze_chain = CODE_EXPERT_PROMPT | llm | StrOutputParser()
    analysis = analyze_chain.invoke({"code": code_segment, "context": "No external context available."})

    # Generate Markdown
    docs_chain = DOCS_EXPERT_PROMPT | llm | StrOutputParser()
    markdown = docs_chain.invoke({"analysis": analysis, "existing_docs": ""})

    return markdown

def evaluate_raw(root_dir: str, llm):
    print("\n--- Naive Raw Chunking ---")
    chunks = index_repo_raw(root_dir)

    # Group per script
    chunks_by_file = defaultdict(list)
    for chunk in chunks:
        chunks_by_file[chunk.file].append(chunk)

    for file_path, file_chunks in chunks_by_file.items():
        if "core.py" not in str(file_path): continue  # Fokus on core.py for comparison

        base_name = Path(file_path).stem
        out_name = f"docs_naive_raw_{base_name}.md"

        print(f"Processing {base_name} (Raw Chunks: {len(file_chunks)})")

        with open(out_name, "w", encoding="utf-8") as f:
            f.write(f"# Doku {base_name} (Raw Chunking)\n")
            f.write("> ATTENTION: Code was cut after every 50 lines.\n\n")

        for chunk in file_chunks:
            print(f"  > Chunk {chunk.chunk_id} ({chunk.start_line}-{chunk.end_line})")
            docs = generate_docs_no_context(llm, chunk.content)

            with open(out_name, "a", encoding="utf-8") as f:
                f.write(f"\n## Chunk {chunk.chunk_id} (Lines {chunk.start_line}-{chunk.end_line})\n")
                f.write(docs)
                f.write("\n\n---\n")

def evaluate_ast(root_dir: str, llm):
    print("\n--- AST Parsing ---")
    symbols = index_repo_ast(root_dir)

    # Group per script so that the docu is written in one MD file per script
    symbols_by_file = defaultdict(list)
    for sym in symbols:
        if sym.kind in ("class", "function", "method"):
            symbols_by_file[sym.file].append(sym)

    for file_path, file_symbols in symbols_by_file.items():
        if "core.py" not in str(file_path): continue

        base_name = Path(file_path).stem
        out_name = f"docs_naive_ast_{base_name}.md"

        print(f"Processing {base_name} (AST Symbols: {len(file_symbols)})")

        with open(out_name, "w", encoding="utf-8") as f:
            f.write(f"# Doku {base_name} (Phase 2: AST Structure)\n")
            f.write("> Code was semantically segmented in functions/classes.\n\n")

        file_symbols.sort(key=lambda s: s.start)

        for sym in file_symbols:
            print(f"  > Symbol {sym.qualname}")

            try:
                full_lines = Path(sym.file).read_text(encoding="utf-8").splitlines()
                code_segment = "\n".join(full_lines[sym.start - 1:sym.end])
            except:
                continue

            docs = generate_docs_no_context(llm, code_segment)

            with open(out_name, "a", encoding="utf-8") as f:
                f.write(f"\n\n")
                f.write(docs)
                f.write("\n---\n")


if __name__ == "__main__":
    llm = APILLM(base_url=LLM_API_BASE, api_key=LLM_API_KEY, model_name=LLM_MODEL_NAME, temperature=0)

    target_dir = "../sample_project"
    if not Path(target_dir).exists():
        print("Sample Project not found!")
        sys.exit(1)

    evaluate_raw(target_dir, llm)
    evaluate_ast(target_dir, llm)