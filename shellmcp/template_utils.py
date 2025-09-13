"""Template utilities and custom Jinja2 filters for MCP server generation."""

from typing import Any


def python_type(yaml_type: str) -> str:
    """Convert YAML type to Python type annotation."""
    type_mapping = {
        "string": "str",
        "number": "float", 
        "boolean": "bool",
        "array": "List[str]"
    }
    return type_mapping.get(yaml_type, "str")


def python_value(value: Any, yaml_type: str) -> str:
    """Convert value to Python representation based on type."""
    if value is None:
        return "None"
    
    if yaml_type == "string":
        return f'"{value}"'
    elif yaml_type == "boolean":
        return "True" if value else "False"
    elif yaml_type == "number":
        return str(value)
    elif yaml_type == "array":
        if isinstance(value, list):
            return str(value)
        else:
            return f'["{value}"]'
    else:
        return f'"{value}"'


def escape_double_quotes(text: str) -> str:
    """Escape double quotes in text for use in triple-quoted strings."""
    return text.replace('"', '\\"')


def get_jinja_filters():
    """Get dictionary of custom Jinja2 filters."""
    return {
        'python_type': python_type,
        'python_value': python_value,
        'escape_double_quotes': escape_double_quotes,
    }