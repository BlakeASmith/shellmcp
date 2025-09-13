#!/usr/bin/env python3
"""Example script demonstrating the template-based FastMCP server generator."""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import shellmcp
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shellmcp.cli import generate

def main():
    """Generate a FastMCP server using the template-based generator."""
    
    # Path to the example configuration
    config_file = "examples/configs/example_config.yml"
    
    print("🚀 Generating FastMCP server using Jinja2 templates...")
    print(f"📁 Configuration file: {config_file}")
    
    # Generate the server with verbose output
    exit_code = generate(config_file, verbose=True)
    
    if exit_code == 0:
        print("\n✅ Template-based server generation completed successfully!")
        
        print("\n📋 Generated files:")
        print("   - filesystem_mcp_server.py (FastMCP server)")
        print("   - requirements.txt (Python dependencies)")
        print("   - README.md (Documentation)")
        
        print("\n🚀 Key improvements with template-based generation:")
        print("   ✨ Clean, maintainable Jinja2 templates")
        print("   ✨ Custom filters for type conversion")
        print("   ✨ Virtual environment best practices")
        print("   ✨ Better code formatting and structure")
        print("   ✨ Comprehensive error handling")
        
        print("\n💡 Next steps:")
        print("   1. Set up virtual environment: python3 -m venv venv")
        print("   2. Activate virtual environment: source venv/bin/activate")
        print("   3. Install dependencies: pip install -r requirements.txt")
        print("   4. Run the server: python filesystem_mcp_server.py")
        print("   5. Connect with your preferred MCP client!")
        
    else:
        print(f"\n❌ Server generation failed with exit code {exit_code}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())