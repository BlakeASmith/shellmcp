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

# Reusable argument definitions
args:
  FilePath:
    help: Path to a file or directory
    pattern: "^[^\\0]+$"

  SearchPattern:
    help: Pattern to search for (supports wildcards and regex)

  OptionalPath:
    help: Optional directory path
    default: "."

tools:
  ListFiles:
    cmd: ls -la $@
    desc: List files in the current directory
    help-cmd: ls --help
    args:
      - name: path
        ref: OptionalPath

  FindFiles:
    cmd: find $PATH -name "$PATTERN" -type f
    desc: Find files matching a pattern
    args:
      - name: PATH
        ref: FilePath
      - name: PATTERN
        ref: SearchPattern

  GrepFiles:
    cmd: grep -r "$PATTERN" "$PATH"
    desc: Search for patterns in files recursively
    args:
      - name: PATH
        ref: FilePath
      - name: PATTERN
        ref: SearchPattern

  GitStatus:
    cmd: git status --porcelain
    desc: Get git repository status

  SimpleEcho:
    cmd: echo "Hello $NAME"
    desc: Simple echo command
    args:
      - name: NAME
        help: Name to greet
        default: "World"

  LocalScript:
    cmd: ./scripts/deploy.sh $ENV $VERSION
    desc: Run local deployment script
    args:
      - name: ENV
        help: Environment to deploy to
        choices: ["dev", "staging", "prod"]
      - name: VERSION
        help: Version to deploy
        default: "latest"

  PythonScript:
    cmd: python scripts/analyze.py --input "$INPUT" --output "$OUTPUT"
    desc: Run Python analysis script
    args:
      - name: INPUT
        help: Input file path
      - name: OUTPUT
        help: Output file path
        default: "results.json"

  MakeCommand:
    cmd: make $TARGET
    desc: Run make target
    args:
      - name: TARGET
        help: Make target to run
        choices: ["build", "test", "clean", "install"]
```

### Local Script Examples

#### Shell Scripts
```yml
tools:
  BackupDatabase:
    cmd: ./scripts/backup-db.sh $DATABASE $BACKUP_DIR
    desc: Backup database using local script
    args:
      - name: DATABASE
        help: Database name to backup
      - name: BACKUP_DIR
        help: Directory to store backup
        default: "./backups"

  DeployApp:
    cmd: ./deploy.sh $ENV
    desc: Deploy application
    args:
      - name: ENV
        help: Environment to deploy to
        choices: ["dev", "staging", "prod"]
```

#### Python Scripts
```yml
tools:
  DataProcessor:
    cmd: python scripts/process_data.py --input "$INPUT" --format "$FORMAT"
    desc: Process data using Python script
    args:
      - name: INPUT
        help: Input data file
      - name: FORMAT
        help: Output format
        choices: ["json", "csv", "xml"]
        default: "json"

  BuildProject:
    cmd: make $TARGET
    desc: Build project using Make
    args:
      - name: TARGET
        help: Make target
        choices: ["all", "debug", "release", "clean"]
        default: "all"
```

### Jinja2 Template Support

Commands support Jinja2 templating for advanced command generation:

#### Basic Template Syntax
```yml
tools:
  ConditionalCommand:
    cmd: |
      {% if env == 'prod' %}
      docker run --restart=always -d $IMAGE
      {% else %}
      docker run -d $IMAGE
      {% endif %}
    desc: Run Docker container with environment-specific options
    args:
      - name: env
        help: Environment
        choices: ["dev", "staging", "prod"]
      - name: IMAGE
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

### Variable Substitution

The YML format supports several types of variable substitution:

#### Argument Variables
- `$ARG_NAME` - Substitutes the value of the argument
- `"$ARG_NAME"` - Quoted substitution (recommended for paths with spaces)

#### Environment Variables
- `$ENV_VAR` - Substitutes environment variable value
- `${ENV_VAR}` - Alternative syntax for environment variables

#### Special Variables
- `$@` - All arguments passed to the tool (space-separated)
- `$*` - All arguments as a single string
- `$#` - Number of arguments passed

#### Example Variable Usage

```yml
tools:
  ComplexCommand:
    cmd: docker run -v "$SOURCE_DIR:/app" -e "NODE_ENV=$ENV" $IMAGE_NAME $@
    desc: Run Docker container with volume mount
    args:
      - name: SOURCE_DIR
        type: string
        required: true
        help: Source directory to mount
      - name: IMAGE_NAME
        type: string
        required: true
        help: Docker image to run
    env:
      ENV: production
```

### Command Execution Patterns

#### Simple Commands
```yml
tools:
  SimpleCmd:
    cmd: echo "Hello World"
    desc: Simple command without arguments
```

#### Commands with Arguments
```yml
tools:
  ArgCmd:
    cmd: echo "Hello $NAME"
    desc: Command with arguments
    args:
      - name: NAME
        type: string
        required: true
        help: Name to greet
```

#### Piped Commands
```yml
tools:
  PipedCmd:
    cmd: cat "$FILE" | grep "$PATTERN" | sort
    desc: Command with pipes
    args:
      - name: FILE
        type: string
        required: true
        help: File to process
      - name: PATTERN
        type: string
        required: true
        help: Pattern to search for
```

#### Conditional Commands
```yml
tools:
  ConditionalCmd:
    cmd: |
      if [ -f "$FILE" ]; then
        cat "$FILE"
      else
        echo "File not found: $FILE"
      fi
    desc: Command with conditional logic
    args:
      - name: FILE
        type: string
        required: true
        help: File to check and display
```

#### Multi-line Commands
```yml
tools:
  MultiLineCmd:
    cmd: |
      echo "Starting backup..."
      tar -czf "$BACKUP_FILE" "$SOURCE_DIR"
      echo "Backup completed: $BACKUP_FILE"
    desc: Multi-step command
    args:
      - name: BACKUP_FILE
        type: string
        required: true
        help: Backup file name
      - name: SOURCE_DIR
        type: string
        required: true
        help: Directory to backup
```

### Validation and Error Handling

#### Input Validation
```yml
tools:
  ValidatedCmd:
    cmd: echo "Processing $EMAIL"
    desc: Command with input validation
    args:
      - name: EMAIL
        type: string
        required: true
        help: Email address
        pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      - name: PORT
        type: number
        required: true
        help: Port number
        choices: [80, 443, 8080, 3000, 5000]
```

#### Error Handling
```yml
tools:
  ErrorHandlingCmd:
    cmd: |
      if ! command -v "$TOOL" &> /dev/null; then
        echo "Error: $TOOL is not installed"
        exit 1
      fi
      $TOOL $@
    desc: Command with error handling
    args:
      - name: TOOL
        type: string
        required: true
        help: Tool name to check and execute
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
