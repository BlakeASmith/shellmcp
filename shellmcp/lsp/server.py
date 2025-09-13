"""LSP server focused on autocomplete for shellmcp YAML files."""

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

# ShellMCP completions
COMPLETIONS = {
    # Root level
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
    "cmd": "Shell command (supports Jinja2 templates)",
    "help-cmd": "Command to get help text",
    "args": "Tool arguments",
    
    # Resource properties
    "uri": "Resource URI",
    "mime_type": "MIME type",
    "file": "File path",
    "text": "Direct text content",
    
    # Prompt properties
    "template": "Jinja2 template content",
    
    # Argument properties
    "help": "Help text",
    "type": "Argument type",
    "default": "Default value",
    "choices": "Allowed values",
    "pattern": "Regex pattern",
    "ref": "Reference to reusable argument",
    
    # Types
    "string": "Text value",
    "number": "Numeric value", 
    "boolean": "True/false value",
    "array": "List of values",
    
    # YAML keywords
    "true": "YAML true",
    "false": "YAML false",
    "null": "YAML null",
}


class ShellMCPLanguageServer(LanguageServer):
    """LSP server focused on autocomplete for shellmcp YAML files."""
    
    def __init__(self):
        super().__init__("shellmcp-lsp", "0.1.0")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up LSP method handlers."""
        self.feature(INITIALIZE)(self._initialize)
        self.feature(COMPLETION)(self._completion)
    
    def _initialize(self, params: InitializeParams):
        """Initialize the language server."""
        return {
            "capabilities": {
                "completionProvider": {
                    "resolveProvider": False,
                    "triggerCharacters": [":", " ", "-", "{", "%"]
                }
            }
        }
    
    def _completion(self, params: CompletionParams) -> CompletionList:
        """Provide autocomplete suggestions."""
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
            
            # Add Jinja2 template completions
            jinja2_completions = [
                ("{{", "Variable interpolation"),
                ("{%", "Control structure"),
                ("{#", "Comment"),
                ("if", "If statement"),
                ("else", "Else clause"),
                ("elif", "Else if clause"),
                ("endif", "End if"),
                ("for", "For loop"),
                ("endfor", "End for"),
                ("set", "Variable assignment"),
                ("now", "Current timestamp"),
            ]
            
            for key, detail in jinja2_completions:
                completions.append(CompletionItem(
                    label=key,
                    kind=CompletionItemKind.Keyword,
                    detail=f"Jinja2: {detail}"
                ))
            
            return CompletionList(is_incomplete=False, items=completions)
            
        except Exception as e:
            logger.error(f"Error in completion: {e}")
            return CompletionList(is_incomplete=False, items=[])


def create_server() -> ShellMCPLanguageServer:
    """Create and return a new language server instance."""
    return ShellMCPLanguageServer()


if __name__ == "__main__":
    # Run the server
    server = create_server()
    server.start_io()