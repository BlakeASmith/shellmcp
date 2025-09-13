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

### Example Configuration

```yml
server:
  name: filesystem-mcp
  desc: MCP Server for filesystem operations

tools:
  ListFiles:
    cmd: ls -la $@
    desc: List files in the current directory
    help-cmd: ls --help
    args:
      - name: path
        type: string
        required: false
        help: Directory path to list
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
        help: File pattern to match
    security:
      allowed_dirs: ["/home", "/tmp", "/workspace"]

  GitStatus:
    cmd: git status --porcelain
    desc: Get git repository status
    working_dir: $GIT_ROOT
    output:
      format: text
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
