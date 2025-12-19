from pathlib import Path
from typing import List, NamedTuple
import sys

IGNORE = [".venv", "site-packages", "build", "dist", "__pycache__", ".git", ".idea", ".vscode"]


class RawChunk(NamedTuple):
    file: str
    chunk_id: int
    start_line: int
    end_line: int
    content: str


def collect_py_files(root: str) -> list[Path]:
    r = Path(root)
    files = []
    for p in r.rglob("*.py"):
        if any(x in p.parts for x in IGNORE):
            continue
        files.append(p)
    return files


def parse_raw_file(path: Path) -> List[RawChunk]:
    try:
        src = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error parsing {path}: {e}")
        return []

    lines = src.splitlines()
    chunks = []
    # NAIVE APPROACH: Fixed chunk size of 50 lines
    # This often cuts functions in half, losing the signature/decorators
    CHUNK_SIZE = 50

    for i in range(0, len(lines), CHUNK_SIZE):
        end = min(i + CHUNK_SIZE, len(lines))
        segment_lines = lines[i:end]
        segment = "\n".join(segment_lines)

        chunks.append(RawChunk(
            file=str(path),
            chunk_id=i // CHUNK_SIZE,
            start_line=i + 1,
            end_line=end,
            content=segment,
        ))
    return chunks


def index_repo_raw(root: str) -> List[RawChunk]:
    """
    Simulates the naive indexing strategy.
    """
    src_root = Path(root)
    files = collect_py_files(str(src_root))
    all_chunks = []

    print(f"Indexing {len(files)} files in {src_root} using naive chunking...")

    for f in files:
        chunks = parse_raw_file(f)
        all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "../sample_project"
    results = index_repo_raw(root_dir)
    print(f"Generated {len(results)} raw chunks.")
    # Print the first chunk to show context loss
    if results:
        print("\n--- Example Raw Chunk ---")
        print(f"File: {results[0].file}")
        print(f"Lines: {results[0].start_line}-{results[0].end_line}")
        print(results[0].content[:200] + "...")