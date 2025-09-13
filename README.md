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
```

### Tool Configuration

```yml
tools:
  ToolName:             # Required: Tool identifier (must be unique)
    cmd: string         # Required: Shell command to execute
    desc: string        # Required: Tool description
    help-cmd: string    # Optional: Command to get help text
    args:               # Optional: Argument definitions
      - name: string    # Required: Argument name
        type: string    # Optional: Argument type (string, number, boolean, array)
        required: bool  # Optional: Whether argument is required (default: true)
        help: string    # Optional: Argument description
        default: any    # Optional: Default value
        choices: []     # Optional: Allowed values for validation
        pattern: string # Optional: Regex pattern for validation
    env:                # Optional: Tool-specific environment variables
      VAR_NAME: value
    working_dir: string # Optional: Tool-specific working directory
    timeout: integer    # Optional: Tool-specific timeout
    output:             # Optional: Output processing
      format: string    # Optional: Output format (text, json, yaml, xml)
      filter: string    # Optional: Command to filter/transform output
    security:           # Optional: Security constraints
      allow_stdin: bool # Optional: Allow stdin input (default: false)
      max_args: int     # Optional: Maximum number of arguments
      allowed_dirs: []  # Optional: Restrict to specific directories
```

### Example Configurations

#### Basic Filesystem Operations

```yml
server:
  name: filesystem-mcp
  desc: MCP Server for filesystem operations
  version: "1.0.0"

tools:
  ListFiles:
    cmd: ls -la $@
    desc: List files in the current directory with detailed information
    help-cmd: ls --help
    args:
      - name: path
        type: string
        required: false
        help: Directory path to list (defaults to current directory)
        default: "."

  FindFiles:
    cmd: find $PATH -name "$PATTERN" -type f
    desc: Find files matching a pattern
    args:
      - name: PATH
        type: string
        required: true
        help: Directory to search in
      - name: PATTERN
        type: string
        required: true
        help: File pattern to match (supports wildcards)
    security:
      allowed_dirs: ["/home", "/tmp", "/workspace"]

  GrepExtract:
    cmd: grep -n "$PATTERN" "$FILE"
    desc: Search for patterns in files
    args:
      - name: PATTERN
        type: string
        required: true
        help: Regular expression pattern to search for
      - name: FILE
        type: string
        required: true
        help: File path to search in
    output:
      format: text
```

#### Development Tools

```yml
server:
  name: dev-tools-mcp
  desc: MCP Server for development operations
  env:
    NODE_ENV: development

tools:
  GitStatus:
    cmd: git status --porcelain
    desc: Get git repository status
    working_dir: $GIT_ROOT
    output:
      format: text

  GitLog:
    cmd: git log --oneline -n $COUNT
    desc: Get recent git commit history
    args:
      - name: COUNT
        type: number
        required: false
        default: 10
        help: Number of commits to show
    working_dir: $GIT_ROOT

  NpmInstall:
    cmd: npm install $PACKAGES
    desc: Install npm packages
    args:
      - name: PACKAGES
        type: string
        required: true
        help: Package names to install (space-separated)
    working_dir: $PROJECT_ROOT
    timeout: 120

  DockerPs:
    cmd: docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    desc: List running Docker containers
    output:
      format: text
```

#### System Administration

```yml
server:
  name: sysadmin-mcp
  desc: MCP Server for system administration
  security:
    max_args: 5

tools:
  SystemStatus:
    cmd: systemctl status $SERVICE
    desc: Check system service status
    args:
      - name: SERVICE
        type: string
        required: true
        help: System service name
        choices: ["nginx", "apache2", "mysql", "postgresql", "redis"]

  ProcessInfo:
    cmd: ps aux | grep "$PATTERN" | grep -v grep
    desc: Find running processes
    args:
      - name: PATTERN
        type: string
        required: true
        help: Process name or pattern to search for
    output:
      format: text

  DiskUsage:
    cmd: df -h $PATH
    desc: Check disk usage
    args:
      - name: PATH
        type: string
        required: false
        default: "/"
        help: Path to check disk usage for
    output:
      format: text
```

#### Database Operations

```yml
server:
  name: database-mcp
  desc: MCP Server for database operations
  env:
    MYSQL_HOST: localhost
    MYSQL_USER: root

tools:
  MySQLQuery:
    cmd: mysql -h $HOST -u $USER -p$PASSWORD -e "$QUERY" $DATABASE
    desc: Execute MySQL query
    args:
      - name: HOST
        type: string
        required: false
        default: $MYSQL_HOST
        help: MySQL host
      - name: USER
        type: string
        required: false
        default: $MYSQL_USER
        help: MySQL username
      - name: PASSWORD
        type: string
        required: true
        help: MySQL password
      - name: DATABASE
        type: string
        required: true
        help: Database name
      - name: QUERY
        type: string
        required: true
        help: SQL query to execute
    output:
      format: text

  RedisGet:
    cmd: redis-cli -h $HOST -p $PORT get "$KEY"
    desc: Get value from Redis
    args:
      - name: HOST
        type: string
        required: false
        default: "localhost"
        help: Redis host
      - name: PORT
        type: number
        required: false
        default: 6379
        help: Redis port
      - name: KEY
        type: string
        required: true
        help: Redis key to retrieve
    output:
      format: text
```

### Advanced Features

#### Output Processing

```yml
tools:
  JsonProcessor:
    cmd: cat "$FILE" | jq "$QUERY"
    desc: Process JSON files with jq
    args:
      - name: FILE
        type: string
        required: true
        help: JSON file path
      - name: QUERY
        type: string
        required: true
        help: jq query expression
    output:
      format: json
      filter: "jq -r ."

  LogAnalyzer:
    cmd: tail -n $LINES "$LOG_FILE" | grep "$PATTERN"
    desc: Analyze log files
    args:
      - name: LOG_FILE
        type: string
        required: true
        help: Log file path
      - name: PATTERN
        type: string
        required: true
        help: Search pattern
      - name: LINES
        type: number
        required: false
        default: 100
        help: Number of lines to analyze
    output:
      format: text
      filter: "grep -E 'ERROR|WARN'"
```

#### Security Constraints

```yml
tools:
  SafeFileOp:
    cmd: cp "$SOURCE" "$DEST"
    desc: Safe file copy operation
    args:
      - name: SOURCE
        type: string
        required: true
        help: Source file path
        pattern: "^/safe/directory/.*"
      - name: DEST
        type: string
        required: true
        help: Destination file path
        pattern: "^/safe/directory/.*"
    security:
      allowed_dirs: ["/safe/directory", "/tmp"]
      max_args: 2
      allow_stdin: false
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
