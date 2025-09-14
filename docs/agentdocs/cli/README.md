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

**Examples:**

```bash
# Basic validation
shellmcp validate config.yml

# Verbose validation with detailed output
shellmcp validate config.yml --verbose
```

### `generate`

Generate a FastMCP server from YAML configuration.

```bash
shellmcp generate <config_file> [--output-dir <dir>] [--verbose]
```

**Arguments:**
- `config_file`: Path to the YAML configuration file

**Flags:**
- `--output-dir`: Optional output directory (defaults to creating a subdirectory with the server name)
- `--verbose` / `-v`: Show detailed generation information

**Default Behavior:**
When no `--output-dir` is specified, the generator automatically creates a subdirectory named after the server (with spaces and hyphens converted to underscores). This prevents accidentally overwriting existing files like README.md in your current directory.

**Examples:**

```bash
# Generate with default output directory (creates ./my-server/ subdirectory)
shellmcp generate my-server.yml --verbose

# Generate with custom output directory
shellmcp generate my-server.yml --output-dir ./output --verbose
```

**Generate Output:**

The `generate` command creates a complete FastMCP server with the following files:

```
✅ FastMCP server generated successfully!
📁 Output directory: /path/to/my_mcp_server
🐍 Server file: /path/to/my_mcp_server/my_mcp_server_server.py
📦 Requirements: /path/to/my_mcp_server/requirements.txt
📖 Documentation: /path/to/my_mcp_server/README.md

🚀 To run the server:
   cd /path/to/my_mcp_server
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   python my_mcp_server_server.py
```

**Validation Output:**

The `validate` command performs comprehensive validation including:

1. **Syntax Validation**: Ensures valid YAML structure
2. **Schema Validation**: Validates against Pydantic models
3. **Template Validation**: Checks Jinja2 template syntax
4. **Reference Resolution**: Validates argument references
5. **Consistency Checks**: Ensures template variables have corresponding arguments

## Output

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
if ! shellmcp validate config.yml; then
    echo "Configuration validation failed"
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