# User Guide

This is the user guide for the filesystem MCP server.

## Getting Started

1. Install the required dependencies
2. Configure your YAML file
3. Run the server

## Configuration

The server uses a YAML configuration file to define tools, resources, and prompts.

### Basic Structure

```yaml
server:
  name: your-server-name
  desc: Description of your server
  version: "1.0.0"

tools:
  # Tool definitions

resources:
  # Resource definitions

prompts:
  # Prompt definitions
```

## Usage Examples

### Using Tools
Tools are executed via shell commands and can accept parameters.

### Using Resources
Resources provide static or dynamic content that can be read by clients.

### Using Prompts
Prompts generate dynamic content for AI interactions.