#!/usr/bin/env python3
"""
Container Manager

A centralized tool for managing container versioning and building across all services.
This script provides functionality for:
- Managing semantic versioning for containers
- Building container images with proper versioning
- Standardizing container metadata

Usage:
    python container_manager.py version get <container_name>
    python container_manager.py version bump <container_name> [major|minor|patch]
    python container_manager.py version set <container_name> <version>
    python container_manager.py build <container_name> [--push] [--registry REGISTRY] [--no-latest]
    python container_manager.py validate <container_name>
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
CONTAINERS_DIR = PROJECT_ROOT / "containers"


def get_container_dir(container_name: str) -> Path:
    """Get the directory for a specific container."""
    container_dir = CONTAINERS_DIR / container_name
    if not container_dir.exists():
        raise ValueError(f"Container '{container_name}' not found in {CONTAINERS_DIR}")
    return container_dir


def get_pyproject_path(container_name: str) -> Path:
    """Get the path to the pyproject.toml file for a container."""
    container_dir = get_container_dir(container_name)
    pyproject_path = container_dir / "pyproject.toml"
    if not pyproject_path.exists():
        raise ValueError(f"pyproject.toml not found for container '{container_name}'")
    return pyproject_path


def get_dockerfile_path(container_name: str) -> Path:
    """Get the path to the Dockerfile for a container."""
    container_dir = get_container_dir(container_name)
    dockerfile_path = container_dir / "Dockerfile"
    if not dockerfile_path.exists():
        raise ValueError(f"Dockerfile not found for container '{container_name}'")
    return dockerfile_path


def get_current_version(container_name: str) -> str:
    """Get the current version from a container's pyproject.toml."""
    pyproject_path = get_pyproject_path(container_name)
    
    with open(pyproject_path, "r") as f:
        content = f.read()
    
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError(f"Could not find version in {pyproject_path}")
    
    return match.group(1)


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse a version string into major, minor, patch components."""
    try:
        major, minor, patch = map(int, version.split("."))
        return major, minor, patch
    except ValueError:
        raise ValueError(f"Invalid version format: {version}. Expected format: X.Y.Z")


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump the version according to the specified type."""
    major, minor, patch = parse_version(current_version)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}. Expected: major, minor, or patch")


def update_pyproject(container_name: str, new_version: str) -> None:
    """Update the version in a container's pyproject.toml."""
    pyproject_path = get_pyproject_path(container_name)
    
    with open(pyproject_path, "r") as f:
        content = f.read()
    
    updated_content = re.sub(
        r'version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    with open(pyproject_path, "w") as f:
        f.write(updated_content)
    
    print(f"Updated {pyproject_path} with version {new_version}")


def update_dockerfile(container_name: str, new_version: str) -> None:
    """Update the version in a container's Dockerfile."""
    dockerfile_path = get_dockerfile_path(container_name)
    
    with open(dockerfile_path, "r") as f:
        content = f.read()
    
    # Check if version label exists
    if "org.opencontainers.image.version" in content:
        updated_content = re.sub(
            r'org\.opencontainers\.image\.version="[^"]+"',
            f'org.opencontainers.image.version="{new_version}"',
            content
        )
    else:
        # Add version labels if they don't exist
        label_section = f"""
# Add version labels
LABEL org.opencontainers.image.title="{container_name.capitalize()} Service" \
      org.opencontainers.image.description="{container_name.capitalize()} service" \
      org.opencontainers.image.version="{new_version}" \
      org.opencontainers.image.vendor="AI Development Team" \
      org.opencontainers.image.created="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
      org.opencontainers.image.source="https://github.com/organization/project"
"""
        # Insert after the ENV sections
        env_pattern = r'(ENV\s+[^\n]+\n\s*(?:ENV\s+[^\n]+\n\s*)*)'
        if re.search(env_pattern, content):
            updated_content = re.sub(
                env_pattern,
                r'\1' + label_section,
                content,
                count=1
            )
        else:
            # If no ENV section, insert after FROM
            updated_content = re.sub(
                r'(FROM\s+[^\n]+\n)',
                r'\1' + label_section,
                content,
                count=1
            )
    
    with open(dockerfile_path, "w") as f:
        f.write(updated_content)
    
    print(f"Updated {dockerfile_path} with version {new_version}")


def build_container(container_name: str, version: Optional[str] = None, 
                   push: bool = False, registry: Optional[str] = None,
                   tag_latest: bool = True) -> None:
    """Build a container with the specified version."""
    if not version:
        version = get_current_version(container_name)
    
    container_dir = get_container_dir(container_name)
    
    # Set image name
    image_name = container_name
    if registry:
        image_name = f"{registry}/{image_name}"
    
    # Build the image
    print(f"Building {container_name} container version {version}...")
    
    build_cmd = [
        "docker", "build",
        "-t", f"{image_name}:{version}",
        "-f", str(container_dir / "Dockerfile"),
        "--build-arg", f"VERSION={version}",
        "."
    ]
    
    # Run the build command
    try:
        subprocess.run(build_cmd, check=True, cwd=PROJECT_ROOT)
    except subprocess.CalledProcessError as e:
        print(f"Error building container: {e}")
        sys.exit(1)
    
    # Tag as latest if requested
    if tag_latest:
        print(f"Tagging {image_name}:{version} as latest...")
        tag_cmd = ["docker", "tag", f"{image_name}:{version}", f"{image_name}:latest"]
        try:
            subprocess.run(tag_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error tagging container: {e}")
            sys.exit(1)
    
    # Push if requested
    if push:
        print(f"Pushing {image_name}:{version}...")
        push_cmd = ["docker", "push", f"{image_name}:{version}"]
        try:
            subprocess.run(push_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error pushing container: {e}")
            sys.exit(1)
        
        if tag_latest:
            print(f"Pushing {image_name}:latest...")
            push_latest_cmd = ["docker", "push", f"{image_name}:latest"]
            try:
                subprocess.run(push_latest_cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error pushing latest tag: {e}")
                sys.exit(1)
    
    print(f"Build completed successfully!")
    print(f"Image: {image_name}:{version}")


def validate_container(container_name: str) -> bool:
    """Validate a container's structure and configuration."""
    container_dir = get_container_dir(container_name)
    
    # Check for required files
    required_files = ["Dockerfile", "pyproject.toml", "README.md"]
    missing_files = [f for f in required_files if not (container_dir / f).exists()]
    
    if missing_files:
        print(f"Container '{container_name}' is missing required files: {', '.join(missing_files)}")
        return False
    
    # Check for required directories
    required_dirs = ["src", "tests"]
    missing_dirs = [d for d in required_dirs if not (container_dir / d).exists()]
    
    if missing_dirs:
        print(f"Container '{container_name}' is missing required directories: {', '.join(missing_dirs)}")
        return False
    
    # Validate pyproject.toml
    try:
        version = get_current_version(container_name)
        parse_version(version)
    except ValueError as e:
        print(f"Invalid version in pyproject.toml: {e}")
        return False
    
    # Validate Dockerfile
    dockerfile_path = get_dockerfile_path(container_name)
    with open(dockerfile_path, "r") as f:
        dockerfile_content = f.read()
    
    # Check for required Dockerfile elements
    required_elements = [
        ("FROM", r'FROM\s+python'),
        ("WORKDIR", r'WORKDIR\s+/app'),
        ("COPY", r'COPY\s+.*pyproject\.toml'),
        ("RUN", r'RUN\s+.*poetry\s+install'),
        ("EXPOSE", r'EXPOSE\s+\d+'),
        ("CMD", r'CMD\s+\[')
    ]
    
    for name, pattern in required_elements:
        if not re.search(pattern, dockerfile_content):
            print(f"Dockerfile missing required element: {name}")
            return False
    
    print(f"Container '{container_name}' validation successful!")
    return True


def list_containers() -> List[str]:
    """List all available containers."""
    return [d.name for d in CONTAINERS_DIR.iterdir() 
            if d.is_dir() and (d / "Dockerfile").exists()]


def handle_version_command(args: argparse.Namespace) -> None:
    """Handle the 'version' subcommand."""
    container_name = args.container_name
    
    if args.version_action == "get":
        try:
            version = get_current_version(container_name)
            print(f"Current version of {container_name}: {version}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.version_action == "bump":
        try:
            current_version = get_current_version(container_name)
            new_version = bump_version(current_version, args.bump_type)
            update_pyproject(container_name, new_version)
            update_dockerfile(container_name, new_version)
            print(f"Bumped {container_name} version from {current_version} to {new_version}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.version_action == "set":
        try:
            current_version = get_current_version(container_name)
            # Validate the version format
            parse_version(args.version)
            update_pyproject(container_name, args.version)
            update_dockerfile(container_name, args.version)
            print(f"Set {container_name} version from {current_version} to {args.version}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)


def handle_build_command(args: argparse.Namespace) -> None:
    """Handle the 'build' subcommand."""
    try:
        build_container(
            args.container_name,
            version=args.version,
            push=args.push,
            registry=args.registry,
            tag_latest=not args.no_latest
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_validate_command(args: argparse.Namespace) -> None:
    """Handle the 'validate' subcommand."""
    if not validate_container(args.container_name):
        sys.exit(1)


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Container Manager - A tool for managing container versioning and building"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Manage container versions")
    version_subparsers = version_parser.add_subparsers(dest="version_action", help="Version action")
    
    # Version get
    get_parser = version_subparsers.add_parser("get", help="Get current version")
    get_parser.add_argument("container_name", help="Name of the container")
    
    # Version bump
    bump_parser = version_subparsers.add_parser("bump", help="Bump version number")
    bump_parser.add_argument("container_name", help="Name of the container")
    bump_parser.add_argument("bump_type", choices=["major", "minor", "patch"], 
                           help="Type of version bump")
    
    # Version set
    set_parser = version_subparsers.add_parser("set", help="Set specific version")
    set_parser.add_argument("container_name", help="Name of the container")
    set_parser.add_argument("version", help="Version to set (format: X.Y.Z)")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build container image")
    build_parser.add_argument("container_name", help="Name of the container to build")
    build_parser.add_argument("--version", "-v", help="Specify the version to build")
    build_parser.add_argument("--push", action="store_true", help="Push the image after building")
    build_parser.add_argument("--registry", help="Specify the registry to push to")
    build_parser.add_argument("--no-latest", action="store_true", help="Don't tag as latest")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate container structure")
    validate_parser.add_argument("container_name", help="Name of the container to validate")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available containers")
    
    args = parser.parse_args()
    
    if args.command == "version":
        if not args.version_action:
            version_parser.print_help()
            sys.exit(1)
        handle_version_command(args)
    
    elif args.command == "build":
        handle_build_command(args)
    
    elif args.command == "validate":
        handle_validate_command(args)
    
    elif args.command == "list":
        containers = list_containers()
        if containers:
            print("Available containers:")
            for container in containers:
                try:
                    version = get_current_version(container)
                    print(f"  - {container} (v{version})")
                except ValueError:
                    print(f"  - {container} (version unknown)")
        else:
            print("No containers found")
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 