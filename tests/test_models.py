"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError
from shellmcp.models import (
    ArgumentDefinition, ToolArgument, ServerConfig, ToolConfig, YMLConfig
)


# ArgumentDefinition tests

def test_valid_argument_definition():
    """Test creating a valid argument definition."""
    arg = ArgumentDefinition(
        help="Test argument",
        type="string",
        default="test",
        choices=["test", "example"],
        pattern="^[a-z]+$"
    )
    assert arg.help == "Test argument"
    assert arg.type == "string"
    assert arg.default == "test"
    assert arg.choices == ["test", "example"]
    assert arg.pattern == "^[a-z]+$"


def test_argument_definition_invalid_regex_pattern():
    """Test validation of invalid regex pattern."""
    with pytest.raises(ValidationError) as exc_info:
        ArgumentDefinition(
            help="Test argument",
            pattern="[invalid regex"
        )
    assert "Invalid regex pattern" in str(exc_info.value)


def test_argument_definition_default_type():
    """Test default type is string."""
    arg = ArgumentDefinition(help="Test argument")
    assert arg.type == "string"


# ToolArgument tests

def test_valid_tool_argument():
    """Test creating a valid tool argument."""
    arg = ToolArgument(
        name="test_arg",
        help="Test argument",
        type="boolean",
        default=True
    )
    assert arg.name == "test_arg"
    assert arg.help == "Test argument"
    assert arg.type == "boolean"
    assert arg.default is True


def test_tool_argument_ref_with_other_properties():
    """Test that ref can be used with other properties (validation removed)."""
    # This should work now since we removed the validation
    arg = ToolArgument(
        name="test_arg",
        help="Test argument",
        ref="SomeRef",
        type="string"
    )
    assert arg.ref == "SomeRef"
    assert arg.type == "string"


def test_tool_argument_valid_ref_only():
    """Test that ref can be used alone."""
    arg = ToolArgument(
        name="test_arg",
        help="Test argument",
        ref="SomeRef"
    )
    assert arg.ref == "SomeRef"
    assert arg.type == "string"  # default value


# ServerConfig tests

def test_valid_server_config():
    """Test creating a valid server config."""
    server = ServerConfig(
        name="test-server",
        desc="Test server description"
    )
    assert server.name == "test-server"
    assert server.desc == "Test server description"
    assert server.version == "1.0.0"  # default


def test_server_config_with_env():
    """Test server config with environment variables."""
    server = ServerConfig(
        name="test-server",
        desc="Test server description",
        env={"NODE_ENV": "production", "DEBUG": "false"}
    )
    assert server.env["NODE_ENV"] == "production"
    assert server.env["DEBUG"] == "false"


# ToolConfig tests

def test_valid_tool_config():
    """Test creating a valid tool config."""
    tool = ToolConfig(
        cmd="echo {{ message }}",
        desc="Echo a message"
    )
    assert tool.cmd == "echo {{ message }}"
    assert tool.desc == "Echo a message"
    assert tool.help_cmd is None


def test_tool_config_with_help_cmd_alias():
    """Test tool config with help-cmd alias."""
    tool = ToolConfig(
        cmd="ls {{ path }}",
        desc="List files",
        help_cmd="ls --help"
    )
    assert tool.help_cmd == "ls --help"


def test_tool_config_with_args():
    """Test tool config with arguments."""
    args = [
        ToolArgument(name="path", help="Directory path", default="."),
        ToolArgument(name="verbose", help="Verbose output", type="boolean", default=False)
    ]
    tool = ToolConfig(
        cmd="ls {{ path }} {% if verbose %}-v{% endif %}",
        desc="List files with optional verbose output",
        args=args
    )
    assert len(tool.args) == 2
    assert tool.args[0].name == "path"
    assert tool.args[1].type == "boolean"


# YMLConfig tests

def test_valid_yml_config():
    """Test creating a valid YML config."""
    config = YMLConfig(
        server=ServerConfig(name="test", desc="Test server"),
        tools={
            "TestTool": ToolConfig(
                cmd="echo {{ message }}",
                desc="Test tool"
            )
        }
    )
    assert config.server.name == "test"
    assert "TestTool" in config.tools


def test_yml_config_duplicate_tool_names():
    """Test that duplicate tool names are handled by dict keys."""
    # Python dicts automatically handle duplicate keys by keeping the last one
    tools_dict = {
        "TestTool": ToolConfig(cmd="echo 1", desc="Tool 1"),
        "TestTool": ToolConfig(cmd="echo 2", desc="Tool 2")  # This overwrites the first
    }
    config = YMLConfig(
        server=ServerConfig(name="test", desc="Test server"),
        tools=tools_dict
    )
    # Should have only one tool with the last definition
    assert len(config.tools) == 1
    assert config.tools["TestTool"].desc == "Tool 2"


def test_yml_config_duplicate_argument_names_in_tool():
    """Test validation of duplicate argument names within a tool."""
    with pytest.raises(ValidationError) as exc_info:
        YMLConfig(
            server=ServerConfig(name="test", desc="Test server"),
            tools={
                "TestTool": ToolConfig(
                    cmd="echo {{ msg1 }} {{ msg2 }}",
                    desc="Test tool",
                    args=[
                        ToolArgument(name="msg1", help="Message 1"),
                        ToolArgument(name="msg1", help="Message 1 duplicate")  # Duplicate name
                    ]
                )
            }
        )
    assert "Argument names must be unique within tool" in str(exc_info.value)


def test_yml_config_invalid_argument_reference():
    """Test validation of invalid argument reference."""
    with pytest.raises(ValidationError) as exc_info:
        YMLConfig(
            server=ServerConfig(name="test", desc="Test server"),
            tools={
                "TestTool": ToolConfig(
                    cmd="echo {{ message }}",
                    desc="Test tool",
                    args=[
                        ToolArgument(name="message", help="Message", ref="NonExistentRef")
                    ]
                )
            }
        )
    assert "references undefined argument 'NonExistentRef'" in str(exc_info.value)


def test_yml_config_valid_argument_reference():
    """Test valid argument reference."""
    config = YMLConfig(
        server=ServerConfig(name="test", desc="Test server"),
        args={
            "MessageArg": ArgumentDefinition(help="A message argument")
        },
        tools={
            "TestTool": ToolConfig(
                cmd="echo {{ message }}",
                desc="Test tool",
                args=[
                    ToolArgument(name="message", help="Message", ref="MessageArg")
                ]
            )
        }
    )
    assert config.args["MessageArg"].help == "A message argument"
    assert config.tools["TestTool"].args[0].ref == "MessageArg"


def test_yml_config_get_resolved_arguments():
    """Test getting resolved arguments."""
    config = YMLConfig(
        server=ServerConfig(name="test", desc="Test server"),
        args={
            "FilePath": ArgumentDefinition(
                help="Path to a file",
                type="string",
                pattern="^[^\\0]+$"
            )
        },
        tools={
            "TestTool": ToolConfig(
                cmd="cat {{ file }}",
                desc="Read file",
                args=[
                    ToolArgument(name="file", help="File to read", ref="FilePath")
                ]
            )
        }
    )
    
    resolved_args = config.get_resolved_arguments("TestTool")
    assert len(resolved_args) == 1
    assert resolved_args[0].name == "file"
    assert resolved_args[0].help == "Path to a file"
    assert resolved_args[0].type == "string"
    assert resolved_args[0].pattern == "^[^\\0]+$"


def test_yml_config_get_resolved_arguments_mixed():
    """Test getting resolved arguments with mixed ref and direct args."""
    config = YMLConfig(
        server=ServerConfig(name="test", desc="Test server"),
        args={
            "FilePath": ArgumentDefinition(help="Path to a file")
        },
        tools={
            "TestTool": ToolConfig(
                cmd="cp {{ source }} {{ dest }}",
                desc="Copy file",
                args=[
                    ToolArgument(name="source", help="Source file", ref="FilePath"),
                    ToolArgument(name="dest", help="Destination", type="string", default=".")
                ]
            )
        }
    )
    
    resolved_args = config.get_resolved_arguments("TestTool")
    assert len(resolved_args) == 2
    assert resolved_args[0].name == "source"
    assert resolved_args[0].ref is None  # Should be resolved
    assert resolved_args[1].name == "dest"
    assert resolved_args[1].default == "."
