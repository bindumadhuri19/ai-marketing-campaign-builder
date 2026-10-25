"""
Validation utilities for URL, UTM, and placeholder detection.
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs
import validators as validator_lib


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
    
    Returns:
        True if valid URL format, False otherwise
    """
    if not url:
        return False
    
    # Use validators library for robust URL validation
    return validator_lib.url(url) is True


def extract_utm_params(url: str) -> Dict[str, str]:
    """
    Extract UTM parameters from URL.
    
    Args:
        url: URL string to parse
    
    Returns:
        Dict of UTM parameters found (e.g., {'utm_source': 'email', 'utm_campaign': 'launch'})
    """
    if not url:
        return {}
    
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Extract only UTM parameters
        utm_params = {}
        for key, value in query_params.items():
            if key.startswith('utm_'):
                # parse_qs returns lists, take first value
                utm_params[key] = value[0] if value else ''
        
        return utm_params
    except Exception:
        return {}


def detect_placeholders(text: str) -> List[str]:
    """
    Detect unreplaced placeholder text in content.
    
    Patterns detected:
    - {{variable}}
    - [VARIABLE]
    - {VARIABLE} (only if not part of {{variable}})
    
    Args:
        text: Text to scan for placeholders
    
    Returns:
        List of detected placeholder strings
    """
    if not text:
        return []
    
    placeholders = []
    
    # Pattern 1: {{variable}} (must check first to avoid overlap with {VARIABLE})
    pattern1 = re.findall(r'\{\{[^}]+\}\}', text)
    placeholders.extend(pattern1)
    
    # Pattern 2: [UPPERCASE_TEXT]
    pattern2 = re.findall(r'\[[A-Z_]+\]', text)
    placeholders.extend(pattern2)
    
    # Pattern 3: {UPPERCASE_TEXT} - but not if it's inside {{...}}
    # Remove {{...}} patterns temporarily to avoid double-matching
    text_without_double_braces = re.sub(r'\{\{[^}]+\}\}', '', text)
    pattern3 = re.findall(r'\{[A-Z_]+\}', text_without_double_braces)
    placeholders.extend(pattern3)
    
    return placeholders


def url_in_text(url: str, text: str) -> bool:
    """
    Check if URL or domain appears in text.
    
    Args:
        url: URL to search for
        text: Text to search in
    
    Returns:
        True if URL or its domain is found in text
    """
    if not url or not text:
        return False
    
    # Check for full URL
    if url in text:
        return True
    
    # Check for domain
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain and domain in text:
            return True
    except Exception:
        pass
    
    return False


def check_character_limit(text: str, limit: Optional[int]) -> Dict[str, any]:
    """
    Check if text exceeds character limit.
    
    Args:
        text: Text to check
        limit: Character limit (None means no limit)
    
    Returns:
        Dict with 'passes' (bool), 'count' (int), 'limit' (int or None)
    """
    if not text:
        text = ""
    
    count = len(text)
    
    if limit is None:
        return {"passes": True, "count": count, "limit": None}
    
    return {
        "passes": count <= limit,
        "count": count,
        "limit": limit
    }
