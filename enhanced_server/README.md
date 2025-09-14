# enhanced-mcp-server

Enhanced MCP server demonstrating new features

## Installation

### Option 1: Using Virtual Environment (Recommended)

1. **Create a virtual environment**:
```bash
python3 -m venv venv
```


2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the server**:
```bash
python enhanced_mcp_server_server.py
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
python enhanced_mcp_server_server.py
```


## Tools


### DatabaseBackup

Create a database backup with compression and validation

**Function**: `databasebackup`

**Arguments**:
- `database` (string): Database name- `backup_file` (string): Path to a file or directory
**Command**: `mysqldump {{ database }} > {{ backup_file }}`


### SystemMonitor

Monitor system metrics (CPU, memory, disk usage)

**Function**: `systemmonitor`

**Arguments**:
- `metric` (string): Metric to monitor [choices: ['cpu', 'memory', 'disk']]- `path` (string): Path for disk usage check [default: /]
**Command**: `{% if metric == "cpu" %}
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
{% elif metric == "memory" %}
free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}'
{% elif metric == "disk" %}
df -h {{ path or "/" }} | awk 'NR==2{print $5}' | cut -d'%' -f1
{% endif %}
`


### FileSearch

Search for files matching a pattern with optional size filtering

**Function**: `filesearch`

**Arguments**:
- `path` (string): Path to a file or directory- `pattern` (string): File pattern to match [default: *]- `size` (string): File size filter (e.g., +100M, -1G)
**Command**: `find {{ path }} -name '{{ pattern }}' -type f {% if size %} -size {{ size }}{% endif %}`


### LogAnalyzer

Analyze log files with various output formats and filtering

**Function**: `loganalyzer`

**Arguments**:
- `log_file` (string): Path to a file or directory- `format` (string): Output format [default: raw] [choices: ['text', 'json', 'raw']]- `lines` (number): Number of lines to show [default: 100]- `pattern` (string): Search pattern for text format- `filter` (string): JQ filter for JSON format
**Command**: `{% if format == "json" %}
jq '{{ filter }}' {{ log_file }}
{% elif format == "text" %}
grep "{{ pattern }}" {{ log_file }} | tail -{{ lines or 100 }}
{% else %}
tail -{{ lines or 100 }} {{ log_file }}
{% endif %}
`


## Configuration

This server was generated from a YAML configuration file. The server exposes shell commands as MCP tools with the following features:

- Jinja2 template support for dynamic command generation
- Argument validation with patterns and choices
- Environment variable support
- Error handling and timeout protection

## Server Information

- **Name**: enhanced-mcp-server
- **Version**: 2.0.0
- **Description**: Enhanced MCP server demonstrating new features
- **Tools**: 4