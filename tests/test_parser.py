"""Tests for YML parser."""

import pytest
import tempfile
from pathlib import Path
from shellmcp.parser import YMLParser


class TestYMLParser:
    """Test YMLParser class."""
    
    def test_load_from_string(self):
        """Test loading configuration from string."""
        yaml_content = """
server:
  name: test-server
  desc: Test server description

tools:
  TestTool:
    cmd: echo {{ message }}
    desc: Test tool
    args:
      - name: message
        help: Message to echo
        default: "Hello World"
"""
        parser = YMLParser()
        config = parser.load_from_string(yaml_content)
        
        assert config.server.name == "test-server"
        assert config.server.desc == "Test server description"
        assert "TestTool" in config.tools
        assert config.tools["TestTool"].cmd == "echo {{ message }}"
    
    def test_load_from_file(self):
        """Test loading configuration from file."""
        yaml_content = """
server:
  name: test-server
  desc: Test server description

tools:
  TestTool:
    cmd: echo {{ message }}
    desc: Test tool
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name
        
        try:
            parser = YMLParser()
            config = parser.load_from_file(temp_path)
            
            assert config.server.name == "test-server"
            assert config.server.desc == "Test server description"
        finally:
            Path(temp_path).unlink()
    
    def test_load_from_file_not_found(self):
        """Test loading from non-existent file."""
        parser = YMLParser()
        with pytest.raises(FileNotFoundError):
            parser.load_from_file("non_existent_file.yml")
    
    def test_load_from_dict(self):
        """Test loading configuration from dictionary."""
        data = {
            "server": {
                "name": "test-server",
                "desc": "Test server description"
            },
            "tools": {
                "TestTool": {
                    "cmd": "echo {{ message }}",
                    "desc": "Test tool"
                }
            }
        }
        
        parser = YMLParser()
        config = parser.load_from_dict(data)
        
        assert config.server.name == "test-server"
        assert "TestTool" in config.tools
    
    def test_invalid_yaml(self):
        """Test handling of invalid YAML."""
        parser = YMLParser()
        with pytest.raises(ValueError, match="Invalid YAML configuration"):
            parser.load_from_string("invalid: yaml: content: [")
    
    def test_validate_all_templates(self):
        """Test template validation for all tools."""
        yaml_content = """
server:
  name: test-server
  desc: Test server description

tools:
  ValidTool:
    cmd: echo {{ message }}
    desc: Valid tool
    
  InvalidTool:
    cmd: echo {{ unclosed_template
    desc: Invalid tool
"""
        parser = YMLParser()
        config = parser.load_from_string(yaml_content)
        
        validation_results = parser.validate_all_templates()
        assert validation_results["ValidTool"] is True
        assert validation_results["InvalidTool"] is False
    
    def test_get_tool_template_variables(self):
        """Test extracting template variables from tools."""
        yaml_content = """
server:
  name: test-server
  desc: Test server description

tools:
  SimpleTool:
    cmd: echo {{ message }}
    desc: Simple tool
    
  ComplexTool:
    cmd: |
      {% if verbose %}
      echo "Verbose: {{ message }}"
      {% else %}
      echo {{ message }}
      {% endif %}
    desc: Complex tool
"""
        parser = YMLParser()
        config = parser.load_from_string(yaml_content)
        
        simple_vars = parser.get_tool_template_variables("SimpleTool")
        assert "message" in simple_vars
        
        complex_vars = parser.get_tool_template_variables("ComplexTool")
        assert "verbose" in complex_vars
        assert "message" in complex_vars
    
    def test_get_resolved_tool_arguments(self):
        """Test getting resolved tool arguments."""
        yaml_content = """
server:
  name: test-server
  desc: Test server description

args:
  FilePath:
    help: Path to a file
    type: string
    pattern: "^[^\\0]+$"

tools:
  TestTool:
    cmd: cat {{ file }}
    desc: Read file
    args:
      - name: file
        help: File to read
        ref: FilePath
      - name: verbose
        help: Verbose output
        type: boolean
        default: false
"""
        parser = YMLParser()
        config = parser.load_from_string(yaml_content)
        
        resolved_args = parser.get_resolved_tool_arguments("TestTool")
        assert len(resolved_args) == 2
        
        # First argument should be resolved from reference
        file_arg = next(arg for arg in resolved_args if arg.name == "file")
        assert file_arg.help == "Path to a file"
        assert file_arg.type == "string"
        assert file_arg.pattern == "^[^\\0]+$"
        assert file_arg.ref is None  # Should be resolved
        
        # Second argument should be as defined
        verbose_arg = next(arg for arg in resolved_args if arg.name == "verbose")
        assert verbose_arg.help == "Verbose output"
        assert verbose_arg.type == "boolean"
        assert verbose_arg.default is False
    
    def test_validate_argument_consistency(self):
        """Test validation of argument consistency."""
        yaml_content = """
server:
  name: test-server
  desc: Test server description

tools:
  ConsistentTool:
    cmd: echo {{ message }}
    desc: Consistent tool
    args:
      - name: message
        help: Message to echo
        
  InconsistentTool:
    cmd: echo {{ message }} {{ extra }}
    desc: Inconsistent tool
    args:
      - name: message
        help: Message to echo
        # Missing 'extra' argument
"""
        parser = YMLParser()
        config = parser.load_from_string(yaml_content)
        
        issues = parser.validate_argument_consistency()
        assert "ConsistentTool" not in issues
        assert "InconsistentTool" in issues
        assert "extra" in issues["InconsistentTool"]
    
    def test_get_server_info(self):
        """Test getting server information."""
        yaml_content = """
server:
  name: test-server
  desc: Test server description
  version: "2.0.0"
  env:
    NODE_ENV: production
    DEBUG: "false"

args:
  FilePath:
    help: Path to a file

tools:
  Tool1:
    cmd: echo {{ message }}
    desc: Tool 1
  Tool2:
    cmd: ls {{ path }}
    desc: Tool 2
"""
        parser = YMLParser()
        config = parser.load_from_string(yaml_content)
        
        server_info = parser.get_server_info()
        assert server_info["name"] == "test-server"
        assert server_info["description"] == "Test server description"
        assert server_info["version"] == "2.0.0"
        assert server_info["environment_variables"]["NODE_ENV"] == "production"
        assert server_info["tools_count"] == 2
        assert server_info["reusable_args_count"] == 1
    
    def test_get_tools_summary(self):
        """Test getting tools summary."""
        yaml_content = """
server:
  name: test-server
  desc: Test server description

tools:
  TestTool:
    cmd: echo {{ message }}
    desc: Test tool
    help-cmd: echo --help
    args:
      - name: message
        help: Message to echo
        default: "Hello"
    env:
      DEBUG: "true"
"""
        parser = YMLParser()
        config = parser.load_from_string(yaml_content)
        
        summary = parser.get_tools_summary()
        assert "TestTool" in summary
        
        tool_info = summary["TestTool"]
        assert tool_info["description"] == "Test tool"
        assert tool_info["command"] == "echo {{ message }}"
        assert tool_info["help_command"] == "echo --help"
        assert tool_info["arguments_count"] == 1
        assert "message" in tool_info["template_variables"]
        assert tool_info["environment_variables"]["DEBUG"] == "true"
        assert tool_info["has_valid_template"] is True