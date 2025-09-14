# AmazonQ Integration

ShellMCP provides simple automation for adding your generated servers to AmazonQ's `mcp.json` configuration file.

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

2. **Add to AmazonQ:**
   ```bash
   # Auto-add to AmazonQ (detects existing config)
   shellmcp install-amazonq my_tools.yml
   ```

3. **Restart AmazonQ** to load your new MCP server!

## Configuration Locations

ShellMCP automatically detects and uses existing AmazonQ MCP configurations in the following locations:

- **Global**: `~/.aws/amazonq/mcp.json` - Available system-wide
- **Local**: `./.amazonq/mcp.json` - Project-specific configuration
- **User Config**: `~/.config/amazonq/mcp.json` - User-specific configuration

## Command Usage

```bash
# Add server to AmazonQ (auto-detects server path)
shellmcp install-amazonq my_tools.yml

# Add with specific server path
shellmcp install-amazonq my_tools.yml ./output/my_tools_server.py

# Add to specific config location
shellmcp install-amazonq my_tools.yml --config-location global

# Overwrite existing server
shellmcp install-amazonq my_tools.yml --force

# Use different Python executable
shellmcp install-amazonq my_tools.yml --python-executable python3.11
```

## Example: File Manager Server

Here's a complete example of creating and adding a file manager server:

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

### 3. Add to AmazonQ

```bash
shellmcp install-amazonq file_manager.yml
```

### 4. Generated MCP Configuration

The installer automatically adds to your `mcp.json`:

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

## Troubleshooting

### Server Not Found

If you get a "server file not found" error:

1. Ensure you've run `shellmcp generate` first
2. Check the server path is correct
3. Verify the generated server file exists

### Configuration Not Loading

If AmazonQ doesn't load your server:

1. Restart AmazonQ after installation
2. Check the `mcp.json` file format is valid JSON
3. Verify the server path is accessible
4. Check AmazonQ logs for error messages

### Permission Issues

If you encounter permission issues:

1. Ensure you have write access to the configuration directory
2. Try using `--config-location local` for project-specific configs
3. Check file permissions on the generated server files

## Best Practices

1. **Use descriptive server names** - They become identifiers in AmazonQ
2. **Test your tools locally** - Validate your YAML configuration before installing
3. **Use version control** - Keep your YAML configurations in version control
4. **Document your tools** - Add clear descriptions for better AmazonQ integration
5. **Start simple** - Begin with basic tools and expand gradually