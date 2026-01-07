from pathlib import Path
from langchain_core.tools import tool
from config import DOCS_ROOT, REPO_ROOT

@tool
def search_code(search_string: str) -> str:
    """
    Search for a string in all files in the code directory.
    Returns the relative file path in the repository with the line which contains the string
    
    Args:
        search_string: The string to search for. Must not be "None"
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
                    if search_string in line:
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