# ShellMCP CLI Interface

The ShellMCP CLI provides a command-line interface for validating YAML configuration files using Google Fire.

## Installation

```bash
pip install shellmcp
```

## Usage

The CLI is accessible via the `shellmcp` command:

```bash
shellmcp <command> [arguments] [flags]
```

## Commands

### `validate`

Validate a YAML configuration file for syntax and semantic correctness.

```bash
shellmcp validate <config_file> [flags]
```

**Arguments:**
- `config_file`: Path to the YAML configuration file

**Flags:**
- `--verbose` / `-v`: Show detailed validation information
- `--output_format` / `-o`: Output format (`text`, `json`, `yaml`)

**Examples:**

```bash
# Basic validation
shellmcp validate config.yml

# Verbose validation with detailed output
shellmcp validate config.yml --verbose

# JSON output format
shellmcp validate config.yml --output_format=json

# YAML output format
shellmcp validate config.yml --output_format=yaml
```

**Output:**

The `validate` command performs comprehensive validation including:

1. **Syntax Validation**: Ensures valid YAML structure
2. **Schema Validation**: Validates against Pydantic models
3. **Template Validation**: Checks Jinja2 template syntax
4. **Reference Resolution**: Validates argument references
5. **Consistency Checks**: Ensures template variables have corresponding arguments

## Output Formats

### Text Format (Default)

Human-readable output with emojis and structured information:

```
✅ Configuration 'config.yml' is valid!

📋 Server: filesystem-mcp v1.0.0
   Description: MCP Server for filesystem operations
   Tools: 6
   Reusable args: 3

🔍 Template validation:
   ✅ ListFiles
   ✅ ReadFile
   ✅ CreateDirectory

✅ All template variables have corresponding arguments
```

### JSON Format

Structured JSON output for programmatic processing:

```json
{
  "valid": true,
  "server": {
    "name": "filesystem-mcp",
    "description": "MCP Server for filesystem operations",
    "version": "1.0.0"
  },
  "tools_count": 6,
  "reusable_args_count": 3,
  "template_validation": {
    "ListFiles": true,
    "ReadFile": true,
    "CreateDirectory": true
  },
  "consistency_issues": {},
  "tools_summary": {
    "ListFiles": {
      "description": "List files in a directory",
      "command": "ls -la {{ path }}",
      "arguments_count": 1,
      "template_variables": ["path"],
      "has_valid_template": true
    }
  }
}
```

### YAML Format

YAML output for configuration processing:

```yaml
valid: true
server:
  name: filesystem-mcp
  description: MCP Server for filesystem operations
  version: "1.0.0"
tools_count: 6
reusable_args_count: 3
template_validation:
  ListFiles: true
  ReadFile: true
  CreateDirectory: true
```

## Error Handling

The CLI provides detailed error messages for various validation failures:

### Missing Required Fields
```
❌ Error validating configuration: Invalid YAML configuration: 1 validation error for YMLConfig
server.desc
  Field required [type=missing, input_value={'name': 'test-server'}, input_type=dict]
```

### Invalid Template Syntax
```
❌ Error validating configuration: Invalid YAML configuration: 1 validation error for YMLConfig
tools.InvalidTool.cmd
  Invalid Jinja2 template syntax: unexpected end of template
```

### Invalid References
```
❌ Error validating configuration: Invalid YAML configuration: 1 validation error for YMLConfig
tools.MyTool.args.0.ref
  Tool 'MyTool' references undefined argument 'NonExistentRef'
```

## Exit Codes

- `0`: Success
- `1`: Validation error or file not found

## Integration

The CLI can be easily integrated into CI/CD pipelines:

```bash
# In a CI script
if ! shellmcp validate config.yml --output_format=json > validation.json; then
    echo "Configuration validation failed"
    exit 1
fi

# Check specific validation results
if jq -r '.template_validation | to_entries[] | select(.value == false) | .key' validation.json; then
    echo "Some tools have invalid templates"
    exit 1
fi
```

## Advanced Usage

### Fire Features

The CLI uses Google Fire, which provides additional features:

```bash
# Get help for any command
shellmcp validate --help
shellmcp info --help
shellmcp list_tools --help

# Use flag syntax for positional arguments
shellmcp validate --config_file=config.yml --verbose

# Chain commands (if supported by your shell)
shellmcp list_tools config.yml | grep "✅" | wc -l
```

### Programmatic Usage

You can also use the CLI classes directly in Python:

```python
from shellmcp.cli import ShellMCPCLI

cli = ShellMCPCLI()

# Validate configuration
result = cli.validate("config.yml", verbose=True)

# Get tool information
cli.info("config.yml", "BackupDatabase")

# List tools
cli.list_tools("config.yml")
```

## Examples

See the `examples/` directory for complete usage examples:

- `basic_example.py`: Simple configuration parsing
- `example_usage.py`: Advanced features demonstration
- `example_config.yml`: Comprehensive configuration example

## Troubleshooting

### Common Issues

1. **File not found**: Ensure the configuration file path is correct
2. **Permission denied**: Check file permissions
3. **Invalid YAML**: Use a YAML validator to check syntax
4. **Template errors**: Validate Jinja2 syntax separately

### Debug Mode

Use the `--verbose` flag to get detailed error information:

```bash
shellmcp validate config.yml --verbose
```

This will show:
- Detailed validation results
- Template validation status
- Argument consistency checks
- Full error traces for debugging