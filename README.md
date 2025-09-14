# shell-operations

Common shell operations for file management, system info, and text processing

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
python shell_operations_server.py
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
python shell_operations_server.py
```


## Tools


### list_files

List files and directories with detailed information

**Function**: `list_files`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `ls -la {{path}}`


### find_files

Find files matching a pattern

**Function**: `find_files`

**Arguments**:
- `path` (string): Directory or file path [default: .]- `pattern` (string): Search pattern or regex
**Command**: `find {{path}} -name '{{pattern}}' -type f`


### find_directories

Find directories matching a pattern

**Function**: `find_directories`

**Arguments**:
- `path` (string): Directory or file path [default: .]- `pattern` (string): Search pattern or regex
**Command**: `find {{path}} -name '{{pattern}}' -type d`


### grep_text

Search for text patterns in files

**Function**: `grep_text`

**Arguments**:
- `pattern` (string): Search pattern or regex- `path` (string): Directory or file path [default: .]- `recursive` (boolean): Perform operation recursively [default: False]
**Command**: `grep -r{{ 'n' if recursive else '' }} '{{pattern}}' {{path}}`


### count_lines

Count lines in a file

**Function**: `count_lines`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `wc -l {{path}}`


### file_size

Get file or directory size

**Function**: `file_size`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `du -h {{path}}`


### disk_usage

Show disk usage information

**Function**: `disk_usage`

**Arguments**:

**Command**: `df -h`


### memory_info

Show memory usage information

**Function**: `memory_info`

**Arguments**:

**Command**: `free -h`


### process_list

List running processes

**Function**: `process_list`

**Arguments**:

**Command**: `ps aux`


### system_info

Show system information

**Function**: `system_info`

**Arguments**:

**Command**: `uname -a`


### current_user

Show current user

**Function**: `current_user`

**Arguments**:

**Command**: `whoami`


### current_directory

Show current working directory

**Function**: `current_directory`

**Arguments**:

**Command**: `pwd`


### create_directory

Create directory (with parent directories if needed)

**Function**: `create_directory`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `mkdir -p {{path}}`


### copy_file

Copy file or directory

**Function**: `copy_file`

**Arguments**:
- `source` (string): Source file or directory path- `destination` (string): Destination file or directory path
**Command**: `cp {{source}} {{destination}}`


### move_file

Move or rename file or directory

**Function**: `move_file`

**Arguments**:
- `source` (string): Source file or directory path- `destination` (string): Destination file or directory path
**Command**: `mv {{source}} {{destination}}`


### remove_file

Remove file (force, no error if not found)

**Function**: `remove_file`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `rm -f {{path}}`


### remove_directory

Remove directory and all contents (force, recursive)

**Function**: `remove_directory`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `rm -rf {{path}}`


### cat_file

Display file contents

**Function**: `cat_file`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `cat {{path}}`


### head_file

Show first N lines of a file

**Function**: `head_file`

**Arguments**:
- `path` (string): Directory or file path [default: .]- `lines` (number): Number of lines to show [default: 10]
**Command**: `head -n {{lines}} {{path}}`


### tail_file

Show last N lines of a file

**Function**: `tail_file`

**Arguments**:
- `path` (string): Directory or file path [default: .]- `lines` (number): Number of lines to show [default: 10]
**Command**: `tail -n {{lines}} {{path}}`


### sort_file

Sort lines in a file

**Function**: `sort_file`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `sort {{path}}`


### unique_lines

Get unique lines from a file

**Function**: `unique_lines`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `sort {{path}} | uniq`


### word_count

Count words in a file

**Function**: `word_count`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `wc -w {{path}}`


### character_count

Count characters in a file

**Function**: `character_count`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `wc -c {{path}}`


### compress_file

Compress file using gzip

**Function**: `compress_file`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `gzip {{path}}`


### decompress_file

Decompress gzip file

**Function**: `decompress_file`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `gunzip {{path}}`


### archive_directory

Create compressed tar archive of directory

**Function**: `archive_directory`

**Arguments**:
- `path` (string): Directory or file path [default: .]- `output` (string): Output file path
**Command**: `tar -czf {{output}} {{path}}`


### extract_archive

Extract compressed tar archive

**Function**: `extract_archive`

**Arguments**:
- `path` (string): Directory or file path [default: .]
**Command**: `tar -xzf {{path}}`


### network_connections

Show network connections

**Function**: `network_connections`

**Arguments**:

**Command**: `netstat -tuln`


### ping_host

Ping a host 4 times

**Function**: `ping_host`

**Arguments**:
- `host` (string): Hostname or IP address to ping
**Command**: `ping -c 4 {{host}}`


### environment_vars

Show environment variables

**Function**: `environment_vars`

**Arguments**:

**Command**: `env`


### set_environment

Set environment variable

**Function**: `set_environment`

**Arguments**:
- `name` (string): Environment variable name- `value` (string): Environment variable value
**Command**: `export {{name}}={{value}}`


## Configuration

This server was generated from a YAML configuration file. The server exposes shell commands as MCP tools with the following features:

- Jinja2 template support for dynamic command generation
- Argument validation with patterns and choices
- Environment variable support
- Error handling and timeout protection

## Server Information

- **Name**: shell-operations
- **Version**: 1.0.0
- **Description**: Common shell operations for file management, system info, and text processing
- **Tools**: 32