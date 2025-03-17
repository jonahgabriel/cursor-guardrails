#!/usr/bin/env python3
"""
Validation Runner

Runs all validators for a specified container.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def validate_container(container_name):
    """Run all validators for a specific container."""
    validators = [
        ("Container Structure", f"python3 scripts/validators/container_validator.py containers/{container_name}"),
        ("Dockerfile", f"python3 scripts/validators/dockerfile_validator.py containers/{container_name}/Dockerfile"),
        ("Poetry Configuration", f"python3 scripts/validators/poetry_validator.py containers/{container_name}"),
    ]
    
    # Docker Compose validation is project-wide
    validators.append(("Docker Compose", "python3 scripts/validators/compose_validator.py containers/dev-environment/docker-compose.dev.yml"))
    
    all_passed = True
    for name, command in validators:
        print(f"\nRunning {name} validation...")
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            all_passed = False
    
    return all_passed

def main():
    parser = argparse.ArgumentParser(description="Validate container configuration")
    parser.add_argument("container", help="Container name to validate")
    args = parser.parse_args()
    
    success = validate_container(args.container)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
