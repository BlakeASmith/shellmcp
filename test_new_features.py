#!/usr/bin/env python3
"""Test script to verify new text resources and direct template prompts functionality."""

from shellmcp.parser import YMLParser
from shellmcp.generator import FastMCPGenerator

def test_text_resources_and_template_prompts():
    """Test that text resources and direct template prompts work correctly."""
    
    # Test configuration with new features
    test_config = """
server:
  name: test-new-features
  desc: Test server for new features
  version: "1.0.0"

resources:
  StaticText:
    uri: "text://static"
    name: "Static Text"
    description: "Static text resource"
    mime_type: "text/plain"
    text: "This is static text content."
  
  DynamicText:
    uri: "text://{{ name }}"
    name: "Dynamic Text"
    description: "Dynamic text resource"
    mime_type: "text/plain"
    text: |
      Hello {{ user }}!
      This is dynamic text for {{ name }}.
      {% if include_time %}
      Generated at: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}
      {% endif %}
    args:
      - name: user
        help: "User name"
        type: string
        default: "User"
      - name: name
        help: "Resource name"
        type: string
        default: "default"
      - name: include_time
        help: "Include timestamp"
        type: boolean
        default: false

prompts:
  SimpleTemplate:
    name: "Simple Template"
    description: "Simple template prompt"
    template: |
      You are a helpful assistant.
      Please help with: {{ request }}
      {% if context %}
      Context: {{ context }}
      {% endif %}
    args:
      - name: request
        help: "User request"
        type: string
      - name: context
        help: "Additional context"
        type: string
        default: ""
  
  AdvancedTemplate:
    name: "Advanced Template"
    description: "Advanced template prompt"
    template: |
      You are a {{ role }} expert.
      {% if task == "analyze" %}
      Please analyze: {{ content }}
      {% elif task == "generate" %}
      Please generate: {{ content }}
      {% else %}
      Please help with: {{ content }}
      {% endif %}
      {% if requirements %}
      Requirements: {{ requirements | join(', ') }}
      {% endif %}
    args:
      - name: role
        help: "Expert role"
        choices: ["technical", "creative", "analytical"]
        default: "technical"
      - name: task
        help: "Task type"
        choices: ["analyze", "generate", "help"]
        default: "help"
      - name: content
        help: "Content to process"
        type: string
      - name: requirements
        help: "List of requirements"
        type: array
        default: []
"""
    
    # Test parsing
    parser = YMLParser()
    config = parser.load_from_string(test_config)
    
    print("✅ Configuration parsed successfully")
    print(f"   Resources: {len(config.resources)}")
    print(f"   Prompts: {len(config.prompts)}")
    
    # Test resource types
    static_text = config.resources['StaticText']
    dynamic_text = config.resources['DynamicText']
    
    assert static_text.text is not None, "StaticText should have text field"
    assert static_text.cmd is None, "StaticText should not have cmd field"
    assert static_text.file is None, "StaticText should not have file field"
    
    assert dynamic_text.text is not None, "DynamicText should have text field"
    assert dynamic_text.cmd is None, "DynamicText should not have cmd field"
    assert dynamic_text.file is None, "DynamicText should not have file field"
    
    print("✅ Resource types validated")
    
    # Test prompt types
    simple_template = config.prompts['SimpleTemplate']
    advanced_template = config.prompts['AdvancedTemplate']
    
    assert simple_template.template is not None, "SimpleTemplate should have template field"
    assert simple_template.cmd is None, "SimpleTemplate should not have cmd field"
    assert simple_template.file is None, "SimpleTemplate should not have file field"
    
    assert advanced_template.template is not None, "AdvancedTemplate should have template field"
    assert advanced_template.cmd is None, "AdvancedTemplate should not have cmd field"
    assert advanced_template.file is None, "AdvancedTemplate should not have file field"
    
    print("✅ Prompt types validated")
    
    # Test template variable extraction
    static_vars = config.get_resource_template_variables('StaticText')
    dynamic_vars = config.get_resource_template_variables('DynamicText')
    simple_vars = config.get_prompt_template_variables('SimpleTemplate')
    advanced_vars = config.get_prompt_template_variables('AdvancedTemplate')
    
    assert len(static_vars) == 0, f"StaticText should have no template variables, got: {static_vars}"
    assert 'user' in dynamic_vars, f"DynamicText should have 'user' variable, got: {dynamic_vars}"
    assert 'name' in dynamic_vars, f"DynamicText should have 'name' variable, got: {dynamic_vars}"
    assert 'request' in simple_vars, f"SimpleTemplate should have 'request' variable, got: {simple_vars}"
    assert 'role' in advanced_vars, f"AdvancedTemplate should have 'role' variable, got: {advanced_vars}"
    assert 'task' in advanced_vars, f"AdvancedTemplate should have 'task' variable, got: {advanced_vars}"
    
    print("✅ Template variable extraction validated")
    
    # Test server generation
    generator = FastMCPGenerator()
    server_code = generator._generate_server_code(config)
    
    print("✅ Server code generated successfully")
    print(f"   Generated code length: {len(server_code)}")
    
    # Verify that new features are in the generated code
    assert "# Use direct text content" in server_code, "Should contain text content logic"
    assert "# Use direct template content" in server_code, "Should contain template content logic"
    assert "@mcp.resource()" in server_code, "Should contain resource decorators"
    assert "@mcp.prompt()" in server_code, "Should contain prompt decorators"
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_text_resources_and_template_prompts()