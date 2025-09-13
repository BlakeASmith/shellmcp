"""FastMCP server generator from YAML configuration."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Template, Environment
from .parser import YMLParser
from .models import YMLConfig


class FastMCPGenerator:
    """Generator for FastMCP servers from YAML configuration."""
    
    def __init__(self):
        self.parser = YMLParser()
        self.jinja_env = Environment()
        
    def generate_server(self, config_file: str, output_file: Optional[str] = None) -> str:
        """
        Generate a FastMCP server from YAML configuration.
        
        Args:
            config_file: Path to the YAML configuration file
            output_file: Optional output file path (defaults to server.py in same directory)
        
        Returns:
            Path to the generated server file
        """
        # Load and validate configuration
        config = self.parser.load_from_file(config_file)
        
        # Generate server code
        server_code = self._generate_server_code(config)
        
        # Determine output path
        if output_file is None:
            config_path = Path(config_file)
            output_file = config_path.parent / f"{config.server.name.replace('-', '_')}_server.py"
        
        # Write server file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(server_code)
        
        return str(output_file)
    
    def _generate_server_code(self, config: YMLConfig) -> str:
        """Generate FastMCP server code from configuration."""
        
        # Generate imports
        imports = self._generate_imports()
        
        # Generate helper functions
        helpers = self._generate_helper_functions()
        
        # Generate server initialization
        server_init = self._generate_server_init(config)
        
        # Generate tool functions
        tool_functions = self._generate_tool_functions(config)
        
        # Generate main execution
        main_code = self._generate_main_code(config)
        
        # Combine all parts
        server_code = f'''{imports}

{helpers}

{server_init}

{tool_functions}

{main_code}'''
        
        return server_code
    
    def _generate_imports(self) -> str:
        """Generate import statements."""
        return '''"""Generated FastMCP server from YAML configuration."""

import os
import subprocess
import tempfile
import shlex
from datetime import datetime
from typing import Any, Dict, Optional
from fastmcp import FastMCP
from jinja2 import Template, Environment'''
    
    def _generate_helper_functions(self) -> str:
        """Generate helper functions for command execution."""
        return '''def execute_command(cmd: str, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
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
        raise ValueError(f"Template rendering error: {e}")'''
    
    def _generate_server_init(self, config: YMLConfig) -> str:
        """Generate server initialization code."""
        server_name = config.server.name.replace('-', '_')
        
        # Set up environment variables
        env_setup = ""
        if config.server.env:
            env_setup = "# Set up server environment variables\n"
            for key, value in config.server.env.items():
                env_setup += f'os.environ["{key}"] = "{value}"\n'
        
        return f'''# Initialize FastMCP server
mcp = FastMCP(name="{config.server.name}")

# Server configuration
SERVER_NAME = "{config.server.name}"
SERVER_DESC = "{config.server.desc}"
SERVER_VERSION = "{config.server.version}"
{env_setup}'''
    
    def _generate_tool_functions(self, config: YMLConfig) -> str:
        """Generate tool function definitions."""
        if not config.tools:
            return ""
        
        functions = []
        
        for tool_name, tool in config.tools.items():
            func_name = tool_name.lower().replace('-', '_')
            
            # Get resolved arguments
            resolved_args = config.get_resolved_arguments(tool_name)
            
            # Generate function signature - parameters with defaults must come last
            params_with_defaults = []
            params_without_defaults = []
            
            for arg in resolved_args:
                param_type = self._get_python_type(arg.type)
                default_value = self._get_default_value(arg.default, arg.type)
                
                param_str = f"{arg.name}: {param_type}"
                if default_value is not None:
                    param_str += f" = {default_value}"
                    params_with_defaults.append(param_str)
                else:
                    params_without_defaults.append(param_str)
            
            param_str = ", ".join(params_without_defaults + params_with_defaults)
            
            # Generate argument validation
            validation_code = self._generate_argument_validation(resolved_args)
            
            # Generate command rendering and execution
            execution_code = self._generate_command_execution(tool)
            
            function_code = f'''@mcp.tool()
def {func_name}({param_str}) -> Dict[str, Any]:
    """
    {tool.desc}
    """
    try:
{validation_code}
        
        # Render command template
        cmd = render_template("""{tool.cmd.replace('"', '\\"')}""", {', '.join([arg.name for arg in resolved_args])})
        
{execution_code}
        
        return result
    except Exception as e:
        return {{
            "success": False,
            "stdout": "",
            "stderr": f"Error in {tool_name}: {{str(e)}}",
            "returncode": -1
        }}'''
            
            functions.append(function_code)
        
        return "\n\n".join(functions)
    
    def _generate_argument_validation(self, resolved_args) -> str:
        """Generate argument validation code."""
        if not resolved_args:
            return ""
        
        validation_lines = []
        
        for arg in resolved_args:
            if arg.pattern:
                validation_lines.append(f'# Validate {arg.name} pattern')
                validation_lines.append(f'import re')
                validation_lines.append(f'if not re.match(r"{arg.pattern}", str({arg.name})):')
                validation_lines.append(f'    raise ValueError(f"Invalid {arg.name}: must match pattern {arg.pattern}")')
            
            if arg.choices:
                validation_lines.append(f'# Validate {arg.name} choices')
                validation_lines.append(f'if {arg.name} not in {arg.choices}:')
                validation_lines.append(f'    raise ValueError(f"Invalid {arg.name}: must be one of {arg.choices}")')
        
        if validation_lines:
            return "\n        ".join(validation_lines)
        return ""
    
    def _generate_command_execution(self, tool) -> str:
        """Generate command execution code."""
        env_setup = ""
        if tool.env:
            env_setup = "        # Set up tool-specific environment variables\n"
            for key, value in tool.env.items():
                env_setup += f'        env_vars["{key}"] = "{value}"\n'
            env_setup += "\n"
        
        return f'''        # Execute command
        env_vars = {{}}
{env_setup}        result = execute_command(cmd, env_vars)'''
    
    def _generate_main_code(self, config: YMLConfig) -> str:
        """Generate main execution code."""
        return f'''if __name__ == "__main__":
    print(f"Starting {{SERVER_NAME}} v{{SERVER_VERSION}}")
    print(f"Description: {{SERVER_DESC}}")
    mcp.run()'''
    
    def _get_python_type(self, yaml_type: str) -> str:
        """Convert YAML type to Python type annotation."""
        type_mapping = {
            "string": "str",
            "number": "float",
            "boolean": "bool",
            "array": "List[str]"
        }
        return type_mapping.get(yaml_type, "str")
    
    def _get_default_value(self, default: Any, yaml_type: str) -> str:
        """Convert default value to Python representation."""
        if default is None:
            return None
        
        if yaml_type == "string":
            return f'"{default}"'
        elif yaml_type == "boolean":
            return "True" if default else "False"
        elif yaml_type == "number":
            return str(default)
        elif yaml_type == "array":
            if isinstance(default, list):
                return str(default)
            else:
                return f'["{default}"]'
        else:
            return f'"{default}"'
    
    def generate_requirements(self, output_file: Optional[str] = None) -> str:
        """Generate requirements.txt file for the FastMCP server."""
        requirements = """fastmcp>=0.1.0
jinja2>=3.0.0
pyyaml>=6.0"""
        
        if output_file is None:
            output_file = "requirements.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        return output_file
    
    def generate_readme(self, config: YMLConfig, output_file: Optional[str] = None) -> str:
        """Generate README.md for the FastMCP server."""
        if output_file is None:
            output_file = "README.md"
        
        # Generate tools documentation
        tools_docs = []
        if config.tools:
            for tool_name, tool in config.tools.items():
                func_name = tool_name.lower().replace('-', '_')
                resolved_args = config.get_resolved_arguments(tool_name)
                
                args_docs = []
                for arg in resolved_args:
                    arg_desc = f"- `{arg.name}` ({arg.type}): {arg.help}"
                    if arg.default is not None:
                        arg_desc += f" [default: {arg.default}]"
                    if arg.choices:
                        arg_desc += f" [choices: {arg.choices}]"
                    args_docs.append(arg_desc)
                
                tool_doc = f"""### {tool_name}

{tool.desc}

**Function**: `{func_name}`

**Arguments**:
{chr(10).join(args_docs)}

**Command**: `{tool.cmd}`
"""
                tools_docs.append(tool_doc)
        
        readme_content = f"""# {config.server.name}

{config.server.desc}

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python {config.server.name.replace('-', '_')}_server.py
```

## Tools

{chr(10).join(tools_docs)}

## Configuration

This server was generated from a YAML configuration file. The server exposes shell commands as MCP tools with the following features:

- Jinja2 template support for dynamic command generation
- Argument validation with patterns and choices
- Environment variable support
- Error handling and timeout protection

## Server Information

- **Name**: {config.server.name}
- **Version**: {config.server.version}
- **Description**: {config.server.desc}
- **Tools**: {len(config.tools) if config.tools else 0}
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return output_file