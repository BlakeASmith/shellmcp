"""Generated FastMCP server from YAML configuration."""

import os
import subprocess
import tempfile
import shlex
from datetime import datetime
from typing import Any, Dict, Optional
from fastmcp import FastMCP
from jinja2 import Template, Environment

def execute_command(cmd: str, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
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
            timeout=300  # 5 minute timeout
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
mcp = FastMCP(name="filesystem-mcp")

# Server configuration
SERVER_NAME = "filesystem-mcp"
SERVER_DESC = "MCP Server for filesystem operations"
SERVER_VERSION = "1.0.0"
os.environ["NODE_ENV"] = "production"
os.environ["DEBUG"] = "false"


@mcp.tool()
def listfiles(path: str) -> Dict[str, Any]:
    """
    List files in a directory with detailed information
    """
    try:
        # Validate path pattern
        import re
        if not re.match(r"^[^\0]+$", str(path)):
            raise ValueError(f"Invalid path: must match pattern ^[^\0]+$")
        
        # Render command template
        cmd = render_template("""ls -la {{ path }}""", path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in ListFiles: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def readfile(file: str) -> Dict[str, Any]:
    """
    Read and display the contents of a file
    """
    try:
        # Validate file pattern
        import re
        if not re.match(r"^[^\0]+$", str(file)):
            raise ValueError(f"Invalid file: must match pattern ^[^\0]+$")
        
        # Render command template
        cmd = render_template("""cat {{ file }}""", file)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in ReadFile: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def createdirectory(path: str) -> Dict[str, Any]:
    """
    Create a directory (and parent directories if needed)
    """
    try:
        # Validate path pattern
        import re
        if not re.match(r"^[^\0]+$", str(path)):
            raise ValueError(f"Invalid path: must match pattern ^[^\0]+$")
        
        # Render command template
        cmd = render_template("""mkdir -p {{ path }}""", path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in CreateDirectory: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def backupdatabase(user: str, password: str, database: str, host: str = "localhost", compress: bool = False, timestamp: str = "{{ now().strftime('%Y%m%d_%H%M%S') }}") -> Dict[str, Any]:
    """
    Database backup with optional compression
    """
    try:
        
        # Render command template
        cmd = render_template("""{% set backup_file = \"backup_\" + timestamp + \".sql\" %}
mysqldump -h {{ host }} -u {{ user }} -p{{ password }} {{ database }} > {{ backup_file }}
{% if compress %}
gzip {{ backup_file }}
{% endif %}
echo \"Backup completed: {{ backup_file }}\"
""", host, user, password, database, compress, timestamp)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in BackupDatabase: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def dockercontainer(action: str, container: str) -> Dict[str, Any]:
    """
    Manage Docker containers
    """
    try:
        # Validate action choices
        if action not in ['start', 'stop', 'restart', 'logs', 'inspect']:
            raise ValueError(f"Invalid action: must be one of ['start', 'stop', 'restart', 'logs', 'inspect']")
        
        # Render command template
        cmd = render_template("""{% if action == 'start' %}
docker start {{ container }}
{% elif action == 'stop' %}
docker stop {{ container }}
{% elif action == 'restart' %}
docker restart {{ container }}
{% else %}
docker {{ action }} {{ container }}
{% endif %}
""", action, container)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in DockerContainer: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def conditionaldeploy(service: str, image: str, env: str = "dev") -> Dict[str, Any]:
    """
    Deploy service with environment-specific configuration
    """
    try:
        # Validate env choices
        if env not in ['dev', 'staging', 'prod']:
            raise ValueError(f"Invalid env: must be one of ['dev', 'staging', 'prod']")
        
        # Render command template
        cmd = render_template("""{% if env == 'prod' %}
docker run --restart=always -d --name {{ service }} {{ image }}
{% elif env == 'staging' %}
docker run -d --name {{ service }}_staging {{ image }}
{% else %}
docker run -d --name {{ service }}_dev {{ image }}
{% endif %}
""", env, service, image)
        
        # Execute command
        env_vars = {}
        env_vars["DOCKER_HOST"] = "unix:///var/run/docker.sock"
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in ConditionalDeploy: {str(e)}",
            "returncode": -1
        }


if __name__ == "__main__":
    print(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    print(f"Description: {SERVER_DESC}")
    mcp.run()