# ShellMCP

**Expose Shell Commands as MCP tools**

ShellMCP is a powerful tool that allows you to easily create Model Context Protocol (MCP) servers by exposing shell commands as structured tools. Define your tools in YAML, and ShellMCP generates a complete FastMCP server for you.

## Motivation

AI agents need safe, controlled access to system functionality. Instead of granting full shell access (which poses security risks), ShellMCP enables you to expose only the specific commands you trust. This allows AI agents to work autonomously with a predefined set of safe operations, eliminating the risk of unintended system modifications or security breaches.

## Quick Start

```bash
# Install
pip install shellmcp

# Create a new server
shellmcp new --name "my-server" --desc "My custom MCP server"

# Add a tool
shellmcp add-tool my-server.yml

# Generate the server
shellmcp generate my-server.yml
```

## Features

- 🚀 **Simple YAML Configuration**: Define tools, resources, and prompts in clean YAML
- 🔧 **Interactive CLI**: Add tools and resources with guided prompts
- 📝 **Template Support**: Use Jinja2 templates for dynamic command generation
- ✅ **Validation**: Built-in configuration validation and error checking
- 🎯 **FastMCP Integration**: Generates production-ready FastMCP servers
- 📦 **Complete Output**: Includes server code, requirements, and documentation

## Example

```yaml
server:
  name: "file-manager"
  desc: "File system operations"
  version: "1.0.0"

tools:
  list_files:
    cmd: "ls -la {{path}}"
    desc: "List files in a directory"
    args:
      - name: path
        help: "Directory path to list"
        type: string
        default: "."
```

## Installation

```bash
pip install shellmcp
```

## Documentation

- [YAML Specification](docs/yml-specification.md)

## License

MIT License - see [LICENSE](LICENSE) for details.