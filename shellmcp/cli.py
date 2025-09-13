"""Command-line interface for YML configuration validation using Google Fire."""

import fire
import sys
from pathlib import Path
from .parser import YMLParser


def validate(config_file: str, verbose: bool = False) -> int:
    """
    Validate a YAML configuration file.
    
    Args:
        config_file: Path to the YAML configuration file
        verbose: Show detailed validation information
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = YMLParser()
    
    try:
        # Check if file exists
        if not Path(config_file).exists():
            print(f"❌ Error: File '{config_file}' not found", file=sys.stderr)
            return 1
        
        # Load and validate configuration
        config = parser.load_from_file(config_file)
        
        _output_validation(config_file, config, parser, verbose)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error validating configuration: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def _output_validation(config_file: str, config, parser, verbose: bool):
    """Output validation results."""
    print(f"✅ Configuration '{config_file}' is valid!")
    
    if verbose:
        # Show detailed information
        server_info = parser.get_server_info()
        print(f"\n📋 Server: {server_info['name']} v{server_info['version']}")
        print(f"   Description: {server_info['description']}")
        print(f"   Tools: {server_info['tools_count']}")
        print(f"   Reusable args: {server_info['reusable_args_count']}")
        
        # Validate templates
        template_validation = parser.validate_all_templates()
        print(f"\n🔍 Template validation:")
        for tool_name, is_valid in template_validation.items():
            status = "✅" if is_valid else "❌"
            print(f"   {status} {tool_name}")
        
        # Check argument consistency
        consistency_issues = parser.validate_argument_consistency()
        if consistency_issues:
            print(f"\n⚠️  Argument consistency issues:")
            for tool_name, missing_args in consistency_issues.items():
                print(f"   {tool_name}: missing arguments for {missing_args}")
        else:
            print(f"\n✅ All template variables have corresponding arguments")


def main():
    """Main CLI entry point using Fire."""
    fire.Fire({
        'validate': validate
    })