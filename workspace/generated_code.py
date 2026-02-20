def factorial(n: int) -> int:
    """
    Calculate the factorial of a non-negative integer using recursion.

    Args:
        n: A non-negative integer whose factorial is to be computed.

    Returns:
        The factorial of n (n!).

    Raises:
        TypeError: If n is not an integer or is a boolean.
        ValueError: If n is a negative integer.
    """
    if isinstance(n, bool):
        raise TypeError("n must be an integer, not a boolean")
    
    if not isinstance(n, int):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    
    if n == 0:
        return 1
    
    return n * factorial(n - 1)