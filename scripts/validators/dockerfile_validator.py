#!/usr/bin/env python3
"""
Dockerfile Validator

Validates Dockerfile against best practices and project standards,
ensuring consistent container builds and runtime behavior.
"""

import sys
import os
import re
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Define validation rules
REQUIRED_INSTRUCTIONS = ['FROM', 'WORKDIR', 'COPY', 'RUN', 'CMD']
RECOMMENDED_INSTRUCTIONS = ['LABEL', 'EXPOSE', 'ENTRYPOINT']
PROHIBITED_PATTERNS = [
    r'npm install -g',  # Global npm installs
    r'apt-get (install|update)(?!.*--no-install-recommends)',  # apt without --no-install-recommends
    r'pip install(?!.*--no-cache-dir)',  # pip without --no-cache-dir
    r'COPY containers/',  # Absolute paths in COPY commands
]
SECURITY_CHECKS = [
    (r'FROM\s+\w+(?::\S+)?\s+[Aa][Ss]\s+\w+', "Multi-stage builds recommended for smaller images"),
    (r'USER\s+(?!root)', "Using non-root user recommended for security"),
    (r'rm -rf /var/lib/apt/lists/\*', "Clean up apt cache to reduce image size"),
]

# Poetry-specific checks
POETRY_CHECKS = [
    (r'(curl -sSL https://install\.python-poetry\.org|pip install poetry)', "Poetry installation"),
    (r'COPY pyproject\.toml poetry\.lock\* \./|COPY \["pyproject\.toml", "poetry\.lock\*", "\./"\]', "Copy Poetry files"),
    (r'poetry (install|config)', "Poetry dependency installation"),
    (r'poetry config virtualenvs.create false', "Poetry virtualenv configuration")
]

def validate_dockerfile(dockerfile_path: str) -> Tuple[List[str], List[str]]:
    """Validate a Dockerfile against project standards."""
    errors = []
    warnings = []
    dockerfile_path = Path(dockerfile_path)
    
    # Check if file exists
    if not dockerfile_path.exists():
        errors.append(f"Dockerfile not found at {dockerfile_path}")
        return errors, warnings
    
    # Read Dockerfile
    try:
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            lines = content.splitlines()
    except Exception as e:
        errors.append(f"Error reading Dockerfile: {e}")
        return errors, warnings
    
    # Check for required instructions
    for instruction in REQUIRED_INSTRUCTIONS:
        if not re.search(rf'^\s*{instruction}\s+', content, re.MULTILINE | re.IGNORECASE):
            errors.append(f"Missing required instruction: {instruction}")
    
    # Check for recommended instructions
    for instruction in RECOMMENDED_INSTRUCTIONS:
        if not re.search(rf'^\s*{instruction}\s+', content, re.MULTILINE | re.IGNORECASE):
            warnings.append(f"Missing recommended instruction: {instruction}")
    
    # Check for prohibited patterns
    for pattern in PROHIBITED_PATTERNS:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        if matches:
            if "containers/" in pattern:
                errors.append(f"Found absolute path in COPY command. Use relative paths instead: {matches}")
            else:
                errors.append(f"Found prohibited pattern: {pattern}")
    
    # Check for multi-stage build
    is_multistage = bool(re.search(r'FROM\s+\w+(?::\S+)?\s+[Aa][Ss]\s+\w+', content, re.MULTILINE | re.IGNORECASE))
    
    # Security checks
    for pattern, message in SECURITY_CHECKS:
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            # Skip multi-stage build warning if we already have a multi-stage build
            if "Multi-stage builds" in message and is_multistage:
                continue
            # Skip apt cache cleanup warning if we have rm -rf /var/lib/apt/lists/*
            if "apt cache" in message and "rm -rf /var/lib/apt/lists/*" in content:
                continue
            warnings.append(f"Security recommendation: {message}")
    
    # Poetry-specific validation
    poetry_installation_found = False
    poetry_config_found = False
    poetry_usage_found = False
    
    for pattern, description in POETRY_CHECKS:
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            if "installation" in description.lower():
                poetry_installation_found = True
            elif "configuration" in description.lower():
                poetry_config_found = True
            elif "dependency" in description.lower():
                poetry_usage_found = True
    
    # Check for Python-based container that should use Poetry
    is_python_container = re.search(r'FROM\s+python', content, re.MULTILINE | re.IGNORECASE)
    if is_python_container:
        if not poetry_installation_found:
            errors.append("Missing Poetry installation in Dockerfile")
            errors.append("Recommendation: Add 'RUN curl -sSL https://install.python-poetry.org | python3 -'")
        
        if not poetry_usage_found and not re.search(r'poetry install', content, re.MULTILINE | re.IGNORECASE):
            errors.append("Missing Poetry dependency installation in Dockerfile")
            errors.append("Recommendation: Add 'RUN poetry install --no-interaction'")
            
        if "COPY pyproject.toml" not in content and "COPY [\"pyproject.toml" not in content:
            errors.append("Missing Poetry configuration file copy in Dockerfile")
            errors.append("Recommendation: Add 'COPY pyproject.toml poetry.lock* ./'")
    
    # Check for relative paths in COPY commands
    copy_commands = re.findall(r'^\s*COPY\s+(.+?)\s+(.+?)$', content, re.MULTILINE)
    for source, dest in copy_commands:
        if 'containers/' in source:
            errors.append(f"Use relative paths in COPY commands: {source} -> {dest}")
            errors.append(f"Recommendation: Change to 'COPY {source.split('/')[-1]} {dest}'")
    
    return errors, warnings

def main():
    """Run standalone validation if script is executed directly."""
    parser = argparse.ArgumentParser(description="Validate Dockerfile against project standards")
    parser.add_argument("dockerfile_path", help="Path to the Dockerfile to validate")
    args = parser.parse_args()

    dockerfile_path = args.dockerfile_path
    errors, warnings = validate_dockerfile(dockerfile_path)

    # Display results
    if warnings:
        logger.warning("Warnings:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    if errors:
        logger.error("Dockerfile validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        return 1
    else:
        if warnings:
            logger.info("Dockerfile validation passed with warnings!")
        else:
            logger.info("Dockerfile validation passed successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
