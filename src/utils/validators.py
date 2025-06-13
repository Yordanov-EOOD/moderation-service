import re
from typing import Dict, Any

def validate_content(content: Any) -> Dict[str, Any]:
    """
    Validate content for toxicity checking
    
    Args:
        content: The content to validate
        
    Returns:
        Dict with 'valid' boolean and 'error' message if invalid
    """
    if content is None:
        return {
            'valid': False,
            'error': 'Content cannot be None'
        }
    
    if not isinstance(content, str):
        return {
            'valid': False,
            'error': 'Content must be a string'
        }
    
    if len(content.strip()) == 0:
        return {
            'valid': False,
            'error': 'Content cannot be empty'
        }
    
    if len(content) > 10000:  # Max content length
        return {
            'valid': False,
            'error': 'Content exceeds maximum length of 10,000 characters'
        }
    
    return {
        'valid': True,
        'error': None
    }

def sanitize_input(text: str) -> str:
    """
    Sanitize input text by removing potentially harmful characters
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes and control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length
    sanitized = sanitized[:10000]
    
    return sanitized.strip()

def validate_yeet_id(yeet_id: Any) -> bool:
    """
    Validate yeet ID format
    
    Args:
        yeet_id: The yeet ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if yeet_id is None:
        return True  # Optional field
    
    if not isinstance(yeet_id, str):
        return False
    
    # Simple validation - alphanumeric and hyphens, reasonable length
    return bool(re.match(r'^[a-zA-Z0-9\-_]{1,50}$', yeet_id))

def validate_user_id(user_id: Any) -> bool:
    """
    Validate user ID format
    
    Args:
        user_id: The user ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if user_id is None:
        return True  # Optional field
    
    if not isinstance(user_id, str):
        return False
    
    # Simple validation - alphanumeric and hyphens, reasonable length
    return bool(re.match(r'^[a-zA-Z0-9\-_]{1,50}$', user_id))
