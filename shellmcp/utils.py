"""Utility functions for user input and file operations."""

import yaml
from pathlib import Path
from typing import List, Optional
from .parser import YMLParser
from .models import YMLConfig, ServerConfig


def get_input(prompt: str, default: str = None, required: bool = True) -> str:
    """Get user input with optional default value."""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        value = input(full_prompt).strip()
        if value:
            return value
        elif default:
            return default
        elif not required:
            return ""
        else:
            print("This field is required. Please enter a value.")


def get_choice(prompt: str, choices: List[str], default: str = None) -> str:
    """Get user choice from a list of options."""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        marker = " (default)" if choice == default else ""
        print(f"  {i}. {choice}{marker}")
    
    while True:
        try:
            choice_input = input(f"Enter choice (1-{len(choices)}): ").strip()
            if not choice_input and default:
                return default
            
            choice_num = int(choice_input)
            if 1 <= choice_num <= len(choices):
                return choices[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print("Please enter a valid number")


def get_yes_no(prompt: str, default: bool = None) -> bool:
    """Get yes/no input from user."""
    if default is True:
        full_prompt = f"{prompt} [Y/n]: "
    elif default is False:
        full_prompt = f"{prompt} [y/N]: "
    else:
        full_prompt = f"{prompt} [y/n]: "
    
    while True:
        value = input(full_prompt).strip().lower()
        if value in ['y', 'yes']:
            return True
        elif value in ['n', 'no']:
            return False
        elif value == "" and default is not None:
            return default
        else:
            print("Please enter 'y' for yes or 'n' for no")


def save_config(config: YMLConfig, file_path: str) -> None:
    """Save configuration to YAML file."""
    config_dict = config.model_dump(exclude_none=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False, indent=2)


def load_or_create_config(config_file: str) -> YMLConfig:
    """Load existing config or create new one."""
    if Path(config_file).exists():
        parser = YMLParser()
        return parser.load_from_file(config_file)
    else:
        # Create minimal config
        return YMLConfig(server=ServerConfig(name="", desc=""))