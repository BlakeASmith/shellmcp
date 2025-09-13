#!/usr/bin/env python3
"""Example script demonstrating how to generate a FastMCP server from YAML configuration."""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import shellmcp
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shellmcp.cli import generate

def main():
    """Generate a FastMCP server from the example configuration."""
    
    # Path to the example configuration
    config_file = "examples/configs/example_config.yml"
    
    print("🚀 Generating FastMCP server from YAML configuration...")
    print(f"📁 Configuration file: {config_file}")
    
    # Generate the server with verbose output
    exit_code = generate(config_file, verbose=True)
    
    if exit_code == 0:
        print("\n✅ Server generation completed successfully!")
        print("\n📋 Generated files:")
        print("   - filesystem_mcp_server.py (FastMCP server)")
        print("   - requirements.txt (Python dependencies)")
        print("   - README.md (Documentation)")
        
        print("\n🚀 To run the generated server:")
        print("   1. cd examples/configs")
        print("   2. pip install -r requirements.txt")
        print("   3. python filesystem_mcp_server.py")
        
        print("\n💡 The server exposes the following tools:")
        print("   - listfiles: List files in a directory")
        print("   - readfile: Read file contents")
        print("   - createdirectory: Create directories")
        print("   - backupdatabase: Database backup with compression")
        print("   - dockercontainer: Manage Docker containers")
        print("   - conditionaldeploy: Environment-specific deployment")
        
    else:
        print(f"\n❌ Server generation failed with exit code {exit_code}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())