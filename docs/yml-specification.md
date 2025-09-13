# YML Configuration Format Specification

This document provides the formal specification for the YML configuration format used by `shellmcp`.

## Schema Definition

```yaml
# Root document structure
type: object
properties:
  server:
    type: object
    required: [name, desc]
    properties:
      name:
        type: string
        description: "Name of the MCP server"
      desc:
        type: string
        description: "Description of the server"
      version:
        type: string
        description: "Server version"
        default: "1.0.0"
      env:
        type: object
        description: "Environment variables"
        additionalProperties:
          type: string
  
  args:
    type: object
    description: "Reusable argument definitions"
    additionalProperties:
      type: object
      required: [help]
      properties:
        help:
          type: string
          description: "Argument description"
        type:
          type: string
          enum: [string, number, boolean, array]
          default: string
        default:
          description: "Default value (makes argument optional)"
        choices:
          type: array
          description: "Allowed values for validation"
        pattern:
          type: string
          description: "Regex pattern for validation"
  
  tools:
    type: object
    description: "Tool definitions"
    additionalProperties:
      type: object
      required: [cmd, desc]
      properties:
        cmd:
          type: string
          description: "Shell command to execute (supports Jinja2 templates)"
        desc:
          type: string
          description: "Tool description"
        help-cmd:
          type: string
          description: "Command to get help text"
        args:
          type: array
          description: "Argument definitions"
          items:
            type: object
            required: [name, help]
            properties:
              name:
                type: string
                description: "Argument name"
              help:
                type: string
                description: "Argument description"
              type:
                type: string
                enum: [string, number, boolean, array]
                default: string
              default:
                description: "Default value (makes argument optional)"
              choices:
                type: array
                description: "Allowed values"
              pattern:
                type: string
                description: "Regex validation pattern"
              ref:
                type: string
                description: "Reference to reusable argument definition"
        env:
          type: object
          description: "Tool-specific environment variables"
          additionalProperties:
            type: string
  
  resources:
    type: object
    description: "Resource definitions"
    additionalProperties:
      type: object
      required: [uri, name]
      properties:
        uri:
          type: string
          description: "Resource URI"
        name:
          type: string
          description: "Resource name"
        description:
          type: string
          description: "Resource description"
        mime_type:
          type: string
          description: "MIME type of the resource"
        cmd:
          type: string
          description: "Shell command to generate resource content (supports Jinja2 templates)"
        file:
          type: string
          description: "File path to read resource content from (supports Jinja2 templates)"
        text:
          type: string
          description: "Direct text content for the resource (supports Jinja2 templates)"
        args:
          type: array
          description: "Argument definitions for resource generation"
          items:
            type: object
            required: [name, help]
            properties:
              name:
                type: string
                description: "Argument name"
              help:
                type: string
                description: "Argument description"
              type:
                type: string
                enum: [string, number, boolean, array]
                default: string
              default:
                description: "Default value (makes argument optional)"
              choices:
                type: array
                description: "Allowed values"
              pattern:
                type: string
                description: "Regex validation pattern"
              ref:
                type: string
                description: "Reference to reusable argument definition"
        env:
          type: object
          description: "Resource-specific environment variables"
          additionalProperties:
            type: string
  
  prompts:
    type: object
    description: "Prompt definitions"
    additionalProperties:
      type: object
      required: [name]
      properties:
        name:
          type: string
          description: "Prompt name"
        description:
          type: string
          description: "Prompt description"
        cmd:
          type: string
          description: "Shell command to generate prompt content (supports Jinja2 templates)"
        file:
          type: string
          description: "File path to read prompt content from (supports Jinja2 templates)"
        template:
          type: string
          description: "Direct Jinja2 template content for the prompt"
        args:
          type: array
          description: "Argument definitions for prompt generation"
          items:
            type: object
            required: [name, help]
            properties:
              name:
                type: string
                description: "Argument name"
              help:
                type: string
                description: "Argument description"
              type:
                type: string
                enum: [string, number, boolean, array]
                default: string
              default:
                description: "Default value (makes argument optional)"
              choices:
                type: array
                description: "Allowed values"
              pattern:
                type: string
                description: "Regex validation pattern"
              ref:
                type: string
                description: "Reference to reusable argument definition"
        env:
          type: object
          description: "Prompt-specific environment variables"
          additionalProperties:
            type: string
```

## Jinja2 Template Context

The `cmd` field supports Jinja2 templating with the following context variables:

```python
# Template context structure
{
    # Argument values (from args definition)
    "arg_name": "argument_value",
    
    # Environment variables (from server.env and tool.env)
    "ENV_VAR": "value",
    
    # Built-in functions
    "now": datetime_function,  # Current timestamp
    
    # Built-in filters
    # Standard Jinja2 filters: upper, lower, replace, etc.
}
```

## Validation Rules

1. **Argument Requirements**: Arguments are required unless they have a `default` value
2. **Reference Resolution**: `ref` must reference a valid argument definition in the `args` section
3. **Template Syntax**: `cmd` and `file` fields must contain valid Jinja2 template syntax
4. **Unique Names**: Tool names and argument names must be unique within their scope
5. **Type Coercion**: Argument values are coerced to their specified type
6. **Resource/Prompt Requirements**: Resources must specify exactly one of `cmd`, `file`, or `text`. Prompts must specify exactly one of `cmd`, `file`, or `template`

## Example Validation

```yaml
# Valid configuration
server:
  name: "my-server"
  desc: "My MCP server"

tools:
  MyTool:
    cmd: "echo {{ message }}"
    desc: "Echo a message"
    args:
      - name: message
        help: "Message to echo"
        default: "Hello World"

# Invalid configurations
# ❌ Missing required fields
server:
  name: "my-server"
  # Missing 'desc'

# ❌ Invalid reference
tools:
  MyTool:
    cmd: "echo {{ message }}"
    desc: "Echo a message"
    args:
      - name: message
        ref: "NonExistentArg"  # Reference doesn't exist

# ❌ Invalid Jinja2 syntax
tools:
  MyTool:
    cmd: "echo {{ message"  # Unclosed template
    desc: "Echo a message"
```

## Data Types

### Argument Types

- **string**: Text value (default)
- **number**: Numeric value (integer or float)
- **boolean**: True/false value
- **array**: List of values

### Type Coercion

Values are automatically coerced to their specified type:

```yaml
args:
  - name: count
    type: number
    # "10" -> 10, "3.14" -> 3.14
  
  - name: enabled
    type: boolean
    # "true" -> True, "false" -> False, "1" -> True, "0" -> False
  
  - name: items
    type: array
    # "a,b,c" -> ["a", "b", "c"]
```

## Environment Variables

Environment variables can be defined at two levels:

### Server Level
```yaml
server:
  env:
    NODE_ENV: production
    API_URL: https://api.example.com
```

### Tool Level
```yaml
tools:
  MyTool:
    env:
      DEBUG: "true"
      TIMEOUT: "30"
```

Tool-level environment variables override server-level variables.

## Reference Resolution

Arguments can reference reusable definitions:

```yaml
args:
  FilePath:
    help: "Path to a file"
    pattern: "^[^\\0]+$"

tools:
  MyTool:
    args:
      - name: input_file
        ref: FilePath  # References the FilePath definition above
```

## Jinja2 Template Features

### Basic Syntax
```yaml
cmd: "echo {{ message }}"
```

### Conditional Logic
```yaml
cmd: |
  {% if debug %}
  echo "Debug mode enabled"
  {% else %}
  echo "Production mode"
  {% endif %}
```

### Loops
```yaml
cmd: |
  {% for service in services %}
  docker start {{ service }}
  {% endfor %}
```

### Variable Assignment
```yaml
cmd: |
  {% set backup_file = "backup_" + timestamp + ".sql" %}
  mysqldump {{ database }} > {{ backup_file }}
```

### Filters
```yaml
cmd: |
  {% set safe_name = name | replace(' ', '_') | lower %}
  echo "{{ safe_name }}"
```

## Error Handling

### Validation Errors
- Missing required fields
- Invalid argument references
- Invalid Jinja2 template syntax
- Duplicate names

### Runtime Errors
- Command execution failures
- Template rendering errors
- Type coercion failures

## Resources and Prompts

### Resources
Resources are static data that clients can read. They can be generated by shell commands or read from files, and can be parameterized using arguments.

#### Command-based Resources
```yaml
resources:
  SystemInfo:
    uri: "system://info"
    name: "System Information"
    description: "Current system information"
    mime_type: "text/plain"
    cmd: "uname -a && df -h"
    
  ConfigFile:
    uri: "file://config/{{ config_name }}"
    name: "Configuration File"
    description: "Read configuration file"
    mime_type: "text/plain"
    cmd: "cat {{ config_path }}"
    args:
      - name: config_path
        help: "Path to configuration file"
        ref: FilePath
      - name: config_name
        help: "Configuration name"
        default: "default"
```

#### File-based Resources
```yaml
resources:
  StaticDocumentation:
    uri: "docs://{{ doc_type }}"
    name: "Static Documentation"
    description: "Read documentation from file"
    mime_type: "text/markdown"
    file: "docs/{{ doc_type }}.md"
    args:
      - name: doc_type
        help: "Type of documentation"
        choices: ["api", "user-guide", "troubleshooting"]
        default: "api"
  
  TemplateFile:
    uri: "template://{{ template_name }}"
    name: "Template File"
    description: "Read template file"
    mime_type: "text/plain"
    file: "templates/{{ template_name }}.txt"
    args:
      - name: template_name
        help: "Template name"
        type: string
```

#### Text-based Resources
```yaml
resources:
  StaticText:
    uri: "text://static"
    name: "Static Text Resource"
    description: "Direct text content"
    mime_type: "text/plain"
    text: "This is a static text resource."
  
  DynamicText:
    uri: "text://{{ resource_name }}"
    name: "Dynamic Text Resource"
    description: "Dynamic text content with variables"
    mime_type: "text/plain"
    text: |
      Hello {{ user_name }}!
      
      This is a dynamic text resource for {{ resource_name }}.
      
      {% if include_timestamp %}
      Generated at: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}
      {% endif %}
    args:
      - name: user_name
        help: "User name"
        type: string
        default: "User"
      - name: resource_name
        help: "Resource name"
        type: string
        default: "default"
      - name: include_timestamp
        help: "Include timestamp"
        type: boolean
        default: false
```

### Prompts
Prompts are dynamic templates that clients can use to generate content. They can be generated by shell commands or read from files, and support Jinja2 templating for flexible prompt generation.

#### Command-based Prompts
```yaml
prompts:
  CodeReview:
    name: "Code Review Prompt"
    description: "Generate a code review prompt"
    cmd: |
      You are a senior software engineer reviewing the following {{ language }} code:
      
      ```{{ language }}
      {{ code }}
      ```
      
      Please provide a thorough code review focusing on:
      - Code quality and best practices
      - Performance implications
      - Security considerations
      - Maintainability
      
      {% if focus_areas %}
      Pay special attention to: {{ focus_areas }}
      {% endif %}
    args:
      - name: language
        help: "Programming language"
        choices: ["python", "javascript", "java", "go"]
        default: "python"
      - name: code
        help: "Code to review"
        type: string
      - name: focus_areas
        help: "Specific areas to focus on"
        type: string
        default: ""
```

#### File-based Prompts
```yaml
prompts:
  CodeReviewTemplate:
    name: "Code Review Template"
    description: "Load code review prompt from template file"
    file: "prompts/code_review_{{ language }}.txt"
    args:
      - name: language
        help: "Programming language"
        choices: ["python", "javascript", "java", "go"]
        default: "python"
  
  CustomPrompt:
    name: "Custom Prompt"
    description: "Load custom prompt from file"
    file: "prompts/{{ prompt_name }}.txt"
    args:
      - name: prompt_name
        help: "Name of the prompt file"
        type: string
```

#### Direct Template Prompts
```yaml
prompts:
  SimpleTemplate:
    name: "Simple Template Prompt"
    description: "Direct Jinja2 template prompt"
    template: |
      You are a helpful assistant. Please help with the following request:
      
      {{ user_request }}
      
      {% if context %}
      Additional context: {{ context }}
      {% endif %}
    args:
      - name: user_request
        help: "User's request"
        type: string
      - name: context
        help: "Additional context"
        type: string
        default: ""
  
  AdvancedTemplate:
    name: "Advanced Template Prompt"
    description: "Complex template with conditional logic"
    template: |
      You are a {{ role }} expert.
      
      {% if task_type == "analysis" %}
      Please analyze the following {{ subject }}:
      {% elif task_type == "generation" %}
      Please generate {{ subject }} with the following requirements:
      {% else %}
      Please help with {{ subject }}:
      {% endif %}
      
      {{ content }}
      
      {% if requirements %}
      Requirements:
      {% for req in requirements %}
      - {{ req }}
      {% endfor %}
      {% endif %}
      
      {% if output_format %}
      Please provide the output in {{ output_format }} format.
      {% endif %}
    args:
      - name: role
        help: "Expert role"
        choices: ["technical", "creative", "analytical", "business"]
        default: "technical"
      - name: task_type
        help: "Type of task"
        choices: ["analysis", "generation", "help"]
        default: "help"
      - name: subject
        help: "Subject matter"
        type: string
      - name: content
        help: "Main content"
        type: string
      - name: requirements
        help: "List of requirements"
        type: array
        default: []
      - name: output_format
        help: "Desired output format"
        type: string
        default: ""
```

## Best Practices

1. **Use descriptive names**: Choose clear, meaningful names for tools, resources, prompts, and arguments
2. **Provide help text**: Always include helpful descriptions
3. **Set sensible defaults**: Use defaults for optional arguments
4. **Validate inputs**: Use patterns and choices for input validation
5. **Reuse definitions**: Create reusable argument definitions for common patterns
6. **Test templates**: Validate Jinja2 templates before deployment
7. **Resource URIs**: Use meaningful URIs for resources (e.g., `system://info`, `file://config`)
8. **Prompt clarity**: Make prompts clear and specific with good structure
9. **MIME types**: Specify appropriate MIME types for resources when possible