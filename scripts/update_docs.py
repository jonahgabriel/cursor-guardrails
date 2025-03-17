#!/usr/bin/env python3
"""
Documentation Generator

Automatically generates and updates documentation for services based on standardization rules.
Extracts API documentation, configuration details, and maintains consistent structure.
"""

import os
import sys
import containers.scripts.yaml
import logging
import containers.scripts.inspect
import containers.scripts.importlib
import containers.scripts.importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class DocGenerator:
    """Generates and updates documentation following project standards."""
    
    def __init__(self, rules_file: str = ".cursor/standardization.cursorrules"):
        """Initialize the generator with rules from the specified file."""
        self.rules_file = Path(rules_file)
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        """Load rules from the YAML file."""
        try:
            with open(self.rules_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load rules file: {e}")
            sys.exit(1)

    def _import_module(self, module_path: str) -> Optional[Any]:
        """Dynamically import a module from file path."""
        try:
            spec = importlib.util.spec_from_file_location(
                module_path.replace('/', '.').replace('.py', ''),
                module_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        except Exception as e:
            logger.warning(f"Failed to import module {module_path}: {e}")
        return None

    def _extract_docstring(self, obj: Any) -> str:
        """Extract and format docstring from an object."""
        doc = inspect.getdoc(obj) or ""
        return doc.strip()

    def _generate_api_docs(self, service_dir: Path) -> str:
        """Generate API documentation from FastAPI endpoints."""
        api_docs = ["## API Reference\n"]
        main_path = service_dir / "api" / "main.py"
        routes_path = service_dir / "api" / "routes.py"
        
        # Document main endpoints
        if main_path.exists():
            main_module = self._import_module(str(main_path))
            if main_module and hasattr(main_module, 'app'):
                for route in main_module.app.routes:
                    if route.path in ["/health", "/version"]:
                        api_docs.append(f"### {route.path}")
                        api_docs.append(f"**Method:** {route.methods}")
                        if route.endpoint.__doc__:
                            api_docs.append(f"\n{route.endpoint.__doc__.strip()}\n")
                        api_docs.append("")

        # Document custom routes
        if routes_path.exists():
            routes_module = self._import_module(str(routes_path))
            if routes_module and hasattr(routes_module, 'router'):
                for route in routes_module.router.routes:
                    api_docs.append(f"### {route.path}")
                    api_docs.append(f"**Method:** {route.methods}")
                    if route.endpoint.__doc__:
                        api_docs.append(f"\n{route.endpoint.__doc__.strip()}\n")
                    api_docs.append("")

        return "\n".join(api_docs)

    def _generate_config_docs(self, service_dir: Path) -> str:
        """Generate configuration documentation."""
        config_docs = ["## Configuration\n"]
        settings_path = service_dir / "config" / "settings.py"
        
        if settings_path.exists():
            settings_module = self._import_module(str(settings_path))
            if settings_module and hasattr(settings_module, 'Settings'):
                settings_class = settings_module.Settings
                config_docs.append("### Environment Variables\n")
                
                # Get annotations (type hints) for settings
                annotations = settings_class.__annotations__
                
                for var_name, var_type in annotations.items():
                    default_value = getattr(settings_class, var_name, None)
                    config_docs.append(f"- `{var_name}` ({var_type.__name__})")
                    if default_value is not None:
                        config_docs.append(f"  - Default: `{default_value}`")
                config_docs.append("")

        return "\n".join(config_docs)

    def _generate_development_docs(self, service_dir: Path) -> str:
        """Generate development documentation."""
        return """## Development

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run tests:
   ```bash
   pytest
   ```

4. Start the service:
   ```bash
   python -m api.main
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document all public functions and classes
- Write unit tests for new features

### Testing

- Write unit tests in `tests/unit/`
- Write integration tests in `tests/integration/`
- Use pytest fixtures for common test setup
- Aim for high test coverage

"""

    def _generate_deployment_docs(self, service_dir: Path) -> str:
        """Generate deployment documentation."""
        return """## Deployment

### Docker

Build the service:
```bash
docker build -t service-name .
```

Run the service:
```bash
docker run -p 8000:8000 service-name
```

### Environment Variables

Ensure all required environment variables are set in your deployment environment.
See the Configuration section for details.

### Health Checks

The service provides a health check endpoint at `/health` that should be used
for monitoring and container orchestration.

### Monitoring

The service exposes the following metrics:
- `requests_total`: Total number of requests
- `request_duration`: Request duration histogram
- `errors_total`: Total number of errors

"""

    def _update_readme(self, service_dir: Path):
        """Update the main README.md with generated documentation."""
        readme_path = service_dir / "README.md"
        if not readme_path.exists():
            logger.warning(f"README.md not found in {service_dir}")
            return

        # Read existing content
        with open(readme_path, 'r') as f:
            content = f.read()

        # Extract service name and overview
        service_name = ""
        overview = ""
        name_match = re.search(r'# (.*?)\n', content)
        if name_match:
            service_name = name_match.group(1)
        overview_match = re.search(r'## Overview\n\n(.*?)\n\n', content, re.DOTALL)
        if overview_match:
            overview = overview_match.group(1)

        # Generate new documentation
        new_content = [
            f"# {service_name}\n",
            "## Overview\n",
            f"{overview}\n",
            self._generate_config_docs(service_dir),
            self._generate_api_docs(service_dir),
            self._generate_development_docs(service_dir),
            self._generate_deployment_docs(service_dir)
        ]

        # Write updated content
        with open(readme_path, 'w') as f:
            f.write("\n".join(new_content))

    def _generate_api_reference(self, service_dir: Path):
        """Generate detailed API reference documentation."""
        api_doc_path = service_dir / "docs" / "API.md"
        api_content = [
            "# API Reference\n",
            "## Overview\n",
            "This document provides detailed information about the service's API endpoints.\n",
            self._generate_api_docs(service_dir)
        ]
        
        os.makedirs(api_doc_path.parent, exist_ok=True)
        with open(api_doc_path, 'w') as f:
            f.write("\n".join(api_content))

    def update_docs(self, service_dir: str = "."):
        """Update all documentation for the service."""
        service_path = Path(service_dir)
        if not service_path.exists():
            logger.error(f"Service directory not found: {service_dir}")
            sys.exit(1)

        logger.info(f"Updating documentation for service in {service_dir}")
        
        # Update main README
        self._update_readme(service_path)
        
        # Generate API reference
        self._generate_api_reference(service_path)
        
        logger.info("Documentation updated successfully!")
        logger.info("\nGenerated/updated files:")
        logger.info("- README.md")
        logger.info("- docs/API.md")

def main():
    """Main entry point for documentation generation."""
    import argparse
    parser = argparse.ArgumentParser(description="Update service documentation.")
    parser.add_argument("--service-dir", default=".", help="Service directory to update docs for")
    args = parser.parse_args()
    
    generator = DocGenerator()
    generator.update_docs(args.service_dir)

if __name__ == "__main__":
    main() 