# shellmcp
Expose Shell Commands as MCP tools

## YML Configuration Format

The `shellmcp` tool uses YAML configuration files to define MCP servers and their tools.

### Formal Specification

#### Schema Definition

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
```

#### Jinja2 Template Context

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

#### Validation Rules

1. **Argument Requirements**: Arguments are required unless they have a `default` value
2. **Reference Resolution**: `ref` must reference a valid argument definition in the `args` section
3. **Template Syntax**: `cmd` field must contain valid Jinja2 template syntax
4. **Unique Names**: Tool names and argument names must be unique within their scope
5. **Type Coercion**: Argument values are coerced to their specified type

#### Example Validation

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

Here's the complete specification:

### Server Configuration

```yml
server:
  name: string          # Required: Name of the MCP server
  desc: string          # Required: Description of the server
  version: string       # Optional: Server version (default: "1.0.0")
  env:                  # Optional: Environment variables
    VAR_NAME: value

# Optional: Reusable argument definitions
args:
  ArgName:              # Argument definition name
    help: string        # Required: Argument description
    type: string        # Optional: string|number|boolean|array (default: string)
    default: any        # Optional: Default value (makes argument optional)
    choices: []         # Optional: Allowed values
    pattern: string     # Optional: Regex validation
```

### Tool Configuration

```yml
tools:
  ToolName:             # Required: Tool identifier (must be unique)
    cmd: string         # Required: Shell command to execute (supports Jinja2 templates)
    desc: string        # Required: Tool description
    help-cmd: string    # Optional: Command to get help text
    args:               # Optional: Argument definitions
      - name: string    # Required: Argument name
        help: string    # Required: Argument description
        type: string    # Optional: string|number|boolean|array (default: string)
        default: any    # Optional: Default value (makes argument optional)
        choices: []     # Optional: Allowed values
        pattern: string # Optional: Regex validation
        # OR reference a reusable argument definition:
        ref: ArgName    # Reference to an argument defined in the 'args' section
    env:                # Optional: Tool-specific environment variables
      VAR_NAME: value
```

### Example Configuration

```yml
server:
  name: filesystem-mcp
  desc: MCP Server for filesystem operations

tools:
  ListFiles:
    cmd: ls -la {{ path }}
    desc: List files in the current directory
    help-cmd: ls --help
    args:
      - name: path
        help: Directory path to list
        default: "."
```

### Local Script Example

```yml
tools:
  BackupDatabase:
    cmd: ./scripts/backup-db.sh {{ database }} {{ backup_dir }}
    desc: Backup database using local script
    args:
      - name: database
        help: Database name to backup
      - name: backup_dir
        help: Directory to store backup
        default: "./backups"
```

### Jinja2 Template Support

Commands support Jinja2 templating for advanced command generation:

#### Basic Template Syntax
```yml
tools:
  ConditionalCommand:
    cmd: |
      {% if env == 'prod' %}
      docker run --restart=always -d {{ image }}
      {% else %}
      docker run -d {{ image }}
      {% endif %}
    desc: Run Docker container with environment-specific options
    args:
      - name: env
        help: Environment
        choices: ["dev", "staging", "prod"]
      - name: image
        help: Docker image to run

  ComplexTemplate:
    cmd: |
      {% set backup_file = "backup_" + timestamp + ".sql" %}
      mysqldump -h {{ host }} -u {{ user }} -p{{ password }} {{ database }} > {{ backup_file }}
      {% if compress %}
      gzip {{ backup_file }}
      {% endif %}
    desc: Database backup with optional compression
    args:
      - name: host
        help: Database host
        default: "localhost"
      - name: user
        help: Database user
      - name: password
        help: Database password
      - name: database
        help: Database name
      - name: compress
        help: Compress backup
        type: boolean
        default: false
      - name: timestamp
        help: Timestamp for backup file
        default: "{{ now().strftime('%Y%m%d_%H%M%S') }}"
```


## Step 2: generate an MCP server executable 

```sh
shellmcp generate server.yml --out ~/.local/bin/filesystem-mco
```

## Step 3: configure mcp.json

```json
TODO
```

## Step 4: DONE! Use tools 
