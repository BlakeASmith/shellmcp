"""Direct MCP server runner from YAML configuration."""

import os
import subprocess
import tempfile
import shlex
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from jinja2 import Template, Environment

from .models import YMLConfig
from .parser import YMLParser


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


class MCPRunner:
    """Direct MCP server runner from YAML configuration."""
    
    def __init__(self, config: YMLConfig):
        self.config = config
        self.mcp = FastMCP(name=config.server.name)
        self._setup_server()
        self._register_tools()
        self._register_resources()
        self._register_prompts()
    
    def _setup_server(self):
        """Set up server configuration and environment variables."""
        # Set server environment variables
        if self.config.server.env:
            for key, value in self.config.server.env.items():
                os.environ[key] = value
    
    def _register_tools(self):
        """Register all tools from the configuration."""
        if not self.config.tools:
            return
        
        for tool_name, tool in self.config.tools.items():
            self._register_tool(tool_name, tool)
    
    def _register_tool(self, tool_name: str, tool):
        """Register a single tool."""
        func_name = tool_name.lower().replace('-', '_')
        resolved_args = self.config.get_resolved_arguments(tool_name)
        
        # Build function signature
        params_with_defaults = []
        params_without_defaults = []
        
        for arg in resolved_args:
            if arg.default is not None:
                param = f"{arg.name}: {self._python_type(arg.type)} = {self._python_value(arg.default, arg.type)}"
                params_with_defaults.append(param)
            else:
                param = f"{arg.name}: {self._python_type(arg.type)}"
                params_without_defaults.append(param)
        
        param_str = ", ".join(params_without_defaults + params_with_defaults)
        
        # Create the tool function with explicit parameters
        def create_tool_func(tool_name, tool, resolved_args):
            # Build the function signature dynamically
            if not resolved_args:
                def tool_func() -> Dict[str, Any]:
                    try:
                        # Render command template
                        cmd = render_template(tool.cmd)
                        
                        # Execute command
                        env_vars = {}
                        if tool.env:
                            env_vars.update(tool.env)
                        
                        result = execute_command(cmd, env_vars)
                        return result
                        
                    except Exception as e:
                        return {
                            "success": False,
                            "stdout": "",
                            "stderr": f"Error in {tool_name}: {str(e)}",
                            "returncode": -1
                        }
            else:
                # Create function with explicit parameters
                import types
                
                # Build parameter list
                param_names = []
                param_defaults = []
                
                for arg in resolved_args:
                    param_names.append(arg.name)
                    if arg.default is not None:
                        param_defaults.append(arg.default)
                
                # Create function code
                func_code = f"""
def {func_name}({', '.join(param_names)}) -> Dict[str, Any]:
    try:
        # Validate arguments
        args_dict = {{{', '.join([f"'{name}': {name}" for name in param_names])}}}
        
        # Validate each argument
        for arg_name, value in args_dict.items():
            if value is None:
                raise ValueError(f"Required argument '{{arg_name}}' not provided")
        
        # Render command template
        cmd = render_template(tool.cmd, **args_dict)
        
        # Execute command
        env_vars = {{}}
        if tool.env:
            env_vars.update(tool.env)
        
        result = execute_command(cmd, env_vars)
        return result
        
    except Exception as e:
        return {{
            "success": False,
            "stdout": "",
            "stderr": f"Error in {tool_name}: {{str(e)}}",
            "returncode": -1
        }}
"""
                
                # Execute the function code
                func_globals = {
                    'render_template': render_template,
                    'execute_command': execute_command,
                    'tool': tool,
                    'tool_name': tool_name,
                    'Dict': Dict,
                    'Any': Any
                }
                func_locals = {}
                exec(func_code, func_globals, func_locals)
                tool_func = func_locals[func_name]
            
            # Set function metadata
            tool_func.__name__ = func_name
            tool_func.__doc__ = self._create_tool_docstring(tool_name, tool, resolved_args)
            return tool_func
        
        # Register the tool
        tool_func = create_tool_func(tool_name, tool, resolved_args)
        self.mcp.tool()(tool_func)
    
    def _register_resources(self):
        """Register all resources from the configuration."""
        if not self.config.resources:
            return
        
        for resource_name, resource in self.config.resources.items():
            self._register_resource(resource_name, resource)
    
    def _register_resource(self, resource_name: str, resource):
        """Register a single resource."""
        func_name = resource_name.lower().replace('-', '_')
        resolved_args = self.config.get_resolved_resource_arguments(resource_name)
        
        # Build function signature
        params_with_defaults = []
        params_without_defaults = []
        
        for arg in resolved_args:
            if arg.default is not None:
                param = f"{arg.name}: {self._python_type(arg.type)} = {self._python_value(arg.default, arg.type)}"
                params_with_defaults.append(param)
            else:
                param = f"{arg.name}: {self._python_type(arg.type)}"
                params_without_defaults.append(param)
        
        param_str = ", ".join(params_without_defaults + params_with_defaults)
        
        # Create the resource function with explicit parameters
        def create_resource_func(resource_name, resource, resolved_args):
            if not resolved_args:
                def resource_func() -> str:
                    try:
                        # Get content based on source type
                        if resource.text:
                            content = render_template(resource.text)
                        elif resource.file:
                            file_path = render_template(resource.file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                            except FileNotFoundError:
                                raise ValueError(f"Resource file not found: {file_path}")
                            except Exception as e:
                                raise ValueError(f"Error reading resource file {file_path}: {str(e)}")
                        else:  # cmd
                            cmd = render_template(resource.cmd)
                            env_vars = {}
                            if resource.env:
                                env_vars.update(resource.env)
                            
                            result = execute_command(cmd, env_vars)
                            if not result["success"]:
                                raise ValueError(f"Command failed: {result['stderr']}")
                            content = result["stdout"]
                        
                        return content
                        
                    except Exception as e:
                        raise ValueError(f"Error in {resource_name}: {str(e)}")
            else:
                # Create function with explicit parameters
                param_names = [arg.name for arg in resolved_args]
                
                func_code = f"""
def {func_name}({', '.join(param_names)}) -> str:
    try:
        # Validate arguments
        args_dict = {{{', '.join([f"'{name}': {name}" for name in param_names])}}}
        
        # Get content based on source type
        if resource.text:
            content = render_template(resource.text, **args_dict)
        elif resource.file:
            file_path = render_template(resource.file, **args_dict)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                raise ValueError(f"Resource file not found: {{file_path}}")
            except Exception as e:
                raise ValueError(f"Error reading resource file {{file_path}}: {{str(e)}}")
        else:  # cmd
            cmd = render_template(resource.cmd, **args_dict)
            env_vars = {{}}
            if resource.env:
                env_vars.update(resource.env)
            
            result = execute_command(cmd, env_vars)
            if not result["success"]:
                raise ValueError(f"Command failed: {{result['stderr']}}")
            content = result["stdout"]
        
        return content
        
    except Exception as e:
        raise ValueError(f"Error in {resource_name}: {{str(e)}}")
"""
                
                # Execute the function code
                func_globals = {
                    'render_template': render_template,
                    'execute_command': execute_command,
                    'resource': resource,
                    'resource_name': resource_name
                }
                func_locals = {}
                exec(func_code, func_globals, func_locals)
                resource_func = func_locals[func_name]
            
            # Set function metadata
            resource_func.__name__ = func_name
            resource_func.__doc__ = self._create_resource_docstring(resource_name, resource, resolved_args)
            return resource_func
        
        # Register the resource
        resource_func = create_resource_func(resource_name, resource, resolved_args)
        # Convert Jinja2 template variables in URI to Python format
        uri = resource.uri.replace('{{ ', '{').replace(' }}', '}').replace('{{', '{').replace('}}', '}')
        self.mcp.resource(uri)(resource_func)
    
    def _register_prompts(self):
        """Register all prompts from the configuration."""
        if not self.config.prompts:
            return
        
        for prompt_name, prompt in self.config.prompts.items():
            self._register_prompt(prompt_name, prompt)
    
    def _register_prompt(self, prompt_name: str, prompt):
        """Register a single prompt."""
        func_name = prompt_name.lower().replace('-', '_')
        resolved_args = self.config.get_resolved_prompt_arguments(prompt_name)
        
        # Build function signature
        params_with_defaults = []
        params_without_defaults = []
        
        for arg in resolved_args:
            if arg.default is not None:
                param = f"{arg.name}: {self._python_type(arg.type)} = {self._python_value(arg.default, arg.type)}"
                params_with_defaults.append(param)
            else:
                param = f"{arg.name}: {self._python_type(arg.type)}"
                params_without_defaults.append(param)
        
        param_str = ", ".join(params_without_defaults + params_with_defaults)
        
        # Create the prompt function with explicit parameters
        def create_prompt_func(prompt_name, prompt, resolved_args):
            if not resolved_args:
                def prompt_func() -> str:
                    try:
                        # Get content based on source type
                        if prompt.template:
                            content = render_template(prompt.template)
                        elif prompt.file:
                            file_path = render_template(prompt.file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                            except FileNotFoundError:
                                raise ValueError(f"Prompt file not found: {file_path}")
                            except Exception as e:
                                raise ValueError(f"Error reading prompt file {file_path}: {str(e)}")
                        else:  # cmd
                            cmd = render_template(prompt.cmd)
                            env_vars = {}
                            if prompt.env:
                                env_vars.update(prompt.env)
                            
                            result = execute_command(cmd, env_vars)
                            if not result["success"]:
                                raise ValueError(f"Command failed: {result['stderr']}")
                            content = result["stdout"]
                        
                        return content
                        
                    except Exception as e:
                        raise ValueError(f"Error in {prompt_name}: {str(e)}")
            else:
                # Create function with explicit parameters
                param_names = [arg.name for arg in resolved_args]
                
                func_code = f"""
def {func_name}({', '.join(param_names)}) -> str:
    try:
        # Validate arguments
        args_dict = {{{', '.join([f"'{name}': {name}" for name in param_names])}}}
        
        # Get content based on source type
        if prompt.template:
            content = render_template(prompt.template, **args_dict)
        elif prompt.file:
            file_path = render_template(prompt.file, **args_dict)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                raise ValueError(f"Prompt file not found: {{file_path}}")
            except Exception as e:
                raise ValueError(f"Error reading prompt file {{file_path}}: {{str(e)}}")
        else:  # cmd
            cmd = render_template(prompt.cmd, **args_dict)
            env_vars = {{}}
            if prompt.env:
                env_vars.update(prompt.env)
            
            result = execute_command(cmd, env_vars)
            if not result["success"]:
                raise ValueError(f"Command failed: {{result['stderr']}}")
            content = result["stdout"]
        
        return content
        
    except Exception as e:
        raise ValueError(f"Error in {prompt_name}: {{str(e)}}")
"""
                
                # Execute the function code
                func_globals = {
                    'render_template': render_template,
                    'execute_command': execute_command,
                    'prompt': prompt,
                    'prompt_name': prompt_name
                }
                func_locals = {}
                exec(func_code, func_globals, func_locals)
                prompt_func = func_locals[func_name]
            
            # Set function metadata
            prompt_func.__name__ = func_name
            prompt_func.__doc__ = self._create_prompt_docstring(prompt_name, prompt, resolved_args)
            return prompt_func
        
        # Register the prompt
        prompt_func = create_prompt_func(prompt_name, prompt, resolved_args)
        self.mcp.prompt()(prompt_func)
    
    def _python_type(self, type_str: str) -> str:
        """Convert YAML type to Python type annotation."""
        type_mapping = {
            "string": "str",
            "number": "float",
            "boolean": "bool",
            "array": "List[str]"
        }
        return type_mapping.get(type_str, "str")
    
    def _python_value(self, value: Any, type_str: str) -> str:
        """Convert value to Python literal string."""
        if type_str == "string":
            return repr(str(value))
        elif type_str == "number":
            return str(value)
        elif type_str == "boolean":
            return str(value)
        elif type_str == "array":
            return repr(value)
        else:
            return repr(str(value))
    
    def _create_tool_docstring(self, tool_name: str, tool, resolved_args: List) -> str:
        """Create docstring for a tool function."""
        doc_parts = [tool.desc]
        
        if resolved_args:
            doc_parts.append("\nParameters:")
            for arg in resolved_args:
                doc_parts.append(f"- {arg.name} ({arg.type}): {arg.help}")
                if arg.default is not None:
                    doc_parts.append(f"  Default: {arg.default}")
                if arg.choices:
                    doc_parts.append(f"  Allowed values: {', '.join(map(str, arg.choices))}")
                if arg.pattern:
                    doc_parts.append(f"  Pattern: {arg.pattern}")
        
        doc_parts.append("\nReturns:")
        doc_parts.append("    Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.")
        
        return "\n".join(doc_parts)
    
    def _create_resource_docstring(self, resource_name: str, resource, resolved_args: List) -> str:
        """Create docstring for a resource function."""
        doc_parts = [resource.description or resource.name]
        
        if resolved_args:
            doc_parts.append("\nParameters:")
            for arg in resolved_args:
                doc_parts.append(f"- {arg.name} ({arg.type}): {arg.help}")
                if arg.default is not None:
                    doc_parts.append(f"  Default: {arg.default}")
                if arg.choices:
                    doc_parts.append(f"  Allowed values: {', '.join(map(str, arg.choices))}")
                if arg.pattern:
                    doc_parts.append(f"  Pattern: {arg.pattern}")
        
        doc_parts.append("\nReturns:")
        doc_parts.append("    str: The resource content.")
        
        return "\n".join(doc_parts)
    
    def _create_prompt_docstring(self, prompt_name: str, prompt, resolved_args: List) -> str:
        """Create docstring for a prompt function."""
        doc_parts = [prompt.description or prompt.name]
        
        if resolved_args:
            doc_parts.append("\nParameters:")
            for arg in resolved_args:
                doc_parts.append(f"- {arg.name} ({arg.type}): {arg.help}")
                if arg.default is not None:
                    doc_parts.append(f"  Default: {arg.default}")
                if arg.choices:
                    doc_parts.append(f"  Allowed values: {', '.join(map(str, arg.choices))}")
                if arg.pattern:
                    doc_parts.append(f"  Pattern: {arg.pattern}")
        
        doc_parts.append("\nReturns:")
        doc_parts.append("    str: The generated prompt content.")
        
        return "\n".join(doc_parts)
    
    def run(self):
        """Run the MCP server."""
        print(f"Starting {self.config.server.name} v{self.config.server.version}")
        print(f"Description: {self.config.server.desc}")
        self.mcp.run()


def get_builtin_config(config_name: str) -> str:
    """Get path to a built-in configuration file."""
    config_dir = Path(__file__).parent / "configs"
    config_file = config_dir / f"{config_name}.yml"
    
    if not config_file.exists():
        available_configs = [f.stem for f in config_dir.glob("*.yml")]
        raise ValueError(f"Built-in config '{config_name}' not found. Available configs: {', '.join(available_configs)}")
    
    return str(config_file)


def run_config(config_file: str):
    """Run an MCP server from a YAML configuration file."""
    parser = YMLParser()
    config = parser.load_from_file(config_file)
    
    runner = MCPRunner(config)
    runner.run()