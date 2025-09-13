"""ShellMCP - Expose Shell Commands as MCP tools."""

__version__ = "0.1.0"

# Import LSP components for easy access
try:
    from .lsp.server import create_server
    __all__ = ["create_server"]
except ImportError:
    # LSP dependencies not available
    __all__ = []