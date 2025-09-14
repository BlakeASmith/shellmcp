"""Simple AmazonQ MCP installation automation for ShellMCP servers."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .models import YMLConfig
from .parser import YMLParser


class AmazonQInstaller:
    """Simple installer for adding ShellMCP servers to AmazonQ mcp.json configuration."""
    
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
                print(f"📁 Found existing MCP config at {location}: {path}")
                return path
        
        return None
    
    def load_mcp_config(self, config_path: Path) -> Dict[str, Any]:
        """Load existing MCP configuration or create new one."""
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✅ Loaded existing MCP configuration from {config_path}")
                return config
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️  Error reading {config_path}: {e}")
                print("Creating new configuration...")
        
        # Create new configuration
        config = {"mcpServers": {}}
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        return config
    
    def save_mcp_config(self, config: Dict[str, Any], config_path: Path) -> None:
        """Save MCP configuration to file."""
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, sort_keys=True)
        
        print(f"✅ Saved MCP configuration to {config_path}")
    
    def generate_server_config(self, yml_config: YMLConfig, server_path: str, 
                             python_executable: str = "python3") -> Dict[str, Any]:
        """Generate MCP server configuration from ShellMCP YAML config."""
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
        Add a ShellMCP server to AmazonQ mcp.json configuration.
        
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
                print(f"❌ YAML configuration file not found: {yml_file}")
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
                    print(f"❌ Invalid config location: {config_location}")
                    print(f"Valid options: {', '.join(self.get_mcp_config_paths().keys())}")
                    return 1
            
            # Load or create MCP configuration
            mcp_config = self.load_mcp_config(mcp_config_path)
            
            # Check if server already exists
            if not mcp_config.get("mcpServers"):
                mcp_config["mcpServers"] = {}
            
            if server_name in mcp_config["mcpServers"] and not force:
                print(f"❌ Server '{server_name}' already exists in MCP configuration")
                print("Use --force to overwrite existing configuration")
                return 1
            
            # Generate server configuration
            server_config = self.generate_server_config(yml_config, server_path, python_executable)
            
            # Add server to configuration
            mcp_config["mcpServers"][server_name] = server_config
            
            # Save configuration
            self.save_mcp_config(mcp_config, mcp_config_path)
            
            # Display success information
            print(f"\n✅ Successfully added server '{server_name}' to AmazonQ MCP configuration!")
            print(f"📋 Server Details:")
            print(f"   Name: {server_name}")
            print(f"   Description: {yml_config.server.desc}")
            print(f"   Version: {yml_config.server.version}")
            print(f"   Server file: {server_path}")
            print(f"   Config location: {mcp_config_path}")
            
            if yml_config.tools:
                print(f"   Tools ({len(yml_config.tools)}): {', '.join(yml_config.tools.keys())}")
            
            print(f"\n🚀 Next step: Restart AmazonQ to load the new MCP server")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error adding server: {e}")
            return 1