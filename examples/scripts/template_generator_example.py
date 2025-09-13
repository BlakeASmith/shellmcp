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
        print("   - README.md (Documentation with Amazon Q CLI instructions)")
        print("   - amazon-q-config.json (Amazon Q CLI configuration)")
        
        print("\n🚀 Key improvements with template-based generation:")
        print("   ✨ Clean, maintainable Jinja2 templates")
        print("   ✨ Custom filters for type conversion")
        print("   ✨ Automatic Amazon Q CLI configuration generation")
        print("   ✨ Virtual environment best practices")
        print("   ✨ Better code formatting and structure")
        
        print("\n🔧 Amazon Q CLI Integration Features:")
        print("   ☁️  AWS-native AI assistance")
        print("   🔐 Enterprise-grade security and compliance")
        print("   🚀 Enhanced productivity with AWS context")
        print("   🔗 Multi-service integration with AWS tools")
        print("   📊 Advanced analytics and insights")
        
        print("\n💡 Next steps:")
        print("   1. Review the generated amazon-q-config.json file")
        print("   2. Install Amazon Q CLI")
        print("   3. Configure AWS credentials")
        print("   4. Copy the configuration to Amazon Q CLI")
        print("   5. Start Amazon Q CLI and test your tools!")
        
    else:
        print(f"\n❌ Server generation failed with exit code {exit_code}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())