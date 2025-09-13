"""Command-line interface for YML configuration validation using Google Fire."""

import fire
import sys
from pathlib import Path
from typing import Optional
from .parser import YMLParser


class ShellMCPCLI:
    """Command-line interface for shellmcp operations."""
    
    def __init__(self):
        self.parser = YMLParser()
    
    def validate(self, config_file: str, verbose: bool = False, output_format: str = "text") -> int:
        """
        Validate a YAML configuration file.
        
        Args:
            config_file: Path to the YAML configuration file
            verbose: Show detailed validation information
            output_format: Output format ('text', 'json', 'yaml')
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            # Check if file exists
            if not Path(config_file).exists():
                print(f"❌ Error: File '{config_file}' not found", file=sys.stderr)
                return 1
            
            # Load and validate configuration
            config = self.parser.load_from_file(config_file)
            
            if output_format == "json":
                self._output_json_validation(config, verbose)
            elif output_format == "yaml":
                self._output_yaml_validation(config, verbose)
            else:
                self._output_text_validation(config_file, config, verbose)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error validating configuration: {e}", file=sys.stderr)
            if verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _output_text_validation(self, config_file: str, config, verbose: bool):
        """Output validation results in text format."""
        print(f"✅ Configuration '{config_file}' is valid!")
        
        if verbose:
            # Show detailed information
            server_info = self.parser.get_server_info()
            print(f"\n📋 Server: {server_info['name']} v{server_info['version']}")
            print(f"   Description: {server_info['description']}")
            print(f"   Tools: {server_info['tools_count']}")
            print(f"   Reusable args: {server_info['reusable_args_count']}")
            
            # Validate templates
            template_validation = self.parser.validate_all_templates()
            print(f"\n🔍 Template validation:")
            for tool_name, is_valid in template_validation.items():
                status = "✅" if is_valid else "❌"
                print(f"   {status} {tool_name}")
            
            # Check argument consistency
            consistency_issues = self.parser.validate_argument_consistency()
            if consistency_issues:
                print(f"\n⚠️  Argument consistency issues:")
                for tool_name, missing_args in consistency_issues.items():
                    print(f"   {tool_name}: missing arguments for {missing_args}")
            else:
                print(f"\n✅ All template variables have corresponding arguments")
    
    def _output_json_validation(self, config, verbose: bool):
        """Output validation results in JSON format."""
        import json
        
        result = {
            "valid": True,
            "server": {
                "name": config.server.name,
                "description": config.server.desc,
                "version": config.server.version
            },
            "tools_count": len(config.tools) if config.tools else 0,
            "reusable_args_count": len(config.args) if config.args else 0
        }
        
        if verbose:
            result["template_validation"] = self.parser.validate_all_templates()
            result["consistency_issues"] = self.parser.validate_argument_consistency()
            result["tools_summary"] = self.parser.get_tools_summary()
        
        print(json.dumps(result, indent=2))
    
    def _output_yaml_validation(self, config, verbose: bool):
        """Output validation results in YAML format."""
        import yaml
        
        result = {
            "valid": True,
            "server": {
                "name": config.server.name,
                "description": config.server.desc,
                "version": config.server.version
            },
            "tools_count": len(config.tools) if config.tools else 0,
            "reusable_args_count": len(config.args) if config.args else 0
        }
        
        if verbose:
            result["template_validation"] = self.parser.validate_all_templates()
            result["consistency_issues"] = self.parser.validate_argument_consistency()
            result["tools_summary"] = self.parser.get_tools_summary()
        
        print(yaml.dump(result, default_flow_style=False))
    
    def info(self, config_file: str, tool_name: Optional[str] = None) -> int:
        """
        Show detailed information about a configuration file or specific tool.
        
        Args:
            config_file: Path to the YAML configuration file
            tool_name: Optional specific tool name to show details for
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            if not Path(config_file).exists():
                print(f"❌ Error: File '{config_file}' not found", file=sys.stderr)
                return 1
            
            config = self.parser.load_from_file(config_file)
            
            if tool_name:
                self._show_tool_info(config, tool_name)
            else:
                self._show_config_info(config)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            return 1
    
    def _show_config_info(self, config):
        """Show general configuration information."""
        server_info = self.parser.get_server_info()
        tools_summary = self.parser.get_tools_summary()
        
        print(f"📋 Configuration Information")
        print(f"   Server: {server_info['name']} v{server_info['version']}")
        print(f"   Description: {server_info['description']}")
        print(f"   Tools: {server_info['tools_count']}")
        print(f"   Reusable Arguments: {server_info['reusable_args_count']}")
        
        if server_info['environment_variables']:
            print(f"\n🌍 Server Environment Variables:")
            for key, value in server_info['environment_variables'].items():
                print(f"   {key}: {value}")
        
        if tools_summary:
            print(f"\n🔧 Tools:")
            for tool_name, tool_info in tools_summary.items():
                print(f"   {tool_name}: {tool_info['description']}")
                print(f"     Arguments: {tool_info['arguments_count']}")
                print(f"     Template Valid: {'✅' if tool_info['has_valid_template'] else '❌'}")
    
    def _show_tool_info(self, config, tool_name: str):
        """Show detailed information for a specific tool."""
        if not config.tools or tool_name not in config.tools:
            print(f"❌ Error: Tool '{tool_name}' not found", file=sys.stderr)
            return
        
        tool = config.tools[tool_name]
        resolved_args = self.parser.get_resolved_tool_arguments(tool_name)
        template_vars = self.parser.get_tool_template_variables(tool_name)
        
        print(f"🔧 Tool: {tool_name}")
        print(f"   Description: {tool.desc}")
        print(f"   Command: {tool.cmd}")
        
        if tool.help_cmd:
            print(f"   Help Command: {tool.help_cmd}")
        
        if resolved_args:
            print(f"\n📝 Arguments:")
            for arg in resolved_args:
                print(f"   - {arg.name}: {arg.help}")
                print(f"     Type: {arg.type}")
                if arg.default is not None:
                    print(f"     Default: {arg.default}")
                if arg.choices:
                    print(f"     Choices: {arg.choices}")
                if arg.pattern:
                    print(f"     Pattern: {arg.pattern}")
        
        if template_vars:
            print(f"\n🔍 Template Variables: {template_vars}")
        
        if tool.env:
            print(f"\n🌍 Environment Variables:")
            for key, value in tool.env.items():
                print(f"   {key}: {value}")
        
        # Check template validity
        is_valid = self.parser.config.validate_jinja2_template(tool_name)
        print(f"\n✅ Template Valid: {'Yes' if is_valid else 'No'}")
    
    def list_tools(self, config_file: str) -> int:
        """
        List all tools in a configuration file.
        
        Args:
            config_file: Path to the YAML configuration file
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            if not Path(config_file).exists():
                print(f"❌ Error: File '{config_file}' not found", file=sys.stderr)
                return 1
            
            config = self.parser.load_from_file(config_file)
            tools_summary = self.parser.get_tools_summary()
            
            if not tools_summary:
                print("No tools found in configuration.")
                return 0
            
            print("🔧 Available Tools:")
            for tool_name, tool_info in tools_summary.items():
                status = "✅" if tool_info['has_valid_template'] else "❌"
                print(f"   {status} {tool_name}: {tool_info['description']}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            return 1


def main():
    """Main CLI entry point using Fire."""
    fire.Fire(ShellMCPCLI)


if __name__ == "__main__":
    main()