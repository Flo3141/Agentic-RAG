"""Markdown writer with idempotent section updates for visual verification."""
from pathlib import Path
import re


class MarkdownWriter:
    def __init__(self, docs_root: Path):
        """
        Initializes the writer with the base directory for documentation.
        """
        self.docs_root = docs_root

    def write_section(self, file_path: Path, symbol_id: str, content: str):
        """
        Inserts a documentation section or updates an existing one.
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing content or start with a default header
        if file_path.exists():
            text = file_path.read_text(encoding="utf-8")
        else:
            text = f"# API Documentation: {file_path.stem}\n\n"

        start_marker = f"<!-- BEGIN: auto:{symbol_id} -->"
        end_marker = f"<!-- END: auto:{symbol_id} -->"

        # Creation of the new block
        new_section = f"{start_marker}\n{content}\n{end_marker}"

        # Regular expression to find an existing block between the markers
        # re.DOTALL ensures that the dot (.) also matches newlines
        pattern = re.compile(
            rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
            re.DOTALL
        )

        if pattern.search(text):
            # Replace existing section
            print(f"  [Writer] Updating section: {symbol_id}")
            text = pattern.sub(new_section, text)
        else:
            # Append new section at the end of the file
            print(f"  [Writer] Adding new section: {symbol_id}")
            text += f"\n\n{new_section}\n\n---"

        file_path.write_text(text, encoding="utf-8")

    def reorder_sections(self, file_path: Path, ordered_symbol_ids: list[str]):
        """
        Reorders the sections in the file based on the passed list.
        Also removes blocks that are no longer in the list.
        """
        if not file_path.exists():
            return

        text = file_path.read_text(encoding="utf-8")

        # 1. Extract header (everything before the first BEGIN block)
        # We look for the first start marker
        first_marker_match = re.search(r"<!-- BEGIN: auto:.*? -->", text)
        if not first_marker_match:
            # No blocks found, nothing to do
            return

        header = text[:first_marker_match.start()].strip()

        # 2. Extract all blocks
        # Regex for complete blocks: matches BEGIN...END
        block_pattern = re.compile(
            r"(<!-- BEGIN: auto:(?P<id>[^ ]+) -->.*?<!-- END: auto:(?P=id) -->)",
            re.DOTALL
        )

        blocks = {}
        for match in block_pattern.finditer(text):
            symbol_id = match.group("id")
            content = match.group(0)
            blocks[symbol_id] = content

        # 3. Reassemble file
        new_content_parts = [header]

        for sym_id in ordered_symbol_ids:
            if sym_id in blocks:
                new_content_parts.append(blocks[sym_id])

        # Join with separators
        new_text = "\n\n".join(new_content_parts)
        if not new_text.endswith("\n"):
            new_text += "\n"

        file_path.write_text(new_text, encoding="utf-8")
        print(f"  [Writer] Reordered sections in: {file_path}")