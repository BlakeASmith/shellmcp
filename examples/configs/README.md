# filesystem-mcp

MCP Server for filesystem operations

## Installation

### Option 1: Using Virtual Environment (Recommended)

1. **Create a virtual environment**:
```bash
python3 -m venv venv
```

**Note**: On Ubuntu/Debian systems, if you get an "ensurepip is not available" error, install the python3-venv package first:
```bash
sudo apt install python3-venv
```

2. **Activate the virtual environment**:
   - **Linux/macOS**:
   ```bash
   source venv/bin/activate
   ```
   - **Windows**:
   ```cmd
   venv\Scripts\activate
   ```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the server**:
```bash
python filesystem_mcp_server.py
```

5. **Deactivate when done** (optional):
```bash
deactivate
```

### Option 2: System-wide Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python filesystem_mcp_server.py
```

## Amazon Q CLI Configuration

The generated `amazon-q-config.json` file contains the configuration needed to integrate this server with Amazon Q CLI for enhanced AI assistance.

### Quick Setup

1. **Install Amazon Q CLI**: `curl -sSL https://amazon-q-cli.s3.amazonaws.com/install.sh | bash`
2. **Configure AWS credentials**: `aws configure` or `aws sso login`
3. **Copy Amazon Q configuration** from the generated `amazon-q-config.json` file
4. **Add to Amazon Q CLI configuration**:
   - **Linux/macOS**: `~/.config/amazon-q/cli-config.json`
   - **Windows**: `%APPDATA%\Amazon\Q\cli-config.json`
5. **Start Amazon Q CLI**: `amazon-q`
6. **Use `@tools` command** to access your MCP tools

### Configuration Parameters

- **`command`**: Python interpreter command (uses virtual environment path)
- **`args`**: Server script path and arguments
- **`cwd`**: Working directory for the server
- **`env`**: Environment variables (PYTHONPATH, AWS_PROFILE, etc.)

### Testing Your Configuration

1. **Manual test**: Run the server directly to ensure it starts
2. **Check Amazon Q CLI**: Use `@tools` command to see available tools
3. **Test commands**: Try using the generated tools through Amazon Q CLI

## Tools


### ListFiles

List files in a directory with detailed information

**Function**: `listfiles`

**Arguments**:
- `path` (string): Path to a directory
**Command**: `ls -la {{ path }}`


### ReadFile

Read and display the contents of a file

**Function**: `readfile`

**Arguments**:
- `file` (string): Path to a file
**Command**: `cat {{ file }}`


### CreateDirectory

Create a directory (and parent directories if needed)

**Function**: `createdirectory`

**Arguments**:
- `path` (string): Path to a directory
**Command**: `mkdir -p {{ path }}`


### BackupDatabase

Database backup with optional compression

**Function**: `backupdatabase`

**Arguments**:
- `host` (string): Database host [default: localhost]- `user` (string): Database user- `password` (string): Database password- `database` (string): Database name- `compress` (boolean): Boolean flag [default: False]- `timestamp` (string): Timestamp for backup file [default: {{ now().strftime('%Y%m%d_%H%M%S') }}]
**Command**: `{% set backup_file = "backup_" + timestamp + ".sql" %}
mysqldump -h {{ host }} -u {{ user }} -p{{ password }} {{ database }} > {{ backup_file }}
{% if compress %}
gzip {{ backup_file }}
{% endif %}
echo "Backup completed: {{ backup_file }}"
`


### DockerContainer

Manage Docker containers

**Function**: `dockercontainer`

**Arguments**:
- `action` (string): Action to perform [choices: ['start', 'stop', 'restart', 'logs', 'inspect']]- `container` (string): Container name or ID
**Command**: `{% if action == 'start' %}
docker start {{ container }}
{% elif action == 'stop' %}
docker stop {{ container }}
{% elif action == 'restart' %}
docker restart {{ container }}
{% else %}
docker {{ action }} {{ container }}
{% endif %}
`


### ConditionalDeploy

Deploy service with environment-specific configuration

**Function**: `conditionaldeploy`

**Arguments**:
- `env` (string): Deployment environment [default: dev] [choices: ['dev', 'staging', 'prod']]- `service` (string): Service name- `image` (string): Docker image to deploy
**Command**: `{% if env == 'prod' %}
docker run --restart=always -d --name {{ service }} {{ image }}
{% elif env == 'staging' %}
docker run -d --name {{ service }}_staging {{ image }}
{% else %}
docker run -d --name {{ service }}_dev {{ image }}
{% endif %}
`


## Configuration

This server was generated from a YAML configuration file. The server exposes shell commands as MCP tools with the following features:

- Jinja2 template support for dynamic command generation
- Argument validation with patterns and choices
- Environment variable support
- Error handling and timeout protection

## Server Information

- **Name**: filesystem-mcp
- **Version**: 1.0.0
- **Description**: MCP Server for filesystem operations
- **Tools**: 6