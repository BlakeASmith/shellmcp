"""Minimal LSP server for shellmcp YAML schema validation."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from jsonschema import Draft7Validator, ValidationError
from pygls.lsp.methods import (
    COMPLETION,
    DID_OPEN,
    DID_SAVE,
    INITIALIZE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
)
from pygls.lsp.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    Diagnostic,
    DiagnosticSeverity,
    InitializeParams,
    Position,
    Range,
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


class ShellMCPLanguageServer(LanguageServer):
    """Minimal language server for shellmcp YAML configuration files."""
    
    def __init__(self):
        super().__init__("shellmcp-lsp", "0.1.0")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up LSP method handlers."""
        self.feature(INITIALIZE)(self._initialize)
        self.feature(TEXT_DOCUMENT_DID_OPEN)(self._did_open)
        self.feature(TEXT_DOCUMENT_DID_SAVE)(self._did_save)
        self.feature(COMPLETION)(self._completion)
    
    def _initialize(self, params: InitializeParams):
        """Initialize the language server."""
        return {
            "capabilities": {
                "textDocumentSync": {
                    "openClose": True,
                    "change": 1,
                    "save": True
                },
                "completionProvider": {
                    "resolveProvider": False,
                    "triggerCharacters": [":", " "]
                },
                "diagnosticProvider": {
                    "interFileDependencies": False,
                    "workspaceDiagnostics": False
                }
            }
        }
    
    def _did_open(self, params: TextDocumentItem):
        """Handle document open event."""
        self._validate_document(params.uri)
    
    def _did_save(self, params: TextDocumentItem):
        """Handle document save event."""
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
            # Simple error reporting at line 0 for now
            return Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=10)
                ),
                message=error.message,
                severity=DiagnosticSeverity.Error,
                source="shellmcp-lsp"
            )
        except Exception:
            return None
    
    def _publish_diagnostics(self, uri: str, diagnostics: List[Diagnostic]):
        """Publish diagnostics to the client."""
        self.publish_diagnostics(uri, diagnostics)
    
    def _completion(self, params) -> CompletionList:
        """Provide basic completion suggestions."""
        try:
            # Basic completions for shellmcp keys
            completions = [
                CompletionItem(
                    label="server",
                    kind=CompletionItemKind.Property,
                    detail="Server configuration"
                ),
                CompletionItem(
                    label="tools",
                    kind=CompletionItemKind.Property,
                    detail="Tool definitions"
                ),
                CompletionItem(
                    label="resources",
                    kind=CompletionItemKind.Property,
                    detail="Resource definitions"
                ),
                CompletionItem(
                    label="prompts",
                    kind=CompletionItemKind.Property,
                    detail="Prompt definitions"
                ),
                CompletionItem(
                    label="args",
                    kind=CompletionItemKind.Property,
                    detail="Reusable argument definitions"
                )
            ]
            
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