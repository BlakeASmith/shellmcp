"""Pydantic models for YAML configuration parsing."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
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
    
    @field_validator('pattern')
    @classmethod
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
    
    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v):
        """Validate that pattern is a valid regex."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v
    
    # Note: We allow ref to be used with other properties
    # The resolution logic will handle merging properties from the reference


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
    
    model_config = {"populate_by_name": True}


class ResourceConfig(BaseModel):
    """Resource configuration."""
    
    uri: str = Field(..., description="Resource URI")
    name: str = Field(..., description="Resource name")
    description: Optional[str] = Field(None, description="Resource description")
    mime_type: Optional[str] = Field(None, description="MIME type of the resource")
    cmd: str = Field(..., description="Shell command to generate resource content (supports Jinja2 templates)")
    args: Optional[List[ToolArgument]] = Field(None, description="Argument definitions for resource generation")
    env: Optional[Dict[str, str]] = Field(None, description="Resource-specific environment variables")


class PromptConfig(BaseModel):
    """Prompt configuration."""
    
    name: str = Field(..., description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    cmd: str = Field(..., description="Shell command to generate prompt content (supports Jinja2 templates)")
    args: Optional[List[ToolArgument]] = Field(None, description="Argument definitions for prompt generation")
    env: Optional[Dict[str, str]] = Field(None, description="Prompt-specific environment variables")


class YMLConfig(BaseModel):
    """Root YAML configuration model."""
    
    server: ServerConfig = Field(..., description="Server configuration")
    args: Optional[Dict[str, ArgumentDefinition]] = Field(
        None, description="Reusable argument definitions"
    )
    tools: Optional[Dict[str, ToolConfig]] = Field(None, description="Tool definitions")
    resources: Optional[Dict[str, ResourceConfig]] = Field(None, description="Resource definitions")
    prompts: Optional[Dict[str, PromptConfig]] = Field(None, description="Prompt definitions")
    
    @model_validator(mode='after')
    def validate_argument_references(self):
        """Validate that all argument references exist."""
        args = self.args or {}
        tools = self.tools or {}
        resources = self.resources or {}
        prompts = self.prompts or {}
        
        # Validate tool argument references
        if tools:
            for tool_name, tool in tools.items():
                if tool.args:
                    for arg in tool.args:
                        if arg.ref and arg.ref not in args:
                            raise ValueError(
                                f"Tool '{tool_name}' references undefined argument '{arg.ref}'"
                            )
        
        # Validate resource argument references
        if resources:
            for resource_name, resource in resources.items():
                if resource.args:
                    for arg in resource.args:
                        if arg.ref and arg.ref not in args:
                            raise ValueError(
                                f"Resource '{resource_name}' references undefined argument '{arg.ref}'"
                            )
        
        # Validate prompt argument references
        if prompts:
            for prompt_name, prompt in prompts.items():
                if prompt.args:
                    for arg in prompt.args:
                        if arg.ref and arg.ref not in args:
                            raise ValueError(
                                f"Prompt '{prompt_name}' references undefined argument '{arg.ref}'"
                            )
        
        return self
    
    @model_validator(mode='after')
    def validate_unique_names(self):
        """Validate that tool, resource, prompt names and argument names are unique."""
        tools = self.tools or {}
        resources = self.resources or {}
        prompts = self.prompts or {}
        
        # Check for duplicate tool names
        if tools:
            tool_names = list(tools.keys())
            if len(tool_names) != len(set(tool_names)):
                raise ValueError("Tool names must be unique")
            
            # Check for duplicate argument names within each tool
            for tool_name, tool in tools.items():
                if tool.args:
                    arg_names = [arg.name for arg in tool.args]
                    if len(arg_names) != len(set(arg_names)):
                        raise ValueError(f"Argument names must be unique within tool '{tool_name}'")
        
        # Check for duplicate resource names
        if resources:
            resource_names = list(resources.keys())
            if len(resource_names) != len(set(resource_names)):
                raise ValueError("Resource names must be unique")
            
            # Check for duplicate argument names within each resource
            for resource_name, resource in resources.items():
                if resource.args:
                    arg_names = [arg.name for arg in resource.args]
                    if len(arg_names) != len(set(arg_names)):
                        raise ValueError(f"Argument names must be unique within resource '{resource_name}'")
        
        # Check for duplicate prompt names
        if prompts:
            prompt_names = list(prompts.keys())
            if len(prompt_names) != len(set(prompt_names)):
                raise ValueError("Prompt names must be unique")
            
            # Check for duplicate argument names within each prompt
            for prompt_name, prompt in prompts.items():
                if prompt.args:
                    arg_names = [arg.name for arg in prompt.args]
                    if len(arg_names) != len(set(arg_names)):
                        raise ValueError(f"Argument names must be unique within prompt '{prompt_name}'")
        
        return self
    
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
    
    def get_resolved_resource_arguments(self, resource_name: str) -> List[ToolArgument]:
        """Get fully resolved arguments for a resource, expanding references."""
        if not self.resources or resource_name not in self.resources:
            return []
        
        resource = self.resources[resource_name]
        if not resource.args:
            return []
        
        resolved_args = []
        for arg in resource.args:
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
    
    def get_resolved_prompt_arguments(self, prompt_name: str) -> List[ToolArgument]:
        """Get fully resolved arguments for a prompt, expanding references."""
        if not self.prompts or prompt_name not in self.prompts:
            return []
        
        prompt = self.prompts[prompt_name]
        if not prompt.args:
            return []
        
        resolved_args = []
        for arg in prompt.args:
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
    
    def validate_resource_jinja2_template(self, resource_name: str) -> bool:
        """Validate that the resource's command contains valid Jinja2 template syntax."""
        if not self.resources or resource_name not in self.resources:
            return False
        
        try:
            from jinja2 import Template
            template_str = self.resources[resource_name].cmd
            Template(template_str)
            return True
        except Exception:
            return False
    
    def validate_prompt_jinja2_template(self, prompt_name: str) -> bool:
        """Validate that the prompt's command contains valid Jinja2 template syntax."""
        if not self.prompts or prompt_name not in self.prompts:
            return False
        
        try:
            from jinja2 import Template
            template_str = self.prompts[prompt_name].cmd
            Template(template_str)
            return True
        except Exception:
            return False
    
    def get_template_variables(self, tool_name: str) -> List[str]:
        """Extract template variables from a tool's command."""
        if not self.tools or tool_name not in self.tools:
            return []
        
        try:
            from jinja2 import Template, meta
            template_str = self.tools[tool_name].cmd
            template = Template(template_str)
            
            # Get all variables used in the template
            ast = template.environment.parse(template_str)
            variables = meta.find_undeclared_variables(ast)
            
            return list(variables)
        except Exception:
            return []
    
    def get_resource_template_variables(self, resource_name: str) -> List[str]:
        """Extract template variables from a resource's command."""
        if not self.resources or resource_name not in self.resources:
            return []
        
        try:
            from jinja2 import Template, meta
            template_str = self.resources[resource_name].cmd
            template = Template(template_str)
            
            # Get all variables used in the template
            ast = template.environment.parse(template_str)
            variables = meta.find_undeclared_variables(ast)
            
            return list(variables)
        except Exception:
            return []
    
    def get_prompt_template_variables(self, prompt_name: str) -> List[str]:
        """Extract template variables from a prompt's command."""
        if not self.prompts or prompt_name not in self.prompts:
            return []
        
        try:
            from jinja2 import Template, meta
            template_str = self.prompts[prompt_name].cmd
            template = Template(template_str)
            
            # Get all variables used in the template
            ast = template.environment.parse(template_str)
            variables = meta.find_undeclared_variables(ast)
            
            return list(variables)
        except Exception:
            return []
    
    model_config = {"extra": "forbid"}  # Prevent additional fields not defined in the model