"""Command-line interface for YML configuration validation."""

import argparse
import sys
from pathlib import Path
from .parser import YMLParser


def validate_config(file_path: str, verbose: bool = False) -> int:
    """Validate a YAML configuration file."""
    parser = YMLParser()
    
    try:
        config = parser.load_from_file(file_path)
        print(f"✅ Configuration '{file_path}' is valid!")
        
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
        
        return 0
        
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error validating configuration: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate YAML configuration files for shellmcp"
    )
    parser.add_argument(
        "config_file",
        help="Path to the YAML configuration file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed validation information"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.config_file).exists():
        print(f"❌ Error: File '{args.config_file}' not found", file=sys.stderr)
        return 1
    
    return validate_config(args.config_file, args.verbose)


if __name__ == "__main__":
    sys.exit(main())