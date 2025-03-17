#!/usr/bin/env python3
"""Script to check service structure against standardization templates."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set

import containers.scripts.toml
import containers.scripts.yaml


def load_standards() -> Dict:
    """Load standardization templates and requirements."""
    standards_dir = Path(__file__).parent.parent / "docs" / "standards"
    
    with open(standards_dir / "python" / "PYPROJECT_TEMPLATE.toml") as f:
        pyproject_template = toml.load(f)
    
    with open(standards_dir / "docker" / "DOCKERFILE_TEMPLATE") as f:
        dockerfile_template = f.read()
    
    with open(standards_dir / "docker" / "DOCKER_COMPOSE_SERVICE_TEMPLATE.yml") as f:
        docker_compose_template = yaml.safe_load(f)
    
    return {
        "pyproject": pyproject_template,
        "dockerfile": dockerfile_template,
        "docker_compose": docker_compose_template
    }


def check_service_structure(service_dir: Path) -> List[str]:
    """Check if a service directory follows the standard structure."""
    errors = []
    
    # Required directories
    required_dirs = {
        "src",
        "tests",
        "tests/unit",
        "tests/integration"
    }
    
    # Required files
    required_files = {
        "Dockerfile",
        "pyproject.toml",
        "README.md",
        "tests/conftest.py"
    }
    
    # Check directories
    for dir_path in required_dirs:
        full_path = service_dir / dir_path
        if not full_path.is_dir():
            errors.append(f"Missing required directory: {dir_path}")
    
    # Check files
    for file_path in required_files:
        full_path = service_dir / file_path
        if not full_path.is_file():
            errors.append(f"Missing required file: {file_path}")
    
    return errors


def check_pyproject_toml(service_dir: Path, template: Dict) -> List[str]:
    """Check if pyproject.toml follows the template structure."""
    errors = []
    pyproject_path = service_dir / "pyproject.toml"
    
    if not pyproject_path.is_file():
        return ["pyproject.toml not found"]
    
    try:
        with open(pyproject_path) as f:
            pyproject = toml.load(f)
        
        # Check required sections
        required_sections = ["tool.poetry", "tool.poetry.dependencies", "build-system"]
        for section in required_sections:
            if not _get_nested_dict(pyproject, section.split(".")):
                errors.append(f"Missing required section: {section}")
        
        # Check Python version
        py_version = _get_nested_dict(pyproject, ["tool", "poetry", "dependencies", "python"])
        if not py_version or not py_version.startswith("^3.11"):
            errors.append("Python version must be ^3.11.x")
        
    except Exception as e:
        errors.append(f"Error parsing pyproject.toml: {str(e)}")
    
    return errors


def check_dockerfile(service_dir: Path, template: str) -> List[str]:
    """Check if Dockerfile follows the template structure."""
    errors = []
    dockerfile_path = service_dir / "Dockerfile"
    
    if not dockerfile_path.is_file():
        return ["Dockerfile not found"]
    
    try:
        with open(dockerfile_path) as f:
            dockerfile = f.read()
        
        # Check required elements
        required_elements = [
            "FROM python:3.11",
            "POETRY_VERSION",
            "WORKDIR /app",
            "COPY",
            "RUN poetry install",
            "HEALTHCHECK",
            "LABEL maintainer"
        ]
        
        for element in required_elements:
            if element not in dockerfile:
                errors.append(f"Missing required Dockerfile element: {element}")
        
    except Exception as e:
        errors.append(f"Error reading Dockerfile: {str(e)}")
    
    return errors


def _get_nested_dict(d: Dict, keys: List[str]) -> any:
    """Get a value from nested dictionary using a list of keys."""
    for key in keys:
        if not isinstance(d, dict) or key not in d:
            return None
        d = d[key]
    return d


def main() -> int:
    """Main function to check service structure."""
    try:
        standards = load_standards()
        containers_dir = Path(__file__).parent.parent / "containers"
        
        if not containers_dir.is_dir():
            print("Error: containers directory not found")
            return 1
        
        exit_code = 0
        for service_dir in containers_dir.iterdir():
            if not service_dir.is_dir():
                continue
            
            print(f"\nChecking service: {service_dir.name}")
            
            # Check service structure
            structure_errors = check_service_structure(service_dir)
            if structure_errors:
                print("\nStructure errors:")
                for error in structure_errors:
                    print(f"  - {error}")
                exit_code = 1
            
            # Check pyproject.toml
            pyproject_errors = check_pyproject_toml(service_dir, standards["pyproject"])
            if pyproject_errors:
                print("\npyproject.toml errors:")
                for error in pyproject_errors:
                    print(f"  - {error}")
                exit_code = 1
            
            # Check Dockerfile
            dockerfile_errors = check_dockerfile(service_dir, standards["dockerfile"])
            if dockerfile_errors:
                print("\nDockerfile errors:")
                for error in dockerfile_errors:
                    print(f"  - {error}")
                exit_code = 1
        
        return exit_code
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 