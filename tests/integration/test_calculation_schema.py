import pytest
import uuid

from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
    AbstractCalculation
)


# Helper function to create a dummy user_id for testing.
def dummy_user_id():
    return uuid.uuid4()

def test_addition_get_result():
    """
    Test that Addition.get_result returns the correct sum.
    """
    values = [7, 8, 2.5]
    addition = Addition(user_id=dummy_user_id(), inputs=values)
    outcome = addition.get_result()
    assert outcome == sum(values), f"Sum should be {sum(values)}, got {outcome}"

def test_subtraction_get_result():
    """
    Test that Subtraction.get_result returns the correct difference.
    """
    values = [15, 4, 2]
    subtraction = Subtraction(user_id=dummy_user_id(), inputs=values)
    # Expected: 15 - 4 - 2 = 9
    outcome = subtraction.get_result()
    assert outcome == 9, f"Difference should be 9, got {outcome}"

def test_multiplication_get_result():
    """
    Test that Multiplication.get_result returns the correct product.
    """
    values = [5, 2, 3]
    multiplication = Multiplication(user_id=dummy_user_id(), inputs=values)
    outcome = multiplication.get_result()
    assert outcome == 30, f"Product should be 30, got {outcome}"

def test_division_get_result():
    """
    Test that Division.get_result returns the correct quotient.
    """
    values = [60, 3, 4]
    division = Division(user_id=dummy_user_id(), inputs=values)
    # Expected: 60 / 3 / 4 = 5
    outcome = division.get_result()
    assert outcome == 5, f"Quotient should be 5, got {outcome}"

def test_division_by_zero():
    """
    Test that Division.get_result raises ValueError when dividing by zero.
    """
    values = [25, 0, 2]
    division = Division(user_id=dummy_user_id(), inputs=values)
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        division.get_result()

def test_calculation_factory_addition():
    """
    Test the Calculation.create factory method for addition.
    """
    values = [4, 5, 6]
    calc = Calculation.create(
        calculation_type='addition',
        user_id=dummy_user_id(),
        inputs=values,
    )
    # Check that the returned instance is an Addition.
    assert isinstance(calc, Addition), "Should be Addition instance."
    assert calc.get_result() == sum(values), "Addition result mismatch."

def test_calculation_factory_subtraction():
    """
    Test the Calculation.create factory method for subtraction.
    """
    values = [12, 7]
    calc = Calculation.create(
        calculation_type='subtraction',
        user_id=dummy_user_id(),
        inputs=values,
    )
    # Expected: 12 - 7 = 5
    assert isinstance(calc, Subtraction), "Should be Subtraction instance."
    assert calc.get_result() == 5, "Subtraction result mismatch."

def test_calculation_factory_multiplication():
    """
    Test the Calculation.create factory method for multiplication.
    """
    values = [2, 6, 2]
    calc = Calculation.create(
        calculation_type='multiplication',
        user_id=dummy_user_id(),
        inputs=values,
    )
    # Expected: 2 * 6 * 2 = 24
    assert isinstance(calc, Multiplication), "Should be Multiplication instance."
    assert calc.get_result() == 24, "Multiplication result mismatch."

def test_calculation_factory_division():
    """
    Test the Calculation.create factory method for division.
    """
    values = [48, 2, 4]
    calc = Calculation.create(
        calculation_type='division',
        user_id=dummy_user_id(),
        inputs=values,
    )
    # Expected: 48 / 2 / 4 = 6
    assert isinstance(calc, Division), "Should be Division instance."
    assert calc.get_result() == 6, "Division result mismatch."

def test_calculation_factory_invalid_type():
    """
    Test that Calculation.create raises a ValueError for an unsupported calculation type.
    """
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create(
            calculation_type='power',  # unsupported type
            user_id=dummy_user_id(),
            inputs=[5, 2],
        )

def test_invalid_inputs_for_addition():
    """
    Test that providing non-list inputs to Addition.get_result raises a ValueError.
    """
    addition = Addition(user_id=dummy_user_id(), inputs=42)
    with pytest.raises(ValueError, match="Inputs must be a list of numbers."):
        addition.get_result()

def test_invalid_inputs_for_subtraction():
    """
    Test that providing fewer than two numbers to Subtraction.get_result raises a ValueError.
    """
    subtraction = Subtraction(user_id=dummy_user_id(), inputs=[99])
    with pytest.raises(ValueError, match="Inputs must be a list with at least two numbers."):
        subtraction.get_result()

def test_invalid_inputs_for_division():
    """
    Test that providing fewer than two numbers to Division.get_result raises a ValueError.
    """
    division = Division(user_id=dummy_user_id(), inputs=[123])
    with pytest.raises(ValueError, match="Inputs must be a list with at least two numbers."):
        division.get_result()


def test_abstractcalculation_get_result_raises():
    class Dummy(AbstractCalculation):
        pass
    dummy = Dummy()
    with pytest.raises(NotImplementedError):
        dummy.get_result()


def test_abstractcalculation_repr():
    class Dummy(AbstractCalculation):
        type = "multiplication"
        inputs = [7, 8, 9]
    dummy = Dummy()
    assert repr(dummy) == "<Calculation(type=multiplication, inputs=[7, 8, 9])>"

