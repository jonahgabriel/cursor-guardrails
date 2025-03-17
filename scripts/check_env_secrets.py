#!/usr/bin/env python3

import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

class EnvSecretChecker:
    def __init__(self):
        # Patterns to identify potential secrets/configuration
        self.patterns = {
            'port': r'(?:^|\s|=)(\d{2,5})(?:\s|$|:)',  # Matches potential port numbers
            'password': r'(?i)(?:password|passwd|pwd)[\s]*[=:]\s*["\']?([^"\'\s]+)["\']?',
            'username': r'(?i)(?:username|user|uname)[\s]*[=:]\s*["\']?([^"\'\s]+)["\']?',
            'api_key': r'(?i)(?:api[_-]?key|token|secret)[\s]*[=:]\s*["\']?([^"\'\s]+)["\']?',
            'url': r'(?i)(?:url|host|endpoint)[\s]*[=:]\s*["\']?(http[s]?://[^"\'\s]+)["\']?',
            'email': r'[\w\.-]+@[\w\.-]+\.\w+',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }

        # Known safe values that should be ignored
        self.safe_values = {
            'port': {'80', '443', '3000', '8080'},  # Common development ports
            'username': {'postgres', 'root', 'admin'},  # Common default usernames
            'password': {'postgres'},  # Common default passwords
            'host': {'localhost', '127.0.0.1', '0.0.0.0'}  # Common development hosts
        }

        # Files and directories to ignore
        self.ignore_paths = {
            '.git',
            'node_modules',
            'venv',
            '.venv',
            '__pycache__',
            '.pytest_cache',
            'dist',
            'build',
            '.env',
            '.env.example',
            '.env.template',
            'example.env'
        }

        # File extensions to check
        self.check_extensions = {
            '.py',
            '.js',
            '.ts',
            '.jsx',
            '.tsx',
            '.yml',
            '.yaml',
            '.json',
            '.toml',
            '.ini',
            '.conf',
            '.sh',
            '.bash',
            '.zsh',
            '.env',
            'Dockerfile',
            'docker-compose.yml'
        }

    def should_check_file(self, file_path: Path) -> bool:
        """Determine if a file should be checked."""
        # Check if any parent directory is in ignore_paths
        for parent in file_path.parents:
            if parent.name in self.ignore_paths:
                return False

        # Check if file name is in ignore_paths
        if file_path.name in self.ignore_paths:
            return False

        # Check file extension
        return any(
            str(file_path).endswith(ext) for ext in self.check_extensions
        )

    def is_safe_value(self, pattern_type: str, value: str) -> bool:
        """Check if a value is in the safe list."""
        return value in self.safe_values.get(pattern_type, set())

    def check_file(self, file_path: Path) -> List[Tuple[str, str, int, str]]:
        """Check a single file for potential secrets/configuration."""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith(('#', '//', '/*', '*', '--')):
                    continue

                # Check each pattern
                for pattern_type, pattern in self.patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        value = match.group(1)
                        if not self.is_safe_value(pattern_type, value):
                            findings.append((
                                str(file_path),
                                pattern_type,
                                line_num,
                                line.strip()
                            ))

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

        return findings

    def check_directory(self, directory: Path) -> List[Tuple[str, str, int, str]]:
        """Recursively check all files in a directory."""
        findings = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and self.should_check_file(file_path):
                findings.extend(self.check_file(file_path))
                
        return findings

    def format_findings(self, findings: List[Tuple[str, str, int, str]]) -> str:
        """Format findings into a readable report."""
        if not findings:
            return "No potential secrets or configuration values found."

        report = []
        report.append("\nPotential secrets or configuration values found:")
        report.append("=" * 80)

        # Group findings by file
        findings_by_file: Dict[str, List[Tuple[str, int, str]]] = {}
        for file_path, pattern_type, line_num, line in findings:
            if file_path not in findings_by_file:
                findings_by_file[file_path] = []
            findings_by_file[file_path].append((pattern_type, line_num, line))

        # Generate report
        for file_path, file_findings in findings_by_file.items():
            report.append(f"\nFile: {file_path}")
            report.append("-" * 80)
            for pattern_type, line_num, line in file_findings:
                report.append(f"  Line {line_num} ({pattern_type}):")
                report.append(f"    {line}")
            report.append("-" * 80)

        report.append("\nRecommendations:")
        report.append("1. Move these values to environment variables")
        report.append("2. Use a .env file to store sensitive information")
        report.append("3. Reference environment variables in your code instead of hardcoded values")
        report.append("4. Add sensitive files to .gitignore")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(
        description='Check for hardcoded secrets and configuration that should be in .env files'
    )
    parser.add_argument(
        'path',
        type=str,
        help='Path to directory or file to check'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    args = parser.parse_args()

    checker = EnvSecretChecker()
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path {path} does not exist")
        return 1

    findings = []
    if path.is_file():
        if checker.should_check_file(path):
            findings = checker.check_file(path)
    else:
        findings = checker.check_directory(path)

    if args.json:
        import json
        json_findings = [
            {
                'file': f[0],
                'type': f[1],
                'line': f[2],
                'content': f[3]
            }
            for f in findings
        ]
        print(json.dumps(json_findings, indent=2))
    else:
        print(checker.format_findings(findings))

    # Return non-zero exit code if findings were found
    return 1 if findings else 0

if __name__ == "__main__":
    exit(main()) 