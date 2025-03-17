#!/usr/bin/env python3
"""
Poetry Validator for AI Development Platform

This script validates that containers properly use Poetry for dependency management
by checking for required pyproject.toml files and validating their structure.

Usage:
    python poetry_validator.py [container_path]
"""

import os
import sys
import tomli
import argparse
from pathlib import Path

REQUIRED_SECTIONS = ["tool.poetry", "tool.poetry.dependencies"]
REQUIRED_DEV_SECTIONS = ["tool.poetry.group.dev.dependencies"]
REQUIRED_FIELDS = ["name", "version", "description"]


def validate_poetry_config(container_path):
    """Validate poetry configuration for a container."""
    pyproject_path = Path(container_path) / "pyproject.toml"
    
    # Check if pyproject.toml exists
    if not pyproject_path.exists():
        print(f"❌ Error: {pyproject_path} does not exist")
        return False
    
    # Check for requirements.txt or setup.py (should not exist)
    requirements_path = Path(container_path) / "requirements.txt"
    setup_path = Path(container_path) / "setup.py"
    
    if requirements_path.exists():
        print(f"❌ Error: {requirements_path} exists (should use pyproject.toml instead)")
        return False
        
    if setup_path.exists():
        print(f"❌ Error: {setup_path} exists (should use pyproject.toml instead)")
        return False
    
    # Parse and validate pyproject.toml
    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomli.load(f)
        
        # Check required sections
        for section in REQUIRED_SECTIONS:
            parts = section.split(".")
            current = pyproject_data
            for part in parts:
                if part not in current:
                    print(f"❌ Error: Missing section '{section}' in pyproject.toml")
                    return False
                current = current[part]
        
        # Check required fields in [tool.poetry]
        poetry_section = pyproject_data.get("tool", {}).get("poetry", {})
        for field in REQUIRED_FIELDS:
            if field not in poetry_section:
                print(f"❌ Error: Missing required field '{field}' in [tool.poetry]")
                return False
        
        # Check Python version constraint
        if "python" not in pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies", {}):
            print("❌ Error: Missing Python version constraint in dependencies")
            return False
            
        print(f"✅ Poetry configuration valid: {pyproject_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error parsing pyproject.toml: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validate Poetry configuration")
    parser.add_argument("container_path", help="Path to container directory")
    args = parser.parse_args()
    
    success = validate_poetry_config(args.container_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
