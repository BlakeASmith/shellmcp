"""Command-line interface for YML configuration validation using Google Fire."""

import fire
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from .parser import YMLParser
from .generator import FastMCPGenerator
from .models import YMLConfig, ServerConfig, ToolConfig, ResourceConfig, PromptConfig, ToolArgument, ArgumentDefinition
from .utils import get_input, get_choice, get_yes_no, save_config, load_or_create_config


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
            # Create a subdirectory matching the server name by default
            config_dir = Path(config_file).parent
            server_name = config.server.name.replace('-', '_').replace(' ', '_').lower()
            output_dir = config_dir / server_name
        else:
            output_dir = Path(output_dir)
        
        # Create the output directory
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
            name = get_input("Server name", required=True)
        
        # Get server description
        if not desc:
            desc = get_input("Server description", required=True)
        
        # Get version
        if not version:
            version = get_input("Server version", default="1.0.0")
        
        # Determine output file
        if not output_file:
            output_file = f"{name.replace(' ', '_').lower()}.yml"
        
        # Check if file already exists
        if Path(output_file).exists():
            overwrite = get_yes_no(f"File '{output_file}' already exists. Overwrite?", default=False)
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
        save_config(config, output_file)
        
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


def _collect_tool_argument(config: YMLConfig, existing_args: List[str] = None) -> Optional[ToolArgument]:
    """
    Collect a single tool argument from user input.
    
    Args:
        config: Current configuration (for reusable args)
        existing_args: List of already defined argument names
    
    Returns:
        ToolArgument or None if user cancels
    """
    existing_args = existing_args or []
    
    # Get argument name
    while True:
        arg_name = get_input("Argument name", required=True)
        if arg_name in existing_args:
            print(f"❌ Argument '{arg_name}' already exists. Please choose a different name.")
            continue
        break
    
    # Check if user wants to use a reusable argument reference
    use_ref = False
    if config.args:
        available_refs = list(config.args.keys())
        if available_refs:
            use_ref = get_yes_no(
                f"Use a reusable argument reference? Available: {', '.join(available_refs)}", 
                default=False
            )
    
    if use_ref and config.args:
        # Let user choose from available references
        ref_name = get_choice("Select reusable argument", list(config.args.keys()))
        return ToolArgument(
            name=arg_name,
            help="",  # Will be resolved from reference
            ref=ref_name
        )
    
    # Collect argument properties
    arg_help = get_input("Argument description", required=True)
    
    arg_type = get_choice(
        "Argument type",
        ["string", "number", "boolean", "array"],
        default="string"
    )
    
    # Get default value (optional)
    has_default = get_yes_no("Does this argument have a default value?", default=False)
    default_value = None
    if has_default:
        default_input = get_input("Default value (leave empty for null)", required=False)
        if default_input:
            if arg_type == "number":
                try:
                    default_value = float(default_input) if '.' in default_input else int(default_input)
                except ValueError:
                    print("⚠️  Invalid number format, using string value")
                    default_value = default_input
            elif arg_type == "boolean":
                default_value = default_input.lower() in ('true', '1', 'yes', 'on')
            elif arg_type == "array":
                default_value = [item.strip() for item in default_input.split(',')]
            else:
                default_value = default_input
    
    # Get choices (optional)
    has_choices = get_yes_no("Does this argument have predefined choices?", default=False)
    choices = None
    if has_choices:
        choices_input = get_input("Enter choices (comma-separated)", required=True)
        choices = [choice.strip() for choice in choices_input.split(',')]
    
    # Get validation pattern (optional)
    has_pattern = get_yes_no("Does this argument need regex validation?", default=False)
    pattern = None
    if has_pattern:
        pattern = get_input("Enter regex pattern", required=True)
        # Validate the pattern
        try:
            import re
            re.compile(pattern)
        except re.error as e:
            print(f"⚠️  Invalid regex pattern: {e}")
            pattern = None
    
    return ToolArgument(
        name=arg_name,
        help=arg_help,
        type=arg_type,
        default=default_value,
        choices=choices,
        pattern=pattern
    )


def _collect_tool_arguments(config: YMLConfig) -> List[ToolArgument]:
    """
    Collect multiple tool arguments from user input.
    
    Args:
        config: Current configuration
    
    Returns:
        List of ToolArgument objects
    """
    arguments = []
    
    # Ask if user wants to add arguments
    add_args = get_yes_no("Does this tool need arguments/parameters?", default=False)
    if not add_args:
        return arguments
    
    print("\n📝 Adding tool arguments...")
    existing_arg_names = []
    
    while True:
        print(f"\n--- Argument {len(arguments) + 1} ---")
        arg = _collect_tool_argument(config, existing_arg_names)
        if arg:
            arguments.append(arg)
            existing_arg_names.append(arg.name)
            print(f"✅ Added argument: {arg.name} ({arg.type})")
        
        # Ask if user wants to add more arguments
        add_more = get_yes_no("Add another argument?", default=False)
        if not add_more:
            break
    
    return arguments


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
        config = load_or_create_config(config_file)
        
        # Get tool name
        if not name:
            name = get_input("Tool name", required=True)
        
        # Check if tool already exists
        if config.tools and name in config.tools:
            overwrite = get_yes_no(f"Tool '{name}' already exists. Overwrite?", default=False)
            if not overwrite:
                print("❌ Operation cancelled")
                return 1
        
        # Get tool command
        if not cmd:
            cmd = get_input("Shell command (supports Jinja2 templates like {{arg_name}})", required=True)
        
        # Get tool description
        if not desc:
            desc = get_input("Tool description", required=True)
        
        # Get help command (optional)
        if not help_cmd:
            help_cmd = get_input("Help command (optional, press Enter to skip)", required=False)
        
        # Collect tool arguments
        arguments = _collect_tool_arguments(config)
        
        # Create tool configuration
        tool_config = ToolConfig(
            cmd=cmd,
            desc=desc,
            help_cmd=help_cmd if help_cmd else None,
            args=arguments if arguments else None
        )
        
        # Add tool to configuration
        if not config.tools:
            config.tools = {}
        config.tools[name] = tool_config
        
        # Save configuration
        save_config(config, config_file)
        
        print(f"✅ Added tool '{name}' to {config_file}")
        print(f"📋 Tool: {name}")
        print(f"   Description: {desc}")
        print(f"   Command: {cmd}")
        if help_cmd:
            print(f"   Help command: {help_cmd}")
        
        if arguments:
            print(f"   Arguments ({len(arguments)}):")
            for arg in arguments:
                arg_info = f"     • {arg.name} ({arg.type})"
                if arg.ref:
                    arg_info += f" [ref: {arg.ref}]"
                else:
                    arg_info += f": {arg.help}"
                if arg.default is not None:
                    arg_info += f" (default: {arg.default})"
                print(arg_info)
        
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
        config = load_or_create_config(config_file)
        
        # Get resource name
        if not name:
            name = get_input("Resource name (key)", required=True)
        
        # Check if resource already exists
        if config.resources and name in config.resources:
            overwrite = get_yes_no(f"Resource '{name}' already exists. Overwrite?", default=False)
            if not overwrite:
                print("❌ Operation cancelled")
                return 1
        
        # Get URI
        if not uri:
            uri = get_input("Resource URI", required=True)
        
        # Get resource display name
        if not resource_name:
            resource_name = get_input("Resource display name", default=name)
        
        # Get description
        if not description:
            description = get_input("Resource description", required=False)
        
        # Get MIME type
        if not content_type:
            content_type = get_input("MIME type (optional, e.g., text/plain, application/json)", required=False)
        
        # Get content source type
        if not content_source:
            content_source = get_choice(
                "How will the resource content be provided?",
                ["cmd", "file", "text"],
                default="cmd"
            )
        
        # Get content based on source type
        if content_source == "cmd":
            content = get_input("Shell command to generate content (supports Jinja2 templates)", required=True)
            resource_config = ResourceConfig(
                uri=uri,
                name=resource_name,
                description=description,
                mime_type=content_type,
                cmd=content
            )
        elif content_source == "file":
            content = get_input("File path to read content from", required=True)
            resource_config = ResourceConfig(
                uri=uri,
                name=resource_name,
                description=description,
                mime_type=content_type,
                file=content
            )
        else:  # text
            content = get_input("Direct text content", required=True)
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
        save_config(config, config_file)
        
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
        config = load_or_create_config(config_file)
        
        # Get prompt name
        if not name:
            name = get_input("Prompt name (key)", required=True)
        
        # Check if prompt already exists
        if config.prompts and name in config.prompts:
            overwrite = get_yes_no(f"Prompt '{name}' already exists. Overwrite?", default=False)
            if not overwrite:
                print("❌ Operation cancelled")
                return 1
        
        # Get prompt display name
        if not prompt_name:
            prompt_name = get_input("Prompt display name", default=name)
        
        # Get description
        if not description:
            description = get_input("Prompt description", required=False)
        
        # Get content source type
        if not content_source:
            content_source = get_choice(
                "How will the prompt content be provided?",
                ["cmd", "file", "template"],
                default="template"
            )
        
        # Get content based on source type
        if content_source == "cmd":
            content = get_input("Shell command to generate prompt content (supports Jinja2 templates)", required=True)
            prompt_config = PromptConfig(
                name=prompt_name,
                description=description,
                cmd=content
            )
        elif content_source == "file":
            content = get_input("File path to read prompt content from", required=True)
            prompt_config = PromptConfig(
                name=prompt_name,
                description=description,
                file=content
            )
        else:  # template
            content = get_input("Jinja2 template content for the prompt", required=True)
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
        save_config(config, config_file)
        
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