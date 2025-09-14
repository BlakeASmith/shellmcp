"""AmazonQ MCP installation automation for ShellMCP servers."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

import click
import yaml
from jinja2 import Template

from .models import YMLConfig
from .parser import YMLParser


class AmazonQInstaller:
    """Automates installation of ShellMCP servers to AmazonQ mcp.json configuration."""
    
    def __init__(self):
        self.parser = YMLParser()
        
    def get_mcp_config_paths(self) -> Dict[str, Path]:
        """Get possible MCP configuration file paths for AmazonQ."""
        home = Path.home()
        return {
            'global': home / '.aws' / 'amazonq' / 'mcp.json',
            'local': Path.cwd() / '.amazonq' / 'mcp.json',
            'user_config': home / '.config' / 'amazonq' / 'mcp.json'
        }
    
    def find_existing_mcp_config(self) -> Optional[Path]:
        """Find existing mcp.json configuration file."""
        paths = self.get_mcp_config_paths()
        
        for location, path in paths.items():
            if path.exists():
                click.echo(f"📁 Found existing MCP config at {location}: {path}")
                return path
        
        return None
    
    def create_default_mcp_config(self, target_path: Path) -> Dict[str, Any]:
        """Create a default MCP configuration structure."""
        return {
            "mcpServers": {}
        }
    
    def load_mcp_config(self, config_path: Path) -> Dict[str, Any]:
        """Load existing MCP configuration or create new one."""
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                click.echo(f"✅ Loaded existing MCP configuration from {config_path}")
                return config
            except (json.JSONDecodeError, Exception) as e:
                click.echo(f"⚠️  Error reading {config_path}: {e}")
                click.echo("Creating new configuration...")
        
        # Create new configuration
        config = self.create_default_mcp_config(config_path)
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        return config
    
    def save_mcp_config(self, config: Dict[str, Any], config_path: Path) -> None:
        """Save MCP configuration to file."""
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, sort_keys=True)
        
        click.echo(f"✅ Saved MCP configuration to {config_path}")
    
    def generate_server_config(self, yml_config: YMLConfig, server_path: str, 
                             python_executable: str = "python3") -> Dict[str, Any]:
        """Generate MCP server configuration from ShellMCP YAML config."""
        server_name = yml_config.server.name.replace(' ', '-').replace('_', '-').lower()
        
        # Determine if we should use absolute or relative path
        if Path(server_path).is_absolute():
            command = server_path
        else:
            command = str(Path(server_path).resolve())
        
        return {
            "command": python_executable,
            "args": [command],
            "env": {
                "PYTHONPATH": str(Path(server_path).parent)
            }
        }
    
    def install_server(self, yml_file: str, server_path: str, 
                      config_location: str = "auto", 
                      python_executable: str = "python3",
                      force: bool = False) -> int:
        """
        Install a ShellMCP server to AmazonQ mcp.json configuration.
        
        Args:
            yml_file: Path to ShellMCP YAML configuration file
            server_path: Path to the generated server.py file
            config_location: Where to save mcp.json (global/local/user_config/auto)
            python_executable: Python executable to use (default: python3)
            force: Overwrite existing server configuration
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            # Load ShellMCP configuration
            if not Path(yml_file).exists():
                click.echo(f"❌ YAML configuration file not found: {yml_file}", err=True)
                return 1
            
            yml_config = self.parser.load_from_file(yml_file)
            server_name = yml_config.server.name.replace(' ', '-').replace('_', '-').lower()
            
            # Determine MCP config location
            if config_location == "auto":
                existing_config = self.find_existing_mcp_config()
                if existing_config:
                    mcp_config_path = existing_config
                else:
                    # Default to local configuration
                    mcp_config_path = self.get_mcp_config_paths()['local']
            else:
                mcp_config_path = self.get_mcp_config_paths().get(config_location)
                if not mcp_config_path:
                    click.echo(f"❌ Invalid config location: {config_location}", err=True)
                    click.echo(f"Valid options: {', '.join(self.get_mcp_config_paths().keys())}")
                    return 1
            
            # Load or create MCP configuration
            mcp_config = self.load_mcp_config(mcp_config_path)
            
            # Check if server already exists
            if not mcp_config.get("mcpServers"):
                mcp_config["mcpServers"] = {}
            
            if server_name in mcp_config["mcpServers"] and not force:
                click.echo(f"❌ Server '{server_name}' already exists in MCP configuration", err=True)
                click.echo("Use --force to overwrite existing configuration")
                return 1
            
            # Generate server configuration
            server_config = self.generate_server_config(yml_config, server_path, python_executable)
            
            # Add server to configuration
            mcp_config["mcpServers"][server_name] = server_config
            
            # Save configuration
            self.save_mcp_config(mcp_config, mcp_config_path)
            
            # Display success information
            click.echo(f"\n✅ Successfully installed server '{server_name}' to AmazonQ MCP configuration!")
            click.echo(f"📋 Server Details:")
            click.echo(f"   Name: {server_name}")
            click.echo(f"   Description: {yml_config.server.desc}")
            click.echo(f"   Version: {yml_config.server.version}")
            click.echo(f"   Server file: {server_path}")
            click.echo(f"   Config location: {mcp_config_path}")
            
            if yml_config.tools:
                click.echo(f"   Tools ({len(yml_config.tools)}):")
                for tool_name in yml_config.tools.keys():
                    click.echo(f"     • {tool_name}")
            
            if yml_config.resources:
                click.echo(f"   Resources ({len(yml_config.resources)}):")
                for resource_name in yml_config.resources.keys():
                    click.echo(f"     • {resource_name}")
            
            if yml_config.prompts:
                click.echo(f"   Prompts ({len(yml_config.prompts)}):")
                for prompt_name in yml_config.prompts.keys():
                    click.echo(f"     • {prompt_name}")
            
            click.echo(f"\n🚀 Next steps:")
            click.echo(f"   1. Restart AmazonQ to load the new MCP server")
            click.echo(f"   2. The server will be available as '{server_name}' in AmazonQ")
            
            return 0
            
        except Exception as e:
            click.echo(f"❌ Error installing server: {e}", err=True)
            return 1
    
    def list_installed_servers(self, config_location: str = "auto") -> int:
        """List all installed MCP servers."""
        try:
            # Find MCP configuration
            if config_location == "auto":
                mcp_config_path = self.find_existing_mcp_config()
            else:
                mcp_config_path = self.get_mcp_config_paths().get(config_location)
            
            if not mcp_config_path or not mcp_config_path.exists():
                click.echo("❌ No MCP configuration found")
                return 1
            
            # Load configuration
            mcp_config = self.load_mcp_config(mcp_config_path)
            servers = mcp_config.get("mcpServers", {})
            
            if not servers:
                click.echo("📋 No MCP servers installed")
                return 0
            
            click.echo(f"📋 Installed MCP servers ({len(servers)}):")
            click.echo(f"   Config location: {mcp_config_path}")
            click.echo()
            
            for server_name, server_config in servers.items():
                click.echo(f"🔧 {server_name}")
                click.echo(f"   Command: {server_config.get('command', 'N/A')}")
                if server_config.get('args'):
                    click.echo(f"   Args: {' '.join(server_config['args'])}")
                if server_config.get('env'):
                    env_vars = server_config['env']
                    click.echo(f"   Environment: {len(env_vars)} variables")
                click.echo()
            
            return 0
            
        except Exception as e:
            click.echo(f"❌ Error listing servers: {e}", err=True)
            return 1
    
    def uninstall_server(self, server_name: str, config_location: str = "auto", 
                        force: bool = False) -> int:
        """Uninstall an MCP server from AmazonQ configuration."""
        try:
            # Find MCP configuration
            if config_location == "auto":
                mcp_config_path = self.find_existing_mcp_config()
            else:
                mcp_config_path = self.get_mcp_config_paths().get(config_location)
            
            if not mcp_config_path or not mcp_config_path.exists():
                click.echo("❌ No MCP configuration found")
                return 1
            
            # Load configuration
            mcp_config = self.load_mcp_config(mcp_config_path)
            servers = mcp_config.get("mcpServers", {})
            
            if server_name not in servers:
                click.echo(f"❌ Server '{server_name}' not found in MCP configuration")
                return 1
            
            if not force:
                if not click.confirm(f"Are you sure you want to uninstall server '{server_name}'?"):
                    click.echo("❌ Uninstall cancelled")
                    return 1
            
            # Remove server
            del servers[server_name]
            
            # Save configuration
            self.save_mcp_config(mcp_config, mcp_config_path)
            
            click.echo(f"✅ Successfully uninstalled server '{server_name}'")
            click.echo("🚀 Restart AmazonQ to apply changes")
            
            return 0
            
        except Exception as e:
            click.echo(f"❌ Error uninstalling server: {e}", err=True)
            return 1


@click.group()
def amazonq():
    """AmazonQ MCP installation automation for ShellMCP servers."""
    pass


@amazonq.command()
@click.argument('yml_file', type=click.Path(exists=True))
@click.argument('server_path', type=click.Path())
@click.option('--config-location', '-l', 
              type=click.Choice(['global', 'local', 'user_config', 'auto']),
              default='auto',
              help='Where to save mcp.json configuration')
@click.option('--python-executable', '-p',
              default='python3',
              help='Python executable to use for running the server')
@click.option('--force', '-f', is_flag=True,
              help='Overwrite existing server configuration')
def install(yml_file, server_path, config_location, python_executable, force):
    """Install a ShellMCP server to AmazonQ mcp.json configuration."""
    installer = AmazonQInstaller()
    exit_code = installer.install_server(
        yml_file, server_path, config_location, python_executable, force
    )
    sys.exit(exit_code)


@amazonq.command()
@click.option('--config-location', '-l',
              type=click.Choice(['global', 'local', 'user_config', 'auto']),
              default='auto',
              help='MCP configuration location to check')
def list(config_location):
    """List all installed MCP servers."""
    installer = AmazonQInstaller()
    exit_code = installer.list_installed_servers(config_location)
    sys.exit(exit_code)


@amazonq.command()
@click.argument('server_name')
@click.option('--config-location', '-l',
              type=click.Choice(['global', 'local', 'user_config', 'auto']),
              default='auto',
              help='MCP configuration location to modify')
@click.option('--force', '-f', is_flag=True,
              help='Skip confirmation prompt')
def uninstall(server_name, config_location, force):
    """Uninstall an MCP server from AmazonQ configuration."""
    installer = AmazonQInstaller()
    exit_code = installer.uninstall_server(server_name, config_location, force)
    sys.exit(exit_code)


if __name__ == '__main__':
    amazonq()