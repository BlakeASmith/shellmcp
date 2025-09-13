"""Basic example of using the YML parser."""

from shellmcp.parser import YMLParser

# Example YAML configuration
yaml_config = """
server:
  name: filesystem-mcp
  desc: MCP Server for filesystem operations
  version: "1.0.0"
  env:
    NODE_ENV: production

args:
  FilePath:
    help: Path to a file
    pattern: "^[^\\0]+$"
  
  DirectoryPath:
    help: Path to a directory
    pattern: "^[^\\0]+$"

tools:
  ListFiles:
    cmd: ls -la {{ path }}
    desc: List files in the current directory
    help-cmd: ls --help
    args:
      - name: path
        help: Directory path to list
        default: "."
        ref: DirectoryPath

  BackupDatabase:
    cmd: |
      {% set backup_file = "backup_" + timestamp + ".sql" %}
      mysqldump -h {{ host }} -u {{ user }} -p{{ password }} {{ database }} > {{ backup_file }}
      {% if compress %}
      gzip {{ backup_file }}
      {% endif %}
    desc: Database backup with optional compression
    args:
      - name: host
        help: Database host
        default: "localhost"
      - name: user
        help: Database user
      - name: password
        help: Database password
      - name: database
        help: Database name
      - name: compress
        help: Compress backup
        type: boolean
        default: false
      - name: timestamp
        help: Timestamp for backup file
        default: "{{ now().strftime('%Y%m%d_%H%M%S') }}"
"""

def main():
    """Demonstrate basic usage of the YML parser."""
    parser = YMLParser()
    
    try:
        # Parse the configuration
        config = parser.load_from_string(yaml_config)
        print("✅ Configuration parsed successfully!")
        
        # Get server information
        server_info = parser.get_server_info()
        print(f"\n📋 Server: {server_info['name']} v{server_info['version']}")
        print(f"   Description: {server_info['description']}")
        print(f"   Tools: {server_info['tools_count']}")
        print(f"   Reusable args: {server_info['reusable_args_count']}")
        
        # Get tools summary
        tools_summary = parser.get_tools_summary()
        print(f"\n🔧 Tools:")
        for tool_name, tool_info in tools_summary.items():
            print(f"   {tool_name}:")
            print(f"     Description: {tool_info['description']}")
            print(f"     Arguments: {tool_info['arguments_count']}")
            print(f"     Template valid: {tool_info['has_valid_template']}")
            print(f"     Template variables: {tool_info['template_variables']}")
        
        # Validate templates
        template_validation = parser.validate_all_templates()
        print(f"\n🔍 Template validation:")
        for tool_name, is_valid in template_validation.items():
            status = "✅" if is_valid else "❌"
            print(f"   {status} {tool_name}")
        
        # Check argument consistency
        consistency_issues = parser.validate_argument_consistency()
        if consistency_issues:
            print(f"\n⚠️  Argument consistency issues:")
            for tool_name, missing_args in consistency_issues.items():
                print(f"   {tool_name}: missing arguments for {missing_args}")
        else:
            print(f"\n✅ All template variables have corresponding arguments")
        
        # Show resolved arguments for a specific tool
        print(f"\n📝 Resolved arguments for 'BackupDatabase':")
        resolved_args = parser.get_resolved_tool_arguments("BackupDatabase")
        for arg in resolved_args:
            print(f"   - {arg.name}: {arg.help} (type: {arg.type})")
            if arg.default is not None:
                print(f"     default: {arg.default}")
        
    except Exception as e:
        print(f"❌ Error parsing configuration: {e}")

if __name__ == "__main__":
    main()