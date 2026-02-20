import re


def validate_email(email: str) -> bool:
    """
    Validate if a string is a valid email format.
    
    This function checks if the provided email string matches a standard
    email format pattern using regular expressions.
    
    Args:
        email: The email string to validate.
    
    Returns:
        True if the email is valid, False otherwise.
    
    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("john.doe@company.org")
        True
        >>> validate_email("user+tag@domain.co.uk")
        True
        >>> validate_email("invalid-email")
        False
        >>> validate_email("@nodomain.com")
        False
        >>> validate_email("spaces in@email.com")
        False
        >>> validate_email("")
        False
    """
    # Email regex pattern:
    # - Local part: allows letters, digits, dots, hyphens, underscores, and plus signs
    # - @ symbol required
    # - Domain: allows letters, digits, dots, and hyphens
    # - TLD: must be at least 2 characters
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not isinstance(email, str):
        return False
    
    return bool(re.match(pattern, email))


if __name__ == "__main__":
    # Test the function with various examples
    test_emails = [
        "user@example.com",
        "john.doe@company.org",
        "user+tag@domain.co.uk",
        "firstname.lastname@subdomain.example.com",
        "invalid-email",
        "@nodomain.com",
        "noatsign.com",
        "spaces in@email.com",
        "missing@tld.",
        "",
        "valid123@test-domain.net",
    ]
    
    print("Email Validation Results:")
    print("-" * 50)
    for email in test_emails:
        result = validate_email(email)
        status = "✓ Valid" if result else "✗ Invalid"
        print(f"{email!r:40} -> {status}")
