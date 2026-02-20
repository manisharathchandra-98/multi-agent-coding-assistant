import pytest

"""Module for adding two numbers with proper type validation and edge case handling."""

import numbers
import math


def add_two_numbers(num1: int | float, num2: int | float) -> int | float:
    """
    Add two numbers together and return their sum.

    This function accepts integers or floating-point numbers and returns their sum.
    It includes input validation and handles edge cases like overflow to infinity.

    Args:
        num1: The first number to add. Must be an int or float.
        num2: The second number to add. Must be an int or float.

    Returns:
        The sum of num1 and num2. Returns int if both inputs are integers,
        otherwise returns float. Returns float('inf') or float('-inf') if
        the result overflows.

    Raises:
        TypeError: If either parameter is not a numeric type (int or float).
            Complex numbers, strings, lists, None, and other non-numeric
            types will raise this exception.

    Examples:
        >>> add_two_numbers(2, 3)
        5
        >>> add_two_numbers(2.5, 3.5)
        6.0
        >>> add_two_numbers(2, 3.5)
        5.5
        >>> add_two_numbers(-5, 10)
        5
    """
    if not isinstance(num1, numbers.Number) or isinstance(num1, (complex, bool)):
        raise TypeError(
            f"num1 must be an int or float, got {type(num1).__name__}"
        )
    
    if not isinstance(num2, numbers.Number) or isinstance(num2, (complex, bool)):
        raise TypeError(
            f"num2 must be an int or float, got {type(num2).__name__}"
        )
    
    result = num1 + num2
    
    if isinstance(result, float) and math.isinf(result):
        return result
    
    if isinstance(num1, int) and isinstance(num2, int):
        return int(result)
    
    return float(result)


if __name__ == "__main__":
    print(f"add_two_numbers(2, 3) = {add_two_numbers(2, 3)}")
    print(f"add_two_numbers(2.5, 3.5) = {add_two_numbers(2.5, 3.5)}")
    print(f"add_two_numbers(2, 3.5) = {add_two_numbers(2, 3.5)}")
    print(f"add_two_numbers(-5, 10) = {add_two_numbers(-5, 10)}")
    print(f"add_two_numbers(0, 0) = {add_two_numbers(0, 0)}")
    
    large_float = 1e308
    print(f"add_two_numbers({large_float}, {large_float}) = {add_two_numbers(large_float, large_float)}")
    
    try:
        add_two_numbers("5", 3)
    except TypeError as e:
        print(f"TypeError caught: {e}")
    
    try:
        add_two_numbers(5, None)
    except TypeError as e:
        print(f"TypeError caught: {e}")

# ── Tests ──

"""Module for adding two numbers with proper type validation and edge case handling."""

import numbers
import math


def add_two_numbers(num1: int | float, num2: int | float) -> int | float:
    """
    Add two numbers together and return their sum.

    This function accepts integers or floating-point numbers and returns their sum.
    It includes input validation and handles edge cases like overflow to infinity.

    Args:
        num1: The first number to add. Must be an int or float.
        num2: The second number to add. Must be an int or float.

    Returns:
        The sum of num1 and num2. Returns int if both inputs are integers,
        otherwise returns float. Returns float('inf') or float('-inf') if
        the result overflows.

    Raises:
        TypeError: If either parameter is not a numeric type (int or float).
            Complex numbers, strings, lists, None, and other non-numeric
            types will raise this exception.

    Examples:
        >>> add_two_numbers(2, 3)
        5
        >>> add_two_numbers(2.5, 3.5)
        6.0
        >>> add_two_numbers(2, 3.5)
        5.5
        >>> add_two_numbers(-5, 10)
        5
    """
    if not isinstance(num1, numbers.Number) or isinstance(num1, (complex, bool)):
        raise TypeError(
            f"num1 must be an int or float, got {type(num1).__name__}"
        )
    
    if not isinstance(num2, numbers.Number) or isinstance(num2, (complex, bool)):
        raise TypeError(
            f"num2 must be an int or float, got {type(num2).__name__}"
        )
    
    result = num1 + num2
    
    if isinstance(result, float) and math.isinf(result):
        return result
    
    if isinstance(num1, int) and isinstance(num2, int):
        return int(result)
    
    return float(result)


import pytest


class TestAddTwoNumbersHappyPath:
    """Test normal valid inputs that should work correctly."""
    
    def test_add_two_positive_integers(self):
        result = add_two_numbers(2, 3)
        assert result == 5
        assert isinstance(result, int)
    
    def test_add_two_negative_integers(self):
        result = add_two_numbers(-5, -3)
        assert result == -8
        assert isinstance(result, int)
    
    def test_add_positive_and_negative_integers(self):
        result = add_two_numbers(-5, 10)
        assert result == 5
        assert isinstance(result, int)
    
    def test_add_two_positive_floats(self):
        result = add_two_numbers(2.5, 3.5)
        assert result == 6.0
        assert isinstance(result, float)
    
    def test_add_two_negative_floats(self):
        result = add_two_numbers(-2.5, -3.5)
        assert result == -6.0
        assert isinstance(result, float)
    
    def test_add_int_and_float(self):
        result = add_two_numbers(2, 3.5)
        assert result == 5.5
        assert isinstance(result, float)
    
    def test_add_float_and_int(self):
        result = add_two_numbers(3.5, 2)
        assert result == 5.5
        assert isinstance(result, float)
    
    def test_add_large_integers(self):
        result = add_two_numbers(10**100, 10**100)
        assert result == 2 * 10**100
        assert isinstance(result, int)


class TestAddTwoNumbersZeroBoundary:
    """Test boundary inputs involving zero."""
    
    def test_add_zero_integers(self):
        result = add_two_numbers(0, 0)
        assert result == 0
        assert isinstance(result, int)
    
    def test_add_zero_to_positive_int(self):
        result = add_two_numbers(0, 5)
        assert result == 5
        assert isinstance(result, int)
    
    def test_add_positive_int_to_zero(self):
        result = add_two_numbers(5, 0)
        assert result == 5
        assert isinstance(result, int)
    
    def test_add_zero_float_to_zero_float(self):
        result = add_two_numbers(0.0, 0.0)
        assert result == 0.0
        assert isinstance(result, float)
    
    def test_add_zero_int_to_float(self):
        result = add_two_numbers(0, 5.5)
        assert result == 5.5
        assert isinstance(result, float)
    
    def test_add_negative_to_positive_equals_zero(self):
        result = add_two_numbers(-5, 5)
        assert result == 0
        assert isinstance(result, int)


class TestAddTwoNumbersFloatingPointOverflow:
    """Test floating-point overflow edge cases."""
    
    def test_positive_overflow_to_infinity(self):
        large_float = 1e308
        result = add_two_numbers(large_float, large_float)
        assert result == float('inf')
        assert math.isinf(result)
    
    def test_negative_overflow_to_negative_infinity(self):
        large_negative_float = -1e308
        result = add_two_numbers(large_negative_float, large_negative_float)
        assert result == float('-inf')
        assert math.isinf(result)
    
    def test_adding_infinity_values(self):
        result = add_two_numbers(float('inf'), 1.0)
        assert result == float('inf')
    
    def test_adding_negative_infinity_values(self):
        result = add_two_numbers(float('-inf'), 1.0)
        assert result == float('-inf')
    
    def test_adding_two_infinities(self):
        result = add_two_numbers(float('inf'), float('inf'))
        assert result == float('inf')
    
    def test_very_small_floats(self):
        result = add_two_numbers(1e-308, 1e-308)
        assert result == 2e-308
        assert isinstance(result, float)


class TestAddTwoNumbersTypeErrors:
    """Test that TypeError is raised for invalid inputs."""
    
    def test_string_first_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers("5", 3)
        assert "num1 must be an int or float" in str(exc_info.value)
        assert "str" in str(exc_info.value)
    
    def test_string_second_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers(3, "5")
        assert "num2 must be an int or float" in str(exc_info.value)
        assert "str" in str(exc_info.value)
    
    def test_none_first_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers(None, 3)
        assert "num1 must be an int or float" in str(exc_info.value)
        assert "NoneType" in str(exc_info.value)
    
    def test_none_second_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers(5, None)
        assert "num2 must be an int or float" in str(exc_info.value)
        assert "NoneType" in str(exc_info.value)
    
    def test_list_first_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers([1, 2], 3)
        assert "num1 must be an int or float" in str(exc_info.value)
        assert "list" in str(exc_info.value)
    
    def test_list_second_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers(3, [1, 2])
        assert "num2 must be an int or float" in str(exc_info.value)
        assert "list" in str(exc_info.value)
    
    def test_empty_list_argument(self):
        with pytest.raises(TypeError):
            add_two_numbers([], 3)
    
    def test_empty_string_argument(self):
        with pytest.raises(TypeError):
            add_two_numbers("", 3)
    
    def test_dict_argument(self):
        with pytest.raises(TypeError):
            add_two_numbers({}, 3)
    
    def test_complex_first_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers(1+2j, 3)
        assert "num1 must be an int or float" in str(exc_info.value)
        assert "complex" in str(exc_info.value)
    
    def test_complex_second_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers(3, 1+2j)
        assert "num2 must be an int or float" in str(exc_info.value)
        assert "complex" in str(exc_info.value)
    
    def test_bool_true_first_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers(True, 3)
        assert "num1 must be an int or float" in str(exc_info.value)
        assert "bool" in str(exc_info.value)
    
    def test_bool_false_second_argument(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers(3, False)
        assert "num2 must be an int or float" in str(exc_info.value)
        assert "bool" in str(exc_info.value)
    
    def test_both_arguments_invalid(self):
        with pytest.raises(TypeError) as exc_info:
            add_two_numbers("hello", "world")
        assert "num1 must be an int or float" in str(exc_info.value)


class TestAddTwoNumbersSpecialCases:
    """Test special and tricky cases."""
    
    def test_nan_propagation(self):
        result = add_two_numbers(float('nan'), 5.0)
        assert math.isnan(result)
    
    def test_nan_plus_nan(self):
        result = add_two_numbers(float('nan'), float('nan'))
        assert math.isnan(result)
    
    def test_negative_zero(self):
        result = add_two_numbers(-0.0, 0.0)
        assert result == 0.0
        assert isinstance(result, float)
    
    def test_very_small_difference(self):
        result = add_two_numbers(0.1, 0.2)
        assert abs(result - 0.3) < 1e-10
        assert isinstance(result, float)
    
    def test_max_int_values(self):
        import sys
        large_int = sys.maxsize
        result = add_two_numbers(large_int, 1)
        assert result == large_int + 1
        assert isinstance(result, int)
    
    def test_mixed_sign_floats(self):
        result = add_two_numbers(-2.5, 2.5)
        assert result == 0.0
        assert isinstance(result, float)