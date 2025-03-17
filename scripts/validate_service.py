#!/usr/bin/env python3
"""Script to validate services against standardization templates."""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import toml
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

class ServiceValidator:
    """Validates a service against standardization templates."""
    
    def __init__(self, service_path: str):
        """Initialize validator with service path."""
        self.service_path = Path(service_path)
        self.service_name = self.service_path.name
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_structure(self) -> bool:
        """Validate service directory structure."""
        with console.status("[bold blue]Validating service structure..."):
            required_files = [
                "Dockerfile",
                "pyproject.toml",
                "src",
                "tests",
                "README.md"
            ]
            
            missing_files = [
                f for f in required_files 
                if not (self.service_path / f).exists()
            ]
            
            if missing_files:
                self.errors.append(f"Missing required files/directories: {', '.join(missing_files)}")
                return False
            
            # Check src directory structure
            src_dir = self.service_path / "src" / self.service_name
            if not src_dir.exists():
                self.errors.append(f"Missing source directory: {src_dir}")
                return False
            
            # Check tests structure
            tests_dir = self.service_path / "tests"
            required_test_dirs = ["unit", "integration"]
            missing_test_dirs = [
                d for d in required_test_dirs 
                if not (tests_dir / d).exists()
            ]
            if missing_test_dirs:
                self.warnings.append(f"Missing test directories: {', '.join(missing_test_dirs)}")
            
            return True
    
    def validate_pyproject_toml(self) -> bool:
        """Validate pyproject.toml against template."""
        with console.status("[bold blue]Validating pyproject.toml..."):
            try:
                # Read service pyproject.toml
                pyproject_path = self.service_path / "pyproject.toml"
                with open(pyproject_path) as f:
                    service_pyproject = toml.load(f)
                
                # Read template
                template_path = Path("docs/standards/python/PYPROJECT_TEMPLATE.toml")
                with open(template_path) as f:
                    template = toml.load(f)
                
                # Check required sections
                required_sections = [
                    "tool.poetry",
                    "tool.poetry.dependencies",
                    "tool.poetry.group.dev.dependencies",
                    "build-system",
                    "tool.pytest.ini_options",
                    "tool.black",
                    "tool.isort",
                    "tool.mypy",
                    "tool.coverage.run",
                    "tool.coverage.report"
                ]
                
                for section in required_sections:
                    parts = section.split(".")
                    current = service_pyproject
                    for part in parts:
                        if part not in current:
                            self.errors.append(f"Missing required section in pyproject.toml: {section}")
                            return False
                        current = current[part]
                
                return True
                
            except Exception as e:
                self.errors.append(f"Error validating pyproject.toml: {str(e)}")
                return False
    
    def validate_dockerfile(self) -> bool:
        """Validate Dockerfile against template."""
        with console.status("[bold blue]Validating Dockerfile..."):
            try:
                # Read service Dockerfile
                dockerfile_path = self.service_path / "Dockerfile"
                with open(dockerfile_path) as f:
                    service_dockerfile = f.read()
                
                # Read template
                template_path = Path("docs/standards/docker/DOCKERFILE_TEMPLATE")
                with open(template_path) as f:
                    template = f.read()
                
                # Check for required components
                required_components = [
                    "FROM python:3.11-slim",
                    "PYTHONUNBUFFERED=1",
                    "POETRY_VERSION",
                    "HEALTHCHECK",
                    "EXPOSE",
                    "CMD"
                ]
                
                for component in required_components:
                    if component not in service_dockerfile:
                        self.errors.append(f"Missing required component in Dockerfile: {component}")
                        return False
                
                return True
                
            except Exception as e:
                self.errors.append(f"Error validating Dockerfile: {str(e)}")
                return False
    
    def check_environment_variables(self) -> bool:
        """Check if all required environment variables are set."""
        with console.status("[bold blue]Checking environment variables..."):
            try:
                # Read .env.example
                env_example_path = Path(".env.example")
                required_vars = []
                
                with open(env_example_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            var_name = line.split("=")[0]
                            required_vars.append(var_name)
                
                # Check if variables are set in environment
                missing_vars = [
                    var for var in required_vars 
                    if not os.getenv(var)
                ]
                
                if missing_vars:
                    self.warnings.append(f"Missing environment variables: {', '.join(missing_vars)}")
                    return False
                
                return True
                
            except Exception as e:
                self.errors.append(f"Error checking environment variables: {str(e)}")
                return False
    
    def check_container_health(self, timeout: int = 60) -> bool:
        """Check if service containers are healthy using docker-compose."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            try:
                task = progress.add_task(
                    description="[bold blue]Checking container health...",
                    total=None
                )
                
                start_time = time.time()
                while time.time() - start_time < timeout:
                    # Use docker-compose ps to check container status
                    result = subprocess.run(
                        ["./dev", "ps", self.service_name],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if result.returncode != 0:
                        time.sleep(1)
                        continue
                    
                    # Check if container is running and healthy
                    if "Up" in result.stdout and "(healthy)" in result.stdout:
                        return True
                    elif "Up" in result.stdout and "(unhealthy)" in result.stdout:
                        self.errors.append("Container health check failed")
                        return False
                    
                    time.sleep(1)
                
                self.errors.append("Container health check timed out")
                return False
                
            except Exception as e:
                self.errors.append(f"Error checking container health: {str(e)}")
                return False
    
    def run_tests(self) -> bool:
        """Run service tests."""
        with console.status("[bold blue]Running tests..."):
            try:
                # Run tests using run_tests.py as per testing rules
                result = subprocess.run(
                    [
                        "python", "run_tests.py", 
                        self.service_name, 
                        "--type", "unit", 
                        "--extra", "--asyncio-mode=auto --log-cli-level=INFO"
                    ],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    self.errors.append("Tests failed:")
                    self.errors.append(result.stderr)
                    return False
                
                return True
                
            except Exception as e:
                self.errors.append(f"Error running tests: {str(e)}")
                return False
    
    def check_python_path(self) -> Tuple[bool, Optional[str]]:
        """Check PYTHONPATH configuration."""
        try:
            result = subprocess.run(
                [
                    "docker", "compose", "exec",
                    self.service_name,
                    "python", "-c",
                    "import sys; print('\\n'.join(sys.path))"
                ],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, None
            
            return True, result.stdout
            
        except Exception as e:
            self.errors.append(f"Error checking PYTHONPATH: {str(e)}")
            return False, None
    
    def validate(self) -> bool:
        """Run all validations."""
        console.print(Panel(f"[bold blue]Validating {self.service_name} service"))
        
        validations = [
            ("Structure", self.validate_structure),
            ("pyproject.toml", self.validate_pyproject_toml),
            ("Dockerfile", self.validate_dockerfile),
            ("Environment", self.check_environment_variables),
            ("Container Health", self.check_container_health),
            ("Tests", self.run_tests)
        ]
        
        table = Table(show_header=True)
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="bold")
        
        all_passed = True
        for name, func in validations:
            try:
                passed = func()
                status = "[green]✓ Passed" if passed else "[red]✗ Failed"
                table.add_row(name, status)
                all_passed = all_passed and passed
            except Exception as e:
                table.add_row(name, f"[red]✗ Error: {str(e)}")
                all_passed = False
        
        console.print(table)
        
        if self.warnings:
            console.print("\n[yellow]Warnings:")
            for warning in self.warnings:
                console.print(f"[yellow]• {warning}")
        
        if self.errors:
            console.print("\n[red]Errors:")
            for error in self.errors:
                console.print(f"[red]• {error}")
        
        if all_passed:
            console.print("\n[green]All validations passed!")
        else:
            console.print("\n[red]Some validations failed.")
            
            # Print diagnostic information
            console.print("\n[bold blue]Diagnostic Information:")
            
            # Check Python path
            success, python_path = self.check_python_path()
            if success:
                console.print("\n[bold]Python Path:")
                console.print(python_path)
            
            # Check container logs using docker-compose
            try:
                result = subprocess.run(
                    ["./dev", "logs", self.service_name],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    console.print("\n[bold]Container Logs:")
                    console.print(result.stdout)
            except Exception as e:
                console.print(f"[red]Error getting container logs: {str(e)}")
        
        return all_passed

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate a service against project standards"
    )
    parser.add_argument(
        "service_path",
        help="Path to the service directory"
    )
    args = parser.parse_args()
    
    validator = ServiceValidator(args.service_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 