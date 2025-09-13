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
mcp = FastMCP(name="comprehensive-mcp-server")

# Server configuration
SERVER_NAME = "comprehensive-mcp-server"
SERVER_DESC = "Comprehensive MCP Server demonstrating all resource and prompt types"
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

@mcp.resource("system://info")
def systeminfo() -> str:
    """
    Current system information from commands
    """
    try:
        
        # Execute command
        cmd = render_template("""uname -a && df -h""", )
        env_vars = {}
        result = execute_command(cmd, env_vars)
        if not result["success"]:
            raise ValueError(f"Command failed: {result['stderr']}")
        content = result["stdout"]
        
        return content
    except Exception as e:
        raise ValueError(f"Error in SystemInfo: {str(e)}")


@mcp.resource("file://config/{{ config_name }}")
def configfile(config_path: str, config_name: str = "default") -> str:
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
        
        return content
    except Exception as e:
        raise ValueError(f"Error in ConfigFile: {str(e)}")


@mcp.resource("text://static")
def statictext() -> str:
    """
    Direct static text content
    """
    try:
        
        # Use direct text content
        content = render_template("""This is a static text resource that doesn't change.""", )
        
        return content
    except Exception as e:
        raise ValueError(f"Error in StaticText: {str(e)}")


@mcp.resource("text://{{ resource_name }}")
def dynamictext(user_name: str = "User", resource_name: str = "default", include_timestamp: bool = False, include_system_info: bool = False) -> str:
    """
    Dynamic text content with variables
    """
    try:
        
        # Use direct text content
        content = render_template("""Hello {{ user_name }}!

This is a dynamic text resource for {{ resource_name }}.

{% if include_timestamp %}
Generated at: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}
{% endif %}

{% if include_system_info %}
System: {{ now().strftime('%Y-%m-%d') }}
{% endif %}
""", user_name=user_name, resource_name=resource_name, include_timestamp=include_timestamp, include_system_info=include_system_info)
        
        return content
    except Exception as e:
        raise ValueError(f"Error in DynamicText: {str(e)}")


# Prompt handlers

@mcp.prompt()
def codereview(code: str, language: str = "python", focus_areas: str = "") -> str:
    """
    Generate a code review prompt via command
    """
    try:
        # Validate language choices
        if language not in ['python', 'javascript', 'java', 'go']:
            raise ValueError(f"Invalid language: must be one of ['python', 'javascript', 'java', 'go']")
        
        # Execute command
        cmd = render_template("""echo \"You are a senior software engineer reviewing the following {{ language }} code:\"
echo \"\"
echo \"```{{ language }}\"
echo \"{{ code }}\"
echo \"```\"
echo \"\"
echo \"Please provide a thorough code review focusing on:\"
echo \"- Code quality and best practices\"
echo \"- Performance implications\"
echo \"- Security considerations\"
echo \"- Maintainability\"
echo \"\"
{% if focus_areas %}
echo \"Pay special attention to: {{ focus_areas }}\"
{% endif %}
""", language=language, code=code, focus_areas=focus_areas)
        env_vars = {}
        result = execute_command(cmd, env_vars)
        if not result["success"]:
            raise ValueError(f"Command failed: {result['stderr']}")
        content = result["stdout"]
        
        return content
    except Exception as e:
        raise ValueError(f"Error in CodeReview: {str(e)}")


@mcp.prompt()
def codereviewtemplate(language: str = "python") -> str:
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
        
        return content
    except Exception as e:
        raise ValueError(f"Error in CodeReviewTemplate: {str(e)}")


@mcp.prompt()
def simpletemplate(user_request: str, context: str = "", tone: str = "professional") -> str:
    """
    Direct Jinja2 template prompt
    """
    try:
        # Validate tone choices
        if tone not in ['professional', 'casual', 'friendly', 'formal']:
            raise ValueError(f"Invalid tone: must be one of ['professional', 'casual', 'friendly', 'formal']")
        
        # Use direct template content
        content = render_template("""You are a helpful assistant. Please help with the following request:

{{ user_request }}

{% if context %}
Additional context: {{ context }}
{% endif %}

{% if tone %}
Please respond in a {{ tone }} tone.
{% endif %}
""", user_request=user_request, context=context, tone=tone)
        
        return content
    except Exception as e:
        raise ValueError(f"Error in SimpleTemplate: {str(e)}")


@mcp.prompt()
def advancedtemplate(subject: str, content: str, role: str = "technical", task_type: str = "help", requirements: List[str] = [], output_format: str = "", include_examples: bool = False) -> str:
    """
    Complex template with conditional logic
    """
    try:
        # Validate role choices
        if role not in ['technical', 'creative', 'analytical', 'business']:
            raise ValueError(f"Invalid role: must be one of ['technical', 'creative', 'analytical', 'business']")
        # Validate task_type choices
        if task_type not in ['analysis', 'generation', 'help']:
            raise ValueError(f"Invalid task_type: must be one of ['analysis', 'generation', 'help']")
        
        # Use direct template content
        content = render_template("""You are a {{ role }} expert.

{% if task_type == \"analysis\" %}
Please analyze the following {{ subject }}:
{% elif task_type == \"generation\" %}
Please generate {{ subject }} with the following requirements:
{% else %}
Please help with {{ subject }}:
{% endif %}

{{ content }}

{% if requirements %}
Requirements:
{% for req in requirements %}
- {{ req }}
{% endfor %}
{% endif %}

{% if output_format %}
Please provide the output in {{ output_format }} format.
{% endif %}

{% if include_examples %}
Please include examples where appropriate.
{% endif %}
""", role=role, task_type=task_type, subject=subject, content=content, requirements=requirements, output_format=output_format, include_examples=include_examples)
        
        return content
    except Exception as e:
        raise ValueError(f"Error in AdvancedTemplate: {str(e)}")


if __name__ == "__main__":
    print(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    print(f"Description: {SERVER_DESC}")
    mcp.run()