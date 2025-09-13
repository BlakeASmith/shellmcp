#!/usr/bin/env python3
"""Example script demonstrating Amazon Q CLI setup with FastMCP servers."""

import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import shellmcp
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shellmcp.generator import FastMCPGenerator
from shellmcp.parser import YMLParser

def setup_amazon_q_integration(config_file: str, output_dir: str = None):
    """Set up Amazon Q CLI integration for a FastMCP server."""
    
    print("🚀 Setting up Amazon Q CLI integration for FastMCP server")
    print(f"📁 Configuration file: {config_file}")
    
    # Load configuration
    parser = YMLParser()
    config = parser.load_from_file(config_file)
    
    if output_dir is None:
        output_dir = Path(config_file).parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate Amazon Q configuration
    generator = FastMCPGenerator()
    server_file = output_dir / f"{config.server.name.replace('-', '_')}_server.py"
    
    amazon_q_config_file = generator.generate_amazon_q_config(
        config,
        str(output_dir / "amazon-q-config.json"),
        str(server_file),
        str(output_dir)
    )
    
    print(f"✅ Amazon Q configuration generated: {amazon_q_config_file}")
    
    # Show setup instructions
    print(f"\n📋 Amazon Q CLI Setup Instructions:")
    
    print(f"\n1. Install Amazon Q CLI:")
    print(f"   curl -sSL https://amazon-q-cli.s3.amazonaws.com/install.sh | bash")
    
    print(f"\n2. Configure AWS credentials:")
    print(f"   aws configure")
    print(f"   # or use AWS SSO")
    print(f"   aws sso login")
    
    print(f"\n3. Copy Amazon Q configuration:")
    if sys.platform == "win32":
        config_location = "%APPDATA%\\Amazon\\Q\\cli-config.json"
    else:
        config_location = "~/.config/amazon-q/cli-config.json"
    
    print(f"   cp {amazon_q_config_file} {config_location}")
    
    print(f"\n4. Start Amazon Q CLI:")
    print(f"   amazon-q")
    
    print(f"\n5. Use your MCP tools:")
    print(f"   @tools listfiles --path /home/user/projects")
    print(f"   @tools backupdatabase --user admin --password secret --database myapp")
    
    # Show the configuration content
    with open(amazon_q_config_file, 'r') as f:
        config_content = json.load(f)
    
    print(f"\n📄 Generated Amazon Q Configuration:")
    print(json.dumps(config_content, indent=2))
    
    return amazon_q_config_file

def main():
    """Main function to demonstrate Amazon Q CLI setup."""
    
    # Example configuration file
    config_file = "examples/configs/example_config.yml"
    
    if not Path(config_file).exists():
        print(f"❌ Configuration file {config_file} not found")
        print("Please ensure the example configuration exists")
        return 1
    
    try:
        amazon_q_config = setup_amazon_q_integration(config_file)
        print(f"\n✅ Amazon Q CLI integration setup completed successfully!")
        print(f"📁 Configuration file: {amazon_q_config}")
        return 0
    except Exception as e:
        print(f"\n❌ Amazon Q CLI setup failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())