"""Pydantic models for YAML configuration parsing."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
import re


class ArgumentDefinition(BaseModel):
    """Reusable argument definition."""
    
    help: str = Field(..., description="Argument description")
    type: Literal["string", "number", "boolean", "array"] = Field(
        default="string", description="Argument type"
    )
    default: Optional[Any] = Field(None, description="Default value (makes argument optional)")
    choices: Optional[List[Any]] = Field(None, description="Allowed values for validation")
    pattern: Optional[str] = Field(None, description="Regex pattern for validation")
    
    @validator('pattern')
    def validate_pattern(cls, v):
        """Validate that pattern is a valid regex."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v


class ToolArgument(BaseModel):
    """Tool argument definition."""
    
    name: str = Field(..., description="Argument name")
    help: str = Field(..., description="Argument description")
    type: Literal["string", "number", "boolean", "array"] = Field(
        default="string", description="Argument type"
    )
    default: Optional[Any] = Field(None, description="Default value (makes argument optional)")
    choices: Optional[List[Any]] = Field(None, description="Allowed values")
    pattern: Optional[str] = Field(None, description="Regex validation pattern")
    ref: Optional[str] = Field(None, description="Reference to reusable argument definition")
    
    @validator('pattern')
    def validate_pattern(cls, v):
        """Validate that pattern is a valid regex."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v
    
    @validator('ref')
    def validate_ref_exclusive(cls, v, values):
        """Ensure ref is not used with other argument properties."""
        if v is not None:
            # If ref is provided, other properties should not be set
            conflicting_fields = ['type', 'default', 'choices', 'pattern']
            for field in conflicting_fields:
                if field in values and values[field] is not None:
                    raise ValueError(f"Cannot use 'ref' with '{field}' - use one or the other")
        return v


class ServerConfig(BaseModel):
    """Server configuration."""
    
    name: str = Field(..., description="Name of the MCP server")
    desc: str = Field(..., description="Description of the server")
    version: str = Field(default="1.0.0", description="Server version")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")


class ToolConfig(BaseModel):
    """Tool configuration."""
    
    cmd: str = Field(..., description="Shell command to execute (supports Jinja2 templates)")
    desc: str = Field(..., description="Tool description")
    help_cmd: Optional[str] = Field(None, alias="help-cmd", description="Command to get help text")
    args: Optional[List[ToolArgument]] = Field(None, description="Argument definitions")
    env: Optional[Dict[str, str]] = Field(None, description="Tool-specific environment variables")
    
    class Config:
        allow_population_by_field_name = True


class YMLConfig(BaseModel):
    """Root YAML configuration model."""
    
    server: ServerConfig = Field(..., description="Server configuration")
    args: Optional[Dict[str, ArgumentDefinition]] = Field(
        None, description="Reusable argument definitions"
    )
    tools: Optional[Dict[str, ToolConfig]] = Field(None, description="Tool definitions")
    
    @root_validator
    def validate_argument_references(cls, values):
        """Validate that all argument references exist."""
        args = values.get('args', {})
        tools = values.get('tools', {})
        
        if tools:
            for tool_name, tool in tools.items():
                if tool.args:
                    for arg in tool.args:
                        if arg.ref and arg.ref not in args:
                            raise ValueError(
                                f"Tool '{tool_name}' references undefined argument '{arg.ref}'"
                            )
        
        return values
    
    @root_validator
    def validate_unique_names(cls, values):
        """Validate that tool names and argument names are unique."""
        tools = values.get('tools', {})
        
        if tools:
            # Check for duplicate tool names (should be handled by dict keys, but let's be explicit)
            tool_names = list(tools.keys())
            if len(tool_names) != len(set(tool_names)):
                raise ValueError("Tool names must be unique")
            
            # Check for duplicate argument names within each tool
            for tool_name, tool in tools.items():
                if tool.args:
                    arg_names = [arg.name for arg in tool.args]
                    if len(arg_names) != len(set(arg_names)):
                        raise ValueError(f"Argument names must be unique within tool '{tool_name}'")
        
        return values
    
    def get_resolved_arguments(self, tool_name: str) -> List[ToolArgument]:
        """Get fully resolved arguments for a tool, expanding references."""
        if not self.tools or tool_name not in self.tools:
            return []
        
        tool = self.tools[tool_name]
        if not tool.args:
            return []
        
        resolved_args = []
        for arg in tool.args:
            if arg.ref:
                # Resolve reference
                if not self.args or arg.ref not in self.args:
                    raise ValueError(f"Reference '{arg.ref}' not found in args section")
                
                ref_arg = self.args[arg.ref]
                # Create a new argument with the reference properties
                resolved_arg = ToolArgument(
                    name=arg.name,
                    help=ref_arg.help,
                    type=ref_arg.type,
                    default=ref_arg.default,
                    choices=ref_arg.choices,
                    pattern=ref_arg.pattern
                )
                resolved_args.append(resolved_arg)
            else:
                resolved_args.append(arg)
        
        return resolved_args
    
    def validate_jinja2_template(self, tool_name: str) -> bool:
        """Validate that the tool's command contains valid Jinja2 template syntax."""
        if not self.tools or tool_name not in self.tools:
            return False
        
        try:
            from jinja2 import Template
            template_str = self.tools[tool_name].cmd
            Template(template_str)
            return True
        except Exception:
            return False
    
    def get_template_variables(self, tool_name: str) -> List[str]:
        """Extract template variables from a tool's command."""
        if not self.tools or tool_name not in self.tools:
            return []
        
        try:
            from jinja2 import Template
            template_str = self.tools[tool_name].cmd
            template = Template(template_str)
            
            # Get all variables used in the template
            variables = []
            for node in template.parse():
                if hasattr(node, 'name'):
                    variables.append(node.name)
            
            return list(set(variables))
        except Exception:
            return []
    
    class Config:
        extra = "forbid"  # Prevent additional fields not defined in the model