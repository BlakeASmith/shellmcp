#!/usr/bin/env python3
"""Example script demonstrating the template-based FastMCP server generator with MCP configuration."""

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
        print("   - README.md (Documentation with MCP config instructions)")
        print("   - mcp.json (MCP client configuration)")
        
        print("\n🚀 Key improvements with template-based generation:")
        print("   ✨ Clean, maintainable Jinja2 templates")
        print("   ✨ Custom filters for type conversion")
        print("   ✨ Automatic MCP configuration generation")
        print("   ✨ Platform-specific installation instructions")
        print("   ✨ Better code formatting and structure")
        
        print("\n⚙️  MCP Configuration Features:")
        print("   📱 Claude Desktop (macOS/Windows/Linux)")
        print("   🔧 Cursor Editor integration")
        print("   💻 Visual Studio Code with MCP extension")
        print("   🖥️  Neovim with MCP plugin")
        print("   ⚡ Helix Editor support")
        print("   🔧 Generic MCP client compatibility")
        
        print("\n💡 Next steps:")
        print("   1. Review the generated mcp.json file")
        print("   2. Copy the configuration to your editor")
        print("   3. Follow the platform-specific instructions in README.md")
        print("   4. Test your MCP tools in your preferred editor!")
        
    else:
        print(f"\n❌ Server generation failed with exit code {exit_code}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())