# ShellMCP LSP Server

LSP server providing autocomplete for shellmcp YAML configuration files.

## Features

- **Autocomplete**: Simple autocomplete for shellmcp YAML keys and values
- **Type Completions**: Built-in type suggestions (string, number, boolean, array)
- **YAML Keywords**: Basic YAML keyword completions (true, false, null)

## Installation

### Basic Installation
```bash
pip install shellmcp
```

### With LSP Support
```bash
pip install shellmcp[lsp]
```

## Usage

### Run LSP Server

```bash
shellmcp lsp
```

**Note**: If you get an import error, make sure you installed with LSP support:
```bash
pip install shellmcp[lsp]
```

### VS Code Configuration

The LSP server provides autocomplete without requiring schema configuration, but you can still add YAML schema support if desired.

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

### YAML Keywords
- `true` - YAML true value
- `false` - YAML false value
- `null` - YAML null value

## Example

```yaml
server:
  name: my-server
  desc: My MCP server

tools:
  Hello:
    cmd: echo "Hello World"
    desc: Say hello
    args:
      - name: name
        help: Name to greet
        type: string
        default: "World"
```