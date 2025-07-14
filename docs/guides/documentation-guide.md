# Documentation Guide

This guide explains how to work with the SSH Tools Suite documentation, built with MkDocs and Material theme.

## Structure

```
docs/
├── index.md                    # Homepage
├── getting-started/            # Installation and quick start
├── ssh-tunnel-manager/         # SSH Tunnel Manager module documentation  
├── third-party-installer/      # Third Party Installer module documentation
├── guides/                     # User guides and tutorials
├── reference/                  # Auto-generated API reference
└── gen_ref_nav.py             # API reference generator
```

## Building Documentation

### Prerequisites

Install documentation dependencies:

```bash
pip install -e .[docs]
# or
pip install mkdocs mkdocs-material mkdocstrings[python]
```

### Local Development

Serve documentation locally with auto-reload:

```bash
mkdocs serve
```

Visit http://localhost:8000 to view the documentation.

### Building for Production

Build static documentation:

```bash
mkdocs build
```

Output will be in the `site/` directory.

## Writing Documentation

### Adding New Pages

1. Create a new `.md` file in the appropriate directory
2. Add the page to `mkdocs.yml` navigation
3. Use Material theme features and extensions

### API Documentation

API reference is auto-generated from docstrings using mkdocstrings. Ensure your code has proper docstrings:

```python
def example_function(param: str) -> bool:
    """
    Brief description of the function.
    
    Args:
        param: Description of the parameter.
        
    Returns:
        Description of the return value.
        
    Raises:
        ValueError: When something goes wrong.
    """
    pass
```

### Code Examples

Use syntax highlighting for code blocks:

````markdown
```python
from ssh_tunnel_manager import TunnelConfig

config = TunnelConfig(
    name="example",
    ssh_host="localhost"
)
```
````

### Admonitions

Use admonitions for important information:

```markdown
!!! note "Important Note"
    This is an important note.

!!! warning "Warning"
    This is a warning.

!!! danger "Critical"
    This is critical information.
```

## Style Guide

- Use clear, concise language
- Include practical examples
- Test all code examples
- Use consistent formatting
- Add cross-references between related topics
- Include troubleshooting information where relevant

## Contributing

1. Follow the existing structure and style
2. Test documentation locally before submitting
3. Include examples for new features
4. Update navigation in `mkdocs.yml` if adding new sections
