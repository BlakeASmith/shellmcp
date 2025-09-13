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
mcp = FastMCP(name="filesystem-mcp-with-resources")

# Server configuration
SERVER_NAME = "filesystem-mcp-with-resources"
SERVER_DESC = "MCP Server for filesystem operations with resources and prompts"
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
        cmd = render_template("""ls -la {{ path }}""", path=path)
        
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
        cmd = render_template("""cat {{ file }}""", file=file)
        
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


# Resource handlers

@mcp.resource()
def systeminfo() -> Dict[str, Any]:
    """
    Current system information
    """
    try:
        
        # Execute command
        cmd = render_template("""uname -a && df -h""", )
        env_vars = {}
        result = execute_command(cmd, env_vars)
        if not result["success"]:
            raise ValueError(f"Command failed: {result['stderr']}")
        content = result["stdout"]
        
        return {
            "uri": "system://info",
            "name": "System Information",
            "description": "Current system information",
            "mimeType": "text/plain",
            "text": content
        }
    except Exception as e:
        raise ValueError(f"Error in SystemInfo: {str(e)}")


@mcp.resource()
def configfile(config_path: str, config_name: str = "default") -> Dict[str, Any]:
    """
    Read configuration file from filesystem
    """
    try:
        # Validate config_path pattern
        import re
        if not re.match(r"^[^\0]+$", str(config_path)):
            raise ValueError(f"Invalid config_path: must match pattern ^[^\0]+$")
        
        # Read from file
        file_path = render_template("""{{ config_path }}""", config_path=config_path, config_name=config_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise ValueError(f"Resource file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading resource file {file_path}: {str(e)}")
        
        return {
            "uri": "file://config/{{ config_name }}",
            "name": "Configuration File",
            "description": "Read configuration file from filesystem",
            "mimeType": "text/plain",
            "text": content
        }
    except Exception as e:
        raise ValueError(f"Error in ConfigFile: {str(e)}")


@mcp.resource()
def staticdocumentation(doc_type: str = "api") -> Dict[str, Any]:
    """
    Read documentation from file
    """
    try:
        # Validate doc_type choices
        if doc_type not in ['api', 'user-guide', 'troubleshooting']:
            raise ValueError(f"Invalid doc_type: must be one of ['api', 'user-guide', 'troubleshooting']")
        
        # Read from file
        file_path = render_template("""docs/{{ doc_type }}.md""", doc_type=doc_type)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise ValueError(f"Resource file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading resource file {file_path}: {str(e)}")
        
        return {
            "uri": "docs://{{ doc_type }}",
            "name": "Static Documentation",
            "description": "Read documentation from file",
            "mimeType": "text/markdown",
            "text": content
        }
    except Exception as e:
        raise ValueError(f"Error in StaticDocumentation: {str(e)}")


# Prompt handlers

@mcp.prompt()
def codereview(code: str, language: str = "python", focus_areas: str = "") -> Dict[str, Any]:
    """
    Generate a code review prompt
    """
    try:
        # Validate language choices
        if language not in ['python', 'javascript', 'java', 'go']:
            raise ValueError(f"Invalid language: must be one of ['python', 'javascript', 'java', 'go']")
        
        # Execute command
        cmd = render_template("""You are a senior software engineer reviewing the following {{ language }} code:

```{{ language }}
{{ code }}
```

Please provide a thorough code review focusing on:
- Code quality and best practices
- Performance implications
- Security considerations
- Maintainability

{% if focus_areas %}
Pay special attention to: {{ focus_areas }}
{% endif %}
""", language=language, code=code, focus_areas=focus_areas)
        env_vars = {}
        result = execute_command(cmd, env_vars)
        if not result["success"]:
            raise ValueError(f"Command failed: {result['stderr']}")
        content = result["stdout"]
        
        return {
            "name": "Code Review Prompt",
            "description": "Generate a code review prompt",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": content
                    }
                }
            ]
        }
    except Exception as e:
        raise ValueError(f"Error in CodeReview: {str(e)}")


@mcp.prompt()
def codereviewtemplate(language: str = "python") -> Dict[str, Any]:
    """
    Load code review prompt from template file
    """
    try:
        # Validate language choices
        if language not in ['python', 'javascript', 'java', 'go']:
            raise ValueError(f"Invalid language: must be one of ['python', 'javascript', 'java', 'go']")
        
        # Read from file
        file_path = render_template("""prompts/code_review_{{ language }}.txt""", language=language)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise ValueError(f"Prompt file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading prompt file {file_path}: {str(e)}")
        
        return {
            "name": "Code Review Template",
            "description": "Load code review prompt from template file",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": content
                    }
                }
            ]
        }
    except Exception as e:
        raise ValueError(f"Error in CodeReviewTemplate: {str(e)}")


@mcp.prompt()
def customprompt(prompt_name: str) -> Dict[str, Any]:
    """
    Load custom prompt from file
    """
    try:
        
        # Read from file
        file_path = render_template("""prompts/{{ prompt_name }}.txt""", prompt_name=prompt_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise ValueError(f"Prompt file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading prompt file {file_path}: {str(e)}")
        
        return {
            "name": "Custom Prompt",
            "description": "Load custom prompt from file",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": content
                    }
                }
            ]
        }
    except Exception as e:
        raise ValueError(f"Error in CustomPrompt: {str(e)}")


if __name__ == "__main__":
    print(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    print(f"Description: {SERVER_DESC}")
    mcp.run()