"""Generate MCP server configuration JSON."""

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .parser import YMLParser


def generate_mcp_config(yml_file: str, server_path: str = None, 
                       python_executable: str = "python3", output_file: str = None) -> str:
    """
    Generate MCP server configuration JSON.
    
    Args:
        yml_file: Path to ShellMCP YAML configuration file
        server_path: Path to the generated server.py file (auto-detected if not provided)
        python_executable: Python executable to use (default: python3)
        output_file: Optional output file path (defaults to stdout)
    
    Returns:
        Generated JSON configuration
    """
    # Load ShellMCP configuration
    if not Path(yml_file).exists():
        raise FileNotFoundError(f"YAML configuration file not found: {yml_file}")
    
    parser = YMLParser()
    yml_config = parser.load_from_file(yml_file)
    server_name = yml_config.server.name.replace(' ', '-').replace('_', '-').lower()
    
    # Auto-detect server path if not provided
    if server_path is None:
        config_dir = Path(yml_file).parent
        server_name_dir = yml_config.server.name.replace('-', '_').replace(' ', '_').lower()
        server_path = config_dir / server_name_dir / f"{yml_config.server.name.replace('-', '_')}_server.py"
    
    # Ensure server path is absolute
    if not Path(server_path).is_absolute():
        server_path = str(Path(server_path).resolve())
    else:
        server_path = str(server_path)
    
    # Get server directory for PYTHONPATH
    server_dir = str(Path(server_path).parent)
    
    # Set up Jinja2 environment and generate JSON using template
    template_dir = Path(__file__).parent / "templates"
    jinja_env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    template = jinja_env.get_template('mcp_config.json.j2')
    json_config = template.render(
        server_name=server_name,
        python_executable=python_executable,
        server_path=server_path,
        server_dir=server_dir
    )
    
    # Parse and pretty-print JSON
    parsed_config = json.loads(json_config)
    formatted_json = json.dumps(parsed_config, indent=2)
    
    # Write to file or return string
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_json)
        return f"✅ MCP configuration written to {output_file}"
    else:
        return formatted_json