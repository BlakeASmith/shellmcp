"""YAML configuration parser and validator."""

import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from .models import YMLConfig


class YMLParser:
    """Parser for YAML configuration files."""
    
    def __init__(self):
        self.config: Optional[YMLConfig] = None
    
    def load_from_file(self, file_path: str) -> YMLConfig:
        """Load and parse YAML configuration from a file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        return self.load_from_dict(yaml_data)
    
    def load_from_string(self, yaml_string: str) -> YMLConfig:
        """Load and parse YAML configuration from a string."""
        yaml_data = yaml.safe_load(yaml_string)
        return self.load_from_dict(yaml_data)
    
    def load_from_dict(self, data: Dict[str, Any]) -> YMLConfig:
        """Load and parse YAML configuration from a dictionary."""
        try:
            self.config = YMLConfig(**data)
            return self.config
        except Exception as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def validate_all_templates(self) -> Dict[str, Dict[str, bool]]:
        """Validate Jinja2 templates for all tools, resources, and prompts."""
        if not self.config:
            return {}
        
        results = {
            "tools": {},
            "resources": {},
            "prompts": {}
        }
        
        # Validate tool templates
        if self.config.tools:
            for tool_name in self.config.tools:
                results["tools"][tool_name] = self.config.validate_jinja2_template(tool_name)
        
        # Validate resource templates
        if self.config.resources:
            for resource_name in self.config.resources:
                results["resources"][resource_name] = self.config.validate_resource_jinja2_template(resource_name)
        
        # Validate prompt templates
        if self.config.prompts:
            for prompt_name in self.config.prompts:
                results["prompts"][prompt_name] = self.config.validate_prompt_jinja2_template(prompt_name)
        
        return results
    
    def get_tool_template_variables(self, tool_name: str) -> list[str]:
        """Get template variables for a specific tool."""
        if not self.config:
            return []
        
        return self.config.get_template_variables(tool_name)
    
    def get_resource_template_variables(self, resource_name: str) -> list[str]:
        """Get template variables for a specific resource."""
        if not self.config:
            return []
        
        return self.config.get_resource_template_variables(resource_name)
    
    def get_prompt_template_variables(self, prompt_name: str) -> list[str]:
        """Get template variables for a specific prompt."""
        if not self.config:
            return []
        
        return self.config.get_prompt_template_variables(prompt_name)
    
    def get_resolved_tool_arguments(self, tool_name: str) -> list:
        """Get resolved arguments for a specific tool."""
        if not self.config:
            return []
        
        return self.config.get_resolved_arguments(tool_name)
    
    def get_resolved_resource_arguments(self, resource_name: str) -> list:
        """Get resolved arguments for a specific resource."""
        if not self.config:
            return []
        
        return self.config.get_resolved_resource_arguments(resource_name)
    
    def get_resolved_prompt_arguments(self, prompt_name: str) -> list:
        """Get resolved arguments for a specific prompt."""
        if not self.config:
            return []
        
        return self.config.get_resolved_prompt_arguments(prompt_name)
    
    def validate_argument_consistency(self) -> Dict[str, Dict[str, list[str]]]:
        """Validate that all template variables have corresponding arguments for tools, resources, and prompts."""
        if not self.config:
            return {}
        
        issues = {
            "tools": {},
            "resources": {},
            "prompts": {}
        }
        
        # Validate tool argument consistency
        if self.config.tools:
            for tool_name in self.config.tools:
                template_vars = self.get_tool_template_variables(tool_name)
                resolved_args = self.get_resolved_tool_arguments(tool_name)
                arg_names = {arg.name for arg in resolved_args}
                
                missing_args = []
                for var in template_vars:
                    if var not in arg_names and var not in ['now']:  # 'now' is a built-in function
                        missing_args.append(var)
                
                if missing_args:
                    issues["tools"][tool_name] = missing_args
        
        # Validate resource argument consistency
        if self.config.resources:
            for resource_name in self.config.resources:
                template_vars = self.get_resource_template_variables(resource_name)
                resolved_args = self.get_resolved_resource_arguments(resource_name)
                arg_names = {arg.name for arg in resolved_args}
                
                missing_args = []
                for var in template_vars:
                    if var not in arg_names and var not in ['now']:  # 'now' is a built-in function
                        missing_args.append(var)
                
                if missing_args:
                    issues["resources"][resource_name] = missing_args
        
        # Validate prompt argument consistency
        if self.config.prompts:
            for prompt_name in self.config.prompts:
                template_vars = self.get_prompt_template_variables(prompt_name)
                resolved_args = self.get_resolved_prompt_arguments(prompt_name)
                arg_names = {arg.name for arg in resolved_args}
                
                missing_args = []
                for var in template_vars:
                    if var not in arg_names and var not in ['now']:  # 'now' is a built-in function
                        missing_args.append(var)
                
                if missing_args:
                    issues["prompts"][prompt_name] = missing_args
        
        return issues
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server configuration information."""
        if not self.config:
            return {}
        
        return {
            "name": self.config.server.name,
            "description": self.config.server.desc,
            "version": self.config.server.version,
            "environment_variables": self.config.server.env or {},
            "tools_count": len(self.config.tools) if self.config.tools else 0,
            "resources_count": len(self.config.resources) if self.config.resources else 0,
            "prompts_count": len(self.config.prompts) if self.config.prompts else 0,
            "reusable_args_count": len(self.config.args) if self.config.args else 0
        }
    
    def get_tools_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary information for all tools."""
        if not self.config or not self.config.tools:
            return {}
        
        summary = {}
        for tool_name, tool in self.config.tools.items():
            resolved_args = self.get_resolved_tool_arguments(tool_name)
            template_vars = self.get_tool_template_variables(tool_name)
            
            summary[tool_name] = {
                "description": tool.desc,
                "command": tool.cmd,
                "help_command": tool.help_cmd,
                "arguments_count": len(resolved_args),
                "template_variables": template_vars,
                "environment_variables": tool.env or {},
                "has_valid_template": self.config.validate_jinja2_template(tool_name)
            }
        
        return summary
    
    def get_resources_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary information for all resources."""
        if not self.config or not self.config.resources:
            return {}
        
        summary = {}
        for resource_name, resource in self.config.resources.items():
            resolved_args = self.get_resolved_resource_arguments(resource_name)
            template_vars = self.get_resource_template_variables(resource_name)
            
            summary[resource_name] = {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mime_type,
                "command": resource.cmd,
                "arguments_count": len(resolved_args),
                "template_variables": template_vars,
                "environment_variables": resource.env or {},
                "has_valid_template": self.config.validate_resource_jinja2_template(resource_name)
            }
        
        return summary
    
    def get_prompts_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary information for all prompts."""
        if not self.config or not self.config.prompts:
            return {}
        
        summary = {}
        for prompt_name, prompt in self.config.prompts.items():
            resolved_args = self.get_resolved_prompt_arguments(prompt_name)
            template_vars = self.get_prompt_template_variables(prompt_name)
            
            summary[prompt_name] = {
                "name": prompt.name,
                "description": prompt.description,
                "command": prompt.cmd,
                "arguments_count": len(resolved_args),
                "template_variables": template_vars,
                "environment_variables": prompt.env or {},
                "has_valid_template": self.config.validate_prompt_jinja2_template(prompt_name)
            }
        
        return summary