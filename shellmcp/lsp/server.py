"""LSP server for shellmcp YAML schema validation and completion."""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from jsonschema import Draft7Validator, ValidationError
from pygls.lsp.methods import (
    COMPLETION,
    DID_CHANGE,
    DID_OPEN,
    DID_SAVE,
    HOVER,
    INITIALIZE,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
)
from pygls.lsp.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    Hover,
    HoverParams,
    InitializeParams,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    TextDocumentContentChangeEvent,
    TextDocumentItem,
)
from pygls.server import LanguageServer
from pygls.workspace import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the JSON schema
SCHEMA_PATH = Path(__file__).parent / "schema.json"
with open(SCHEMA_PATH, "r") as f:
    SCHEMA = json.load(f)

# Create validator
VALIDATOR = Draft7Validator(SCHEMA)

# Common YAML keywords and values
YAML_KEYWORDS = {
    "true", "false", "null", "on", "off", "yes", "no"
}

# ShellMCP specific completions
SHELLMCP_COMPLETIONS = {
    "server": {
        "name": "Name of the MCP server",
        "desc": "Description of the server", 
        "version": "Server version (default: 1.0.0)",
        "env": "Environment variables"
    },
    "args": "Reusable argument definitions",
    "tools": "Tool definitions",
    "resources": "Resource definitions", 
    "prompts": "Prompt definitions",
    "type": {
        "string": "Text value (default)",
        "number": "Numeric value (integer or float)",
        "boolean": "True/false value",
        "array": "List of values"
    },
    "choices": "Allowed values for validation",
    "pattern": "Regex pattern for validation",
    "default": "Default value (makes argument optional)",
    "ref": "Reference to reusable argument definition",
    "cmd": "Shell command to execute (supports Jinja2 templates)",
    "desc": "Description",
    "help-cmd": "Command to get help text",
    "help": "Help text or description",
    "name": "Name",
    "uri": "Resource URI",
    "description": "Description",
    "mime_type": "MIME type of the resource",
    "file": "File path to read content from",
    "text": "Direct text content",
    "template": "Direct Jinja2 template content",
    "env": "Environment variables"
}

# Jinja2 template syntax
JINJA2_SYNTAX = {
    "{{": "Variable interpolation",
    "{%": "Control structures (if, for, etc.)",
    "{#": "Comments",
    "}}": "End variable interpolation", 
    "%}": "End control structure",
    "#}": "End comment",
    "if": "Conditional statement",
    "else": "Else clause",
    "elif": "Else if clause",
    "endif": "End if statement",
    "for": "Loop statement",
    "endfor": "End for loop",
    "set": "Variable assignment",
    "filter": "Apply filter",
    "endfilter": "End filter",
    "macro": "Define macro",
    "endmacro": "End macro",
    "block": "Define block",
    "endblock": "End block",
    "extends": "Extend template",
    "include": "Include template",
    "import": "Import macros",
    "from": "Import specific items",
    "with": "With statement",
    "endwith": "End with statement"
}

# Common MIME types
MIME_TYPES = [
    "text/plain",
    "text/markdown", 
    "text/html",
    "text/xml",
    "application/json",
    "application/xml",
    "application/yaml",
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/svg+xml"
]

# Common URI schemes
URI_SCHEMES = [
    "file://",
    "http://",
    "https://",
    "system://",
    "text://",
    "template://",
    "docs://"
]


class ShellMCPLanguageServer(LanguageServer):
    """Language server for shellmcp YAML configuration files."""
    
    def __init__(self):
        super().__init__("shellmcp-lsp", "0.1.0")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up LSP method handlers."""
        self.feature(INITIALIZE)(self._initialize)
        self.feature(TEXT_DOCUMENT_DID_OPEN)(self._did_open)
        self.feature(TEXT_DOCUMENT_DID_CHANGE)(self._did_change)
        self.feature(TEXT_DOCUMENT_DID_SAVE)(self._did_save)
        self.feature(COMPLETION)(self._completion)
        self.feature(HOVER)(self._hover)
    
    def _initialize(self, params: InitializeParams):
        """Initialize the language server."""
        logger.info("Initializing shellmcp LSP server")
        return {
            "capabilities": {
                "textDocumentSync": {
                    "openClose": True,
                    "change": 1,  # Full document sync
                    "save": True
                },
                "completionProvider": {
                    "resolveProvider": False,
                    "triggerCharacters": [":", " ", "-", "{", "%", "#"]
                },
                "hoverProvider": True,
                "diagnosticProvider": {
                    "interFileDependencies": False,
                    "workspaceDiagnostics": False
                }
            }
        }
    
    def _did_open(self, params: TextDocumentItem):
        """Handle document open event."""
        logger.info(f"Document opened: {params.uri}")
        self._validate_document(params.uri)
    
    def _did_change(self, params: TextDocumentContentChangeEvent):
        """Handle document change event."""
        logger.info(f"Document changed: {params.textDocument.uri}")
        self._validate_document(params.textDocument.uri)
    
    def _did_save(self, params: TextDocumentItem):
        """Handle document save event."""
        logger.info(f"Document saved: {params.uri}")
        self._validate_document(params.uri)
    
    def _validate_document(self, uri: str):
        """Validate a YAML document against the schema."""
        try:
            doc = self.workspace.get_document(uri)
            if not doc.source.strip():
                return
            
            # Parse YAML
            try:
                yaml_data = yaml.safe_load(doc.source)
            except yaml.YAMLError as e:
                self._publish_diagnostics(uri, [self._create_yaml_error_diagnostic(str(e))])
                return
            
            if yaml_data is None:
                return
            
            # Validate against schema
            errors = list(VALIDATOR.iter_errors(yaml_data))
            diagnostics = []
            
            for error in errors:
                diagnostic = self._create_schema_error_diagnostic(error, doc)
                if diagnostic:
                    diagnostics.append(diagnostic)
            
            # Additional custom validations
            custom_diagnostics = self._validate_custom_rules(yaml_data, doc)
            diagnostics.extend(custom_diagnostics)
            
            self._publish_diagnostics(uri, diagnostics)
            
        except Exception as e:
            logger.error(f"Error validating document {uri}: {e}")
    
    def _create_yaml_error_diagnostic(self, message: str) -> Diagnostic:
        """Create a diagnostic for YAML parsing errors."""
        return Diagnostic(
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=0)
            ),
            message=f"YAML parsing error: {message}",
            severity=DiagnosticSeverity.Error,
            source="shellmcp-lsp"
        )
    
    def _create_schema_error_diagnostic(self, error: ValidationError, doc: Document) -> Optional[Diagnostic]:
        """Create a diagnostic for schema validation errors."""
        try:
            # Try to find the error location in the document
            path = list(error.absolute_path)
            if not path:
                return None
            
            # Find the line and column for the error
            line, col = self._find_error_location(doc.source, path)
            
            return Diagnostic(
                range=Range(
                    start=Position(line=line, character=col),
                    end=Position(line=line, character=col + 10)
                ),
                message=error.message,
                severity=DiagnosticSeverity.Error,
                source="shellmcp-lsp"
            )
        except Exception:
            return None
    
    def _find_error_location(self, source: str, path: List[Union[str, int]]) -> tuple[int, int]:
        """Find the line and column for a JSON path in YAML source."""
        lines = source.split('\n')
        current_line = 0
        current_col = 0
        
        for i, path_part in enumerate(path):
            if isinstance(path_part, str):
                # Look for the key
                for line_idx, line in enumerate(lines[current_line:], current_line):
                    if f"{path_part}:" in line:
                        current_line = line_idx
                        current_col = line.find(f"{path_part}:")
                        break
            elif isinstance(path_part, int):
                # Look for array item
                array_count = 0
                for line_idx, line in enumerate(lines[current_line:], current_line):
                    stripped = line.strip()
                    if stripped.startswith('- '):
                        if array_count == path_part:
                            current_line = line_idx
                            current_col = line.find('- ')
                            break
                        array_count += 1
        
        return current_line, current_col
    
    def _validate_custom_rules(self, yaml_data: Dict[str, Any], doc: Document) -> List[Diagnostic]:
        """Validate custom rules specific to shellmcp."""
        diagnostics = []
        
        # Validate that resources have exactly one content source
        if "resources" in yaml_data:
            for resource_name, resource in yaml_data["resources"].items():
                content_sources = [k for k in ["cmd", "file", "text"] if k in resource]
                if len(content_sources) == 0:
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=0, character=0)
                        ),
                        message=f"Resource '{resource_name}' must specify exactly one of: cmd, file, or text",
                        severity=DiagnosticSeverity.Error,
                        source="shellmcp-lsp"
                    ))
                elif len(content_sources) > 1:
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=0, character=0)
                        ),
                        message=f"Resource '{resource_name}' can only specify one of: cmd, file, or text",
                        severity=DiagnosticSeverity.Error,
                        source="shellmcp-lsp"
                    ))
        
        # Validate that prompts have exactly one content source
        if "prompts" in yaml_data:
            for prompt_name, prompt in yaml_data["prompts"].items():
                content_sources = [k for k in ["cmd", "file", "template"] if k in prompt]
                if len(content_sources) == 0:
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=0, character=0)
                        ),
                        message=f"Prompt '{prompt_name}' must specify exactly one of: cmd, file, or template",
                        severity=DiagnosticSeverity.Error,
                        source="shellmcp-lsp"
                    ))
                elif len(content_sources) > 1:
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=0, character=0)
                        ),
                        message=f"Prompt '{prompt_name}' can only specify one of: cmd, file, or template",
                        severity=DiagnosticSeverity.Error,
                        source="shellmcp-lsp"
                    ))
        
        return diagnostics
    
    def _publish_diagnostics(self, uri: str, diagnostics: List[Diagnostic]):
        """Publish diagnostics to the client."""
        self.publish_diagnostics(uri, diagnostics)
    
    def _completion(self, params: CompletionParams) -> CompletionList:
        """Provide completion suggestions."""
        try:
            doc = self.workspace.get_document(params.textDocument.uri)
            line = doc.lines[params.position.line]
            char_pos = params.position.character
            
            # Get the current line up to cursor
            current_line = line[:char_pos]
            
            # Determine completion context
            completions = []
            
            # Check if we're in a Jinja2 template
            if self._is_in_jinja2_template(current_line):
                completions.extend(self._get_jinja2_completions())
            
            # Check if we're completing a key
            elif self._is_completing_key(current_line):
                completions.extend(self._get_key_completions(current_line, doc))
            
            # Check if we're completing a value
            elif self._is_completing_value(current_line):
                completions.extend(self._get_value_completions(current_line, doc))
            
            # Check if we're completing a type
            elif self._is_completing_type(current_line):
                completions.extend(self._get_type_completions())
            
            # Check if we're completing a MIME type
            elif self._is_completing_mime_type(current_line):
                completions.extend(self._get_mime_type_completions())
            
            # Check if we're completing a URI scheme
            elif self._is_completing_uri_scheme(current_line):
                completions.extend(self._get_uri_scheme_completions())
            
            return CompletionList(is_incomplete=False, items=completions)
            
        except Exception as e:
            logger.error(f"Error in completion: {e}")
            return CompletionList(is_incomplete=False, items=[])
    
    def _is_in_jinja2_template(self, line: str) -> bool:
        """Check if we're inside a Jinja2 template."""
        return "{{" in line or "{%" in line or "{#" in line
    
    def _is_completing_key(self, line: str) -> bool:
        """Check if we're completing a YAML key."""
        return ":" not in line or line.strip().endswith(":")
    
    def _is_completing_value(self, line: str) -> bool:
        """Check if we're completing a YAML value."""
        return ":" in line and not line.strip().endswith(":")
    
    def _is_completing_type(self, line: str) -> bool:
        """Check if we're completing a type value."""
        return "type:" in line.lower()
    
    def _is_completing_mime_type(self, line: str) -> bool:
        """Check if we're completing a MIME type."""
        return "mime_type:" in line.lower()
    
    def _is_completing_uri_scheme(self, line: str) -> bool:
        """Check if we're completing a URI scheme."""
        return "uri:" in line.lower() and not line.strip().endswith("uri:")
    
    def _get_jinja2_completions(self) -> List[CompletionItem]:
        """Get Jinja2 template completions."""
        completions = []
        for syntax, description in JINJA2_SYNTAX.items():
            completions.append(CompletionItem(
                label=syntax,
                kind=CompletionItemKind.Keyword,
                detail=description,
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**Jinja2 Syntax**: {description}"
                )
            ))
        return completions
    
    def _get_key_completions(self, line: str, doc: Document) -> List[CompletionItem]:
        """Get YAML key completions based on context."""
        completions = []
        
        # Determine the current context (server, tools, resources, etc.)
        context = self._get_yaml_context(line, doc)
        
        if context in SHELLMCP_COMPLETIONS:
            if isinstance(SHELLMCP_COMPLETIONS[context], dict):
                for key, description in SHELLMCP_COMPLETIONS[context].items():
                    completions.append(CompletionItem(
                        label=key,
                        kind=CompletionItemKind.Property,
                        detail=description,
                        documentation=MarkupContent(
                            kind=MarkupKind.Markdown,
                            value=f"**{key}**: {description}"
                        )
                    ))
            else:
                completions.append(CompletionItem(
                    label=context,
                    kind=CompletionItemKind.Property,
                    detail=SHELLMCP_COMPLETIONS[context],
                    documentation=MarkupContent(
                        kind=MarkupKind.Markdown,
                        value=f"**{context}**: {SHELLMCP_COMPLETIONS[context]}"
                    )
                ))
        
        # Add common YAML keys
        for key, description in SHELLMCP_COMPLETIONS.items():
            if isinstance(description, str) and key not in ["server", "args", "tools", "resources", "prompts"]:
                completions.append(CompletionItem(
                    label=key,
                    kind=CompletionItemKind.Property,
                    detail=description,
                    documentation=MarkupContent(
                        kind=MarkupKind.Markdown,
                        value=f"**{key}**: {description}"
                    )
                ))
        
        return completions
    
    def _get_value_completions(self, line: str, doc: Document) -> List[CompletionItem]:
        """Get YAML value completions."""
        completions = []
        
        # Add YAML keywords
        for keyword in YAML_KEYWORDS:
            completions.append(CompletionItem(
                label=keyword,
                kind=CompletionItemKind.Keyword,
                detail=f"YAML {keyword}",
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**YAML Keyword**: {keyword}"
                )
            ))
        
        return completions
    
    def _get_type_completions(self) -> List[CompletionItem]:
        """Get type value completions."""
        completions = []
        for type_name, description in SHELLMCP_COMPLETIONS["type"].items():
            completions.append(CompletionItem(
                label=type_name,
                kind=CompletionItemKind.EnumMember,
                detail=description,
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**Type**: {description}"
                )
            ))
        return completions
    
    def _get_mime_type_completions(self) -> List[CompletionItem]:
        """Get MIME type completions."""
        completions = []
        for mime_type in MIME_TYPES:
            completions.append(CompletionItem(
                label=mime_type,
                kind=CompletionItemKind.EnumMember,
                detail=f"MIME type: {mime_type}",
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**MIME Type**: {mime_type}"
                )
            ))
        return completions
    
    def _get_uri_scheme_completions(self) -> List[CompletionItem]:
        """Get URI scheme completions."""
        completions = []
        for scheme in URI_SCHEMES:
            completions.append(CompletionItem(
                label=scheme,
                kind=CompletionItemKind.EnumMember,
                detail=f"URI scheme: {scheme}",
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**URI Scheme**: {scheme}"
                )
            ))
        return completions
    
    def _get_yaml_context(self, line: str, doc: Document) -> str:
        """Determine the current YAML context."""
        # Simple context detection based on indentation and previous lines
        lines = doc.lines
        current_line_num = 0
        
        # Find current line number
        for i, doc_line in enumerate(lines):
            if doc_line == line:
                current_line_num = i
                break
        
        # Look backwards for context
        for i in range(current_line_num - 1, -1, -1):
            prev_line = lines[i].strip()
            if prev_line.startswith("server:"):
                return "server"
            elif prev_line.startswith("args:"):
                return "args"
            elif prev_line.startswith("tools:"):
                return "tools"
            elif prev_line.startswith("resources:"):
                return "resources"
            elif prev_line.startswith("prompts:"):
                return "prompts"
        
        return "root"
    
    def _hover(self, params: HoverParams) -> Optional[Hover]:
        """Provide hover information."""
        try:
            doc = self.workspace.get_document(params.textDocument.uri)
            line = doc.lines[params.position.line]
            char_pos = params.position.character
            
            # Get the word at the cursor position
            word = self._get_word_at_position(line, char_pos)
            if not word:
                return None
            
            # Check if it's a known keyword
            if word in SHELLMCP_COMPLETIONS:
                if isinstance(SHELLMCP_COMPLETIONS[word], dict):
                    # For nested objects, show the first few keys
                    keys = list(SHELLMCP_COMPLETIONS[word].keys())[:3]
                    description = f"**{word}**: {SHELLMCP_COMPLETIONS[word]}\n\n**Available keys**: {', '.join(keys)}"
                else:
                    description = f"**{word}**: {SHELLMCP_COMPLETIONS[word]}"
                
                return Hover(
                    contents=MarkupContent(
                        kind=MarkupKind.Markdown,
                        value=description
                    )
                )
            
            # Check if it's a Jinja2 syntax element
            if word in JINJA2_SYNTAX:
                return Hover(
                    contents=MarkupContent(
                        kind=MarkupKind.Markdown,
                        value=f"**Jinja2 Syntax**: {JINJA2_SYNTAX[word]}"
                    )
                )
            
            # Check if it's a YAML keyword
            if word in YAML_KEYWORDS:
                return Hover(
                    contents=MarkupContent(
                        kind=MarkupKind.Markdown,
                        value=f"**YAML Keyword**: {word}"
                    )
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in hover: {e}")
            return None
    
    def _get_word_at_position(self, line: str, char_pos: int) -> Optional[str]:
        """Get the word at the given position in the line."""
        # Find word boundaries
        start = char_pos
        end = char_pos
        
        # Move start backwards to beginning of word
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] in "_-"):
            start -= 1
        
        # Move end forwards to end of word
        while end < len(line) and (line[end].isalnum() or line[end] in "_-"):
            end += 1
        
        if start < end:
            return line[start:end]
        return None


def create_server() -> ShellMCPLanguageServer:
    """Create and return a new language server instance."""
    return ShellMCPLanguageServer()


if __name__ == "__main__":
    # Run the server
    server = create_server()
    server.start_io()