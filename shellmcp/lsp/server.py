"""LSP server focused on simple autocomplete for shellmcp YAML files."""

import logging
from typing import List

from pygls.lsp.methods import (
    COMPLETION,
    INITIALIZE,
)
from pygls.lsp.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    InitializeParams,
)
from pygls.server import LanguageServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = LanguageServer("shellmcp-lsp", "0.1.0")

# ShellMCP completions - focused on simple values
COMPLETIONS = {
    # Root level keys
    "server": "Server configuration",
    "tools": "Tool definitions", 
    "resources": "Resource definitions",
    "prompts": "Prompt definitions",
    "args": "Reusable argument definitions",
    
    # Server properties
    "name": "Server name",
    "desc": "Server description",
    "version": "Server version",
    "env": "Environment variables",
    
    # Tool properties
    "cmd": "Shell command",
    "help-cmd": "Command to get help text",
    "args": "Tool arguments",
    
    # Resource properties
    "uri": "Resource URI",
    "mime_type": "MIME type",
    "file": "File path",
    "text": "Direct text content",
    
    # Prompt properties
    "template": "Template content",
    
    # Argument properties
    "help": "Help text",
    "type": "Argument type",
    "default": "Default value",
    "choices": "Allowed values",
    "pattern": "Regex pattern",
    "ref": "Reference to reusable argument",
    
    # Simple types
    "string": "Text value",
    "number": "Numeric value", 
    "boolean": "True/false value",
    "array": "List of values",
    
    # YAML keywords
    "true": "YAML true",
    "false": "YAML false",
    "null": "YAML null",
}


@server.feature(INITIALIZE)
def initialize(params: InitializeParams):
    """Initialize the language server."""
    return {
        "capabilities": {
            "completionProvider": {
                "resolveProvider": False,
                "triggerCharacters": [":", " "]
            }
        }
    }


@server.feature(COMPLETION)
def completion(params: CompletionParams) -> CompletionList:
    """Provide simple autocomplete suggestions."""
    try:
        completions = []
        
        # Add all available completions
        for key, detail in COMPLETIONS.items():
            # Determine completion kind based on key
            if key in ["server", "tools", "resources", "prompts", "args"]:
                kind = CompletionItemKind.Module
            elif key in ["name", "desc", "version", "env", "cmd", "help-cmd", "args", "uri", "mime_type", "file", "text", "template", "help", "type", "default", "choices", "pattern", "ref"]:
                kind = CompletionItemKind.Property
            elif key in ["string", "number", "boolean", "array"]:
                kind = CompletionItemKind.EnumMember
            else:
                kind = CompletionItemKind.Keyword
            
            completions.append(CompletionItem(
                label=key,
                kind=kind,
                detail=detail
            ))
        
        return CompletionList(is_incomplete=False, items=completions)
        
    except Exception as e:
        logger.error(f"Error in completion: {e}")
        return CompletionList(is_incomplete=False, items=[])


def create_server() -> LanguageServer:
    """Create and return the language server instance."""
    return server


if __name__ == "__main__":
    # Run the server
    server.start_io()