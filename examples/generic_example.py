"""Basic example demonstrating PydanticValidator usage.

This example shows how to validate JSON data against a Pydantic model,
handle both successful and failed validations, and route data accordingly.

Usage:
    python examples/generic_example.py

"""

import asyncio
import json

from genai_processors import processor, streams
from pydantic import BaseModel, Field

from genai_processors_pydantic import PydanticValidator


class UserData(BaseModel):
    """Simple user data model for validation."""

    user_id: int
    username: str = Field(min_length=3)
    email: str
    is_active: bool = True


async def main() -> None:
    """Demonstrates basic PydanticValidator usage."""
    # Create validator and convert to processor for stream processing
    validator = PydanticValidator(UserData).to_processor()

    # Sample data with mixed quality
    test_data = [
        # Valid user data
        {"user_id": 1, "username": "alice", "email": "alice@example.com"},

        # Invalid: username too short
        {"user_id": 2, "username": "bo", "email": "bob@example.com"},

        # Invalid: missing email
        {"user_id": 3, "username": "charlie"},

        # Not JSON - will be passed through
        "This is just text and will be ignored",
    ]

    # Convert to processor parts
    parts = [
        processor.ProcessorPart(
            json.dumps(data) if isinstance(data, dict) else data,
        )
        for data in test_data
    ]

    # Create input stream
    input_stream = streams.stream_content(parts)

    # Process through validator
    print("Processing data through PydanticValidator...")
    print("=" * 50)

    async for result_part in validator(input_stream):
        # Handle status messages
        if result_part.substream_name == processor.STATUS_STREAM:
            print(f"Status: {result_part.text}")
            continue

        # Handle validation results
        validation_status = result_part.metadata.get("validation_status")

        if validation_status == "success":
            validated_user = result_part.metadata["validated_instance"]
            print(
                f"✅ Valid user: {validated_user.username} "
                f"({validated_user.email})",
            )

        elif validation_status == "failure":
            errors = result_part.metadata["validation_errors"]
            print(f"❌ Validation failed with {len(errors)} errors:")
            for error in errors:
                print(f"   - {error['loc'][0]}: {error['msg']}")

        else:
            # Passed through without validation
            print(f"⚪ Passed through: {result_part.text[:50]}...")
        print()


if __name__ == "__main__":
    asyncio.run(main())
