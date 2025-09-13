#!/usr/bin/env python3
"""Test script to verify file-based resources and prompts functionality."""

import tempfile
import os
from pathlib import Path
from shellmcp.parser import YMLParser
from shellmcp.generator import FastMCPGenerator

def test_file_based_resources_prompts():
    """Test that file-based resources and prompts work correctly."""
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        docs_dir = temp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "api.md").write_text("# API Documentation\nThis is test API docs.")
        
        prompts_dir = temp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "test_prompt.txt").write_text("This is a test prompt with {{ variable }}.")
        
        # Create test configuration
        test_config = """
server:
  name: test-server
  desc: Test server for file-based resources and prompts
  version: "1.0.0"

resources:
  TestDoc:
    uri: "test://doc"
    name: "Test Documentation"
    description: "Test documentation from file"
    mime_type: "text/markdown"
    file: "docs/api.md"
    
  DynamicDoc:
    uri: "test://doc/{{ doc_name }}"
    name: "Dynamic Documentation"
    description: "Dynamic documentation from file"
    mime_type: "text/markdown"
    file: "docs/{{ doc_name }}.md"
    args:
      - name: doc_name
        help: "Document name"
        default: "api"

prompts:
  TestPrompt:
    name: "Test Prompt"
    description: "Test prompt from file"
    file: "prompts/test_prompt.txt"
    args:
      - name: variable
        help: "Test variable"
        default: "test_value"
"""
        
        # Test parsing
        parser = YMLParser()
        config = parser.load_from_string(test_config)
        
        print("✅ Configuration parsed successfully")
        print(f"   Resources: {len(config.resources)}")
        print(f"   Prompts: {len(config.prompts)}")
        
        # Test that file-based resources don't have template variables
        test_doc_vars = config.get_resource_template_variables("TestDoc")
        print(f"   TestDoc template variables: {test_doc_vars}")
        assert len(test_doc_vars) == 0, "File-based resource should have no template variables"
        
        # Test that file-based prompts don't have template variables from cmd
        test_prompt_vars = config.get_prompt_template_variables("TestPrompt")
        print(f"   TestPrompt template variables: {test_prompt_vars}")
        assert len(test_prompt_vars) == 0, "File-based prompt should have no template variables from cmd"
        
        # Test that dynamic file paths work
        dynamic_doc_vars = config.get_resource_template_variables("DynamicDoc")
        print(f"   DynamicDoc template variables: {dynamic_doc_vars}")
        print(f"   DynamicDoc file field: {repr(config.resources['DynamicDoc'].file)}")
        assert "doc_name" in dynamic_doc_vars, f"Dynamic file path should have template variables, got: {dynamic_doc_vars}"
        
        # Test server generation
        generator = FastMCPGenerator()
        server_code = generator._generate_server_code(config)
        
        print("✅ Server code generated successfully")
        print(f"   Generated code length: {len(server_code)}")
        
        # Verify that file-based resources and prompts are in the generated code
        assert "# Read from file" in server_code, "Should contain file reading logic"
        assert "@mcp.resource()" in server_code, "Should contain resource decorators"
        assert "@mcp.prompt()" in server_code, "Should contain prompt decorators"
        
        print("✅ All tests passed!")

if __name__ == "__main__":
    test_file_based_resources_prompts()