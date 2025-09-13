#!/usr/bin/env python3

import subprocess
import tempfile
import os

# Read the current template
with open('/home/blake/p/shellmcp/shellmcp/templates/server.py.j2', 'r') as f:
    content = f.read()

# Replace the simple help message with actual help command execution
old_help_section = '''{% if tool.help_cmd %}
    
    Help: Run `{{ tool.help_cmd }}` for more information.
{% endif %}'''

new_help_section = '''{% if tool.help_cmd %}
    
    Help:
{% raw %}
    {% set help_result = execute_command(tool.help_cmd) %}
    {% if help_result.success %}
    {{ help_result.stdout|indent(4, first=True) }}
    {% else %}
    Failed to get help: {{ help_result.stderr }}
    {% endif %}
{% endraw %}
{% endif %}'''

# Replace the content
updated_content = content.replace(old_help_section, new_help_section)

# Write the updated template
with open('/home/blake/p/shellmcp/shellmcp/templates/server.py.j2', 'w') as f:
    f.write(updated_content)

print("Help command execution added to template!")
