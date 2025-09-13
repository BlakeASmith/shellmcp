#!/usr/bin/env python3
"""Example script demonstrating virtual environment setup for FastMCP servers."""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_virtual_environment(server_dir):
    """Set up a virtual environment for the FastMCP server."""
    server_path = Path(server_dir)
    
    print(f"🚀 Setting up virtual environment for FastMCP server in {server_path}")
    
    # Check if virtual environment already exists
    venv_path = server_path / "venv"
    if venv_path.exists():
        print(f"✅ Virtual environment already exists at {venv_path}")
        return True
    
    # Create virtual environment
    print("📦 Creating virtual environment...")
    success, stdout, stderr = run_command("python3 -m venv venv", cwd=server_path)
    
    if not success:
        print(f"❌ Failed to create virtual environment: {stderr}")
        return False
    
    print("✅ Virtual environment created successfully")
    
    # Determine activation script path
    activate_script = venv_path / "bin" / "activate"
    pip_path = venv_path / "bin" / "pip"
    
    # Install dependencies
    requirements_file = server_path / "requirements.txt"
    if requirements_file.exists():
        print("📦 Installing dependencies...")
        success, stdout, stderr = run_command(f"{pip_path} install -r requirements.txt", cwd=server_path)
        
        if not success:
            print(f"❌ Failed to install dependencies: {stderr}")
            return False
        
        print("✅ Dependencies installed successfully")
    else:
        print("⚠️  No requirements.txt file found")
    
    # Show activation instructions
    print(f"\n🎉 Virtual environment setup complete!")
    print(f"\n📋 To activate the virtual environment:")
    print(f"   source {activate_script}")
    
    print(f"\n🚀 To run the server:")
    print(f"   cd {server_path}")
    print(f"   source {activate_script}")
    
    # Find the server script
    server_scripts = list(server_path.glob("*_server.py"))
    if server_scripts:
        server_script = server_scripts[0]
        print(f"   python {server_script.name}")
    
    print(f"\n⚙️  For MCP configuration:")
    print(f"   Use Python path: {venv_path / 'bin' / 'python'}")
    
    return True

def main():
    """Main function to demonstrate virtual environment setup."""
    
    # Example server directory
    server_dir = "examples/configs"
    
    if not Path(server_dir).exists():
        print(f"❌ Server directory {server_dir} not found")
        print("Please run the FastMCP generator first to create the server files")
        return 1
    
    success = setup_virtual_environment(server_dir)
    
    if success:
        print(f"\n✅ Virtual environment setup completed successfully!")
        return 0
    else:
        print(f"\n❌ Virtual environment setup failed")
        return 1

if __name__ == "__main__":
    exit(main())