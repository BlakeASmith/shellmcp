"""Tests for AmazonQ installer functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from shellmcp.amazonq_installer import AmazonQInstaller
from shellmcp.models import ServerConfig, YMLConfig


class TestAmazonQInstaller:
    """Test cases for AmazonQInstaller."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.installer = AmazonQInstaller()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_mcp_config_paths(self):
        """Test MCP configuration path detection."""
        paths = self.installer.get_mcp_config_paths()
        
        assert 'global' in paths
        assert 'local' in paths
        assert 'user_config' in paths
        
        # Check that paths are Path objects
        for path in paths.values():
            assert isinstance(path, Path)
    
    def test_create_default_mcp_config(self):
        """Test default MCP configuration creation."""
        config = self.installer.create_default_mcp_config(self.temp_dir / "test.json")
        
        assert "mcpServers" in config
        assert config["mcpServers"] == {}
    
    def test_load_mcp_config_existing(self):
        """Test loading existing MCP configuration."""
        # Create test config file
        config_path = self.temp_dir / "mcp.json"
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python3",
                    "args": ["test.py"]
                }
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Load configuration
        loaded_config = self.installer.load_mcp_config(config_path)
        
        assert loaded_config == test_config
    
    def test_load_mcp_config_new(self):
        """Test creating new MCP configuration when file doesn't exist."""
        config_path = self.temp_dir / "nonexistent.json"
        
        config = self.installer.load_mcp_config(config_path)
        
        assert "mcpServers" in config
        assert config["mcpServers"] == {}
    
    def test_save_mcp_config(self):
        """Test saving MCP configuration."""
        config_path = self.temp_dir / "test.json"
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python3",
                    "args": ["test.py"]
                }
            }
        }
        
        self.installer.save_mcp_config(test_config, config_path)
        
        assert config_path.exists()
        
        with open(config_path, 'r') as f:
            saved_config = json.load(f)
        
        assert saved_config == test_config
    
    def test_generate_server_config(self):
        """Test server configuration generation."""
        # Create test YML config
        yml_config = YMLConfig(
            server=ServerConfig(
                name="test-server",
                desc="Test server",
                version="1.0.0"
            )
        )
        
        server_path = "/path/to/server.py"
        config = self.installer.generate_server_config(yml_config, server_path)
        
        assert config["command"] == "python3"
        assert config["args"] == [server_path]
        assert "env" in config
        assert "PYTHONPATH" in config["env"]
    
    @patch('shellmcp.amazonq_installer.YMLParser')
    def test_install_server_basic(self, mock_parser):
        """Test basic server installation."""
        # Mock YML config
        mock_config = YMLConfig(
            server=ServerConfig(
                name="test-server",
                desc="Test server",
                version="1.0.0"
            )
        )
        mock_parser.return_value.load_from_file.return_value = mock_config
        
        # Create test files
        yml_file = self.temp_dir / "test.yml"
        server_file = self.temp_dir / "test_server.py"
        
        yml_file.write_text("test: config")
        server_file.write_text("print('test server')")
        
        # Mock config path methods
        with patch.object(self.installer, 'get_mcp_config_paths') as mock_paths, \
             patch.object(self.installer, 'load_mcp_config') as mock_load, \
             patch.object(self.installer, 'save_mcp_config') as mock_save:
            
            mock_paths.return_value = {'local': self.temp_dir / 'mcp.json'}
            mock_load.return_value = {"mcpServers": {}}
            
            result = self.installer.install_server(
                str(yml_file),
                str(server_file),
                config_location="local"
            )
            
            assert result == 0
            mock_save.assert_called_once()
    
    @patch('shellmcp.amazonq_installer.YMLParser')
    def test_install_server_already_exists(self, mock_parser):
        """Test server installation when server already exists."""
        # Mock YML config
        mock_config = YMLConfig(
            server=ServerConfig(
                name="existing-server",
                desc="Existing server",
                version="1.0.0"
            )
        )
        mock_parser.return_value.load_from_file.return_value = mock_config
        
        # Create test files
        yml_file = self.temp_dir / "test.yml"
        server_file = self.temp_dir / "test_server.py"
        
        yml_file.write_text("test: config")
        server_file.write_text("print('test server')")
        
        # Mock config with existing server
        existing_config = {
            "mcpServers": {
                "existing-server": {
                    "command": "python3",
                    "args": ["existing.py"]
                }
            }
        }
        
        with patch.object(self.installer, 'get_mcp_config_paths') as mock_paths, \
             patch.object(self.installer, 'load_mcp_config') as mock_load:
            
            mock_paths.return_value = {'local': self.temp_dir / 'mcp.json'}
            mock_load.return_value = existing_config
            
            result = self.installer.install_server(
                str(yml_file),
                str(server_file),
                config_location="local",
                force=False
            )
            
            assert result == 1  # Should fail due to existing server
    
    def test_list_installed_servers_no_config(self):
        """Test listing servers when no config exists."""
        with patch.object(self.installer, 'find_existing_mcp_config') as mock_find:
            mock_find.return_value = None
            
            result = self.installer.list_installed_servers()
            
            assert result == 1
    
    def test_list_installed_servers_with_config(self):
        """Test listing servers with existing config."""
        test_config = {
            "mcpServers": {
                "server1": {
                    "command": "python3",
                    "args": ["server1.py"]
                },
                "server2": {
                    "command": "python3",
                    "args": ["server2.py"]
                }
            }
        }
        
        config_path = self.temp_dir / "mcp.json"
        
        with patch.object(self.installer, 'find_existing_mcp_config') as mock_find, \
             patch.object(self.installer, 'load_mcp_config') as mock_load:
            
            mock_find.return_value = config_path
            mock_load.return_value = test_config
            
            result = self.installer.list_installed_servers()
            
            assert result == 0
    
    def test_uninstall_server_not_found(self):
        """Test uninstalling a non-existent server."""
        config_path = self.temp_dir / "mcp.json"
        
        with patch.object(self.installer, 'find_existing_mcp_config') as mock_find, \
             patch.object(self.installer, 'load_mcp_config') as mock_load:
            
            mock_find.return_value = config_path
            mock_load.return_value = {"mcpServers": {}}
            
            result = self.installer.uninstall_server("nonexistent-server")
            
            assert result == 1