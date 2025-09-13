"""Utility functions for user input and file operations."""

import yaml
import sys
from pathlib import Path
from typing import List, Optional
import questionary
from .parser import YMLParser
from .models import YMLConfig, ServerConfig


def get_input(prompt: str, default: str = None, required: bool = True) -> str:
    """Get user input with optional default value using questionary."""
    try:
        if required:
            result = questionary.text(
                prompt,
                default=default or "",
                validate=lambda x: len(x.strip()) > 0 if required else True
            ).ask()
        else:
            result = questionary.text(
                prompt,
                default=default or ""
            ).ask()
        
        if result is None:
            print("Operation cancelled by user.")
            sys.exit(0)
        
        return result.strip() if result else (default or "")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)


def get_choice(prompt: str, choices: List[str], default: str = None) -> str:
    """Get user choice from a list of options using questionary."""
    try:
        result = questionary.select(
            prompt,
            choices=choices,
            default=default
        ).ask()
        
        if result is None:
            print("Operation cancelled by user.")
            sys.exit(0)
        
        return result
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)


def get_yes_no(prompt: str, default: bool = None) -> bool:
    """Get yes/no input from user using questionary."""
    try:
        result = questionary.confirm(
            prompt,
            default=default or False
        ).ask()
        
        if result is None:
            print("Operation cancelled by user.")
            sys.exit(0)
        
        return result
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)


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