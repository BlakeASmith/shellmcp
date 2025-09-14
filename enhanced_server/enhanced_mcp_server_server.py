"""Generated FastMCP server from YAML configuration."""

import os
import subprocess
import tempfile
import shlex
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from jinja2 import Template, Environment

def execute_command(cmd: str, env_vars: Optional[Dict[str, str]] = None, timeout: int = 300) -> Dict[str, Any]:
    """Execute a shell command and return the result."""
    try:
        # Prepare environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        # Execute command
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 5 minutes",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def render_template(template_str: str, **kwargs) -> str:
    """Render Jinja2 template with provided variables."""
    try:
        # Add built-in functions
        context = {
            'now': datetime.now,
            **kwargs
        }
        
        template = Template(template_str)
        return template.render(**context)
    except Exception as e:
        raise ValueError(f"Template rendering error: {e}")

# Initialize FastMCP server
mcp = FastMCP(name="enhanced-mcp-server")

# Server configuration
SERVER_NAME = "enhanced-mcp-server"
SERVER_DESC = "Enhanced MCP server demonstrating new features"
SERVER_VERSION = "2.0.0"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["MAX_CONCURRENT"] = "10"


@mcp.tool(name="db-backup", tags=['backup', 'database', 'maintenance'])
def databasebackup(database: str, backup_file: str) -> Dict[str, Any]:
    """
    Create a database backup with compression and validation
    
    Metadata:
    - Version: 2.1.0
    - Author: DevOps Team
    - Category: database
    
    Parameters:
    - database (string): Database name
      Pattern: ^[a-zA-Z][a-zA-Z0-9_]*$
    - backup_file (string): Path to a file or directory
      Pattern: ^[^\0]+$
    
    Examples:
    - Backup production database:
      db-backup --database=prod_db --backup_file=prod_backup.sql
    - Backup with timestamp:
      db-backup --database=test_db --backup_file=test_$(date +%Y%m%d).sql
    
    Dependencies:
    - mysqldump
    - mysql
    
    Required Permissions:
    - database:read
    - file:write
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        # Check dependencies
        missing_deps = []
        try:
            subprocess.run(["which", "mysqldump"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_deps.append("mysqldump")
        try:
            subprocess.run(["which", "mysql"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_deps.append("mysql")
        if missing_deps:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Missing dependencies: {', '.join(missing_deps)}",
                "returncode": -1
            }
        # Validate database pattern
        import re
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", str(database)):
            raise ValueError(f"Invalid database: must match pattern ^[a-zA-Z][a-zA-Z0-9_]*$")
        # Validate backup_file pattern
        import re
        if not re.match(r"^[^\0]+$", str(backup_file)):
            raise ValueError(f"Invalid backup_file: must match pattern ^[^\0]+$")
        
        # Render command template
        cmd = render_template("""mysqldump {{ database }} > {{ backup_file }}""", database=database, backup_file=backup_file)
        
        # Execute command with retries
        env_vars = {}
        
        max_retries = 2
        timeout = 600
        
        for attempt in range(max_retries + 1):
            try:
                result = execute_command(cmd, env_vars, timeout=timeout)
                if result["success"] or attempt == max_retries:
                    return result
                else:
                    if attempt < max_retries:
                        import time
                        time.sleep(1)  # Brief delay before retry
            except Exception as e:
                if attempt == max_retries:
                    raise e
                import time
                time.sleep(1)  # Brief delay before retry
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in DatabaseBackup: {str(e)}",
            "returncode": -1
        }


@mcp.tool(name="system-monitor", tags=['system', 'monitoring', 'health'])
def systemmonitor(metric: str, path: str = "/") -> Dict[str, Any]:
    """
    Monitor system metrics (CPU, memory, disk usage)
    
    Metadata:
    - Version: 1.0.0
    - Author: System Admin
    - Category: monitoring
    
    Parameters:
    - metric (string): Metric to monitor
      Allowed values: cpu, memory, disk
    - path (string): Path for disk usage check
      Default: /
    
    Examples:
    - Check CPU usage:
      system-monitor --metric=cpu
    - Check memory usage:
      system-monitor --metric=memory
    - Check disk usage for specific path:
      system-monitor --metric=disk --path=/var
    
    Dependencies:
    - top
    - free
    - df
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        # Check dependencies
        missing_deps = []
        try:
            subprocess.run(["which", "top"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_deps.append("top")
        try:
            subprocess.run(["which", "free"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_deps.append("free")
        try:
            subprocess.run(["which", "df"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_deps.append("df")
        if missing_deps:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Missing dependencies: {', '.join(missing_deps)}",
                "returncode": -1
            }
        # Validate metric choices
        if metric not in ['cpu', 'memory', 'disk']:
            raise ValueError(f"Invalid metric: must be one of ['cpu', 'memory', 'disk']")
        
        # Render command template
        cmd = render_template("""{% if metric == \"cpu\" %}
top -bn1 | grep \"Cpu(s)\" | awk '{print $2}' | cut -d'%' -f1
{% elif metric == \"memory\" %}
free | grep Mem | awk '{printf \"%.2f\", $3/$2 * 100.0}'
{% elif metric == \"disk\" %}
df -h {{ path or \"/\" }} | awk 'NR==2{print $5}' | cut -d'%' -f1
{% endif %}
""", metric=metric, path=path)
        
        # Execute command with retries
        env_vars = {}
        
        max_retries = 1
        timeout = 30
        
        for attempt in range(max_retries + 1):
            try:
                result = execute_command(cmd, env_vars, timeout=timeout)
                if result["success"] or attempt == max_retries:
                    return result
                else:
                    if attempt < max_retries:
                        import time
                        time.sleep(1)  # Brief delay before retry
            except Exception as e:
                if attempt == max_retries:
                    raise e
                import time
                time.sleep(1)  # Brief delay before retry
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in SystemMonitor: {str(e)}",
            "returncode": -1
        }


@mcp.tool(name="find-files", tags=['file', 'search', 'utility'])
def filesearch(path: str, size: str, pattern: str = "*") -> Dict[str, Any]:
    """
    Search for files matching a pattern with optional size filtering
    
    Metadata:
    - Version: 1.0.0
    - Author: File System Team
    - Category: file-system
    
    Parameters:
    - path (string): Path to a file or directory
      Pattern: ^[^\0]+$
    - pattern (string): File pattern to match
      Default: *
    - size (string): File size filter (e.g., +100M, -1G)
    
    Examples:
    - Find Python files:
      find-files --path=/home/user --pattern='*.py'
    - Find large files:
      find-files --path=/var --pattern='*' --size='+100M'
    
    Dependencies:
    - find
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        # Check dependencies
        missing_deps = []
        try:
            subprocess.run(["which", "find"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_deps.append("find")
        if missing_deps:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Missing dependencies: {', '.join(missing_deps)}",
                "returncode": -1
            }
        # Validate path pattern
        import re
        if not re.match(r"^[^\0]+$", str(path)):
            raise ValueError(f"Invalid path: must match pattern ^[^\0]+$")
        
        # Render command template
        cmd = render_template("""find {{ path }} -name '{{ pattern }}' -type f {% if size %} -size {{ size }}{% endif %}""", path=path, pattern=pattern, size=size)
        
        # Execute command with retries
        env_vars = {}
        
        max_retries = 1
        timeout = 120
        
        for attempt in range(max_retries + 1):
            try:
                result = execute_command(cmd, env_vars, timeout=timeout)
                if result["success"] or attempt == max_retries:
                    return result
                else:
                    if attempt < max_retries:
                        import time
                        time.sleep(1)  # Brief delay before retry
            except Exception as e:
                if attempt == max_retries:
                    raise e
                import time
                time.sleep(1)  # Brief delay before retry
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in FileSearch: {str(e)}",
            "returncode": -1
        }


@mcp.tool(name="log-analyzer", tags=['logs', 'analysis', 'debugging'])
def loganalyzer(log_file: str, pattern: str, filter: str, format: str = "raw", lines: float = 100) -> Dict[str, Any]:
    """
    Analyze log files with various output formats and filtering
    
    Metadata:
    - Version: 1.2.0
    - Author: Monitoring Team
    - Category: logging
    
    Parameters:
    - log_file (string): Path to a file or directory
      Pattern: ^[^\0]+$
    - format (string): Output format
      Default: raw
      Allowed values: text, json, raw
    - lines (number): Number of lines to show
      Default: 100
    - pattern (string): Search pattern for text format
    - filter (string): JQ filter for JSON format
    
    Examples:
    - Show last 50 lines of error log:
      log-analyzer --log_file=/var/log/error.log --lines=50
    - Filter JSON logs for errors:
      log-analyzer --log_file=/var/log/app.json --format=json --filter='.level == "error"'
    - Search for specific pattern:
      log-analyzer --log_file=/var/log/access.log --format=text --pattern='404'
    
    Dependencies:
    - jq
    - grep
    - tail
    
    Required Permissions:
    - file:read
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        # Check dependencies
        missing_deps = []
        try:
            subprocess.run(["which", "jq"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_deps.append("jq")
        try:
            subprocess.run(["which", "grep"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_deps.append("grep")
        try:
            subprocess.run(["which", "tail"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_deps.append("tail")
        if missing_deps:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Missing dependencies: {', '.join(missing_deps)}",
                "returncode": -1
            }
        # Validate log_file pattern
        import re
        if not re.match(r"^[^\0]+$", str(log_file)):
            raise ValueError(f"Invalid log_file: must match pattern ^[^\0]+$")
        # Validate format choices
        if format not in ['text', 'json', 'raw']:
            raise ValueError(f"Invalid format: must be one of ['text', 'json', 'raw']")
        
        # Render command template
        cmd = render_template("""{% if format == \"json\" %}
jq '{{ filter }}' {{ log_file }}
{% elif format == \"text\" %}
grep \"{{ pattern }}\" {{ log_file }} | tail -{{ lines or 100 }}
{% else %}
tail -{{ lines or 100 }} {{ log_file }}
{% endif %}
""", log_file=log_file, format=format, lines=lines, pattern=pattern, filter=filter)
        
        # Execute command with retries
        env_vars = {}
        
        max_retries = 0
        timeout = 60
        
        for attempt in range(max_retries + 1):
            try:
                result = execute_command(cmd, env_vars, timeout=timeout)
                if result["success"] or attempt == max_retries:
                    return result
                else:
                    if attempt < max_retries:
                        import time
                        time.sleep(1)  # Brief delay before retry
            except Exception as e:
                if attempt == max_retries:
                    raise e
                import time
                time.sleep(1)  # Brief delay before retry
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in LogAnalyzer: {str(e)}",
            "returncode": -1
        }


# Resource handlers

@mcp.resource("system://info")
def systeminfo() -> str:
    """
    Current system information and status
    
    Returns:
        str: The resource content.
    """
    try:
        
        # Execute command
        cmd = render_template("""echo \"=== System Information ===\"
uname -a
echo \"\"
echo \"=== CPU Info ===\"
lscpu | grep -E \"(Model name|CPU\(s\)|Thread|Core)\"
echo \"\"
echo \"=== Memory Info ===\"
free -h
echo \"\"
echo \"=== Disk Usage ===\"
df -h
""", )
        env_vars = {}
        result = execute_command(cmd, env_vars)
        if not result["success"]:
            raise ValueError(f"Command failed: {result['stderr']}")
        content = result["stdout"]
        
        return content
    except Exception as e:
        raise ValueError(f"Error in SystemInfo: {str(e)}")


@mcp.resource("template://{template_name}")
def configtemplate(template_name: str) -> str:
    """
    Load configuration template
    
    Parameters:
    - template_name (string): Template name
      Allowed values: nginx, apache, mysql, redis
    
    Returns:
        str: The resource content.
    """
    try:
        # Validate template_name choices
        if template_name not in ['nginx', 'apache', 'mysql', 'redis']:
            raise ValueError(f"Invalid template_name: must be one of ['nginx', 'apache', 'mysql', 'redis']")
        
        # Read from file
        file_path = render_template("""templates/{{ template_name }}.conf""", template_name=template_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise ValueError(f"Resource file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading resource file {file_path}: {str(e)}")
        
        return content
    except Exception as e:
        raise ValueError(f"Error in ConfigTemplate: {str(e)}")


# Prompt handlers

@mcp.prompt()
def codereview(code: str, language: str = "python", focus_areas: str = "", include_examples: bool = True) -> str:
    """
    Generate a comprehensive code review prompt
    
    Parameters:
    - language (string): Programming language
      Default: python
      Allowed values: python, javascript, java, go, rust, typescript
    - code (string): Code to review
    - focus_areas (string): Specific areas to focus on
      Default: 
    - include_examples (boolean): Include improvement examples
      Default: True
    
    Returns:
        str: The generated prompt content.
    """
    try:
        # Validate language choices
        if language not in ['python', 'javascript', 'java', 'go', 'rust', 'typescript']:
            raise ValueError(f"Invalid language: must be one of ['python', 'javascript', 'java', 'go', 'rust', 'typescript']")
        
        # Use direct template content
        content = render_template("""You are a senior software engineer reviewing the following {{ language }} code:

```{{ language }}
{{ code }}
```

Please provide a thorough code review focusing on:
- Code quality and best practices
- Performance implications
- Security considerations
- Maintainability and readability
- Test coverage recommendations

{% if focus_areas %}
Pay special attention to: {{ focus_areas }}
{% endif %}

{% if include_examples %}
Please provide specific examples of improvements where applicable.
{% endif %}
""", language=language, code=code, focus_areas=focus_areas, include_examples=include_examples)
        
        return content
    except Exception as e:
        raise ValueError(f"Error in CodeReview: {str(e)}")


if __name__ == "__main__":
    print(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    print(f"Description: {SERVER_DESC}")
    mcp.run()