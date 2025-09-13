# Pydantic Models for YAML Configuration

This directory contains Pydantic models for parsing and validating YAML configuration files for the `shellmcp` project.

## Models Overview

### Core Models

- **`YMLConfig`**: Root configuration model that validates the entire YAML structure
- **`ServerConfig`**: Server configuration (name, description, version, environment variables)
- **`ToolConfig`**: Individual tool configuration (command, description, arguments, environment)
- **`ArgumentDefinition`**: Reusable argument definitions
- **`ToolArgument`**: Tool-specific argument definitions

### Key Features

1. **Full Validation**: All models include comprehensive validation rules
2. **Reference Resolution**: Support for reusable argument definitions via `ref` fields
3. **Jinja2 Template Validation**: Built-in validation for Jinja2 template syntax
4. **Type Safety**: Strong typing with Pydantic for all configuration fields
5. **Error Handling**: Detailed error messages for validation failures

## Usage

### Basic Usage

```python
from shellmcp.parser import YMLParser

# Parse from file
parser = YMLParser()
config = parser.load_from_file("config.yml")

# Parse from string
yaml_content = """
server:
  name: my-server
  desc: My MCP server
tools:
  MyTool:
    cmd: echo {{ message }}
    desc: Echo a message
"""
config = parser.load_from_string(yaml_content)
```

### Advanced Features

```python
# Validate Jinja2 templates
template_validation = parser.validate_all_templates()

# Check argument consistency
consistency_issues = parser.validate_argument_consistency()

# Get resolved arguments (expanding references)
resolved_args = parser.get_resolved_tool_arguments("MyTool")

# Get template variables
template_vars = parser.get_tool_template_variables("MyTool")
```

## Validation Rules

### Server Configuration
- `name` and `desc` are required
- `version` defaults to "1.0.0"
- `env` is optional dictionary of environment variables

### Tool Configuration
- `cmd` and `desc` are required
- `help-cmd` is optional
- `args` is optional list of arguments
- `env` is optional dictionary of environment variables

### Argument Definitions
- `help` is required for all arguments
- `type` defaults to "string" (options: string, number, boolean, array)
- `default` makes argument optional
- `choices` restricts allowed values
- `pattern` provides regex validation
- `ref` references reusable argument definitions

### Validation Checks
1. **Required Fields**: All required fields must be present
2. **Unique Names**: Tool names and argument names must be unique within their scope
3. **Reference Resolution**: All `ref` fields must reference existing argument definitions
4. **Regex Validation**: All `pattern` fields must be valid regex
5. **Template Syntax**: Jinja2 templates must be syntactically valid
6. **Argument Consistency**: Template variables should have corresponding arguments

## Error Handling

The models provide detailed error messages for common issues:

```python
try:
    config = YMLConfig(**data)
except ValidationError as e:
    print(f"Validation error: {e}")
```

Common validation errors:
- Missing required fields
- Invalid argument references
- Duplicate names
- Invalid regex patterns
- Invalid Jinja2 template syntax

## Examples

See the `examples/` directory for complete usage examples:
- `basic_example.py`: Simple configuration parsing
- `example_usage.py`: Advanced features demonstration
- `example_config.yml`: Comprehensive configuration example

## Testing

Run the test suite to verify model functionality:

```bash
pytest tests/
```

The tests cover:
- Model validation
- Reference resolution
- Template validation
- Error handling
- Edge cases