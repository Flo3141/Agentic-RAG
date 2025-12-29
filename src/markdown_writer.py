"""Markdown writer with idempotent section updates for visual verification."""
from pathlib import Path
import re


class MarkdownWriter:
    def __init__(self, docs_root: Path):
        """
        Initialisiert den Writer mit dem Basisverzeichnis für die Dokumentation.
        """
        self.docs_root = docs_root

    def write_section(self, file_path: Path, symbol_id: str, content: str):
        """
        Fügt eine Dokumentationssektion ein oder aktualisiert eine bestehende.
        """
        # Sicherstellen, dass das Zielverzeichnis existiert
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Bestehenden Inhalt laden oder mit einer Standardüberschrift starten
        if file_path.exists():
            text = file_path.read_text(encoding="utf-8")
        else:
            text = f"# API Documentation: {file_path.stem}\n\n"

        # Definition der Marker genau nach Ihren Vorgaben
        start_marker = f"<!-- BEGIN: auto:{symbol_id} -->"
        end_marker = f"<!-- END: auto:{symbol_id} -->"

        # Erstellung des neuen Blocks
        new_section = f"{start_marker}\n{content}\n{end_marker}"

        # Regulärer Ausdruck, um einen bestehenden Block zwischen den Markern zu finden
        # re.DOTALL sorgt dafür, dass der Punkt (.) auch Zeilenumbrüche matcht
        pattern = re.compile(
            rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
            re.DOTALL
        )

        if pattern.search(text):
            # Vorhandene Sektion chirurgisch ersetzen
            print(f"  [Writer] Updating section: {symbol_id}")
            text = pattern.sub(new_section, text)
        else:
            # Neue Sektion am Ende der Datei anhängen
            print(f"  [Writer] Adding new section: {symbol_id}")
            text += f"\n\n{new_section}\n\n---"

        # Datei mit den Änderungen speichern
        file_path.write_text(text, encoding="utf-8")