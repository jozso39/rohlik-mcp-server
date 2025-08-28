def sanitize_string(text):
    """Clean and sanitize input strings."""
    if isinstance(text, str):
        return text.strip()
    return ""