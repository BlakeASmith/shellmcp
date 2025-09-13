"""Command-line interface for YML configuration validation using Google Fire."""

import fire
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from .parser import YMLParser
from .generator import FastMCPGenerator
from .models import YMLConfig, ServerConfig, ToolConfig, ResourceConfig, PromptConfig, ToolArgument, ArgumentDefinition


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
        
        
        print(f"✅ FastMCP server generated successfully!")
        print(f"📁 Output directory: {output_dir}")
        print(f"🐍 Server file: {server_file}")
        print(f"📦 Requirements: {requirements_file}")
        print(f"📖 Documentation: {readme_file}")
        
        if verbose:
            print(f"\n🚀 To run the server:")
            print(f"   cd {output_dir}")
            print(f"   # Create and activate virtual environment (recommended):")
            print(f"   python3 -m venv venv")
            print(f"   source venv/bin/activate")
            print(f"   pip install -r requirements.txt")
            print(f"   python {Path(server_file).name}")
            
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating server: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def _get_input(prompt: str, default: str = None, required: bool = True) -> str:
    """Get user input with optional default value."""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        value = input(full_prompt).strip()
        if value:
            return value
        elif default:
            return default
        elif not required:
            return ""
        else:
            print("This field is required. Please enter a value.")


def _get_choice(prompt: str, choices: List[str], default: str = None) -> str:
    """Get user choice from a list of options."""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        marker = " (default)" if choice == default else ""
        print(f"  {i}. {choice}{marker}")
    
    while True:
        try:
            choice_input = input(f"Enter choice (1-{len(choices)}): ").strip()
            if not choice_input and default:
                return default
            
            choice_num = int(choice_input)
            if 1 <= choice_num <= len(choices):
                return choices[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print("Please enter a valid number")


def _get_yes_no(prompt: str, default: bool = None) -> bool:
    """Get yes/no input from user."""
    if default is True:
        full_prompt = f"{prompt} [Y/n]: "
    elif default is False:
        full_prompt = f"{prompt} [y/N]: "
    else:
        full_prompt = f"{prompt} [y/n]: "
    
    while True:
        value = input(full_prompt).strip().lower()
        if value in ['y', 'yes']:
            return True
        elif value in ['n', 'no']:
            return False
        elif value == "" and default is not None:
            return default
        else:
            print("Please enter 'y' for yes or 'n' for no")


def _save_config(config: YMLConfig, file_path: str) -> None:
    """Save configuration to YAML file."""
    config_dict = config.model_dump(exclude_none=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False, indent=2)


def _load_or_create_config(config_file: str) -> YMLConfig:
    """Load existing config or create new one."""
    if Path(config_file).exists():
        parser = YMLParser()
        return parser.load_from_file(config_file)
    else:
        # Create minimal config
        return YMLConfig(server=ServerConfig(name="", desc=""))


def new(name: str = None, desc: str = None, version: str = None, output_file: str = None) -> int:
    """
    Create a new shellmcp server configuration.
    
    Args:
        name: Server name
        desc: Server description  
        version: Server version (default: 1.0.0)
        output_file: Output YAML file path (default: {name}.yml)
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Get server name
        if not name:
            name = _get_input("Server name", required=True)
        
        # Get server description
        if not desc:
            desc = _get_input("Server description", required=True)
        
        # Get version
        if not version:
            version = _get_input("Server version", default="1.0.0")
        
        # Determine output file
        if not output_file:
            output_file = f"{name.replace(' ', '_').lower()}.yml"
        
        # Check if file already exists
        if Path(output_file).exists():
            overwrite = _get_yes_no(f"File '{output_file}' already exists. Overwrite?", default=False)
            if not overwrite:
                print("❌ Operation cancelled")
                return 1
        
        # Create server configuration
        server_config = ServerConfig(
            name=name,
            desc=desc,
            version=version
        )
        
        config = YMLConfig(server=server_config)
        
        # Save configuration
        _save_config(config, output_file)
        
        print(f"✅ Created new server configuration: {output_file}")
        print(f"📋 Server: {name} v{version}")
        print(f"   Description: {desc}")
        print(f"\n🚀 Next steps:")
        print(f"   shellmcp add-tool {output_file}    # Add a tool")
        print(f"   shellmcp validate {output_file}    # Validate configuration")
        print(f"   shellmcp generate {output_file}    # Generate server")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating server: {e}", file=sys.stderr)
        return 1


def add_tool(config_file: str, name: str = None, cmd: str = None, desc: str = None, help_cmd: str = None) -> int:
    """
    Add a new tool to an existing server configuration.
    
    Args:
        config_file: Path to the YAML configuration file
        name: Tool name
        cmd: Shell command (supports Jinja2 templates)
        desc: Tool description
        help_cmd: Command to get help text (optional)
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Load existing configuration
        config = _load_or_create_config(config_file)
        
        # Get tool name
        if not name:
            name = _get_input("Tool name", required=True)
        
        # Check if tool already exists
        if config.tools and name in config.tools:
            overwrite = _get_yes_no(f"Tool '{name}' already exists. Overwrite?", default=False)
            if not overwrite:
                print("❌ Operation cancelled")
                return 1
        
        # Get tool command
        if not cmd:
            cmd = _get_input("Shell command (supports Jinja2 templates like {{arg_name}})", required=True)
        
        # Get tool description
        if not desc:
            desc = _get_input("Tool description", required=True)
        
        # Get help command (optional)
        if not help_cmd:
            help_cmd = _get_input("Help command (optional, press Enter to skip)", required=False)
        
        # Create tool configuration
        tool_config = ToolConfig(
            cmd=cmd,
            desc=desc,
            help_cmd=help_cmd if help_cmd else None
        )
        
        # Add tool to configuration
        if not config.tools:
            config.tools = {}
        config.tools[name] = tool_config
        
        # Save configuration
        _save_config(config, config_file)
        
        print(f"✅ Added tool '{name}' to {config_file}")
        print(f"📋 Tool: {name}")
        print(f"   Description: {desc}")
        print(f"   Command: {cmd}")
        if help_cmd:
            print(f"   Help command: {help_cmd}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error adding tool: {e}", file=sys.stderr)
        return 1


def add_resource(config_file: str, name: str = None, uri: str = None, resource_name: str = None, 
                description: str = None, content_type: str = None, content_source: str = None) -> int:
    """
    Add a new resource to an existing server configuration.
    
    Args:
        config_file: Path to the YAML configuration file
        name: Resource key name
        uri: Resource URI
        resource_name: Display name for the resource
        description: Resource description
        content_type: MIME type (optional)
        content_source: Content source type (cmd/file/text)
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Load existing configuration
        config = _load_or_create_config(config_file)
        
        # Get resource name
        if not name:
            name = _get_input("Resource name (key)", required=True)
        
        # Check if resource already exists
        if config.resources and name in config.resources:
            overwrite = _get_yes_no(f"Resource '{name}' already exists. Overwrite?", default=False)
            if not overwrite:
                print("❌ Operation cancelled")
                return 1
        
        # Get URI
        if not uri:
            uri = _get_input("Resource URI", required=True)
        
        # Get resource display name
        if not resource_name:
            resource_name = _get_input("Resource display name", default=name)
        
        # Get description
        if not description:
            description = _get_input("Resource description", required=False)
        
        # Get MIME type
        if not content_type:
            content_type = _get_input("MIME type (optional, e.g., text/plain, application/json)", required=False)
        
        # Get content source type
        if not content_source:
            content_source = _get_choice(
                "How will the resource content be provided?",
                ["cmd", "file", "text"],
                default="cmd"
            )
        
        # Get content based on source type
        if content_source == "cmd":
            content = _get_input("Shell command to generate content (supports Jinja2 templates)", required=True)
            resource_config = ResourceConfig(
                uri=uri,
                name=resource_name,
                description=description,
                mime_type=content_type,
                cmd=content
            )
        elif content_source == "file":
            content = _get_input("File path to read content from", required=True)
            resource_config = ResourceConfig(
                uri=uri,
                name=resource_name,
                description=description,
                mime_type=content_type,
                file=content
            )
        else:  # text
            content = _get_input("Direct text content", required=True)
            resource_config = ResourceConfig(
                uri=uri,
                name=resource_name,
                description=description,
                mime_type=content_type,
                text=content
            )
        
        # Add resource to configuration
        if not config.resources:
            config.resources = {}
        config.resources[name] = resource_config
        
        # Save configuration
        _save_config(config, config_file)
        
        print(f"✅ Added resource '{name}' to {config_file}")
        print(f"📋 Resource: {name}")
        print(f"   URI: {uri}")
        print(f"   Display name: {resource_name}")
        if description:
            print(f"   Description: {description}")
        if content_type:
            print(f"   MIME type: {content_type}")
        print(f"   Content source: {content_source}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error adding resource: {e}", file=sys.stderr)
        return 1


def add_prompt(config_file: str, name: str = None, prompt_name: str = None, description: str = None, 
              content_source: str = None) -> int:
    """
    Add a new prompt to an existing server configuration.
    
    Args:
        config_file: Path to the YAML configuration file
        name: Prompt key name
        prompt_name: Display name for the prompt
        description: Prompt description
        content_source: Content source type (cmd/file/template)
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Load existing configuration
        config = _load_or_create_config(config_file)
        
        # Get prompt name
        if not name:
            name = _get_input("Prompt name (key)", required=True)
        
        # Check if prompt already exists
        if config.prompts and name in config.prompts:
            overwrite = _get_yes_no(f"Prompt '{name}' already exists. Overwrite?", default=False)
            if not overwrite:
                print("❌ Operation cancelled")
                return 1
        
        # Get prompt display name
        if not prompt_name:
            prompt_name = _get_input("Prompt display name", default=name)
        
        # Get description
        if not description:
            description = _get_input("Prompt description", required=False)
        
        # Get content source type
        if not content_source:
            content_source = _get_choice(
                "How will the prompt content be provided?",
                ["cmd", "file", "template"],
                default="template"
            )
        
        # Get content based on source type
        if content_source == "cmd":
            content = _get_input("Shell command to generate prompt content (supports Jinja2 templates)", required=True)
            prompt_config = PromptConfig(
                name=prompt_name,
                description=description,
                cmd=content
            )
        elif content_source == "file":
            content = _get_input("File path to read prompt content from", required=True)
            prompt_config = PromptConfig(
                name=prompt_name,
                description=description,
                file=content
            )
        else:  # template
            content = _get_input("Jinja2 template content for the prompt", required=True)
            prompt_config = PromptConfig(
                name=prompt_name,
                description=description,
                template=content
            )
        
        # Add prompt to configuration
        if not config.prompts:
            config.prompts = {}
        config.prompts[name] = prompt_config
        
        # Save configuration
        _save_config(config, config_file)
        
        print(f"✅ Added prompt '{name}' to {config_file}")
        print(f"📋 Prompt: {name}")
        print(f"   Display name: {prompt_name}")
        if description:
            print(f"   Description: {description}")
        print(f"   Content source: {content_source}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error adding prompt: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point using Fire."""
    fire.Fire({
        'validate': validate,
        'generate': generate,
        'new': new,
        'add-tool': add_tool,
        'add-resource': add_resource,
        'add-prompt': add_prompt
    })