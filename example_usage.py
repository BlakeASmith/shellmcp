"""Example usage of the YML parser with the example configuration."""

from shellmcp.parser import YMLParser

def main():
    """Demonstrate usage with the example configuration file."""
    parser = YMLParser()
    
    try:
        # Load the example configuration
        config = parser.load_from_file("example_config.yml")
        print("✅ Configuration loaded successfully!")
        
        # Display server information
        server_info = parser.get_server_info()
        print(f"\n📋 Server Information:")
        print(f"   Name: {server_info['name']}")
        print(f"   Description: {server_info['description']}")
        print(f"   Version: {server_info['version']}")
        print(f"   Environment Variables: {len(server_info['environment_variables'])}")
        print(f"   Tools: {server_info['tools_count']}")
        print(f"   Reusable Arguments: {server_info['reusable_args_count']}")
        
        # Display tools summary
        tools_summary = parser.get_tools_summary()
        print(f"\n🔧 Tools Summary:")
        for tool_name, tool_info in tools_summary.items():
            print(f"   {tool_name}:")
            print(f"     Description: {tool_info['description']}")
            print(f"     Arguments: {tool_info['arguments_count']}")
            print(f"     Template Variables: {tool_info['template_variables']}")
            print(f"     Valid Template: {'✅' if tool_info['has_valid_template'] else '❌'}")
            if tool_info['environment_variables']:
                print(f"     Environment Variables: {tool_info['environment_variables']}")
            print()
        
        # Validate all templates
        template_validation = parser.validate_all_templates()
        print(f"🔍 Template Validation Results:")
        for tool_name, is_valid in template_validation.items():
            status = "✅" if is_valid else "❌"
            print(f"   {status} {tool_name}")
        
        # Check argument consistency
        consistency_issues = parser.validate_argument_consistency()
        if consistency_issues:
            print(f"\n⚠️  Argument Consistency Issues:")
            for tool_name, missing_args in consistency_issues.items():
                print(f"   {tool_name}: missing arguments for {missing_args}")
        else:
            print(f"\n✅ All template variables have corresponding arguments")
        
        # Show detailed information for a specific tool
        print(f"\n📝 Detailed Information for 'BackupDatabase':")
        resolved_args = parser.get_resolved_tool_arguments("BackupDatabase")
        for arg in resolved_args:
            print(f"   - {arg.name}:")
            print(f"     Help: {arg.help}")
            print(f"     Type: {arg.type}")
            if arg.default is not None:
                print(f"     Default: {arg.default}")
            if arg.choices:
                print(f"     Choices: {arg.choices}")
            if arg.pattern:
                print(f"     Pattern: {arg.pattern}")
        
        # Show template variables for a complex tool
        print(f"\n🔍 Template Variables for 'ConditionalDeploy':")
        template_vars = parser.get_tool_template_variables("ConditionalDeploy")
        print(f"   Variables: {template_vars}")
        
        # Show how to access the raw configuration
        print(f"\n📊 Raw Configuration Access:")
        print(f"   Server name: {config.server.name}")
        print(f"   Number of reusable args: {len(config.args) if config.args else 0}")
        print(f"   Number of tools: {len(config.tools) if config.tools else 0}")
        
        if config.args:
            print(f"   Reusable arguments:")
            for arg_name, arg_def in config.args.items():
                print(f"     {arg_name}: {arg_def.help}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()