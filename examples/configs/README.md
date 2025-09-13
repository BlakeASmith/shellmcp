# filesystem-mcp

MCP Server for filesystem operations

## Installation

### Option 1: Using Virtual Environment (Recommended)

1. **Create a virtual environment**:
```bash
python -m venv venv
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

## MCP Configuration

The generated `mcp.json` file contains the configuration needed to integrate this server with MCP-compatible editors and clients.

### Quick Setup

1. **Copy the MCP configuration** from the generated `mcp.json` file
2. **Add to your editor's MCP configuration** (see platform-specific instructions below)
3. **Restart your editor**

### Platform-Specific Instructions

#### Claude Desktop
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

#### Cursor Editor
- Add to Cursor settings under MCP configuration
- Restart Cursor after configuration

#### Visual Studio Code
- Install MCP extension
- Add configuration to VS Code settings
- Reload VS Code

#### Neovim
- Use MCP plugin with the provided configuration
- Run `:PackerSync` to install

#### Helix Editor
- Add to `~/.config/helix/config.toml`
- Restart Helix

### Configuration Parameters

- **`command`**: Python interpreter command
- **`args`**: Server script path and arguments
- **`cwd`**: Working directory for the server
- **`env`**: Environment variables (PYTHONPATH, etc.)

### Testing Your Configuration

1. **Manual test**: Run the server directly to ensure it starts
2. **Check tools**: Verify tools appear in your editor's MCP interface
3. **Test commands**: Try using the generated tools through the editor

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