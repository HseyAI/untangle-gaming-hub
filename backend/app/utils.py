"""
Utility functions for UNTANGLE.
"""
import re


def normalize_mobile(mobile: str) -> str:
    """
    Normalize mobile number to 10-digit format.

    Removes all non-digit characters and extracts the last 10 digits.
    Handles formats like:
    - "+639171234567" -> "9171234567"
    - "09171234567" -> "9171234567"
    - "9171234567" -> "9171234567"

    Args:
        mobile: Raw mobile number string

    Returns:
        Normalized 10-digit mobile number

    Raises:
        ValueError: If mobile number is invalid
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', mobile)

    # Handle country code (63)
    if digits.startswith('63'):
        digits = digits[2:]

    # Handle leading zero
    if digits.startswith('0'):
        digits = digits[1:]

    # Get last 10 digits
    normalized = digits[-10:] if len(digits) >= 10 else digits

    # Validate length
    if len(normalized) != 10:
        raise ValueError(f"Invalid mobile number: {mobile}. Must be 10 digits after normalization.")

    return normalized
