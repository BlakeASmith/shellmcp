#!/usr/bin/env python3
"""Test the functional LSP server."""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import shellmcp
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_server_creation():
    """Test that the server can be created."""
    print("🧪 Testing functional LSP server creation...")
    
    try:
        from shellmcp.lsp.server import create_server, server
        
        # Test server creation
        lsp_server = create_server()
        print("✅ LSP server created successfully")
        print(f"   Server name: {lsp_server.name}")
        print(f"   Server version: {lsp_server.version}")
        
        # Test that the server instance is the same
        assert lsp_server is server, "Server instances should be the same"
        print("✅ Server instance consistency verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Server creation test failed: {e}")
        return False


def test_completion_function():
    """Test that the completion function exists and is callable."""
    print("\n🧪 Testing completion function...")
    
    try:
        from shellmcp.lsp.server import completion
        
        # Test that completion is callable
        assert callable(completion), "Completion should be callable"
        print("✅ Completion function is callable")
        
        # Test completion with mock params
        class MockParams:
            def __init__(self):
                self.textDocument = type('obj', (object,), {'uri': 'test.yml'})
                self.position = type('obj', (object,), {'line': 0, 'character': 0})
        
        mock_params = MockParams()
        result = completion(mock_params)
        
        # Check that result has expected structure
        assert hasattr(result, 'items'), "Result should have items"
        assert hasattr(result, 'is_incomplete'), "Result should have is_incomplete"
        print(f"✅ Completion returned {len(result.items)} items")
        
        # Check that we have expected completions
        labels = [item.label for item in result.items]
        expected_keys = ["server", "tools", "resources", "prompts", "args"]
        
        for key in expected_keys:
            if key in labels:
                print(f"   ✅ {key} completion found")
            else:
                print(f"   ❌ {key} completion missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Completion function test failed: {e}")
        return False


def test_initialize_function():
    """Test that the initialize function exists and is callable."""
    print("\n🧪 Testing initialize function...")
    
    try:
        from shellmcp.lsp.server import initialize
        
        # Test that initialize is callable
        assert callable(initialize), "Initialize should be callable"
        print("✅ Initialize function is callable")
        
        # Test initialize with mock params
        class MockParams:
            def __init__(self):
                self.processId = None
                self.rootUri = None
                self.capabilities = {}
        
        mock_params = MockParams()
        result = initialize(mock_params)
        
        # Check that result has expected structure
        assert 'capabilities' in result, "Result should have capabilities"
        assert 'completionProvider' in result['capabilities'], "Should have completionProvider"
        print("✅ Initialize returned proper capabilities")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialize function test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Running functional LSP server tests...\n")
    
    tests = [
        test_server_creation,
        test_completion_function,
        test_initialize_function
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