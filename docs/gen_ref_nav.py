"""Generate API reference documentation for mkdocs."""
import os
from pathlib import Path

import mkdocs_gen_files

# Define the source directory
src_dir = Path("src")
nav_file = mkdocs_gen_files.open("reference/SUMMARY.md", "w")

print("# API Reference", file=nav_file)
print("", file=nav_file)

# Skip these files/modules that cause issues
SKIP_FILES = {
    "__init__.py",
    "__main__.py",  # Skip main files as they're not typically documented
    "vlc_icon.py",  # Skip icon files
    "setup.py",     # Skip setup files
}

SKIP_MODULES = {
    "ssh_tunnel_manager.gui.assets.vlc_icon",  # Icon file that causes import issues
    "third_party_installer.setup",  # Setup file
}

# Skip modules that contain only data or cause import issues
SKIP_PATTERNS = [
    "assets",  # Skip asset directories
    "test",    # Skip test directories  
    "tests",   # Skip test directories
]

# Generate documentation for each module
for path in sorted(src_dir.rglob("*.py")):
    if path.name in SKIP_FILES:
        continue
    
    # Skip paths containing patterns
    if any(pattern in str(path) for pattern in SKIP_PATTERNS):
        continue
    
    # Convert file path to module path
    module_path = path.relative_to(src_dir).with_suffix("")
    doc_path = path.relative_to(src_dir).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)
    
    # Convert to module name
    module_name = str(module_path).replace(os.sep, ".")
    
    # Skip problematic modules
    if module_name in SKIP_MODULES:
        continue
    
    # Create the documentation file
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        print(f"# {module_name}", file=fd)
        print("", file=fd)
        print(f"::: {module_name}", file=fd)
    
    # Add to navigation with proper path formatting
    parts = list(module_path.parts)
    indent = "  " * (len(parts) - 1)
    # Fix path separators for cross-platform compatibility
    nav_doc_path = str(doc_path).replace("\\", "/")
    print(f"{indent}* [{parts[-1]}]({nav_doc_path})", file=nav_file)

nav_file.close()

# Create a main reference index page
with mkdocs_gen_files.open("reference/index.md", "w") as index_file:
    print("# API Reference", file=index_file)
    print("", file=index_file)
    print("This section contains auto-generated API documentation for all SSH Tools Suite modules.", file=index_file)
    print("", file=index_file)
    print("## Navigation", file=index_file)
    print("", file=index_file)
    print("Use the navigation menu to browse through the different modules:", file=index_file)
    print("", file=index_file)
    print("- **ssh_tools_common**: Common utilities and shared code", file=index_file)
    print("- **ssh_tunnel_manager**: Main SSH tunnel management functionality", file=index_file)
    print("  - **core**: Core tunnel management logic", file=index_file)
    print("  - **gui**: Graphical user interface components", file=index_file)
    print("  - **utils**: Utility functions and helpers", file=index_file)
    print("- **third_party_installer**: Third-party software installation tools", file=index_file)
    print("", file=index_file)
    print("## Module Overview", file=index_file)
    print("", file=index_file)
    print("Each module page contains:", file=index_file)
    print("", file=index_file)
    print("- **Classes and Functions**: Complete API documentation", file=index_file)
    print("- **Docstrings**: Detailed descriptions and usage examples", file=index_file)
    print("- **Type Hints**: Parameter and return type information", file=index_file)
    print("- **Source Code**: Links to source code when available", file=index_file)
