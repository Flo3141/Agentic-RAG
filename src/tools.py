from typing import Optional
from pathlib import Path
from langchain_core.tools import tool
from config import DOCS_ROOT, REPO_ROOT

@tool
def list_directory(dir_path: str = REPO_ROOT) -> str:
    """List the contents of a directory.
    
    Args:
        dir_path: The path to the directory. Defaults to code repository root specified in config.
    """
    try:
        path = Path(dir_path)
        if not path.exists():
            return f"Error: Directory {dir_path} does not exist."
        
        items = []
        for item in path.iterdir():
            prefix = "[DIR] " if item.is_dir() else "[FILE]"
            items.append(f"{prefix} {item.name}")
        return "\n".join(sorted(items))
    except Exception as e:
        return f"Error listing directory: {e}"

@tool
def search_code(symbol_name: str) -> str:
    """Search for a string in all files in the code directory.
    
    Args:
        symbol_name: The string to search for.
    """
    usages = []
    try:
        root = Path(REPO_ROOT)
        # Rekursiv alle .py Dateien durchsuchen
        for file_path in root.rglob("*.py"):
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if symbol_name in line:
                        # Format: relative_path:line_no: content (stripped)
                        try:
                            relative_path = file_path.relative_to(root)
                        except ValueError:
                            relative_path = file_path.name
                        
                        usages.append(f"{relative_path}:{i+1}: {line.strip()}")
                        if len(usages) >= 10:
                            break
            except Exception:
                # Ignore errors reading specific files
                continue
            if len(usages) >= 10:
                break
    except Exception as e:
        print(f"Warning: Could not search usages: {e}")
    
    return "\n".join(usages) if usages else "No direct usages found."

@tool
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
                return match.group(0) # Return the whole block including markers
        except Exception as e:
            continue
            
    return f"No documentation found for symbol: {symbol_id}"