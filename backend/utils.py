"""
Utility functions for the backend
"""

import os
import re
import hashlib
from typing import Optional


def sanitize_name(name: str) -> str:
    """
    Sanitize name for Kubernetes compatibility
    
    Args:
        name: Original name
        
    Returns:
        Sanitized name
    """
    # Convert to lowercase
    name = name.lower()
    
    # Replace spaces and underscores with hyphens
    name = name.replace(' ', '-').replace('_', '-')
    
    # Remove invalid characters
    name = re.sub(r'[^a-z0-9-]', '', name)
    
    # Remove leading/trailing hyphens
    name = name.strip('-')
    
    # Limit length to 63 characters
    if len(name) > 63:
        # Keep first 50 chars and add hash of full name
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:8]
        name = name[:50] + '-' + hash_suffix
    
    return name


def parse_model_name(model_str: str) -> str:
    """
    Parse model name from format like "OpenAI gpt-4o"
    
    Args:
        model_str: Model string
        
    Returns:
        Model name
    """
    parts = model_str.split()
    if len(parts) > 1:
        return parts[-1]
    return model_str


def validate_resource_string(resource: str, resource_type: str) -> bool:
    """
    Validate Kubernetes resource string (CPU or memory)
    
    Args:
        resource: Resource string (e.g., "500m", "1Gi")
        resource_type: "cpu" or "memory"
        
    Returns:
        True if valid
    """
    if resource_type == "cpu":
        # Valid formats: "500m", "1", "2", "0.5"
        pattern = r'^(\d+m|\d+\.?\d*)$'
    else:  # memory
        # Valid formats: "512Mi", "1Gi", "2G"
        pattern = r'^(\d+)(Mi|Gi|M|G|Ki|K)?$'
    
    return bool(re.match(pattern, resource))


def get_env_or_raise(key: str, default: Optional[str] = None) -> str:
    """
    Get environment variable or raise error
    
    Args:
        key: Environment variable key
        default: Default value if not found
        
    Returns:
        Environment variable value
        
    Raises:
        ValueError: If environment variable not found and no default
    """
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} not set")
    return value
