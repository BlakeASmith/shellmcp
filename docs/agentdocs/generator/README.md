# FastMCP Server Generator

The FastMCP Server Generator is a powerful feature that converts YAML configuration files into fully functional FastMCP servers. This allows you to quickly create MCP (Model Context Protocol) servers that expose shell commands as tools.

## Overview

The generator takes a YAML configuration file and produces:
- A complete FastMCP server implementation
- Requirements file with all necessary dependencies
- Comprehensive documentation
- Ready-to-run server code

## Features

- **Template-Based Generation**: Uses Jinja2 templates for clean, maintainable code generation
- **Jinja2 Template Support**: Commands can use Jinja2 templates for dynamic content
- **Argument Validation**: Automatic validation with patterns and choices
- **Environment Variables**: Support for server and tool-specific environment variables
- **Error Handling**: Built-in timeout protection and error handling
- **Type Safety**: Proper Python type annotations for all arguments
- **Custom Filters**: Built-in Jinja2 filters for Python type conversion and formatting
- **Virtual Environment Support**: Proper dependency isolation and management

## Usage

### Command Line Interface

```bash
# Generate server from YAML configuration
python -m shellmcp.cli generate config.yml --verbose

# Generate with custom output directory
python -m shellmcp.cli generate config.yml --output-dir ./output --verbose
```

### Programmatic Usage

```python
from shellmcp.generator import FastMCPGenerator

generator = FastMCPGenerator()

# Generate server file
server_file = generator.generate_server("config.yml")

# Generate requirements
requirements_file = generator.generate_requirements()

# Generate documentation
readme_file = generator.generate_readme(config)
```

## YAML Configuration Format

### Basic Structure

```yaml
server:
  name: my-mcp-server
  desc: Description of the server
  version: "1.0.0"
  env:
    NODE_ENV: production
    DEBUG: "false"

args:
  FilePath:
    help: Path to a file
    type: string
    pattern: "^[^\\0]+$"

tools:
  ListFiles:
    cmd: ls -la {{ path }}
    desc: List files in a directory
    args:
      - name: path
        help: Directory path to list
        default: "."
        ref: FilePath
```

### Server Configuration

- `name`: Server name (used for FastMCP initialization)
- `desc`: Server description
- `version`: Server version
- `env`: Environment variables (optional)

### Reusable Arguments

Define common argument patterns that can be referenced by tools:

```yaml
args:
  FilePath:
    help: Path to a file
    type: string
    pattern: "^[^\\0]+$"
  
  BooleanFlag:
    help: Boolean flag
    type: boolean
    default: false
```

### Tool Configuration

Each tool represents a shell command that will be exposed as an MCP tool:

```yaml
tools:
  ToolName:
    cmd: shell command with {{ variables }}
    desc: Tool description
    help-cmd: command --help  # Optional
    args:
      - name: variable_name
        help: Argument description
        type: string
        default: "default_value"
        choices: ["option1", "option2"]
        pattern: "^pattern$"
        ref: FilePath  # Reference to reusable argument
    env:
      CUSTOM_VAR: "value"  # Tool-specific environment variables
```

### Advanced Features

#### Jinja2 Templates

Commands support full Jinja2 templating:

```yaml
tools:
  BackupDatabase:
    cmd: |
      {% set backup_file = "backup_" + timestamp + ".sql" %}
      mysqldump -h {{ host }} -u {{ user }} -p{{ password }} {{ database }} > {{ backup_file }}
      {% if compress %}
      gzip {{ backup_file }}
      {% endif %}
      echo "Backup completed: {{ backup_file }}"
    desc: Database backup with optional compression
    args:
      - name: host
        default: "localhost"
      - name: user
        type: string
      - name: password
        type: string
      - name: database
        type: string
      - name: compress
        ref: BooleanFlag
      - name: timestamp
        default: "{{ now().strftime('%Y%m%d_%H%M%S') }}"
```

#### Conditional Logic

```yaml
tools:
  ConditionalDeploy:
    cmd: |
      {% if env == 'prod' %}
      docker run --restart=always -d --name {{ service }} {{ image }}
      {% elif env == 'staging' %}
      docker run -d --name {{ service }}_staging {{ image }}
      {% else %}
      docker run -d --name {{ service }}_dev {{ image }}
      {% endif %}
    desc: Deploy service with environment-specific configuration
    args:
      - name: env
        choices: ["dev", "staging", "prod"]
        default: "dev"
      - name: service
        type: string
      - name: image
        type: string
```

## Generated Server Features

### Automatic Features

- **Command Execution**: Safe subprocess execution with timeout
- **Template Rendering**: Jinja2 template processing with built-in functions
- **Error Handling**: Comprehensive error handling and reporting
- **Type Validation**: Automatic argument type checking
- **Pattern Validation**: Regex pattern validation for string arguments
- **Choice Validation**: Validation against allowed values

### Built-in Functions

The generator provides these built-in functions in templates:

- `now()`: Current datetime object (useful for timestamps)

### Return Format

All tools return a consistent format:

```python
{
    "success": bool,      # True if command succeeded
    "stdout": str,        # Standard output
    "stderr": str,        # Standard error
    "returncode": int     # Process return code
}
```

## Template System

The generator uses a sophisticated Jinja2 template system for code generation:

### Template Files

- **`server.py.j2`**: Main server template with all tool functions
- **`requirements.txt.j2`**: Python dependencies template
- **`README.md.j2`**: Documentation template with virtual environment instructions

### Custom Jinja2 Filters

The generator includes custom filters for better template functionality:

- **`python_type`**: Converts YAML types to Python type annotations
- **`python_value`**: Converts values to Python representations based on type
- **`escape_double_quotes`**: Escapes quotes for use in triple-quoted strings

### Template Features

- **Clean Code Generation**: Templates produce properly formatted, readable Python code
- **Dynamic Content**: Full access to configuration data through template variables
- **Maintainable**: Easy to modify templates without changing generator logic
- **Extensible**: Add new templates or modify existing ones as needed

## Example Generated Server

Here's what a generated server looks like:

```python
"""Generated FastMCP server from YAML configuration."""

import os
import subprocess
from datetime import datetime
from typing import Any, Dict, Optional
from fastmcp import FastMCP
from jinja2 import Template

def execute_command(cmd: str, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Execute a shell command and return the result."""
    # ... implementation

def render_template(template_str: str, **kwargs) -> str:
    """Render Jinja2 template with provided variables."""
    # ... implementation

# Initialize FastMCP server
mcp = FastMCP(name="my-mcp-server")

@mcp.tool()
def listfiles(path: str = ".") -> Dict[str, Any]:
    """
    List files in a directory
    """
    try:
        # Validate path pattern
        import re
        if not re.match(r"^[^\0]+$", str(path)):
            raise ValueError(f"Invalid path: must match pattern ^[^\0]+$")
        
        # Render command template
        cmd = render_template("ls -la {{ path }}", path)
        
        # Execute command
        result = execute_command(cmd, {})
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in ListFiles: {str(e)}",
            "returncode": -1
        }

if __name__ == "__main__":
    print(f"Starting my-mcp-server v1.0.0")
    mcp.run()
```

## Running the Generated Server

### Recommended: Using Virtual Environment

1. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Server**:
   ```bash
   python my_mcp_server.py
   ```

5. **Deactivate when done**:
   ```bash
   deactivate
   ```

### Alternative: System-wide Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   python my_mcp_server.py
   ```

### Why Use Virtual Environments?

- **Dependency Isolation**: Prevents conflicts with system Python packages
- **Clean Environment**: Ensures consistent dependency versions
- **Easy Cleanup**: Simply delete the `venv` folder to remove all dependencies
- **Multiple Projects**: Run different servers with different dependency versions
- **Production Safety**: Avoids modifying system Python installation

3. **Connect with MCP Client**:
   The server runs on STDIO transport and can be connected to by any MCP-compatible client.



### Virtual Environment Setup Issues

**Common Issues:**
- **Virtual environment not found**: Ensure `venv` directory exists in your server directory
- **Python interpreter not found**: Check that `venv/bin/python` exists
- **Dependencies missing**: Activate the virtual environment and run `pip install -r requirements.txt`

**Quick Fix:**
```bash
# Navigate to your server directory
cd /path/to/your/server

# Create virtual environment if missing
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**Alternative: Using virtualenv**
If `python3 -m venv` doesn't work:
```bash
# Install virtualenv
pip install virtualenv

# Create virtual environment
virtualenv venv

# Activate
source venv/bin/activate
```

### Testing Your Configuration

1. **Manual Test**: Run the server directly to ensure it starts:
   ```bash
   python /path/to/your/filesystem_mcp_server.py
   ```

2. **Check Tools**: Verify that your tools are available in the editor's MCP interface

3. **Test Commands**: Try using your generated tools through the editor's MCP integration

## Best Practices

### Security

- **Validate Inputs**: Always use pattern validation for file paths and user inputs
- **Limit Commands**: Only expose necessary commands
- **Environment Variables**: Use environment variables for sensitive data
- **Timeouts**: The generator includes 5-minute timeouts by default

### Performance

- **Simple Commands**: Keep commands simple and fast
- **Error Handling**: Provide meaningful error messages
- **Resource Limits**: Consider adding resource limits for long-running commands

### Maintainability

- **Clear Descriptions**: Provide clear descriptions for all tools and arguments
- **Consistent Naming**: Use consistent naming conventions
- **Documentation**: Keep the generated README updated

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Template Errors**: Check Jinja2 syntax in command templates
3. **Validation Errors**: Verify argument patterns and choices
4. **Permission Errors**: Ensure the server has necessary permissions

### Debug Mode

Run the server with verbose output to debug issues:

```bash
python my_mcp_server.py --verbose
```

## Integration with MCP Clients

The generated servers are fully compatible with MCP clients and can be used in:

- Claude Desktop
- Custom MCP applications
- Development environments
- Production deployments

## Contributing

To contribute to the FastMCP generator:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the same terms as the main shellmcp project.