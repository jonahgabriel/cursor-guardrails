#!/usr/bin/env python3
"""Script to check Docker Compose file against standardization templates."""

import sys
from pathlib import Path
from typing import Dict, List, Set

import containers.scripts.yaml


def load_template() -> Dict:
    """Load Docker Compose service template."""
    standards_dir = Path(__file__).parent.parent / "docs" / "standards"
    template_path = standards_dir / "docker" / "DOCKER_COMPOSE_SERVICE_TEMPLATE.yml"
    
    with open(template_path) as f:
        return yaml.safe_load(f)


def check_service_config(service_name: str, config: Dict, template: Dict) -> List[str]:
    """Check if a service configuration follows the template standards."""
    errors = []
    
    # Required top-level keys
    required_keys = {
        "build",
        "environment",
        "volumes",
        "healthcheck"
    }
    
    # Check required keys
    for key in required_keys:
        if key not in config:
            errors.append(f"Service '{service_name}' is missing required key: {key}")
    
    # Check environment variables
    if "environment" in config:
        env_vars = set()
        for env in config["environment"]:
            if isinstance(env, str):
                env_vars.add(env.split("=")[0])
            elif isinstance(env, dict):
                env_vars.update(env.keys())
        
        required_env_vars = {
            "PYTHONPATH",
            "ENV"
        }
        
        for var in required_env_vars:
            if var not in env_vars:
                errors.append(f"Service '{service_name}' is missing required environment variable: {var}")
    
    # Check build configuration
    if "build" in config:
        if "context" not in config["build"]:
            errors.append(f"Service '{service_name}' build is missing context")
        if "dockerfile" not in config["build"]:
            errors.append(f"Service '{service_name}' build is missing dockerfile path")
    
    # Check volumes
    if "volumes" in config:
        source_mounted = False
        for volume in config["volumes"]:
            if "/app" in volume:
                source_mounted = True
                break
        if not source_mounted:
            errors.append(f"Service '{service_name}' must mount source code to /app")
    
    # Check healthcheck
    if "healthcheck" in config:
        required_health_keys = {"test", "interval", "timeout", "retries"}
        health_config = config["healthcheck"]
        
        for key in required_health_keys:
            if key not in health_config:
                errors.append(f"Service '{service_name}' healthcheck is missing: {key}")
    
    return errors


def check_networks(compose_config: Dict) -> List[str]:
    """Check if required networks are defined."""
    errors = []
    
    if "networks" not in compose_config:
        errors.append("Missing top-level networks configuration")
        return errors
    
    required_networks = {"platform-net"}
    defined_networks = set(compose_config["networks"].keys())
    
    for network in required_networks:
        if network not in defined_networks:
            errors.append(f"Missing required network: {network}")
    
    return errors


def check_dependencies(compose_config: Dict) -> List[str]:
    """Check if service dependencies are properly configured."""
    errors = []
    
    for service_name, config in compose_config.get("services", {}).items():
        if "depends_on" in config:
            deps = config["depends_on"]
            if isinstance(deps, dict):
                for dep, dep_config in deps.items():
                    if "condition" not in dep_config:
                        errors.append(f"Service '{service_name}' dependency on '{dep}' should specify a condition")
            elif isinstance(deps, list):
                errors.append(f"Service '{service_name}' should use healthcheck conditions in depends_on")
    
    return errors


def main() -> int:
    """Main function to check Docker Compose configuration."""
    try:
        template = load_template()
        compose_path = Path("docker-compose.yml")
        
        if not compose_path.is_file():
            print("Error: docker-compose.yml not found")
            return 1
        
        with open(compose_path) as f:
            compose_config = yaml.safe_load(f)
        
        if not compose_config or "services" not in compose_config:
            print("Error: Invalid docker-compose.yml format")
            return 1
        
        exit_code = 0
        
        # Check networks
        network_errors = check_networks(compose_config)
        if network_errors:
            print("\nNetwork configuration errors:")
            for error in network_errors:
                print(f"  - {error}")
            exit_code = 1
        
        # Check dependencies
        dependency_errors = check_dependencies(compose_config)
        if dependency_errors:
            print("\nDependency configuration errors:")
            for error in dependency_errors:
                print(f"  - {error}")
            exit_code = 1
        
        # Check each service
        for service_name, config in compose_config["services"].items():
            service_errors = check_service_config(service_name, config, template)
            if service_errors:
                print(f"\nErrors in service '{service_name}':")
                for error in service_errors:
                    print(f"  - {error}")
                exit_code = 1
        
        return exit_code
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 