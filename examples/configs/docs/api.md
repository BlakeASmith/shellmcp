# API Documentation

This is the API documentation for the filesystem MCP server.

## Available Tools

### ListFiles
Lists files in a directory with detailed information.

**Parameters:**
- `path` (string): Directory path to list (default: ".")

### ReadFile
Reads and displays the contents of a file.

**Parameters:**
- `file` (string): File to read

## Available Resources

### SystemInfo
Provides current system information including OS details and disk usage.

### ConfigFile
Reads configuration files from the filesystem.

### StaticDocumentation
Provides static documentation files.

## Available Prompts

### CodeReview
Generates a code review prompt for various programming languages.

### CodeReviewTemplate
Loads code review prompts from template files.

### CustomPrompt
Loads custom prompts from files.