import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate an email address according to a reasonable subset of RFC 5321/5322 standards.

    Args:
        email (str): The email address string to validate.

    Returns:
        bool: True if the email is valid, False otherwise.

    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("a@example.com")
        True
        >>> validate_email("user@a.co")
        True
        >>> validate_email("user+tag@example.com")
        True
        >>> validate_email("user@@example.com")
        False
        >>> validate_email("user@localhost")
        False
        >>> validate_email("  user@example.com  ")
        False
    """
    if not isinstance(email, str):
        raise TypeError(f"email must be a string, not {type(email).__name__}")

    # Check for leading/trailing whitespace
    if email != email.strip():
        return False

    # Check for empty string
    if not email:
        return False

    # Check for exactly one @ symbol
    if email.count("@") != 1:
        return False

    local_part, domain_part = email.rsplit("@", 1)

    # Validate local part (before @)
    if not local_part:
        return False

    # Check for spaces in local part
    if " " in local_part:
        return False

    # Check for consecutive dots in local part
    if ".." in local_part:
        return False

    # Check for leading/trailing dots in local part
    if local_part.startswith(".") or local_part.endswith("."):
        return False

    # Local part must contain only valid characters (including '+')
    if not re.match(r"^[a-zA-Z0-9._+\-]+$", local_part):
        return False

    # Validate domain part (after @)
    if not domain_part:
        return False

    # Check for spaces in domain part
    if " " in domain_part:
        return False

    # Check for consecutive dots in domain part
    if ".." in domain_part:
        return False

    # Check for leading/trailing dots in domain part
    if domain_part.startswith(".") or domain_part.endswith("."):
        return False

    # Check for at least one dot in domain
    if "." not in domain_part:
        return False

    # Validate domain structure
    domain_parts = domain_part.split(".")

    # Each domain part must be non-empty
    for part in domain_parts:
        if not part:
            return False

        # Each part should only contain alphanumeric and hyphens
        if not re.match(r"^[a-zA-Z0-9-]+$", part):
            return False

        # Each part cannot start or end with hyphen
        if part.startswith("-") or part.endswith("-"):
            return False

    # TLD must be at least 2 characters and contain only letters and numbers
    tld = domain_parts[-1]
    if not re.match(r"^[a-zA-Z0-9]{2,}$", tld):
        return False

    return True