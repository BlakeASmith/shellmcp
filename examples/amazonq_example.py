#!/usr/bin/env python3
"""
Example script demonstrating ShellMCP AmazonQ integration.

This script shows how to:
1. Create a ShellMCP server configuration
2. Generate the server code
3. Install it to AmazonQ MCP configuration
"""

import tempfile
import subprocess
import sys
from pathlib import Path


def create_example_config():
    """Create an example ShellMCP configuration."""
    config_content = """
server:
  name: "example-tools"
  desc: "Example tools for AmazonQ integration"
  version: "1.0.0"

args:
  path_arg:
    help: "Directory path"
    type: string
    default: "."

tools:
  list_files:
    cmd: "ls -la {{path}}"
    desc: "List files in a directory"
    args:
      - name: path
        ref: path_arg
  
  get_system_info:
    cmd: "uname -a && whoami && pwd"
    desc: "Get basic system information"
    help_cmd: "uname --help"

resources:
  system_info:
    uri: "file:///tmp/system-info.txt"
    name: "System Information"
    description: "Current system status and info"
    cmd: "uname -a && df -h && free -h"
    mime_type: "text/plain"

prompts:
  system_analysis:
    name: "System Analysis Assistant"
    description: "Helps analyze system information"
    template: |
      Analyze the following system information:
      
      System: {{system_info}}
      Current directory: {{path}}
      
      Provide insights about the system status and suggest any improvements.
    args:
      - name: path
        help: "Directory path to analyze"
        type: string
        default: "."
      - name: system_info
        help: "System information to analyze"
        type: string
"""
    return config_content


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
    print("🚀 ShellMCP AmazonQ Integration Example")
    print("=" * 50)
    
    # Create temporary directory for example
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "example_tools.yml"
        
        print(f"📁 Working in temporary directory: {temp_path}")
        
        # Step 1: Create configuration file
        print("\n📝 Step 1: Creating ShellMCP configuration...")
        config_content = create_example_config()
        config_file.write_text(config_content)
        print(f"✅ Created configuration: {config_file}")
        
        # Step 2: Validate configuration
        print("\n🔍 Step 2: Validating configuration...")
        if not run_command(f"shellmcp validate {config_file} --verbose", "Configuration validation"):
            print("❌ Configuration validation failed")
            return 1
        
        # Step 3: Generate server
        print("\n🏗️  Step 3: Generating FastMCP server...")
        if not run_command(f"shellmcp generate {config_file} --output-dir {temp_path}/output --verbose", 
                          "Server generation"):
            print("❌ Server generation failed")
            return 1
        
        # Step 4: Install to AmazonQ (dry run - we'll show the config that would be created)
        print("\n🔧 Step 4: Installing to AmazonQ MCP configuration...")
        
        # Find the generated server file
        output_dir = temp_path / "output"
        server_files = list(output_dir.glob("*_server.py"))
        
        if not server_files:
            print("❌ No server file found in output directory")
            return 1
        
        server_file = server_files[0]
        print(f"📄 Found server file: {server_file}")
        
        # Show what the MCP configuration would look like
        print("\n📋 Generated MCP configuration (example):")
        example_mcp_config = {
            "mcpServers": {
                "example-tools": {
                    "command": "python3",
                    "args": [str(server_file)],
                    "env": {
                        "PYTHONPATH": str(output_dir)
                    }
                }
            }
        }
        
        import json
        print(json.dumps(example_mcp_config, indent=2))
        
        # Note: We don't actually install in this example to avoid modifying user's system
        print("\n💡 To actually install to AmazonQ, run:")
        print(f"   shellmcp install-amazonq {config_file}")
        print("   or")
        print(f"   shellmcp-amazonq install {config_file} {server_file}")
        
        print("\n🎉 Example completed successfully!")
        print("\n📖 Next steps:")
        print("   1. Customize the YAML configuration for your needs")
        print("   2. Generate your server with 'shellmcp generate'")
        print("   3. Install to AmazonQ with 'shellmcp install-amazonq'")
        print("   4. Restart AmazonQ to load your new MCP server")
        
        return 0


if __name__ == "__main__":
    sys.exit(main())