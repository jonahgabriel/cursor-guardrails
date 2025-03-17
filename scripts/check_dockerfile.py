#!/usr/bin/env python3
"""Script to check Dockerfile against standardization templates."""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def load_template() -> str:
    """Load Dockerfile template."""
    standards_dir = Path(__file__).parent.parent / "docs" / "standards"
    template_path = standards_dir / "docker" / "DOCKERFILE_TEMPLATE"
    
    with open(template_path) as f:
        return f.read()


def parse_dockerfile(content: str) -> List[Tuple[str, str]]:
    """Parse Dockerfile content into a list of (instruction, argument) tuples."""
    instructions = []
    current_instruction = None
    current_args = []
    
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        if line.endswith("\\"):
            if current_instruction is None:
                instruction, arg = line.split(None, 1)
                current_instruction = instruction
                current_args = [arg.rstrip("\\").strip()]
            else:
                current_args.append(line.rstrip("\\").strip())
        else:
            if current_instruction is not None:
                current_args.append(line)
                instructions.append((current_instruction, " ".join(current_args)))
                current_instruction = None
                current_args = []
            else:
                instruction, arg = line.split(None, 1)
                instructions.append((instruction, arg))
    
    return instructions


def check_base_image(instructions: List[Tuple[str, str]]) -> List[str]:
    """Check if the base image is correct."""
    errors = []
    
    if not instructions or instructions[0][0] != "FROM":
        errors.append("Dockerfile must start with FROM instruction")
        return errors
    
    base_image = instructions[0][1]
    if not base_image.startswith("python:3.11"):
        errors.append("Base image must be python:3.11")
    
    return errors


def check_environment_variables(instructions: List[Tuple[str, str]]) -> List[str]:
    """Check if required environment variables are set."""
    errors = []
    required_env_vars = {
        "PYTHONUNBUFFERED",
        "PYTHONDONTWRITEBYTECODE",
        "POETRY_VERSION",
        "POETRY_HOME",
        "POETRY_VIRTUALENVS_IN_PROJECT",
        "POETRY_NO_INTERACTION",
        "PYSETUP_PATH",
        "VENV_PATH"
    }
    
    found_env_vars = set()
    for instruction, args in instructions:
        if instruction == "ENV":
            # Handle both formats: ENV KEY=VALUE and ENV KEY VALUE
            if "=" in args:
                key = args.split("=")[0].strip()
            else:
                key = args.split()[0].strip()
            found_env_vars.add(key)
    
    for var in required_env_vars:
        if var not in found_env_vars:
            errors.append(f"Missing required environment variable: {var}")
    
    return errors


def check_poetry_installation(instructions: List[Tuple[str, str]]) -> List[str]:
    """Check if Poetry is installed correctly."""
    errors = []
    poetry_install_found = False
    
    for instruction, args in instructions:
        if instruction == "RUN" and "curl -sSL https://install.python-poetry.org" in args:
            poetry_install_found = True
            break
    
    if not poetry_install_found:
        errors.append("Poetry installation command not found")
    
    return errors


def check_dependencies_installation(instructions: List[Tuple[str, str]]) -> List[str]:
    """Check if dependencies are installed correctly."""
    errors = []
    poetry_install_found = False
    copy_requirements_found = False
    
    for instruction, args in instructions:
        if instruction == "COPY" and "pyproject.toml" in args and "poetry.lock" in args:
            copy_requirements_found = True
        elif instruction == "RUN" and "poetry install" in args:
            poetry_install_found = True
    
    if not copy_requirements_found:
        errors.append("Must copy pyproject.toml and poetry.lock files")
    if not poetry_install_found:
        errors.append("Must install dependencies using poetry install")
    
    return errors


def check_healthcheck(instructions: List[Tuple[str, str]]) -> List[str]:
    """Check if healthcheck is configured correctly."""
    errors = []
    healthcheck_found = False
    
    for instruction, args in instructions:
        if instruction == "HEALTHCHECK":
            healthcheck_found = True
            if "--interval" not in args or "--timeout" not in args or "--retries" not in args:
                errors.append("Healthcheck must specify interval, timeout, and retries")
            break
    
    if not healthcheck_found:
        errors.append("Healthcheck configuration not found")
    
    return errors


def check_labels(instructions: List[Tuple[str, str]]) -> List[str]:
    """Check if required labels are present."""
    errors = []
    required_labels = {"maintainer", "version", "description"}
    found_labels = set()
    
    for instruction, args in instructions:
        if instruction == "LABEL":
            for label in args.split():
                if "=" in label:
                    found_labels.add(label.split("=")[0].strip())
    
    for label in required_labels:
        if label not in found_labels:
            errors.append(f"Missing required label: {label}")
    
    return errors


def main() -> int:
    """Main function to check Dockerfile configuration."""
    try:
        template = load_template()
        dockerfile_path = Path("Dockerfile")
        
        if not dockerfile_path.is_file():
            print("Error: Dockerfile not found")
            return 1
        
        with open(dockerfile_path) as f:
            content = f.read()
        
        instructions = parse_dockerfile(content)
        exit_code = 0
        
        # Run all checks
        checks = [
            ("Base image", check_base_image),
            ("Environment variables", check_environment_variables),
            ("Poetry installation", check_poetry_installation),
            ("Dependencies installation", check_dependencies_installation),
            ("Healthcheck", check_healthcheck),
            ("Labels", check_labels)
        ]
        
        for check_name, check_func in checks:
            errors = check_func(instructions)
            if errors:
                print(f"\n{check_name} errors:")
                for error in errors:
                    print(f"  - {error}")
                exit_code = 1
        
        return exit_code
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 