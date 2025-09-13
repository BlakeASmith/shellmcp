"""Command-line interface for YML configuration validation using Google Fire."""

import fire
import sys
from pathlib import Path
from .parser import YMLParser
from .generator import FastMCPGenerator


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


def generate(config_file: str, output_dir: str = None, verbose: bool = False) -> int:
    """
    Generate a FastMCP server from YAML configuration.
    
    Args:
        config_file: Path to the YAML configuration file
        output_dir: Optional output directory (defaults to same directory as config file)
        verbose: Show detailed generation information
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    generator = FastMCPGenerator()
    
    try:
        # Check if file exists
        if not Path(config_file).exists():
            print(f"❌ Error: File '{config_file}' not found", file=sys.stderr)
            return 1
        
        # Load and validate configuration first
        parser = YMLParser()
        config = parser.load_from_file(config_file)
        
        if verbose:
            print(f"✅ Configuration '{config_file}' is valid!")
            server_info = parser.get_server_info()
            print(f"📋 Server: {server_info['name']} v{server_info['version']}")
            print(f"   Description: {server_info['description']}")
            print(f"   Tools: {server_info['tools_count']}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = Path(config_file).parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate server file
        server_file = generator.generate_server(config_file, str(output_dir / f"{config.server.name.replace('-', '_')}_server.py"))
        
        # Generate requirements.txt
        requirements_file = generator.generate_requirements(str(output_dir / "requirements.txt"))
        
        # Generate README.md
        readme_file = generator.generate_readme(config, str(output_dir / "README.md"))
        
        # Generate MCP configuration
        mcp_config_file = generator.generate_mcp_config(
            config, 
            str(output_dir / "mcp.json"),
            str(server_file),
            str(output_dir)
        )
        
        print(f"✅ FastMCP server generated successfully!")
        print(f"📁 Output directory: {output_dir}")
        print(f"🐍 Server file: {server_file}")
        print(f"📦 Requirements: {requirements_file}")
        print(f"📖 Documentation: {readme_file}")
        print(f"⚙️  MCP Config: {mcp_config_file}")
        
        if verbose:
            print(f"\n🚀 To run the server:")
            print(f"   cd {output_dir}")
            print(f"   # Create and activate virtual environment (recommended):")
            print(f"   python -m venv venv")
            print(f"   source venv/bin/activate  # Linux/macOS")
            print(f"   # venv\\Scripts\\activate  # Windows")
            print(f"   pip install -r requirements.txt")
            print(f"   python {Path(server_file).name}")
            
            print(f"\n⚙️  To configure MCP clients:")
            print(f"   Copy the contents of {Path(mcp_config_file).name}")
            print(f"   Add to your editor's MCP configuration file")
            print(f"   See README.md for detailed instructions")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating server: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main CLI entry point using Fire."""
    fire.Fire({
        'validate': validate,
        'generate': generate
    })