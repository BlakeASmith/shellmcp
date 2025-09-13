# ShellMCP LSP Server

Minimal Language Server Protocol implementation for shellmcp YAML configuration files.

## Features

- **Schema Validation**: Basic validation against shellmcp YAML schema
- **Auto-completion**: Simple completion for main YAML keys
- **Error Reporting**: YAML parsing and schema validation errors

## Installation

```bash
pip install shellmcp
```

## Usage

### Run LSP Server

```bash
shellmcp lsp
```

### VS Code Configuration

Add to your VS Code settings:

```json
{
  "yaml.schemas": {
    "file:///path/to/shellmcp/lsp/schema.json": ["*.yml", "*.yaml"]
  }
}
```

## Supported Features

- Server configuration validation
- Tool definitions
- Resource definitions  
- Prompt definitions
- Reusable argument definitions

## Example

```yaml
server:
  name: my-server
  desc: My MCP server

tools:
  MyTool:
    cmd: echo "Hello {{ name }}"
    desc: Simple tool
    args:
      - name: name
        help: Name to greet
        type: string
        default: "World"
```