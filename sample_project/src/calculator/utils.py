"""Utility functions for mathematical formatting."""
from typing import List, Union

def format_result(value: Union[int, float], prefix: str = "Result:") -> str:
    """Formats a numeric value into a string with a prefix."""
    return f"{prefix} {value}"

def sum_list(numbers: List[float]) -> float:
    """Calculates the sum of a list of floats."""
    return sum(numbers)