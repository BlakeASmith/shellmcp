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

# Completion kind mapping
COMPLETION_KINDS = {
    # Root level keys
    "server": CompletionItemKind.Module,
    "tools": CompletionItemKind.Module,
    "resources": CompletionItemKind.Module,
    "prompts": CompletionItemKind.Module,
    "args": CompletionItemKind.Module,
    
    # Properties
    "name": CompletionItemKind.Property,
    "desc": CompletionItemKind.Property,
    "version": CompletionItemKind.Property,
    "env": CompletionItemKind.Property,
    "cmd": CompletionItemKind.Property,
    "help-cmd": CompletionItemKind.Property,
    "args": CompletionItemKind.Property,
    "uri": CompletionItemKind.Property,
    "mime_type": CompletionItemKind.Property,
    "file": CompletionItemKind.Property,
    "text": CompletionItemKind.Property,
    "template": CompletionItemKind.Property,
    "help": CompletionItemKind.Property,
    "type": CompletionItemKind.Property,
    "default": CompletionItemKind.Property,
    "choices": CompletionItemKind.Property,
    "pattern": CompletionItemKind.Property,
    "ref": CompletionItemKind.Property,
    
    # Types
    "string": CompletionItemKind.EnumMember,
    "number": CompletionItemKind.EnumMember,
    "boolean": CompletionItemKind.EnumMember,
    "array": CompletionItemKind.EnumMember,
    
    # YAML keywords
    "true": CompletionItemKind.Keyword,
    "false": CompletionItemKind.Keyword,
    "null": CompletionItemKind.Keyword,
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
    """Provide context-aware autocomplete suggestions."""
    try:
        # Get the document and cursor position
        doc = server.workspace.get_document(params.textDocument.uri)
        line = doc.lines[params.position.line]
        char_pos = params.position.character
        
        # Get the current line up to cursor
        current_line = line[:char_pos]
        
        # Determine completion context
        context = _get_completion_context(current_line, doc, params.position.line)
        
        # Get appropriate completions based on context
        completions = _get_context_completions(context)
        
        return CompletionList(is_incomplete=False, items=completions)
        
    except Exception as e:
        logger.error(f"Error in completion: {e}")
        return CompletionList(is_incomplete=False, items=[])


def _get_completion_context(current_line: str, doc, line_num: int) -> str:
    """Determine the completion context based on current position."""
    # Check if we're completing a key (before colon)
    if ":" not in current_line or current_line.strip().endswith(":"):
        return "key"
    
    # Check if we're completing a value (after colon)
    if ":" in current_line and not current_line.strip().endswith(":"):
        # Look at the key to determine what type of value
        key_part = current_line.split(":")[0].strip()
        
        # Check for type-specific completions
        if key_part == "type":
            return "type_value"
        elif key_part in ["true", "false"]:
            return "boolean_value"
        else:
            return "value"
    
    return "general"


def _get_context_completions(context: str) -> List[CompletionItem]:
    """Get completions based on context."""
    completions = []
    
    if context == "key":
        # Show all possible keys
        for key, detail in COMPLETIONS.items():
            kind = COMPLETION_KINDS.get(key, CompletionItemKind.Keyword)
            completions.append(CompletionItem(
                label=key,
                kind=kind,
                detail=detail
            ))
    
    elif context == "type_value":
        # Show only type values
        type_completions = ["string", "number", "boolean", "array"]
        for key in type_completions:
            if key in COMPLETIONS:
                completions.append(CompletionItem(
                    label=key,
                    kind=CompletionItemKind.EnumMember,
                    detail=COMPLETIONS[key]
                ))
    
    elif context == "boolean_value":
        # Show boolean values
        boolean_completions = ["true", "false"]
        for key in boolean_completions:
            if key in COMPLETIONS:
                completions.append(CompletionItem(
                    label=key,
                    kind=CompletionItemKind.Keyword,
                    detail=COMPLETIONS[key]
                ))
    
    elif context == "value":
        # Show YAML keywords and common values
        value_completions = ["true", "false", "null"]
        for key in value_completions:
            if key in COMPLETIONS:
                completions.append(CompletionItem(
                    label=key,
                    kind=CompletionItemKind.Keyword,
                    detail=COMPLETIONS[key]
                ))
    
    else:
        # Default: show all completions
        for key, detail in COMPLETIONS.items():
            kind = COMPLETION_KINDS.get(key, CompletionItemKind.Keyword)
            completions.append(CompletionItem(
                label=key,
                kind=kind,
                detail=detail
            ))
    
    return completions


def create_server() -> LanguageServer:
    """Create and return the language server instance."""
    return server


if __name__ == "__main__":
    # Run the server
    server.start_io()