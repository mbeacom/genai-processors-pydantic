"""Processor that validates ProcessorPart content against a Pydantic model."""

import json
from collections.abc import AsyncIterable
from dataclasses import dataclass
from typing import Any

from genai_processors import mime_types, processor
from pydantic import BaseModel, ValidationError

# Type alias for JSON-compatible data
JsonData = dict[str, object] | list[object] | str | int | float | bool | None


@dataclass
class ValidationConfig:
    """Configuration for PydanticValidator behavior."""

    fail_on_error: bool = False
    strict_mode: bool = False


class PydanticValidator(processor.PartProcessor):
    """A PartProcessor that validates ProcessorPart content using Pydantic.

    This processor inspects incoming parts for JSON data in `part.text` and
    validates it against a given Pydantic model.

    It provides feedback through the status stream and can be configured
    to either fail fast or continue on validation errors.

    Current Limitations (see MAINTAINER_FEEDBACK.md for details):
    - Works best with complete JSON in single Parts (streaming challenges)
    - Single-model validation only (stackability limitations)
    - Standard JSON Parts only (tool response integration planned)

    Example:
        ```python
        from pydantic import BaseModel
        from genai_processors_pydantic import (
            PydanticValidator,
            ValidationConfig,
        )

        class User(BaseModel):
            name: str
            age: int

        # Permissive validation that continues on errors (default)
        permissive_validator = PydanticValidator(User)

        # Strict validation that fails fast
        strict_validator = PydanticValidator(
            User,
            config=ValidationConfig(fail_on_error=True, strict_mode=True)
        )
        ```

    """

    def __init__(
        self,
        model: type[BaseModel],
        config: ValidationConfig | None = None,
    ) -> None:
        """Initialize the validator with a Pydantic model and configuration.

        Args:
            model: The Pydantic model class to validate against.
            config: Validation configuration. Uses defaults if None.

        Raises:
            TypeError: If model is not a Pydantic BaseModel subclass.

        """
        if not issubclass(model, BaseModel):
            msg = "model must be a Pydantic BaseModel subclass"
            raise TypeError(msg)

        self.model = model
        self.config = config or ValidationConfig()

    def match(self, part: processor.ProcessorPart) -> bool:
        """Determine if this part should be processed.

        Uses dual detection strategy to address MIME type marking limitations:
        1. Check for properly marked JSON Parts (preferred)
        2. Fallback to heuristic JSON detection (addresses unmarked JSON)

        Args:
            part: The ProcessorPart to check.

        Returns:
            True if the part has JSON data that can be validated.

        """
        # Check for JSON content in parts with JSON mimetype
        if mime_types.is_json(part.mimetype) and part.text:
            return True

        # Use lightweight heuristic to check if text looks like JSON
        if part.text and isinstance(part.text, str):
            text = part.text.strip()
            if ((text.startswith("{") and text.endswith("}")) or
                    (text.startswith("[") and text.endswith("]"))):
                return True

        return False

    def _get_data_to_validate(
        self,
        part: processor.ProcessorPart,
    ) -> JsonData:
        """Extract JSON data from a part's text.

        Args:
            part: The ProcessorPart to extract data from.

        Returns:
            Parsed JSON data if valid, otherwise None.

        """
        if part.text:
            try:
                return json.loads(part.text)
            except json.JSONDecodeError:
                return None
        return None

    def _create_part_with_merged_metadata(
        self,
        content: str,
        mimetype: str,
        original_part: processor.ProcessorPart,
        additional_metadata: dict[str, Any],
    ) -> processor.ProcessorPart:
        """Help by creating a ProcessorPart with merged metadata.

        Args:
            content: The content for the new part.
            mimetype: The MIME type for the new part.
            original_part: The original ProcessorPart to merge metadata from.
            additional_metadata: Additional metadata to include.

        Returns:
            A ProcessorPart with merged metadata.

        """
        return processor.ProcessorPart(
            content,
            mimetype=mimetype,
            metadata={**original_part.metadata, **additional_metadata},
        )

    async def _handle_success(
        self,
        validated_data: BaseModel,
        original_part: processor.ProcessorPart,
    ) -> AsyncIterable[processor.ProcessorPart]:
        """Yield parts for a successful validation.

        We store the serialized validated data in metadata to ensure
        ProcessorParts remain serializable for distributed systems.

        Args:
            validated_data: The validated Pydantic model instance.
            original_part: The original ProcessorPart that was validated.

        Returns:
            An async iterable of ProcessorParts with validation results.

        """
        # Store the validated data as JSON text
        validated_json_text = json.dumps(validated_data.model_dump(), indent=2)

        # Store serialized data to maintain ProcessorPart serializability
        success_metadata = {
            "validation_status": "success",
            "validated_model": self.model.__name__,
            "validated_data": validated_data.model_dump(),
        }

        validated_part = self._create_part_with_merged_metadata(
            validated_json_text,
            f"application/json; validated_model={self.model.__name__}",
            original_part,
            success_metadata,
        )
        yield validated_part
        yield processor.status(
            f"✅ Successfully validated data against {self.model.__name__}",
        )

    async def _handle_failure(
        self,
        error: ValidationError,
        raw_data: JsonData,
        original_part: processor.ProcessorPart,
    ) -> AsyncIterable[processor.ProcessorPart]:
        """Yield parts for a failed validation.

        Args:
            error: The ValidationError raised during validation.
            raw_data: The original data that failed validation.
            original_part: The original ProcessorPart that was validated.

        Returns:
            An async iterable of ProcessorParts with validation errors.

        """
        yield processor.status(
            f"❌ Validation failed against {self.model.__name__}: "
            f"{len(error.errors())} errors",
        )
        if self.config.fail_on_error:
            raise error

        error_details = {
            "validation_status": "failure",
            "validated_model": self.model.__name__,
            "validation_errors": error.errors(),
            "original_data": raw_data,
        }
        failed_part = self._create_part_with_merged_metadata(
            original_part.text,  # Preserve original text
            original_part.mimetype,
            original_part,
            error_details,
        )
        yield failed_part

    async def call(
        self,
        part: processor.ProcessorPart,
    ) -> AsyncIterable[processor.ProcessorPart]:
        """Validate a ProcessorPart using the Pydantic model.

        Args:
            part: The ProcessorPart to validate.

        Yields:
            ProcessorParts with validation results or status messages.

        """
        data_to_validate = self._get_data_to_validate(part)

        if data_to_validate is None:
            # If no valid JSON data is found, pass the part through.
            yield part
            return

        try:
            validation_kwargs = {"strict": self.config.strict_mode}
            validated_data = self.model.model_validate(
                data_to_validate,
                **validation_kwargs,
            )
            async for p in self._handle_success(validated_data, part):
                yield p

        except ValidationError as e:
            async for p in self._handle_failure(e, data_to_validate, part):
                yield p
