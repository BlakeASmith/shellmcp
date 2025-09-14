"""Command-line interface for ShellMCP."""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

import fire

from .generator import FastMCPGenerator
from .models import (
    ArgumentDefinition,
    PromptConfig,
    ResourceConfig,
    ServerConfig,
    ToolArgument,
    ToolConfig,
    YMLConfig,
)
from .parser import YMLParser
from .generator import FastMCPGenerator
from .utils import get_choice, get_input, get_yes_no, load_or_create_config, save_config


def _get_builtin_config(config_name: str) -> str:
    """Get path to a built-in configuration file."""
    from pathlib import Path
    config_dir = Path(__file__).parent / "configs"
    config_file = config_dir / f"{config_name}.yml"
    
    if not config_file.exists():
        available_configs = [f.stem for f in config_dir.glob("*.yml")]
        raise ValueError(f"Built-in config '{config_name}' not found. Available configs: {', '.join(available_configs)}")
    
    return str(config_file)


def _handle_error(error_msg: str, verbose: bool = False, exception: Exception = None) -> int:
    """Common error handling for CLI functions."""
    print(f"❌ {error_msg}", file=sys.stderr)
    if verbose and exception:
        import traceback
        traceback.print_exc()
    return 1


def _check_file_exists(file_path: str) -> bool:
    """Check if file exists and return True/False."""
    return Path(file_path).exists()


def validate(config_file: str, verbose: bool = False) -> int:
    """
    Validate a YAML configuration file.
    
    Args:
        config_file: Path to the YAML configuration file
        verbose: Show detailed validation information
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        if not _check_file_exists(config_file):
            return _handle_error(f"File '{config_file}' not found")
        
        parser = YMLParser()
        config = parser.load_from_file(config_file)
        _output_validation(config_file, config, parser, verbose)
        return 0
        
    except Exception as e:
        return _handle_error(f"Error validating configuration: {e}", verbose, e)


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
        output_dir: Optional output directory (defaults to creating a subdirectory with the server name)
        verbose: Show detailed generation information
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        if not _check_file_exists(config_file):
            return _handle_error(f"File '{config_file}' not found")
        
        # Load and validate configuration
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
            # Default behavior: create a subdirectory with the server name
            # This prevents accidentally overwriting existing files like README.md
            config_dir = Path(config_file).parent
            server_name = config.server.name.replace('-', '_').replace(' ', '_').lower()
            output_dir = config_dir / server_name
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate files
        generator = FastMCPGenerator()
        server_file = generator.generate_server(config_file, str(output_dir / f"{config.server.name.replace('-', '_')}_server.py"))
        requirements_file = generator.generate_requirements(str(output_dir / "requirements.txt"))
        readme_file = generator.generate_readme(config, str(output_dir / "README.md"))
        
        print(f"✅ FastMCP server generated successfully!")
        print(f"📁 Output directory: {output_dir}")
        print(f"🐍 Server file: {server_file}")
        print(f"📦 Requirements: {requirements_file}")
        print(f"📖 Documentation: {readme_file}")
        
        if verbose:
            print(f"\n🚀 To run the server:")
            print(f"   cd {output_dir}")
            print(f"   python3 -m venv venv && source venv/bin/activate")
            print(f"   pip install -r requirements.txt")
            print(f"   python {Path(server_file).name}")
        
        return 0
        
    except Exception as e:
        return _handle_error(f"Error generating server: {e}", verbose, e)


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
        # Get required inputs
        name = name or get_input("Server name", required=True)
        desc = desc or get_input("Server description", required=True)
        version = version or get_input("Server version", default="1.0.0")
        
        # Determine output file
        output_file = output_file or f"{name.replace(' ', '_').lower()}.yml"
        
        # Check if file already exists
        if Path(output_file).exists():
            if not get_yes_no(f"File '{output_file}' already exists. Overwrite?", default=False):
                print("❌ Operation cancelled")
                return 1
        
        # Create and save configuration
        config = YMLConfig(server=ServerConfig(name=name, desc=desc, version=version))
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
        return _handle_error(f"Error creating server: {e}", exception=e)


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
        config = load_or_create_config(config_file)
        
        # Get tool details
        name = name or get_input("Tool name", required=True)
        cmd = cmd or get_input("Shell command (supports Jinja2 templates like {{arg_name}})", required=True)
        desc = desc or get_input("Tool description", required=True)
        help_cmd = help_cmd or get_input("Help command (optional, press Enter to skip)", required=False)
        
        # Check if tool already exists
        if config.tools and name in config.tools:
            if not get_yes_no(f"Tool '{name}' already exists. Overwrite?", default=False):
                print("❌ Operation cancelled")
                return 1
        
        # Collect tool arguments
        arguments = _collect_tool_arguments(config)
        
        # Create and add tool configuration
        tool_config = ToolConfig(
            cmd=cmd,
            desc=desc,
            help_cmd=help_cmd if help_cmd else None,
            args=arguments if arguments else None
        )
        
        if not config.tools:
            config.tools = {}
        config.tools[name] = tool_config
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
        return _handle_error(f"Error adding tool: {e}", exception=e)


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
        config = load_or_create_config(config_file)
        
        # Get resource details
        name = name or get_input("Resource name (key)", required=True)
        uri = uri or get_input("Resource URI", required=True)
        resource_name = resource_name or get_input("Resource display name", default=name)
        description = description or get_input("Resource description", required=False)
        content_type = content_type or get_input("MIME type (optional, e.g., text/plain, application/json)", required=False)
        content_source = content_source or get_choice("How will the resource content be provided?", ["cmd", "file", "text"], default="cmd")
        
        # Check if resource already exists
        if config.resources and name in config.resources:
            if not get_yes_no(f"Resource '{name}' already exists. Overwrite?", default=False):
                print("❌ Operation cancelled")
                return 1
        
        # Get content based on source type
        content = get_input(
            "Shell command to generate content (supports Jinja2 templates)" if content_source == "cmd"
            else "File path to read content from" if content_source == "file"
            else "Direct text content",
            required=True
        )
        
        # Create resource configuration
        resource_config = ResourceConfig(
            uri=uri,
            name=resource_name,
            description=description,
            mime_type=content_type,
            **{content_source: content}
        )
        
        # Add resource to configuration
        if not config.resources:
            config.resources = {}
        config.resources[name] = resource_config
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
        return _handle_error(f"Error adding resource: {e}", exception=e)


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
        config = load_or_create_config(config_file)
        
        # Get prompt details
        name = name or get_input("Prompt name (key)", required=True)
        prompt_name = prompt_name or get_input("Prompt display name", default=name)
        description = description or get_input("Prompt description", required=False)
        content_source = content_source or get_choice("How will the prompt content be provided?", ["cmd", "file", "template"], default="template")
        
        # Check if prompt already exists
        if config.prompts and name in config.prompts:
            if not get_yes_no(f"Prompt '{name}' already exists. Overwrite?", default=False):
                print("❌ Operation cancelled")
                return 1
        
        # Get content based on source type
        content = get_input(
            "Shell command to generate prompt content (supports Jinja2 templates)" if content_source == "cmd"
            else "File path to read prompt content from" if content_source == "file"
            else "Jinja2 template content for the prompt",
            required=True
        )
        
        # Create prompt configuration
        prompt_config = PromptConfig(
            name=prompt_name,
            description=description,
            **{content_source: content}
        )
        
        # Add prompt to configuration
        if not config.prompts:
            config.prompts = {}
        config.prompts[name] = prompt_config
        save_config(config, config_file)
        
        print(f"✅ Added prompt '{name}' to {config_file}")
        print(f"📋 Prompt: {name}")
        print(f"   Display name: {prompt_name}")
        if description:
            print(f"   Description: {description}")
        print(f"   Content source: {content_source}")
        
        return 0
        
    except Exception as e:
        return _handle_error(f"Error adding prompt: {e}", exception=e)


def run(config_name: str = None, config_file: str = None) -> int:
    """
    Run an MCP server from a built-in configuration or YAML file.
    
    Args:
        config_name: Name of built-in configuration (e.g., 'basics')
        config_file: Path to YAML configuration file
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        if config_name and config_file:
            return _handle_error("Cannot specify both config_name and config_file. Use one or the other.")
        
        if not config_name and not config_file:
            return _handle_error("Must specify either config_name (for built-in configs) or config_file (for custom configs)")
        
        # Determine which config to use
        if config_name:
            # Use built-in configuration
            try:
                config_path = _get_builtin_config(config_name)
                print(f"🚀 Starting built-in MCP server: {config_name}")
                print(f"📁 Configuration: {config_path}")
            except ValueError as e:
                return _handle_error(str(e))
        else:
            # Use custom configuration file
            if not _check_file_exists(config_file):
                return _handle_error(f"Configuration file '{config_file}' not found")
            
            config_path = config_file
            print(f"🚀 Starting MCP server from configuration: {config_file}")
        
        # Generate and run the server
        _generate_and_run_server(config_path)
        return 0
        
    except Exception as e:
        return _handle_error(f"Error running MCP server: {e}", exception=e)


def _generate_and_run_server(config_file: str):
    """Generate MCP server code and execute it."""
    import tempfile
    import subprocess
    import os
    from pathlib import Path
    
    # Load and validate configuration
    parser = YMLParser()
    config = parser.load_from_file(config_file)
    
    # Generate server code
    generator = FastMCPGenerator()
    server_code = generator._generate_server_code(config)
    
    # Create a temporary file for the server
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(server_code)
        temp_server_file = f.name
    
    try:
        # Execute the generated server
        print(f"🐍 Executing generated MCP server...")
        subprocess.run([sys.executable, temp_server_file], check=True)
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_server_file)
        except OSError:
            pass  # File might already be deleted


def main():
    """Main CLI entry point using Fire."""
    fire.Fire({
        'validate': validate,
        'generate': generate,
        'new': new,
        'add-tool': add_tool,
        'add-resource': add_resource,
        'add-prompt': add_prompt,
        'run': run
    })