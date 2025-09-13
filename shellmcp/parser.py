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
    
    def validate_all_templates(self) -> Dict[str, bool]:
        """Validate Jinja2 templates for all tools."""
        if not self.config or not self.config.tools:
            return {}
        
        results = {}
        for tool_name in self.config.tools:
            results[tool_name] = self.config.validate_jinja2_template(tool_name)
        
        return results
    
    def get_tool_template_variables(self, tool_name: str) -> list[str]:
        """Get template variables for a specific tool."""
        if not self.config:
            return []
        
        return self.config.get_template_variables(tool_name)
    
    def get_resolved_tool_arguments(self, tool_name: str) -> list:
        """Get resolved arguments for a specific tool."""
        if not self.config:
            return []
        
        return self.config.get_resolved_arguments(tool_name)
    
    def validate_argument_consistency(self) -> Dict[str, list[str]]:
        """Validate that all template variables have corresponding arguments."""
        if not self.config or not self.config.tools:
            return {}
        
        issues = {}
        for tool_name in self.config.tools:
            template_vars = self.get_tool_template_variables(tool_name)
            resolved_args = self.get_resolved_tool_arguments(tool_name)
            arg_names = {arg.name for arg in resolved_args}
            
            missing_args = []
            for var in template_vars:
                if var not in arg_names and var not in ['now']:  # 'now' is a built-in function
                    missing_args.append(var)
            
            if missing_args:
                issues[tool_name] = missing_args
        
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