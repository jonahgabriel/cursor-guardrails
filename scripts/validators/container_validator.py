#!/usr/bin/env python3
"""
Container Structure Validator

Validates container directory structure against architectural standards,
ensuring consistent organization and file presence.
"""

import sys
import logging
import ast
from pathlib import Path
import os
from typing import List, Optional, Tuple
import black

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Directories to exclude from validation
EXCLUDED_DIRS = {
    '__pycache__',
    'common',
    'tools',
    'monitoring',
    '.pytest_cache',
    '.git',
    '.venv',
    'node_modules',
    'build',
    'dist',
    'coverage',
    '.coverage',
    '.mypy_cache',
    '.tox',
    '.eggs',
}

def should_skip_directory(dir_path: Path) -> bool:
    """Check if a directory should be skipped during validation."""
    return (
    any(part.startswith('.') for part in dir_path.parts) or
    any(part in EXCLUDED_DIRS for part in dir_path.parts)
    )

def format_python_files(container_path: Path) -> List[str]:
    """Format all Python files in the container using black."""
    errors = []
    mode = black.Mode(
    target_versions={black.TargetVersion.PY311},
    line_length=88,
    string_normalization=True,
    is_pyi=False,
    )

    for py_file in container_path.rglob("*.py"):
        if not should_skip_directory(py_file.parent):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    src = f.read()
                try:
                    formatted_src = black.format_str(src, mode=mode)
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(formatted_src)
                except black.InvalidInput as e:
                    errors.append(f"Syntax error in {py_file}: {str(e)}")
            except Exception as e:
                errors.append(f"Error reading/writing {py_file}: {str(e)}")

    return errors

def validate_container_structure(container_path: Path) -> List[str]:
    """Validate an individual container's structure and organization."""
    errors = []
    container_name = container_path.name

    # Skip validation for certain directories
    if container_name in EXCLUDED_DIRS:
        return []

    # First format all Python files
    if has_python_code(container_path):
        logger.info("Formatting Python files with black...")
        format_errors = format_python_files(container_path)
        errors.extend(format_errors)

    # Continue with regular validation
    if container_path.is_dir():
        # Service containers need a Dockerfile
        if not is_utility_container(container_name):
            if not (container_path / "Dockerfile").exists():
                errors.append(f"Missing required file: Dockerfile")

        # Check Python package structure
        if has_python_code(container_path):
            # Check src directory structure
            src_path = container_path / "src"
            if src_path.exists():
                errors.extend(validate_python_package(src_path, container_name))

            # Check tests directory structure
            tests_path = container_path / "tests"
            if tests_path.exists():
                if not (tests_path / "__init__.py").exists():
                    errors.append(f"Missing __init__.py in tests directory")
                else:
                    errors.extend(validate_python_package(tests_path, "tests"))
        
        # Poetry validation - Check for pyproject.toml and absence of requirements.txt/setup.py
        poetry_errors = validate_poetry_configuration(container_path)
        errors.extend(poetry_errors)

    return errors

def validate_poetry_configuration(container_path: Path) -> List[str]:
    """Validate Poetry configuration for a container."""
    errors = []
    
    # Check for pyproject.toml
    pyproject_path = container_path / "pyproject.toml"
    if not pyproject_path.exists() and has_python_code(container_path):
        errors.append(f"Missing pyproject.toml (required for Poetry dependency management)")
    
    # Check for absence of requirements.txt and setup.py
    requirements_path = container_path / "requirements.txt"
    if requirements_path.exists():
        errors.append(f"requirements.txt found - should use pyproject.toml with Poetry instead")
    
    setup_path = container_path / "setup.py"
    if setup_path.exists():
        errors.append(f"setup.py found - should use pyproject.toml with Poetry instead")
    
    return errors

def validate_python_package(package_path: Path, package_name: str) -> List[str]:
    """Validate a Python package structure and its imports."""
    errors = []

    # Check for root __init__.py
    root_init = package_path / package_name / "__init__.py"
    if not root_init.exists() and package_name != "tests":  # Skip this check for tests directory
        errors.append(f"Missing package __init__.py file at {root_init.relative_to(package_path)}")
    elif root_init.exists():
        # Validate __init__.py contents
        init_errors = validate_init_file(root_init)
        errors.extend(init_errors)

    # Check all Python subdirectories for __init__.py files
    for py_dir in package_path.rglob("*"):
        if py_dir.is_dir() and not should_skip_directory(py_dir):
            init_file = py_dir / "__init__.py"
            if not init_file.exists():
                errors.append(f"Missing __init__.py in Python package directory: {py_dir.relative_to(package_path)}")
            else:
                # Validate __init__.py contents
                init_errors = validate_init_file(init_file)
                errors.extend(init_errors)

    # Check for relative imports in Python files
    for py_file in package_path.rglob("*.py"):
        if py_file.name != "__init__.py" and not should_skip_directory(py_file.parent):
            import_errors = validate_imports(py_file, package_path)
            errors.extend(import_errors)

    return errors

def validate_init_file(init_file: Path) -> List[str]:
    """Validate the contents of an __init__.py file."""
    errors = []
    try:
        with open(init_file, 'r') as f:
            content = f.read()

        # Parse the file
        try:
            tree = ast.parse(content)

            # Check for __all__ definition
            has_all = any(
                isinstance(node, ast.Assign) and
                any(t.id == "__all__" for t in node.targets if isinstance(t, ast.Name))
                for node in ast.walk(tree)
            )

            if not has_all and any(
                isinstance(node, ast.ImportFrom) for node in ast.walk(tree)
            ):
                errors.append(f"Missing __all__ definition in {init_file} when it contains imports")

        except SyntaxError as e:
            errors.append(f"Syntax error in {init_file}: {str(e)}")

    except Exception as e:
        errors.append(f"Error reading {init_file}: {str(e)}")

    return errors

def validate_imports(py_file: Path, package_path: Path) -> List[str]:
    """Validate imports in a Python file."""
    errors = []
    try:
        with open(py_file, 'r') as f:
            content = f.read()

        # Parse the file
        try:
            tree = ast.parse(content)

            # Check for relative imports and non-standardized internal imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.level > 0:
                        errors.append(f"Relative import found in {py_file}: from {'.' * node.level}{node.module or ''} import ...")
                    # Check for imports that start with 'containers.' which is now deprecated
                    elif node.module and node.module.startswith('containers.'):
                        errors.append(f"Deprecated import format in {py_file}: from {node.module} import ... (should start with the container name directly, e.g., 'foundation.' instead of 'containers.foundation.')")

        except SyntaxError as e:
            errors.append(f"Syntax error in {py_file}: {str(e)}")

    except Exception as e:
        errors.append(f"Error reading {py_file}: {str(e)}")

    return errors

def is_utility_container(container_name: str) -> bool:
    """Determine if a container is a utility container that may not need a Dockerfile."""
    utility_containers = ['common', 'tools', 'monitoring', 'resource_monitor']
    return container_name in utility_containers

def has_python_code(container_path: Path) -> bool:
    """Check if the container has Python code."""
    python_files = list(container_path.glob("**/*.py"))
    return len(python_files) > 0 and (container_path / "src").exists()

def main():
    """Run standalone validation if script is executed directly."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate container directory structure")
    parser.add_argument("container", help="Path to the container directory to validate")
    args = parser.parse_args()

    container_path = Path(args.container)
    if not container_path.exists() or not container_path.is_dir():
        logger.error(f"Container directory not found: {container_path}")
        return 1

    errors = validate_container_structure(container_path)

    if errors:
        logger.error("Container validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        return 1
    else:
        logger.info("Container validation passed successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
