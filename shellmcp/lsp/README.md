# ShellMCP LSP Server

Language Server Protocol (LSP) implementation for shellmcp YAML configuration files. Provides intelligent code completion, validation, and documentation for shellmcp YAML schemas.

## Features

- **Schema Validation**: Real-time validation against the shellmcp YAML schema
- **Auto-completion**: Intelligent completion for YAML keys, values, and Jinja2 templates
- **Hover Documentation**: Contextual help and documentation on hover
- **Error Reporting**: Detailed error messages for invalid configurations
- **Jinja2 Support**: Specialized support for Jinja2 template syntax in commands

## Installation

The LSP server is included with the shellmcp package. Install shellmcp to get the LSP server:

```bash
pip install shellmcp
```

## Editor Configuration

### VS Code

Create or update your VS Code settings to use the shellmcp LSP server:

```json
{
  "yaml.schemas": {
    "file:///path/to/shellmcp/lsp/schema.json": ["*.yml", "*.yaml"]
  },
  "yaml.customTags": [
    "!And",
    "!If",
    "!Not",
    "!Equals",
    "!Or",
    "!FindInMap sequence",
    "!Base64",
    "!Cidr",
    "!Ref",
    "!Sub",
    "!GetAtt",
    "!GetAZs",
    "!ImportValue",
    "!Select",
    "!Split",
    "!Join sequence"
  ]
}
```

For a more advanced setup with the LSP server, create a client configuration:

```json
{
  "languageServerExample.general.enableTelemetry": false,
  "languageServerExample.general.trace.server": "verbose",
  "languageServerExample.general.trace.client": "verbose"
}
```

### Neovim

For Neovim with nvim-lspconfig, add this to your configuration:

```lua
local lspconfig = require('lspconfig')

-- Configure shellmcp LSP
lspconfig.yamlls.setup({
  settings = {
    yaml = {
      schemas = {
        ["file:///path/to/shellmcp/lsp/schema.json"] = {"*.yml", "*.yaml"}
      }
    }
  }
})
```

### Vim/Neovim with coc.nvim

Add to your `coc-settings.json`:

```json
{
  "yaml.schemas": {
    "file:///path/to/shellmcp/lsp/schema.json": ["*.yml", "*.yaml"]
  }
}
```

### Emacs

For Emacs with lsp-mode:

```elisp
(use-package lsp-mode
  :hook (yaml-mode . lsp)
  :config
  (lsp-register-client
   (make-lsp-client :new-connection (lsp-stdio-connection '("python" "-m" "shellmcp.lsp.server"))
                    :major-modes '(yaml-mode)
                    :server-id 'shellmcp-lsp)))
```

## Usage

### Running the LSP Server

The LSP server can be run directly:

```bash
python -m shellmcp.lsp.server
```

Or through the shellmcp CLI:

```bash
shellmcp lsp
```

### Supported File Types

The LSP server automatically activates for:
- `.yml` files
- `.yaml` files

### Schema Validation

The server validates your YAML files against the shellmcp schema and provides:

- **Required field validation**: Ensures all required fields are present
- **Type validation**: Validates data types (string, number, boolean, array)
- **Reference validation**: Ensures argument references exist
- **Content source validation**: Ensures resources and prompts have exactly one content source
- **Jinja2 template validation**: Validates Jinja2 template syntax

### Auto-completion

The server provides intelligent completion for:

- **YAML keys**: Based on the current context (server, tools, resources, prompts)
- **Type values**: string, number, boolean, array
- **MIME types**: Common MIME types for resources
- **URI schemes**: file://, http://, system://, etc.
- **Jinja2 syntax**: Template variables, control structures, filters
- **YAML keywords**: true, false, null, etc.

### Hover Documentation

Hover over any element to see:

- **Field descriptions**: What each field does
- **Type information**: Expected data types
- **Usage examples**: How to use the field
- **Jinja2 help**: Template syntax and functions

## Configuration Examples

### Basic Server Configuration

```yaml
server:
  name: my-mcp-server
  desc: My custom MCP server
  version: "1.0.0"
  env:
    DEBUG: "false"
```

### Tool with Arguments

```yaml
tools:
  ListFiles:
    cmd: ls -la {{ path }}
    desc: List files in a directory
    args:
      - name: path
        help: Directory path to list
        type: string
        default: "."
```

### Resource with Template

```yaml
resources:
  SystemInfo:
    uri: "system://info"
    name: "System Information"
    description: "Current system information"
    mime_type: "text/plain"
    cmd: |
      echo "=== System Information ==="
      uname -a
      echo ""
      echo "=== Disk Usage ==="
      df -h
```

### Prompt with Jinja2 Template

```yaml
prompts:
  CodeReview:
    name: "Code Review Assistant"
    description: "Generate a code review prompt"
    template: |
      You are a senior software engineer reviewing the following {{ language }} code:
      
      ```{{ language }}
      {{ code }}
      ```
      
      Please provide a thorough code review focusing on:
      - Code quality and best practices
      - Performance implications
      - Security considerations
      - Maintainability
      
      {% if focus_areas %}
      Pay special attention to: {{ focus_areas }}
      {% endif %}
    args:
      - name: language
        help: "Programming language"
        choices: ["python", "javascript", "java", "go"]
        default: "python"
      - name: code
        help: "Code to review"
        type: string
      - name: focus_areas
        help: "Specific areas to focus on"
        type: string
        default: ""
```

## Troubleshooting

### Common Issues

1. **LSP server not starting**: Ensure all dependencies are installed
2. **No completions**: Check that the file has a `.yml` or `.yaml` extension
3. **Schema validation errors**: Verify your YAML syntax and required fields

### Debug Mode

Run the LSP server in debug mode for detailed logging:

```bash
python -m shellmcp.lsp.server --log-level DEBUG
```

### Logs

The server logs to stderr by default. Check your editor's LSP logs for detailed error information.

## Contributing

To contribute to the LSP server:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the same license as shellmcp.