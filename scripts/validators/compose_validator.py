#!/usr/bin/env python3
"""
Docker Compose Validator

Validates docker-compose.yml files against architectural standards,
ensuring consistent service configuration and integration.
"""

import sys
import yaml
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def validate_compose_service(service_name: str, service_config: Dict[str, Any]) -> List[str]:
    """
    Validate a single service entry in docker-compose.yml.

    Args:
        service_name: Name of the service
        service_config: Service configuration dictionary

    Returns:
        List of error messages, empty list if valid
    """
    errors = []

    # Check build context is component-based
    if 'build' in service_config:
        build = service_config['build']
        if isinstance(build, dict):
            # Validate context follows pattern
            if 'context' in build:
                context = build['context']
                # Special case for dev container
                if service_name == "dev":
                    if not (context == "./containers/dev-environment" or context == "." or context == "../.."):
                        errors.append(f"Dev container build context should be './containers/dev-environment', '.' or '../..'")

                    # Special case for dev container dockerfile path
                    if 'dockerfile' in build:
                        if not (build['dockerfile'] == "Dockerfile" or build['dockerfile'] == "containers/dev-environment/Dockerfile"):
                            errors.append(f"Dev container dockerfile should be 'Dockerfile' or 'containers/dev-environment/Dockerfile'")
                else:
                    if not (context == f"./containers/{service_name}" or context == "."):
                        errors.append(f"Build context should be './containers/{service_name}' or '.'")

                    # If using component-specific context, validate dockerfile is at root
                    if context == f"./containers/{service_name}" and 'dockerfile' in build:
                        if build['dockerfile'] != "Dockerfile":
                            errors.append(f"When using component context, dockerfile should be 'Dockerfile'")

                    # If using root context, validate dockerfile includes component path
                    if context == "." and 'dockerfile' in build:
                        if not build['dockerfile'].startswith(f"containers/{service_name}/"):
                            errors.append(f"When using root context, dockerfile should include component path")

            # Check for Poetry-related args in build configuration
            if 'args' in build and isinstance(build['args'], dict):
                poetry_args = [arg for arg in build['args'] if 'poetry' in arg.lower()]
                if not poetry_args and is_python_service(service_name):
                    errors.append(f"Python service {service_name} should include Poetry-related build args")

    # Check for volumes mounting Poetry configuration
    if 'volumes' in service_config and isinstance(service_config['volumes'], list):
        poetry_volume_found = False
        for volume in service_config['volumes']:
            if isinstance(volume, str) and ('pyproject.toml' in volume or 'poetry.lock' in volume):
                poetry_volume_found = True
                break
        
        if not poetry_volume_found and is_python_service(service_name):
            errors.append(f"Python service {service_name} should mount pyproject.toml/poetry.lock for development")
            errors.append(f"  Consider adding: './containers/{service_name}/pyproject.toml:/app/pyproject.toml'")

    # Check for environment variables related to Python/Poetry
    if 'environment' in service_config:
        env_vars = service_config['environment']
        if isinstance(env_vars, list):
            python_path_found = any('PYTHONPATH' in env for env in env_vars if isinstance(env, str))
        elif isinstance(env_vars, dict):
            python_path_found = 'PYTHONPATH' in env_vars
        else:
            python_path_found = False
            
        if not python_path_found and is_python_service(service_name):
            errors.append(f"Python service {service_name} should define PYTHONPATH environment variable")

    return errors

def is_python_service(service_name: str) -> bool:
    """
    Determine if a service is likely a Python service based on name.
    This is a heuristic and may need improvement for specific projects.
    """
    python_service_indicators = [
        'python', 'django', 'flask', 'fastapi', 'celery', 
        'worker', 'api', 'service', 'app', 'backend',
        'foundation', 'agent', 'model', 'processor', 'analyzer'
    ]
    return any(indicator in service_name.lower() for indicator in python_service_indicators)

def validate_compose_file(compose_file: str) -> List[str]:
    """
    Validate the entire docker-compose.yml file.

    Args:
        compose_file: Path to the docker-compose.yml file

    Returns:
        List of error messages, empty list if valid
    """
    try:
        with open(compose_file, 'r') as f:
            compose_data = yaml.safe_load(f)

        if not compose_data or 'services' not in compose_data:
            return ["Invalid docker-compose.yml: missing services section"]

        errors = []
        for service_name, service_config in compose_data['services'].items():
            service_errors = validate_compose_service(service_name, service_config)
            if service_errors:
                errors.append(f"Service '{service_name}' has configuration issues:")
                for error in service_errors:
                    errors.append(f"  - {error}")

        # Check for Poetry-related global configurations
        if 'x-poetry' not in compose_data and any(is_python_service(name) for name in compose_data['services']):
            errors.append("Missing recommended Poetry YAML extension for shared configuration")
            errors.append("  Consider adding: 'x-poetry: &poetry-settings' with common Poetry configurations")

        return errors

    except yaml.YAMLError as e:
        return [f"YAML parsing error: {str(e)}"]
    except Exception as e:
        return [f"Error validating compose file: {str(e)}"]

def main():
    """Run standalone validation if script is executed directly."""
    parser = argparse.ArgumentParser(description="Validate docker-compose.yml file")
    parser.add_argument("compose_file", help="Path to docker-compose.yml")
    args = parser.parse_args()

    errors = validate_compose_file(args.compose_file)
    if errors:
        for error in errors:
            logger.error(error)
        sys.exit(1)
    else:
        logger.info("Docker Compose validation successful")
        sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
