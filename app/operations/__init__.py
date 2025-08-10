###################
# app/operations/__init__.py
###################

"""
A simple arithmetic operations module.
This module provides functions to perform basic arithmetic operations:
- Addition
- Subtraction
- Multiplication
- Division
Each function takes two numbers (int or floats) as input and returns the result (int or float) of the operation.

Usage:
These functions can be imported and used in other modules or integrated into APIs
for performing arithmetic calculations based on user input.

"""

from typing import Union

Number = Union[int, float]

def add(a: Number, b: Number) -> Number:
    """Add two numbers and return the result.
    
    Parameters:
    - a (Number): The first number to add.
    - b (Number): The second number to add.
    
    Returns:
    - Number: The sum of the two numbers.
    
    Example:
    >>> add(2, 3)
    5
    >>> add(2.5, 3.5)
    6.0"""

    #perform addition
    result = a + b
    return result


def subtract(a: Number, b: Number) -> Number:
    """Subtract the second number from the first and return the result.
    
    Parameters:
    - a (Number): The number to subtract from.
    - b (Number): The number to subtract.
    
    Returns:
    - Number: The result of the subtraction.
    
    Example:
    >>> subtract(5, 3)
    2
    >>> subtract(5.5, 2.5)
    3.0"""
    
    #perform subtraction
    result = a - b
    return result


def multiply(a: Number, b: Number) -> Number:
    """Multiply two numbers and return the result.
    
    Parameters:
    - a (Number): The first number to multiply.
    - b (Number): The second number to multiply.
    
    Returns:
    - Number: The product of the two numbers.
    
    Example:
    >>> multiply(2, 3)
    6
    >>> multiply(2.5, 4)
    10.0"""
    
    #perform multiplication
    result = a * b
    return result


def divide(a: Number, b: Number) -> Number:
    """Divide the first number by the second and return the result.
    
    Parameters:
    - a (Number): The number to be divided.
    - b (Number): The number to divide by.
    
    Returns:
    - Number: The result of the division.
    
    Raises:
    - ValueError: If the second number is zero.
    
    Example:
    >>> divide(6, 3)
    2.0
    >>> divide(7.5, 2.5)
    3.0
    >>> divide(5, 0)  # Raises ValueError
    ValueError: Cannot divide by zero.
    """
    #check for division by zero
    if b == 0:
        # raise an error if b is zero
        raise ValueError("Cannot divide by zero.")
    
    #perform division
    result = a / b
    return result

