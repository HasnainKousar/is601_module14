#app/schemas/calculation.py
"""
Schemas for calculation operations in the application.

Defines Pydantic models for calculation creation, update, response, and validation logic.
Used for data validation and serialization in API endpoints.
"""

from dataclasses import field
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database import Base

class CalculationType(str, Enum):
    """Enumeration for calculation types."""
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"


class CalculationBase(BaseModel):
    """
    Base schema for a calculation, including type and input values.

    This class provides validation for calculation type and input values,
    ensuring correct data is provided for mathematical operations.
    """
    type: CalculationType = Field(
        ...,  # The ... means this field is required
        description="Type of calculation (addition, subtraction, multiplication, division)",
        example="addition"
    )
    inputs: List[float] = Field(
        ...,  # The ... means this field is required
        description="List of numeric inputs for the calculation",
        example=[10.5, 3, 2],
        min_items=2  # Ensures at least 2 numbers are provided
    )

    @field_validator("type", mode='before')
    @classmethod
    def validate_type(cls, v):
        """
        Validates the calculation type before conversion to an enum.

        It ensure that:
        1. The input is a string
        2. The value is one of the allowed calculation types
        3. The value is consistently converted to lowercase

        Args:
            v: The input value to validate

        Returns:
            str: The validated and normalized string value

        Raises:
            ValueError: If the input is not a valid calculation type
        """
        allowed = {e.value for e in CalculationType}
        # Ensure v is a string and check (in lowercase) if it's allowed.
        if not isinstance(v, str) or v.lower() not in allowed:
            raise ValueError(f"Type must be one of: {', '.join(sorted(allowed))}")
        return v.lower()
    
    @field_validator("inputs", mode="before")
    @classmethod
    def check_inputs_is_list(cls, v):
        """
        Validates that the input field is a list.

        This validator ensures that the input is a list type.

        Args:
            v: The input value to validate

        Returns:
            list: The validated list

        Raises:
            ValueError: If the input is not a valid list
        """
        if not isinstance(v, list):
            raise ValueError("Input should be a valid list")
        return v
    
    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationBase":
        """
        Validates the inputs based on calculation type.

        This method checks the validity of the inputs after the main model validation has occurred.

        It ensures that:
        1. At least two numbers are provided
        2. Division by zero is not attempted

        Args:
            v: The input value to validate

        Returns:
            "CalculationBase": The validated model instance

        Raises:
            ValueError: If the inputs are not valid
        """
        if len(self.inputs) < 2:
            raise ValueError("At least two numbers are required for calculation")
        if self.type == CalculationType.DIVISION:
            # Prevent division by zero (skip the first value as numerator)
            if any(x == 0 for x in self.inputs[1:]):
                raise ValueError("Cannot divide by zero")
        return self
    
    model_config = ConfigDict(
        # Allow conversion from SQLAlchemy models to Pydantic models
        from_attributes=True,
        
        # Add examples to the OpenAPI schema for better API documentation
        json_schema_extra={
            "examples": [
                {"type": "addition", "inputs": [10.5, 3, 2]},
                {"type": "division", "inputs": [100, 2]}
            ]
        }
    )


class CalculationCreate(CalculationBase):
    """
    Schema for creating a new calculation.

    Extends CalculationBase by adding a user_id field to associate the calculation with a user.
    """
    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        example="123e4567-e89b-12d3-a456-426614174000"
    )

    model_config = ConfigDict(
        # Example for documentation and testing
        json_schema_extra={
            "example": {
                "type": "addition",
                "inputs": [10.5, 3, 2],
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )

class CalculationUpdate(BaseModel):
    """
    Schema for updating an existing calculation.

    Allows updating the input values for a calculation.
    """
    inputs: Optional[List[float]] = Field(
        None,  # None means this field is optional
        description="Updated list of numeric inputs for the calculation",
        example=[42, 7],
        min_items=2  # If provided, at least 2 items are required
    )

    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationUpdate":
        """
        Validates that if inputs are provided, at least two numbers are present.

        Returns:
            CalculationUpdate: The validated model instance

        Raises:
            ValueError: If less than two numbers are provided
        """
        if self.inputs is not None and len(self.inputs) < 2:
            raise ValueError("At least two numbers are required for calculation")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"inputs": [42, 7]}}
    )

class CalculationResponse(CalculationBase):
    """
    Schema for returning a calculation response.

    Extends CalculationBase by adding fields for id, user_id, timestamps, and result.
    Used for API responses containing calculation details.
    """
    id: UUID = Field(
        ...,
        description="Unique UUID of the calculation",
        example="123e4567-e89b-12d3-a456-426614174999"
    )
    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    created_at: datetime = Field(
        ..., 
        description="Time when the calculation was created"
    )
    updated_at: datetime = Field(
        ..., 
        description="Time when the calculation was last updated"
    )
    result: float = Field(
        ...,
        description="Result of the calculation",
        example=15.5
    )

    model_config = ConfigDict(
        # Allow conversion from SQLAlchemy models to this Pydantic model
        from_attributes=True,
        
        # Add a complete example for API documentation
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174999",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "addition",
                "inputs": [10.5, 3, 2],
                "result": 15.5,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
    )





    





