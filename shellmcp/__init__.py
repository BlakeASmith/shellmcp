"""ShellMCP - Expose Shell Commands as MCP tools."""

__version__ = "0.1.0"

# Import LSP components for easy access
try:
    from .lsp.server import create_server
    from .lsp.schema import SCHEMA
    __all__ = ["create_server", "SCHEMA"]
except ImportError:
    # LSP dependencies not available
    __all__ = []