#!/usr/bin/env python3
"""Test script for the shellmcp LSP server."""

import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import shellmcp
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shellmcp.lsp.server import create_server


def test_lsp_server():
    """Test the LSP server functionality."""
    print("🧪 Testing shellmcp LSP server...")
    
    try:
        # Create server instance
        server = create_server()
        print("✅ LSP server created successfully")
        
        # Test initialization
        init_params = {
            "processId": None,
            "rootUri": None,
            "capabilities": {
                "textDocument": {
                    "completion": {"dynamicRegistration": True},
                    "hover": {"dynamicRegistration": True}
                }
            }
        }
        
        result = server._initialize(init_params)
        print("✅ LSP server initialized successfully")
        print(f"   Capabilities: {json.dumps(result['capabilities'], indent=2)}")
        
        # Test with a sample YAML document
        sample_yaml = """
server:
  name: test-server
  desc: Test MCP server
  version: "1.0.0"

tools:
  TestTool:
    cmd: echo "Hello {{ name }}"
    desc: Test tool
    args:
      - name: name
        help: Name to greet
        type: string
        default: "World"
"""
        
        # Simulate document open
        doc_item = {
            "uri": "file:///test.yml",
            "languageId": "yaml",
            "version": 1,
            "text": sample_yaml
        }
        
        server._did_open(doc_item)
        print("✅ Document validation completed")
        
        # Test completion
        completion_params = {
            "textDocument": {"uri": "file:///test.yml"},
            "position": {"line": 1, "character": 8}  # After "server:"
        }
        
        completions = server._completion(completion_params)
        print(f"✅ Completion test completed: {len(completions.items)} items")
        
        # Test hover
        hover_params = {
            "textDocument": {"uri": "file:///test.yml"},
            "position": {"line": 1, "character": 2}  # On "server"
        }
        
        hover = server._hover(hover_params)
        if hover:
            print("✅ Hover test completed")
        else:
            print("⚠️  Hover test returned no results")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_lsp_server()
    sys.exit(0 if success else 1)