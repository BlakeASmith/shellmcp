# ShellMCP LSP Server

LSP server providing autocomplete for shellmcp YAML configuration files.

## Features

- **Autocomplete**: Comprehensive autocomplete for shellmcp YAML keys and values
- **Jinja2 Support**: Autocomplete for Jinja2 template syntax
- **Type Completions**: Built-in type suggestions (string, number, boolean, array)

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

## Autocomplete Features

### YAML Keys
- `server` - Server configuration
- `tools` - Tool definitions
- `resources` - Resource definitions
- `prompts` - Prompt definitions
- `args` - Reusable argument definitions

### Properties
- `name`, `desc`, `version`, `env` - Server properties
- `cmd`, `help-cmd`, `args` - Tool properties
- `uri`, `mime_type`, `file`, `text` - Resource properties
- `template` - Prompt properties
- `help`, `type`, `default`, `choices`, `pattern`, `ref` - Argument properties

### Types
- `string` - Text value
- `number` - Numeric value
- `boolean` - True/false value
- `array` - List of values

### Jinja2 Templates
- `{{` - Variable interpolation
- `{%` - Control structure
- `{#` - Comment
- `if`, `else`, `elif`, `endif` - Conditional logic
- `for`, `endfor` - Loops
- `set` - Variable assignment
- `now` - Current timestamp

## Example

```yaml
server:
  name: my-server
  desc: My MCP server

tools:
  Hello:
    cmd: echo "Hello {{ name }}"
    desc: Say hello
    args:
      - name: name
        help: Name to greet
        type: string
        default: "World"
```