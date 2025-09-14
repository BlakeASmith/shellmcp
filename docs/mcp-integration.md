# MCP Integration

ShellMCP can generate MCP server configuration JSON. This allows you to easily add your generated servers to MCP client configuration files.

## Quick Start

1. **Create and generate your ShellMCP server:**
   ```bash
   # Create a new server configuration
   shellmcp new --name "my-tools" --desc "My custom tools"
   
   # Add some tools
   shellmcp add-tool my_tools.yml
   
   # Generate the server
   shellmcp generate my_tools.yml
   ```

2. **Generate MCP configuration:**
   ```bash
   # Output JSON to stdout
   shellmcp mcp-config my_tools.yml
   
   # Or save to file
   shellmcp mcp-config my_tools.yml --output-file mcp.json
   ```

3. **Add to your MCP client** by copying the JSON to your configuration file

## Command Usage

```bash
# Generate JSON and output to stdout
shellmcp mcp-config my_tools.yml

# Generate JSON and save to file
shellmcp mcp-config my_tools.yml --output-file mcp.json

# Use specific server path
shellmcp mcp-config my_tools.yml --server-path ./output/my_tools_server.py

# Use different Python executable
shellmcp mcp-config my_tools.yml --python-executable python3.11

# Enable auto-trusting for tools
shellmcp mcp-config my_tools.yml --allow-auto-confirm
```


## MCP Configuration Locations

MCP clients typically look for configuration in these locations:

- **Global**: `~/.config/mcp/config.json`
- **Local**: `./mcp.json`
- **User Config**: `~/.mcp/config.json`

## Manual Integration

1. **Generate the configuration:**
   ```bash
   shellmcp mcp-config my_tools.yml --output-file mcp_config.json
   ```

2. **Copy to your MCP client config:**
   ```bash
   # For local project
   cp mcp_config.json ./mcp.json
   
   # Or merge with existing config
   # (manually edit your existing config to add the new server)
   ```

3. **Restart your MCP client** to load your new MCP server

## Auto-Trusting Tools

You can enable auto-trusting for your tools using the `--allow-auto-confirm` flag. This adds the `--no-confirm-dangerous` argument to the server command, allowing tools to run without user confirmation:

```bash
shellmcp mcp-config my_tools.yml --allow-auto-confirm
```

This generates:

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "python3",
      "args": ["--no-confirm-dangerous", "/path/to/my_tools_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/server/directory"
      }
    }
  }
}
```

**Security Note**: Only enable auto-trusting for tools you fully trust, as this allows them to run without user confirmation.

## Template Customization

The MCP JSON is generated using a Jinja2 template located at `shellmcp/templates/mcp_config.json.j2`:

```json
{
  "mcpServers": {
    "{{ server_name }}": {
      "command": "{{ python_executable }}",
      "args": [{% if allow_auto_confirm %}"--no-confirm-dangerous", {% endif %}"{{ server_path }}"],
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

1. **Use descriptive server names** - They become identifiers in your MCP client
2. **Test your tools locally** - Validate your YAML configuration before generating JSON
3. **Use absolute paths** - The generator automatically converts relative paths to absolute
4. **Version control** - Keep your YAML configurations in version control
5. **Document your tools** - Add clear descriptions for better MCP integration