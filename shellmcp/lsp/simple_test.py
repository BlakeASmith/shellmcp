#!/usr/bin/env python3
"""Simple test for the shellmcp LSP server components."""

import json
import sys
from pathlib import Path

def test_schema_loading():
    """Test that the JSON schema loads correctly."""
    print("🧪 Testing JSON schema loading...")
    
    try:
        schema_path = Path(__file__).parent / "schema.json"
        with open(schema_path, "r") as f:
            schema = json.load(f)
        
        print("✅ JSON schema loaded successfully")
        print(f"   Schema title: {schema.get('title', 'N/A')}")
        print(f"   Required fields: {schema.get('required', [])}")
        
        # Check that all expected properties are present
        properties = schema.get("properties", {})
        expected_props = ["server", "args", "tools", "resources", "prompts"]
        
        for prop in expected_props:
            if prop in properties:
                print(f"   ✅ {prop} property found")
            else:
                print(f"   ❌ {prop} property missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Schema loading failed: {e}")
        return False


def test_example_config():
    """Test that the example configuration is valid YAML."""
    print("\n🧪 Testing example configuration...")
    
    try:
        import yaml
        
        config_path = Path(__file__).parent / "example-config.yml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        print("✅ Example configuration loaded successfully")
        print(f"   Server name: {config.get('server', {}).get('name', 'N/A')}")
        print(f"   Tools count: {len(config.get('tools', {}))}")
        print(f"   Resources count: {len(config.get('resources', {}))}")
        print(f"   Prompts count: {len(config.get('prompts', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Example configuration test failed: {e}")
        return False


def test_cli_integration():
    """Test that the CLI can import the LSP module."""
    print("\n🧪 Testing CLI integration...")
    
    try:
        # Add the parent directory to the path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from shellmcp.cli import lsp
        
        print("✅ CLI LSP command imported successfully")
        print(f"   LSP function: {lsp.__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Running shellmcp LSP server tests...\n")
    
    tests = [
        test_schema_loading,
        test_example_config,
        test_cli_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)