# Examples

This directory contains examples demonstrating how to use the ShellMCP YAML configuration format and Pydantic models.

## Directory Structure

```
examples/
├── configs/          # Example YAML configuration files
├── scripts/          # Example Python scripts
├── tutorials/        # Tutorial examples (future)
└── README.md         # This file
```

## Configuration Examples

### `configs/example_config.yml`
A comprehensive example configuration demonstrating:
- Server configuration with environment variables
- Reusable argument definitions
- Multiple tools with various argument types
- Jinja2 template usage
- Reference resolution

## Script Examples

### `scripts/basic_example.py`
Basic usage example showing:
- Loading configuration from string
- Parsing and validation
- Accessing server and tool information
- Template validation

### `scripts/example_usage.py`
Advanced usage example demonstrating:
- Loading configuration from file
- Detailed validation reporting
- Template variable extraction
- Argument resolution
- Error handling

## Usage

To run the example scripts:

```bash
# Basic example
python examples/scripts/basic_example.py

# Advanced example (requires example_config.yml)
python examples/scripts/example_usage.py
```

To validate example configurations:

```bash
# Validate the example configuration
shellmcp validate examples/configs/example_config.yml --verbose
```