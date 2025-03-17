#!/usr/bin/env python3
"""Standards checker with modular validator integration"""

import sys
from pathlib import Path

# Import validators
from containers.scripts.validators.dockerfile_validator import validate_dockerfile
from containers.scripts.validators.container_validator import validate_container_structure
from containers.scripts.validators.compose_validator import validate_compose_file
from containers.scripts.validators.poetry_validator import validate_poetry_config

def check_containers():
    """Validate all containers using the modular validators"""
    print("Validating containers...")
    all_valid = True
    container_dirs = [p for p in Path('./containers').glob('*') if p.is_dir()]
    
    for container_dir in container_dirs:
        # Structural validation
        structure_errors = validate_container_structure(container_dir)
        if structure_errors:
            all_valid = False
            print(f"Container structure validation errors in {container_dir}:")
            for error in structure_errors:
                print(f"  - {error}")
        
        # Poetry validation
        poetry_errors = validate_poetry_config(container_dir)
        if poetry_errors:
            all_valid = False
            print(f"Poetry configuration errors in {container_dir}:")
            for error in poetry_errors:
                print(f"  - {error}")
        
        # Dockerfile validation if file exists
        dockerfile_path = container_dir / "Dockerfile"
        if dockerfile_path.exists():
            dockerfile_errors, dockerfile_warnings = validate_dockerfile(dockerfile_path)
            if dockerfile_errors:
                all_valid = False
                print(f"Dockerfile validation errors in {dockerfile_path}:")
                for error in dockerfile_errors:
                    print(f"  - {error}")
            if dockerfile_warnings:
                print(f"Dockerfile validation warnings in {dockerfile_path}:")
                for warning in dockerfile_warnings:
                    print(f"  - Warning: {warning}")
    
    # Validate compose file
    compose_path = Path('./containers/dev-environment/docker-compose.dev.yml')
    if compose_path.exists():
        compose_errors = validate_compose_file(str(compose_path))
        if compose_errors:
            all_valid = False
            print(f"Docker Compose validation errors:")
            for error in compose_errors:
                print(f"  - {error}")
    
    return all_valid

# Then in the main execution flow:
if __name__ == "__main__":
    containers_valid = check_containers()
    # ... other validations ...
    
    if not containers_valid:
        sys.exit(1)
    sys.exit(0)
