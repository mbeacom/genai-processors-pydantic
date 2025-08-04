"""genai-processors-pydantic: A Pydantic validator for genai-processors.

This package provides a PydanticValidator processor that validates JSON content
against Pydantic models for use with Google's genai-processors framework.

This is an independent contrib processor for the genai-processors ecosystem.
"""

from .validator import PydanticValidator, ValidationConfig

__version__ = "0.1.1"
__all__ = ["PydanticValidator", "ValidationConfig"]
