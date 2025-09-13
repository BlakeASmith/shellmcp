"""FastMCP server generator from YAML configuration."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Template, Environment, FileSystemLoader
from .parser import YMLParser
from .models import YMLConfig
from .template_utils import get_jinja_filters


class FastMCPGenerator:
    """Generator for FastMCP servers from YAML configuration."""
    
    def __init__(self):
        self.parser = YMLParser()
        # Set up Jinja2 environment with templates directory
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        # Add custom filters
        self.jinja_env.filters.update(get_jinja_filters())
        
    def generate_server(self, config_file: str, output_file: Optional[str] = None) -> str:
        """
        Generate a FastMCP server from YAML configuration.
        
        Args:
            config_file: Path to the YAML configuration file
            output_file: Optional output file path (defaults to server.py in same directory)
        
        Returns:
            Path to the generated server file
        """
        # Load and validate configuration
        config = self.parser.load_from_file(config_file)
        
        # Generate server code
        server_code = self._generate_server_code(config)
        
        # Determine output path
        if output_file is None:
            config_path = Path(config_file)
            output_file = config_path.parent / f"{config.server.name.replace('-', '_')}_server.py"
        
        # Write server file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(server_code)
        
        return str(output_file)
    
    def _generate_server_code(self, config: YMLConfig) -> str:
        """Generate FastMCP server code from configuration using Jinja2 templates."""
        template = self.jinja_env.get_template('server.py.j2')
        return template.render(config=config)
    
    
    def generate_requirements(self, output_file: Optional[str] = None) -> str:
        """Generate requirements.txt file for the FastMCP server."""
        template = self.jinja_env.get_template('requirements.txt.j2')
        requirements = template.render()
        
        if output_file is None:
            output_file = "requirements.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        return output_file
    
    def generate_readme(self, config: YMLConfig, output_file: Optional[str] = None) -> str:
        """Generate README.md for the FastMCP server."""
        template = self.jinja_env.get_template('README.md.j2')
        readme_content = template.render(config=config)
        
        if output_file is None:
            output_file = "README.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return output_file
    
    
    def generate_amazon_q_config(self, config: YMLConfig, output_file: str, server_script_path: str, server_directory: str) -> str:
        """Generate Amazon Q CLI configuration file for the FastMCP server."""
        template = self.jinja_env.get_template('amazon-q-config.json.j2')
        amazon_q_config = template.render(
            config=config,
            server_script_path=server_script_path,
            server_directory=server_directory
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(amazon_q_config)
        
        return output_file