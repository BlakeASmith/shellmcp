# shellmcp
Expose Shell Commands as MCP tools

## YML Configuration Format

The `shellmcp` tool uses YAML configuration files to define MCP servers and their tools. Here's the complete specification:

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
