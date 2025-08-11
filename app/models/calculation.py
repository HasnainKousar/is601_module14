# app/models/calculation.py

"""
SQLAlchemy models for calculation operations.

This module defines abstract and concrete classes for addition, subtraction, multiplication, and division.
It implements polymorphic behavior and result computation for each calculation type.
"""
from datetime import datetime
import uuid
from typing import List
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.ext.declarative import declared_attr
from app.database import Base

class AbstractCalculation:
    """
    Abstract base class for calculation models.

    Provides common table columns and relationships for all calculation types.
    Implements factory method and interface for result computation.
    """
    
    @declared_attr
    def __tablename__(cls):
        """
        Returns the table name for the calculation model.
        """
        return 'calculations'

    @declared_attr
    def id(cls):
        """
        Returns the primary key column for the calculation model.
        """
        return Column(
            UUID(as_uuid=True), 
            primary_key=True, 
            default=uuid.uuid4,  # Auto-generate UUIDs
            nullable=False
        )

    @declared_attr
    def user_id(cls):
        """
        Returns the user_id column for the calculation model.
        """
        return Column(
            UUID(as_uuid=True), 
            ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
            index=True  # Index for faster queries filtering by user_id
        )

    @declared_attr
    def type(cls):
        """
        Returns the type column for the calculation model.
        """
        return Column(
            String(50), 
            nullable=False,
            index=True  # Index for faster queries filtering by type
        )

    @declared_attr
    def inputs(cls):
        """
        Returns the inputs column for the calculation model.
        """
        return Column(
            JSON, 
            nullable=False
        )

    @declared_attr
    def result(cls):
        """
        Returns the result column for the calculation model.
        """
        return Column(
            Float,
            nullable=True
        )

    @declared_attr
    def created_at(cls):
        """
        Returns the created_at column for the calculation model.
        """
        return Column(
            DateTime, 
            default=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def updated_at(cls):
        """
        Returns the updated_at column for the calculation model.
        """
        return Column(
            DateTime, 
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def user(cls):
        """
        Returns the relationship to the User model.
        """
        return relationship("User", back_populates="calculations")

    @classmethod
    def create(cls, calculation_type: str, user_id: uuid.UUID, inputs: List[float]) -> "Calculation":
        """
        Factory method to create calculation instances of the appropriate type.
        
        This implements the Factory Method design pattern, which provides an
        interface for creating objects but allows subclasses to decide which
        class to instantiate.
        
        Args:
            calculation_type: The type of calculation to create (e.g., "addition")
            user_id: The UUID of the user who owns this calculation
            inputs: List of numeric inputs for the calculation
            
        Returns:
            An instance of the appropriate Calculation subclass
            
        Raises:
            ValueError: If the calculation_type is not supported
        """
        calculation_classes = {
            'addition': Addition,
            'subtraction': Subtraction,
            'multiplication': Multiplication,
            'division': Division,
        }
        calculation_class = calculation_classes.get(calculation_type.lower())
        if not calculation_class:
            raise ValueError(f"Unsupported calculation type: {calculation_type}")
        return calculation_class(user_id=user_id, inputs=inputs)

    def get_result(self) -> float:
        """
        Method to compute calculation result.
        
        This is an abstract method that must be implemented by subclasses.
        It defines the interface that all calculation types must implement.
        
        Returns:
            float: The result of the calculation
            
        Raises:
            NotImplementedError: If not implemented by a subclass
        """
        raise NotImplementedError

    def __repr__(self):
        """
        String representation of the calculation for debugging.
        
        Returns:
            str: A string showing the calculation type and inputs
        """
        return f"<Calculation(type={self.type}, inputs={self.inputs})>"

class Calculation(Base, AbstractCalculation):
    """
    Concrete calculation model for database storage.

    Implements polymorphic identity for SQLAlchemy ORM.
    """
    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "calculation",
        #"with_polymorphic": "*"  # Eager load all subclass columns (commented out)
    }

class Addition(Calculation):
    """
    Addition calculation subclass.
    
    Implements addition of multiple numbers.
    Examples:
        [1, 2, 3] -> 1 + 2 + 3 = 6
        [10, -5] -> 10 + (-5) = 5
    """
    __mapper_args__ = {"polymorphic_identity": "addition"}

    def get_result(self) -> float:
        """
        Calculate the sum of all input values.
        
        Validates inputs and returns the sum using Python's built-in sum() function.
        
        Returns:
            float: The sum of all input values
            
        Raises:
            ValueError: If inputs are not a list or if fewer than 2 numbers provided
        """
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.")
        if len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.") #pragma: no cover
        return sum(self.inputs)

class Subtraction(Calculation):
    """
    Subtraction calculation subclass.
    
    Implements sequential subtraction starting from the first number.
    Examples:
        [10, 3, 2] -> 10 - 3 - 2 = 5
        [100, 50, 25] -> 100 - 50 - 25 = 25
    """
    __mapper_args__ = {"polymorphic_identity": "subtraction"}

    def get_result(self) -> float:
        """
        Calculate the result of subtracting subsequent values from the first value.
        
        Takes the first number and subtracts all remaining numbers sequentially.
        
        Returns:
            float: The result of the subtraction sequence
            
        Raises:
            ValueError: If inputs are not a list or if fewer than 2 numbers provided
        """
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.") #pragma: no cover
        if len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")
        result = self.inputs[0]
        for value in self.inputs[1:]:
            result -= value
        return result

class Multiplication(Calculation):
    """
    Multiplication calculation subclass.
    
    Implements multiplication of multiple numbers.
    Examples:
        [2, 3, 4] -> 2 * 3 * 4 = 24
        [10, 0.5] -> 10 * 0.5 = 5
    """
    __mapper_args__ = {"polymorphic_identity": "multiplication"}

    def get_result(self) -> float:
        """
        Calculate the product of all input values.
        
        Returns:
            float: The product of all input values
            
        Raises:
            ValueError: If inputs are not a list or if fewer than 2 numbers provided
        """
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.") #pragma: no cover
        if len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.") #pragma: no cover
        result = 1
        for value in self.inputs:
            result *= value
        return result

class Division(Calculation):
    """
    Division calculation subclass.
    
    Implements sequential division starting from the first number.
    Examples:
        [10, 2, 5] -> 10 / 2 / 5 = 1
        [100, 4, 5] -> 100 / 4 / 5 = 5
        
    Special case handling:
        - Division by zero raises a ValueError
    """
    __mapper_args__ = {"polymorphic_identity": "division"}

    def get_result(self) -> float:
        """
        Calculate the result of dividing the first value by all subsequent values.
        
        Takes the first number and divides by all remaining numbers sequentially.
        Includes validation to prevent division by zero.
        
        Returns:
            float: The result of the division sequence
            
        Raises:
            ValueError: If inputs are not a list, if fewer than 2 numbers provided,
                        or if attempting to divide by zero
        """
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.") #pragma: no cover
        if len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")
        result = self.inputs[0]
        for value in self.inputs[1:]:
            if value == 0:
                raise ValueError("Cannot divide by zero.")
            result /= value
        return result
    
