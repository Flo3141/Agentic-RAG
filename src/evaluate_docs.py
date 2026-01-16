
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# Ensure project root is in sys.path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import project modules
from src import config
from src.symbols_ast import parse_symbols_file, Symbol

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
EVALUATION_PROMPT = PromptTemplate(
    input_variables=["code", "doc"],
    template="""You are an expert code reviewer and documentation auditor.
Your task is to evaluate how accurately the provided DOCUMENTATION describes the provided SOURCE CODE.

SOURCE CODE:
```python
{code}
```

DOCUMENTATION:
```markdown
{doc}
```

INSTRUCTIONS:
1. Compare the code logic, parameters, return values, and exceptions with the documentation.
2. Identify inaccuracies, missing information, or hallucinations.
3. Provide a concise critique explaining the issues.
4. If there are no issues, state that the documentation is accurate.
"""
)

class DocEvaluator:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=config.LLM_API_BASE,
            api_key=config.LLM_API_KEY,
            model=config.LLM_MODEL_NAME,
            temperature=0
        )
        self.results = []

    def extract_code_symbols(self, file_path: Path) -> List[Symbol]:
        """Extracts AST symbols from a Python file, ordered by appearance."""
        if not file_path.exists():
            logger.error(f"Code file not found: {file_path}")
            return []
        
        # parse_symbols_file returns symbols sorted by appearance
        symbols = parse_symbols_file(file_path, file_path.parent)
        return symbols

    def parse_markdown_docs(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parses a markdown file and extracts sections.
        Supports two formats:
        1. Explicit Tags: <!-- BEGIN: auto:Name --> ... <!-- END: auto:Name -->
        2. Separators: '---' delimiter. Assumes order matches the AST order.
        
        Returns a list of dicts: {'name': Optional[str], 'content': str}
        """
        if not file_path.exists():
            logger.error(f"Doc file not found: {file_path}")
            return []

        content = file_path.read_text(encoding="utf-8")
        results = []

        # 1. Try Tag-based parsing (Priority)
        # Format: <!-- BEGIN: auto:calculator.core.CalculatorError -->Content...<!-- END: auto:calculator.core.CalculatorError -->
        tag_pattern = re.compile(r"<!-- BEGIN: auto:(?P<name>.*?) -->(?P<content>.*?)<!-- END: auto:.*? -->", re.DOTALL)
        matches = list(tag_pattern.finditer(content))

        if matches:
            logger.info(f"Parsing {file_path.name}: Found {len(matches)} tagged sections.")
            for m in matches:
                results.append({
                    "name": m.group("name").strip(),
                    "content": m.group("content").strip()
                })
            return results

        # 2. Fallback to Separator-based parsing
        # Assumes the file is split by "---", and order matters.
        logger.info(f"Parsing {file_path.name}: No tags found, splitting by '---'.")
        parts = re.split(r"\n-{3,}\n", content)
        # Filter out empty or whitespace-only chunks
        parts = [p.strip() for p in parts if p.strip()]
        
        for p in parts:
            results.append({
                "name": None, # Name is unknown, must rely on order
                "content": p
            })
            
        return results

    def evaluate_pair(self, code_symbol: Symbol, doc_content: str) -> str:
        """Invokes the LLM to evaluate the code vs doc pair."""
        
        try:
            full_lines = Path(code_symbol.file).read_text(encoding="utf-8").splitlines()
            # AST lines are 1-indexed
            code_segment = "\n".join(full_lines[code_symbol.start - 1 : code_symbol.end])
        except Exception as e:
            return f"Could not read code: {e}"

        chain = EVALUATION_PROMPT | self.llm | StrOutputParser()
        return chain.invoke({
            "code": code_segment,
            "doc": doc_content
        })

    def run_comparison(self, code_path: Path, doc_path: Path) -> List[dict]:
        """Runs the full comparison for a file pair."""
        logger.info(f"Comparing {code_path.name} with {doc_path.name}")
        
        # Get ordered lists
        code_symbols = self.extract_code_symbols(code_path)
        doc_sections = self.parse_markdown_docs(doc_path)

        file_results = []
        
        # Check strategy
        has_names = any(bool(d['name']) for d in doc_sections)
        
        if has_names:
            # Match by Name (Robust)
            logger.info("  Strategy: Match by Name")
            doc_map = {d['name']: d['content'] for d in doc_sections if d['name']}
            
            for sym in code_symbols:
                name = sym.qualname
                doc_content = doc_map.get(name)
                
                # Fuzzy fallback (e.g. handle implicit module prefix diffs)
                if not doc_content:
                     # Try simple name
                     simple_name = name.split(".")[-1]
                     for d_name, d_cont in doc_map.items():
                         if d_name.endswith(f".{simple_name}") or d_name == simple_name:
                             doc_content = d_cont
                             break
                
                result_entry = self._process_entry(sym, doc_content, name)
                file_results.append(result_entry)
                
        else:
            # Match by Order (Strict)
            logger.info("  Strategy: Match by Order")
            # We iterate over code symbols and try to pop from doc sections
            # NOTE: If counts mismatch, we might have misalignment.
            
            limit = max(len(code_symbols), len(doc_sections))
            for i in range(limit):
                sym = code_symbols[i] if i < len(code_symbols) else None
                doc_item = doc_sections[i] if i < len(doc_sections) else None
                
                if sym and doc_item:
                    # Both exist - Evaluate
                    result_entry = self._process_entry(sym, doc_item['content'], sym.qualname)
                    result_entry = f"{code_path.name} <-> {doc_path.name}: \n{result_entry}"
                    file_results.append(result_entry)
                
                elif sym and not doc_item:
                    # Code exists, doc missing
                    result_entry = f"{code_path.name} <-> {doc_path.name}: \nDocumentation section missing (end of file reached)."
                    file_results.append(result_entry)
                
                elif not sym and doc_item:
                    # Doc exists, code missing (Hallucination/Stale?)
                    result_entry = f"{code_path.name} <-> {doc_path.name}: \nExtra documentation section found with no corresponding code."
                    file_results.append(result_entry)

        return file_results

    def _process_entry(self, sym, doc_content, name):
        if not doc_content:
             return "Documentation not found for symbol."
        
        logger.info(f"  Evaluating {name}...")
        eval_data = self.evaluate_pair(sym, doc_content)
        return eval_data


def main():
    root_dir = Path("results/eval_results_RTX_3060Ti")
    if not root_dir.exists():
        print(f"Directory not found: {root_dir}")
        return

    evaluator = DocEvaluator()
    all_results = []

    # Defined pairs
    code_new = root_dir / "core_new.py"
    docs_new = [
        root_dir / "calculator_core_llm_new.md",
        root_dir / "calculator_core_rag_new.md",
        root_dir / "calculator_core_agentic_rag_new.md"
    ]
    
    code_update = root_dir / "core_update.py"
    docs_update = [
        root_dir / "calculator_core_rag_update.md",
        root_dir / "calculator_core_agentic_rag_update.md"
    ]

    # Run comparisons
    if code_new.exists():
        for doc in docs_new:
            if doc.exists():
                all_results.extend(evaluator.run_comparison(code_new, doc))
    
    if code_update.exists():
        for doc in docs_update:
            if doc.exists():
                all_results.extend(evaluator.run_comparison(code_update, doc))

    # Output Results
    output_file = root_dir / "evaluation_summary.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Evaluation Results (LLM as a Judge)\n")
        f.write("===================================\n\n")
        
        pair_stats = {}
        
        for res in all_results:
            f.write(res + "\n")
            f.write("-" * 40 + "\n")

    print(f"\nEvaluation complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
