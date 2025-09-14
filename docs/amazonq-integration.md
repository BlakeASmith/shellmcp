# AmazonQ Integration

ShellMCP can generate MCP server configuration JSON for AmazonQ. This allows you to easily add your generated servers to AmazonQ's `mcp.json` configuration file.

## Quick Start

1. **Create and generate your ShellMCP server:**
   ```bash
   # Create a new server configuration
   shellmcp new --name "my-tools" --desc "My custom tools for AmazonQ"
   
   # Add some tools
   shellmcp add-tool my_tools.yml
   
   # Generate the server
   shellmcp generate my_tools.yml
   ```

2. **Generate MCP JSON configuration:**
   ```bash
   # Output JSON to stdout
   shellmcp mcp-json my_tools.yml
   
   # Or save to file
   shellmcp mcp-json my_tools.yml --output-file mcp.json
   ```

3. **Add to AmazonQ** by copying the JSON to your `mcp.json` file

## Command Usage

```bash
# Generate JSON and output to stdout
shellmcp mcp-json my_tools.yml

# Generate JSON and save to file
shellmcp mcp-json my_tools.yml --output-file mcp.json

# Use specific server path
shellmcp mcp-json my_tools.yml --server-path ./output/my_tools_server.py

# Use different Python executable
shellmcp mcp-json my_tools.yml --python-executable python3.11
```

## Example: File Manager Server

Here's a complete example of creating and generating MCP JSON for a file manager server:

### 1. Create Configuration

```bash
shellmcp new --name "file-manager" --desc "File system operations" --version "1.0.0"
```

This creates `file_manager.yml`:

```yaml
server:
  name: "file-manager"
  desc: "File system operations"
  version: "1.0.0"

args:
  path_arg:
    help: "Directory path"
    type: string
    default: "."

tools:
  list_files:
    cmd: "ls -la {{path}}"
    desc: "List files in a directory"
    args:
      - name: path
        ref: path_arg
  
  search_files:
    cmd: "find {{path}} -name '{{pattern}}' -type f"
    desc: "Search for files matching a pattern"
    args:
      - name: path
        ref: path_arg
      - name: pattern
        help: "Search pattern"
        type: string
```

### 2. Generate Server

```bash
shellmcp generate file_manager.yml
```

### 3. Generate MCP JSON

```bash
shellmcp mcp-json file_manager.yml
```

### 4. Generated MCP Configuration

The command outputs:

```json
{
  "mcpServers": {
    "file-manager": {
      "command": "python3",
      "args": ["/path/to/file_manager/file_manager_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/file_manager"
      }
    }
  }
}
```

## AmazonQ Configuration Locations

AmazonQ looks for `mcp.json` in these locations:

- **Global**: `~/.aws/amazonq/mcp.json`
- **Local**: `./.amazonq/mcp.json`
- **User Config**: `~/.config/amazonq/mcp.json`

## Manual Integration

1. **Generate the JSON:**
   ```bash
   shellmcp mcp-json my_tools.yml --output-file mcp_config.json
   ```

2. **Copy to your AmazonQ config:**
   ```bash
   # For local project
   mkdir -p .amazonq
   cp mcp_config.json .amazonq/mcp.json
   
   # Or merge with existing config
   # (manually edit your existing mcp.json to add the new server)
   ```

3. **Restart AmazonQ** to load your new MCP server

## Template Customization

The MCP JSON is generated using a Jinja2 template located at `shellmcp/templates/mcp_config.json.j2`:

```json
{
  "mcpServers": {
    "{{ server_name }}": {
      "command": "{{ python_executable }}",
      "args": ["{{ server_path }}"],
      "env": {
        "PYTHONPATH": "{{ server_dir }}"
      }
    }
  }
}
```

You can modify this template to customize the generated configuration format.

## Troubleshooting

### Server Not Found

If you get a "server file not found" error:

1. Ensure you've run `shellmcp generate` first
2. Check the server path is correct
3. Use `--server-path` to specify the exact path

### JSON Format Issues

If the generated JSON is invalid:

1. Check that your YAML configuration is valid
2. Verify the server file exists at the specified path
3. Ensure file paths don't contain special characters

## Best Practices

1. **Use descriptive server names** - They become identifiers in AmazonQ
2. **Test your tools locally** - Validate your YAML configuration before generating JSON
3. **Use absolute paths** - The generator automatically converts relative paths to absolute
4. **Version control** - Keep your YAML configurations in version control
5. **Document your tools** - Add clear descriptions for better AmazonQ integration