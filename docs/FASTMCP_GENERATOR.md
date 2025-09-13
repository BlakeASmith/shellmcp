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
- **`README.md.j2`**: Documentation template

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
   python -m venv venv
   ```

2. **Activate Virtual Environment**:
   - **Linux/macOS**:
   ```bash
   source venv/bin/activate
   ```
   - **Windows**:
   ```cmd
   venv\Scripts\activate
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

## MCP Configuration for Editors

To use your generated FastMCP server with various editors and MCP clients, you need to configure the `mcp.json` file. Here are the installation instructions for different platforms:

### Claude Desktop (macOS)

1. **Locate the configuration file**:
   ```bash
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. **Add your server configuration**:
   ```json
   {
     "mcpServers": {
       "filesystem-mcp": {
         "command": "/path/to/your/venv/bin/python",
         "args": ["/path/to/your/filesystem_mcp_server.py"],
         "env": {
           "NODE_ENV": "production"
         }
       }
     }
   }
   ```
   
   **Note**: Use the Python interpreter from your virtual environment (`/path/to/your/venv/bin/python`) instead of system Python for better dependency isolation.

3. **Restart Claude Desktop** for changes to take effect.

### Claude Desktop (Windows)

1. **Locate the configuration file**:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Add your server configuration**:
   ```json
   {
     "mcpServers": {
       "filesystem-mcp": {
         "command": "C:\\path\\to\\your\\venv\\Scripts\\python.exe",
         "args": ["C:\\path\\to\\your\\filesystem_mcp_server.py"],
         "env": {
           "NODE_ENV": "production"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### Claude Desktop (Linux)

1. **Locate the configuration file**:
   ```bash
   ~/.config/Claude/claude_desktop_config.json
   ```

2. **Add your server configuration**:
   ```json
   {
     "mcpServers": {
       "filesystem-mcp": {
         "command": "/path/to/your/venv/bin/python",
         "args": ["/path/to/your/filesystem_mcp_server.py"],
         "env": {
           "NODE_ENV": "production"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### Cursor Editor

1. **Open Cursor Settings**:
   - Press `Cmd/Ctrl + ,` to open settings
   - Search for "MCP" or navigate to Extensions

2. **Add MCP Server**:
   ```json
   {
     "mcp.servers": {
       "filesystem-mcp": {
         "command": "python",
         "args": ["/path/to/your/filesystem_mcp_server.py"],
         "cwd": "/path/to/your/server/directory"
       }
     }
   }
   ```

3. **Restart Cursor**

### Visual Studio Code with MCP Extension

1. **Install MCP Extension**:
   - Open VS Code
   - Go to Extensions (`Ctrl+Shift+X`)
   - Search for "MCP" and install the MCP extension

2. **Configure in settings.json**:
   ```json
   {
     "mcp.servers": {
       "filesystem-mcp": {
         "command": "python",
         "args": ["/path/to/your/filesystem_mcp_server.py"],
         "cwd": "/path/to/your/server/directory"
       }
     }
   }
   ```

3. **Reload VS Code**

### Neovim with MCP Plugin

1. **Install MCP Plugin** (using packer.nvim):
   ```lua
   use {
     'mcp/mcp.nvim',
     config = function()
       require('mcp').setup({
         servers = {
           filesystem_mcp = {
             command = "python",
             args = { "/path/to/your/filesystem_mcp_server.py" },
             cwd = "/path/to/your/server/directory"
           }
         }
       })
     end
   }
   ```

2. **Run `:PackerSync`** to install the plugin

### Helix Editor

1. **Add to helix configuration** (`~/.config/helix/config.toml`):
   ```toml
   [language-server.mcp]
   command = "python"
   args = ["/path/to/your/filesystem_mcp_server.py"]
   config.root = "/path/to/your/server/directory"
   ```

2. **Restart Helix**

### Amazon Q CLI

Amazon Q CLI supports MCP servers for enhanced AI assistance. Here's how to configure your FastMCP server:

#### Prerequisites

1. **Install Amazon Q CLI**:
   ```bash
   # Download and install Amazon Q CLI
   curl -sSL https://amazon-q-cli.s3.amazonaws.com/install.sh | bash
   ```

2. **Authenticate with AWS**:
   ```bash
   aws configure
   # or use AWS SSO
   aws sso login
   ```

#### Configuration

1. **Locate Amazon Q CLI configuration file**:
   ```bash
   # Linux/macOS
   ~/.config/amazon-q/cli-config.json
   
   # Windows
   %APPDATA%\Amazon\Q\cli-config.json
   ```

2. **Add MCP server configuration**:
   ```json
   {
     "mcpServers": {
       "{{ config.server.name }}": {
         "command": "/path/to/your/venv/bin/python",
         "args": ["/path/to/your/filesystem_mcp_server.py"],
         "cwd": "/path/to/your/server/directory",
         "env": {
           "PYTHONPATH": "/path/to/your/server/directory",
           "AWS_PROFILE": "default"
         }
       }
     }
   }
   ```

3. **Restart Amazon Q CLI**:
   ```bash
   # Kill any running Amazon Q processes
   pkill -f amazon-q
   
   # Start Amazon Q CLI
   amazon-q
   ```

#### Using with Amazon Q

1. **Start Amazon Q CLI**:
   ```bash
   amazon-q
   ```

2. **Access MCP tools**:
   - Use the `@tools` command to see available MCP tools
   - Reference your tools directly in conversations
   - Example: "Use the listfiles tool to show the contents of the current directory"

3. **Integration features**:
   - **Context awareness**: Amazon Q can use your tools with project context
   - **Multi-tool workflows**: Chain multiple tools together for complex tasks
   - **AWS integration**: Tools work alongside AWS services and resources

#### Amazon Q CLI Examples

```bash
# Start Amazon Q CLI
amazon-q

# Use your MCP tools
@tools listfiles --path /home/user/projects

# Chain multiple tools
@tools createdirectory --path /tmp/backup && @tools backupdatabase --user admin --password secret --database myapp

# Use with AWS context
@tools dockercontainer --action logs --container my-app-container
```

#### Benefits of Amazon Q CLI Integration

- **AWS-Native**: Seamless integration with AWS services and resources
- **Context Awareness**: Amazon Q understands your AWS environment and can provide relevant suggestions
- **Enhanced Productivity**: Combine your custom MCP tools with AWS best practices and recommendations
- **Enterprise Features**: Access to enterprise-grade AI assistance with AWS security and compliance
- **Multi-Service Integration**: Use your tools alongside AWS CLI, SDKs, and other AWS tools

#### Use Cases

- **DevOps Automation**: Use filesystem tools for deployment scripts alongside AWS infrastructure
- **Database Management**: Combine database backup tools with AWS RDS and DynamoDB operations
- **Container Orchestration**: Use Docker tools with AWS ECS, EKS, and Lambda deployments
- **File Management**: Organize and manage files across AWS S3, EFS, and local filesystems
- **Development Workflows**: Integrate development tools with AWS CodeCommit, CodeBuild, and CodeDeploy

#### Troubleshooting Amazon Q CLI

1. **Check MCP server status**:
   ```bash
   amazon-q --list-mcp-servers
   ```

2. **Test MCP connection**:
   ```bash
   amazon-q --test-mcp-server filesystem-mcp
   ```

3. **View logs**:
   ```bash
   # Amazon Q CLI logs
   tail -f ~/.config/amazon-q/cli.log
   
   # Your MCP server logs (if logging is enabled)
   tail -f /path/to/your/server/mcp.log
   ```

4. **Common issues**:
   - **Authentication**: Ensure AWS credentials are properly configured
   - **Permissions**: Check IAM permissions for Amazon Q service
   - **Network**: Verify network connectivity to AWS services
   - **MCP server**: Ensure your FastMCP server starts without errors

### Generic MCP Client Configuration

For any MCP-compatible client, use this standard configuration:

**With Virtual Environment (Recommended):**
```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["/absolute/path/to/your_server.py"],
      "cwd": "/path/to/server/directory",
      "env": {
        "PYTHONPATH": "/path/to/server/directory"
      }
    }
  }
}
```

**With System Python:**
```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "python",
      "args": ["/absolute/path/to/your_server.py"],
      "cwd": "/path/to/server/directory",
      "env": {
        "PYTHONPATH": "/path/to/server/directory"
      }
    }
  }
}
```

### Configuration Parameters

- **`command`**: The Python interpreter command
- **`args`**: Array of arguments (first should be the server script path)
- **`cwd`**: Working directory for the server process
- **`env`**: Environment variables to pass to the server

### Troubleshooting MCP Configuration

1. **Check Paths**: Ensure all paths are absolute and correct
2. **Python Path**: Make sure Python can find your server script
3. **Virtual Environment**: Verify the venv path in MCP config points to the correct Python interpreter
4. **Dependencies**: Verify all required packages are installed in the virtual environment
5. **Permissions**: Check that the server script is executable
6. **Logs**: Check editor logs for MCP connection errors

### Virtual Environment Setup Issues

**Common Issues:**
- **Virtual environment not found**: Ensure `venv` directory exists in your server directory
- **Python interpreter not found**: Check that `venv/bin/python` (Linux/macOS) or `venv\Scripts\python.exe` (Windows) exists
- **Dependencies missing**: Activate the virtual environment and run `pip install -r requirements.txt`
- **`ensurepip` not available**: Install the python3-venv package (Ubuntu/Debian)

**Quick Fix:**
```bash
# Navigate to your server directory
cd /path/to/your/server

# Create virtual environment if missing
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Ubuntu/Debian Systems:**
If you get an "ensurepip is not available" error:
```bash
# Install python3-venv package
sudo apt install python3-venv

# Then create the virtual environment
python3 -m venv venv
```

**Alternative: Using virtualenv**
If `python3 -m venv` doesn't work:
```bash
# Install virtualenv
pip install virtualenv

# Create virtual environment
virtualenv venv

# Activate
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows
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