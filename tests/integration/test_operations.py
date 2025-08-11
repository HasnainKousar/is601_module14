import pytest
from app.operations import add, subtract, multiply, divide

# Addition tests
def test_add_integers():
    assert add(2, 3) == 5

def test_add_floats():
    assert add(2.5, 3.5) == 6.0

# Subtraction tests
def test_subtract_integers():
    assert subtract(5, 3) == 2

def test_subtract_floats():
    assert subtract(5.5, 2.5) == 3.0

# Multiplication tests
def test_multiply_integers():
    assert multiply(2, 3) == 6

def test_multiply_floats():
    assert multiply(2.5, 4) == 10.0

# Division tests
def test_divide_integers():
    assert divide(6, 3) == 2.0

def test_divide_floats():
    assert divide(7.5, 2.5) == 3.0

# Division by zero
def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        divide(5, 0)
