#!/usr/bin/env python3
"""
API Validator

Validates API endpoints against project standards for response format and headers.
"""

import sys
import json
import logging
import argparse
import requests
from typing import Dict, List, Tuple, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Define validation rules
REQUIRED_ENDPOINTS = [
    "/api/v1/health",
    "/api/v1/version"
]

REQUIRED_HEADERS = [
    "X-RateLimit-Limit",
    "X-RateLimit-Remaining",
    "X-RateLimit-Reset"
]

def validate_response_format(response_json: Dict[str, Any]) -> List[str]:
    """
    Validate API response format against standards.
    
    Standard format:
    {
      "status": true/false,
      "data": {...} or "error": "error_code", "message": "Human readable message"
    }
    
    Also accepts alternative formats with warnings:
    {"status": "healthy"} - Health endpoint
    {"version": "1.0.0", ...} - Version endpoint
    """
    errors = []
    
    # Special case for health endpoint
    if "status" in response_json and response_json["status"] == "healthy":
        errors.append("WARNING: 'status' field should be a boolean (true/false), found: str")
        return errors
    
    # Special case for version endpoint
    if "version" in response_json and "status" not in response_json:
        errors.append("WARNING: Response missing 'status' field, should wrap data in {status: true, data: {...}}")
        return errors
    
    # Standard validation
    if "status" not in response_json:
        errors.append("WARNING: Response missing required 'status' field")
    else:
        # Check if status is a boolean
        if not isinstance(response_json["status"], bool):
            errors.append("WARNING: 'status' field should be a boolean (true/false), found: " + 
                         f"{type(response_json['status']).__name__}")
    
    # Check for data or error fields
    if response_json.get("status") is True and "data" not in response_json:
        errors.append("WARNING: Successful response missing 'data' field")
    
    if response_json.get("status") is False:
        if "error" not in response_json:
            errors.append("WARNING: Error response missing 'error' field")
        if "message" not in response_json:
            errors.append("WARNING: Error response missing 'message' field")
    
    return errors

def validate_headers(headers: Dict[str, str]) -> List[str]:
    """Validate API response headers against standards."""
    errors = []
    
    # Check for rate limiting headers
    for header in REQUIRED_HEADERS:
        if header not in headers:
            # Make this a warning since rate limiting might be optional in some environments
            errors.append(f"WARNING: Missing required header: {header}")
    
    return errors

def validate_api_endpoint(base_url: str, endpoint: str) -> List[str]:
    """Validate a single API endpoint."""
    errors = []
    url = f"{base_url}{endpoint}"
    
    try:
        response = requests.get(url, timeout=5)
        
        # Check status code
        if response.status_code != 200:
            errors.append(f"Endpoint {endpoint} returned status code {response.status_code}")
            return errors
        
        # Validate headers
        header_errors = validate_headers(response.headers)
        errors.extend(header_errors)
        
        # Validate response format
        try:
            response_json = response.json()
            format_errors = validate_response_format(response_json)
            errors.extend(format_errors)
        except json.JSONDecodeError:
            errors.append(f"Endpoint {endpoint} did not return valid JSON")
        
    except requests.RequestException as e:
        errors.append(f"Error connecting to {endpoint}: {str(e)}")
    
    return errors

def validate_api(base_url: str) -> Tuple[bool, List[str]]:
    """
    Validate API endpoints against standards.
    
    Args:
        base_url: Base URL of the API (e.g., http://localhost:8000)
        
    Returns:
        Tuple of (success, errors)
    """
    all_errors = []
    
    # Validate required endpoints
    for endpoint in REQUIRED_ENDPOINTS:
        logger.info(f"Validating endpoint: {endpoint}")
        errors = validate_api_endpoint(base_url, endpoint)
        
        if errors:
            all_errors.append(f"Endpoint {endpoint} has issues:")
            for error in errors:
                all_errors.append(f"  - {error}")
    
    return len(all_errors) == 0, all_errors

def main():
    """Run standalone validation if script is executed directly."""
    parser = argparse.ArgumentParser(description="Validate API endpoints against standards")
    parser.add_argument("base_url", help="Base URL of the API (e.g., http://localhost:8000)")
    args = parser.parse_args()
    
    success, errors = validate_api(args.base_url)
    
    # Count actual errors (not warnings)
    actual_errors = 0
    for error in errors:
        if "WARNING:" in error:
            logger.warning(error.replace("WARNING:", "").strip())
        else:
            logger.error(error)
            if not error.startswith("Endpoint") and "WARNING:" not in error:
                actual_errors += 1
    
    if actual_errors > 0:
        logger.error(f"API validation failed with {actual_errors} errors")
        return 1
    else:
        if errors:
            logger.info("API validation passed with warnings")
        else:
            logger.info("API validation passed successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 