#!/usr/bin/env python3
"""
Simple example demonstrating ShellMCP MCP JSON generation.

This script shows how to:
1. Create a ShellMCP server configuration
2. Generate the server code
3. Generate MCP JSON configuration for AmazonQ
"""

import subprocess
import sys
from pathlib import Path
from shellmcp.amazonq_installer import generate_mcp_json


def create_simple_config():
    """Create a simple ShellMCP configuration."""
    config_content = """
server:
  name: "simple-tools"
  desc: "Simple example tools for AmazonQ"
  version: "1.0.0"

tools:
  hello_world:
    cmd: "echo 'Hello from ShellMCP!'"
    desc: "Simple hello world command"
  
  current_time:
    cmd: "date"
    desc: "Get current date and time"
    help_cmd: "date --help"
"""
    return config_content.strip()


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False


def main():
    """Main example workflow."""
    print("🚀 ShellMCP MCP JSON Generation Example")
    print("=" * 45)
    
    # Create temporary directory for example
    temp_dir = Path("example_output")
    temp_dir.mkdir(exist_ok=True)
    
    config_file = temp_dir / "simple_tools.yml"
    
    print(f"📁 Working in directory: {temp_dir}")
    
    # Step 1: Create configuration file
    print("\n📝 Step 1: Creating ShellMCP configuration...")
    config_content = create_simple_config()
    config_file.write_text(config_content)
    print(f"✅ Created configuration: {config_file}")
    
    # Step 2: Validate configuration
    print("\n🔍 Step 2: Validating configuration...")
    if not run_command(f"python3 -m shellmcp.cli validate {config_file} --verbose", 
                      "Configuration validation"):
        print("❌ Configuration validation failed")
        return 1
    
    # Step 3: Generate server
    print("\n🏗️  Step 3: Generating FastMCP server...")
    if not run_command(f"python3 -m shellmcp.cli generate {config_file} --output-dir {temp_dir}/output --verbose", 
                      "Server generation"):
        print("❌ Server generation failed")
        return 1
    
    # Step 4: Generate MCP JSON
    print("\n🔧 Step 4: Generating MCP JSON configuration...")
    
    # Find the generated server file
    output_dir = temp_dir / "output"
    server_files = list(output_dir.glob("*_server.py"))
    
    if not server_files:
        print("❌ No server file found in output directory")
        return 1
    
    server_file = server_files[0]
    print(f"📄 Found server file: {server_file}")
    
    # Generate MCP JSON to stdout
    print("\n📋 Generated MCP JSON configuration:")
    if not run_command(f"python3 -m shellmcp.cli mcp-json {config_file}", 
                      "MCP JSON generation"):
        print("❌ MCP JSON generation failed")
        return 1
    
    # Generate MCP JSON to file
    mcp_json_file = temp_dir / "mcp.json"
    if not run_command(f"python3 -m shellmcp.cli mcp-json {config_file} --output-file {mcp_json_file}", 
                      "MCP JSON file generation"):
        print("❌ MCP JSON file generation failed")
        return 1
    
    print(f"\n📄 MCP JSON saved to: {mcp_json_file}")
    
    print("\n🎉 Example completed successfully!")
    print("\n📖 Next steps:")
    print("   1. Copy the generated JSON to your AmazonQ mcp.json file")
    print("   2. Restart AmazonQ to load your new MCP server")
    print(f"   3. Your server will be available as 'simple-tools' in AmazonQ")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())