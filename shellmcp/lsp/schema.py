"""Schema module for shellmcp LSP server."""

import json
from pathlib import Path

# Load the JSON schema
SCHEMA_PATH = Path(__file__).parent / "schema.json"
with open(SCHEMA_PATH, "r") as f:
    SCHEMA = json.load(f)

__all__ = ["SCHEMA"]