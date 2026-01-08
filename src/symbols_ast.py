import hashlib
import pprint
from pathlib import Path
import ast
from typing import List
from src.types_ast import Symbol

IGNORE = [".venv", "site-packages", "build", "dist", "__pycache__", ".git", ".idea", ".vscode"]


def _sha(s: str) -> str:
    """Berechnet den Hash des Code-Inhalts."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def collect_py_files(root: str) -> list[Path]:
    r = Path(root)
    files = []
    for p in r.rglob("*.py"):
        if any(x in p.parts for x in IGNORE):
            continue
        files.append(Path(p))
    return files


def module_qualname(path: Path, src_root: Path) -> str:
    try:
        rel = path.relative_to(src_root).with_suffix("")
        return ".".join(rel.parts)
    except ValueError:
        return path.stem


def parse_symbols_file(path: Path, src_root: Path) -> list[Symbol]:
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(path))
    except Exception as e:
        print(f"Error parsing {path}: {e}")
        return []

    mod = module_qualname(path, src_root)
    out: list[Symbol] = []
    lines = src.splitlines()

    class V(ast.NodeVisitor):
        def visit_ClassDef(self, n):
            doc = ast.get_docstring(n) or ""
            # take the source code as fingerprint --> make hash so that if the code changes,the hash also changes
            # Then the vector db is only updated, if the hash of a function changes.
            segment = "\n".join(lines[n.lineno - 1:n.end_lineno])
            content_hash = _sha(segment)

            out.append(Symbol(
                symbol_id=f"{mod}.{n.name}",
                kind="class",
                file=str(path),
                qualname=f"{mod}.{n.name}",
                parent=mod,
                start=n.lineno,
                end=n.end_lineno,
                docstring=doc,
                hash=content_hash
            ))
            for item in n.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self.visit_Method(item, f"{mod}.{n.name}")

        def visit_Method(self, n, parent_qualname):
            doc = ast.get_docstring(n) or ""
            segment = "\n".join(lines[n.lineno - 1:n.end_lineno])
            content_hash = _sha(segment)

            out.append(Symbol(
                symbol_id=f"{parent_qualname}.{n.name}",
                kind="method",
                file=str(path),
                qualname=f"{parent_qualname}.{n.name}",
                parent=parent_qualname,
                start=n.lineno,
                end=n.end_lineno,
                docstring=doc,
                hash=content_hash
            ))

        def visit_FunctionDef(self, n):
            doc = ast.get_docstring(n) or ""
            segment = "\n".join(lines[n.lineno - 1:n.end_lineno])
            content_hash = _sha(segment)
            out.append(Symbol(
                symbol_id=f"{mod}.{n.name}",
                kind="function",
                file=str(path),
                qualname=f"{mod}.{n.name}",
                parent=mod,
                start=n.lineno,
                end=n.end_lineno,
                docstring=doc,
                hash=content_hash
            ))

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            V().visit_ClassDef(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            V().visit_FunctionDef(node)

    return out


def index_repo_ast(root: str, changed_files: list[str] | None = None) -> List[Symbol]:
    src_root = Path(root)
    if Path(src_root / "src").exists():
        package_root = Path(src_root / "src")
    else:
        package_root = src_root

    files = collect_py_files(str(package_root))
    all_symbols = []

    print(f"Indexing {len(files)} files in {package_root} using AST...")
    print(changed_files)
    if changed_files is not None:
        for f in files:
            print(f)
            if f in changed_files:
                syms = parse_symbols_file(f, package_root)
                all_symbols.extend(syms)
    else:
        for f in files:
            syms = parse_symbols_file(f, package_root)
            all_symbols.extend(syms)
    return all_symbols
