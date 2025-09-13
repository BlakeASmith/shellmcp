# mCP Server Examples

This directory contains example mCP servers demonstrating different features and capabilities.

## 📁 Files

### Configuration Files
- **`example_config.yml`** - Basic filesystem MCP server with tools only
- **`comprehensive_config.yml`** - Complete example with tools, resources, and prompts

### Generated Servers
- **`comprehensive_mcp_server.py`** - Working server generated from comprehensive config

### Supporting Files
- **`requirements.txt`** - Python dependencies
- **`docs/`** - Documentation files for file-based resources
- **`prompts/`** - Template files for file-based prompts

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Comprehensive Server
```bash
python3 comprehensive_mcp_server.py
```

## 📋 What's Demonstrated

### Tools
- **ListFiles** - List directory contents with `ls -la`
- **ReadFile** - Read file contents with `cat`

### Resources (3 types)
- **Command-based**: `SystemInfo` - System information via shell commands
- **File-based**: `ConfigFile` - Read files from filesystem
- **Text-based**: `StaticText` and `DynamicText` - Direct text content with Jinja2 templating

### Prompts (3 types)
- **Command-based**: `CodeReview` - Generate prompts via shell commands
- **File-based**: `CodeReviewTemplate` - Load prompts from template files
- **Template-based**: `SimpleTemplate` and `AdvancedTemplate` - Direct Jinja2 templates

## 🔧 Features

- ✅ **Full FastMCP compatibility** - Proper URI templates and decorators
- ✅ **Jinja2 templating** - Variables, conditionals, loops, filters
- ✅ **Argument validation** - Types, patterns, choices, defaults
- ✅ **Multiple content sources** - Commands, files, and direct text/templates
- ✅ **Error handling** - Graceful failures and validation

## 📖 Configuration

The servers are generated from YAML configuration files. See the YAML files for examples of:

- Server metadata (name, description, version)
- Reusable argument definitions
- Tool configurations with shell commands
- Resource configurations (cmd/file/text)
- Prompt configurations (cmd/file/template)
- Environment variables and validation rules

## 🎯 Usage

1. **Modify the YAML configuration** to match your needs
2. **Generate a new server** using the shellmcp generator
3. **Run the generated server** with FastMCP

Example generation:
```bash
cd /workspace
python3 -m shellmcp.generator /workspace/examples/configs/comprehensive_config.yml
```

The generated server will be ready to run with FastMCP and will expose all configured tools, resources, and prompts via the MCP protocol.