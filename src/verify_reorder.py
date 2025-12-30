import re
from pathlib import Path
from markdown_writer import MarkdownWriter
import tempfile
import os

def test_reorder_sections():
    # Setup temporary directory and file
    with tempfile.TemporaryDirectory() as tmpdirname:
        docs_root = Path(tmpdirname)
        writer = MarkdownWriter(docs_root)
        
        test_file = docs_root / "test_doc.md"
        
        # Initial content with out-of-order blocks and some extra text
        initial_content = """# Title

Description here.

<!-- BEGIN: auto:func_c -->
### func_c
Doc for C
<!-- END: auto:func_c -->

<!-- BEGIN: auto:func_a -->
### func_a
Doc for A
<!-- END: auto:func_a -->

<!-- BEGIN: auto:func_b -->
### func_b
Doc for B
<!-- END: auto:func_b -->
"""
        test_file.write_text(initial_content, encoding="utf-8")
        
        print("Initial content written.")
        
        # Define the desired order
        ordered_ids = ["func_a", "func_b", "func_c"]
        
        # Call reorder
        writer.reorder_sections(test_file, ordered_ids)
        
        # Verify
        new_content = test_file.read_text(encoding="utf-8")
        print("\n--- New Content ---")
        print(new_content)
        print("-------------------")
        
        # Checks
        # 1. Header check
        assert new_content.startswith("# Title\n\nDescription here."), "Header preserved failed"
        
        # 2. Order check
        pos_a = new_content.find("<!-- BEGIN: auto:func_a -->")
        pos_b = new_content.find("<!-- BEGIN: auto:func_b -->")
        pos_c = new_content.find("<!-- BEGIN: auto:func_c -->")
        
        assert pos_a != -1 and pos_b != -1 and pos_c != -1, "Blocks missing"
        assert pos_a < pos_b < pos_c, f"Order incorrect: A({pos_a}) < B({pos_b}) < C({pos_c})"
        
        # 3. Removal check (simulate a removed symbol)
        ordered_ids_subset = ["func_a", "func_c"] # func_b removed
        writer.reorder_sections(test_file, ordered_ids_subset)
        new_content_subset = test_file.read_text(encoding="utf-8")
        
        assert "func_b" not in new_content_subset, "func_b should have been removed"
        assert "func_a" in new_content_subset and "func_c" in new_content_subset, "a and c should remain"
        
        print("\nAll tests passed!")

if __name__ == "__main__":
    test_reorder_sections()
