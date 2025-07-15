"""Advanced example showing multi-model validation patterns.

This example demonstrates how to work around the single-model limitation
by composing multiple validators in a pipeline pattern.

Usage:
    python examples/multi_model_example.py

"""

import asyncio
import json

from genai_processors import processor, streams
from pydantic import BaseModel, Field

from genai_processors_pydantic import PydanticValidator


class UserData(BaseModel):
    """User profile data model."""

    user_id: int
    username: str = Field(min_length=3)
    email: str


class ProductData(BaseModel):
    """Product data model."""

    product_id: int
    name: str
    price: float = Field(gt=0)
    category: str


class OrderData(BaseModel):
    """Order data model."""

    order_id: int
    user_id: int
    items: list[int]
    total: float


async def multi_validator_pipeline():
    """Demonstrates composition of multiple validators."""
    # Create separate validators for each model (don't wrap them)
    user_validator = PydanticValidator(UserData)
    product_validator = PydanticValidator(ProductData)
    order_validator = PydanticValidator(OrderData)

    # Sample mixed data
    test_data = [
        # User data
        {"user_id": 1, "username": "alice", "email": "alice@example.com"},
        # Product data
        {"product_id": 101, "name": "Widget", "price": 29.99, "category": "gadgets"},
        # Order data
        {"order_id": 1001, "user_id": 1, "items": [101], "total": 29.99},
        # Invalid user (will fail)
        {"user_id": 2, "username": "x", "email": "invalid"},
        # Non-JSON data
        "This is just text and will be ignored",
    ]

    # Convert to processor parts
    parts = [
        processor.ProcessorPart(
            json.dumps(data) if isinstance(data, dict) else data,
        )
        for data in test_data
    ]

    input_stream = streams.stream_content(parts)

    print("Processing with multiple validators...")
    print("=" * 60)

    # Process through all validators
    # Each validator will handle its matching data types
    all_validators = [user_validator, product_validator, order_validator]

    async def process_with_all_validators(stream):
        """Process stream through all validators, collecting results."""
        # Convert stream to list for multiple processing
        parts_list = []
        async for part in stream:
            parts_list.append(part)

        # Process each part through all validators
        for part in parts_list:
            matched_any = False

            for i, validator in enumerate(all_validators):
                validator_name = ["User", "Product", "Order"][i]

                # Check if this validator can handle the data
                try:
                    # Test if the JSON structure looks like it could match
                    data = json.loads(part.text)

                    # Simple heuristic - check for key fields
                    model_hints = {
                        0: "user_id" in data and "username" in data,  # User
                        1: "product_id" in data and "price" in data,  # Product
                        2: "order_id" in data and "items" in data,  # Order
                    }

                    if not model_hints.get(i, False):
                        continue  # Skip this validator

                except json.JSONDecodeError:
                    continue  # Skip non-JSON data for this validator

                if validator.match(part):
                    matched_any = True
                    print(f"\n🔍 {validator_name} Validator processing...")

                    async for result in validator(part):
                        if result.substream_name == processor.STATUS_STREAM:
                            print(f"   Status: {result.text}")
                        else:
                            status = result.metadata.get("validation_status")
                            if status == "success":
                                model_name = result.metadata["validated_model"]
                                data = result.metadata["validated_data"]
                                print(f"   ✅ Valid {model_name}: {data}")
                            elif status == "failure":
                                errors = result.metadata["validation_errors"]
                                error_count = len(errors)
                                print(f"   ❌ Failed: {error_count} errors")
                                for error in errors:
                                    loc = error["loc"][0]
                                    msg = error["msg"]
                                    print(f"      - {loc}: {msg}")
                            else:
                                text_preview = result.text[:50]
                                print(f"   ⚪ Passed: {text_preview}...")
                    break  # Only process with first matching validator

            if not matched_any:
                print(f"\n⚪ No validators matched: {part.text[:50]}...")

    await process_with_all_validators(input_stream)


async def conditional_validator_pattern():
    """Demonstrates conditional routing based on data characteristics."""
    print("\n" + "=" * 60)
    print("Conditional Validator Pattern")
    print("=" * 60)

    # Sample data with type hints in the data itself
    test_data = [
        {
            "type": "user",
            "user_id": 1,
            "username": "alice",
            "email": "alice@example.com",
        },
        {
            "type": "product",
            "product_id": 101,
            "name": "Widget",
            "price": 29.99,
            "category": "gadgets",
        },
        {
            "type": "order",
            "order_id": 1001,
            "user_id": 1,
            "items": [101],
            "total": 29.99,
        },
    ]

    parts = [processor.ProcessorPart(json.dumps(data)) for data in test_data]

    input_stream = streams.stream_content(parts)

    # Create validators (don't wrap them)
    validators = {
        "user": PydanticValidator(UserData),
        "product": PydanticValidator(ProductData),
        "order": PydanticValidator(OrderData),
    }

    async for part in input_stream:
        try:
            data = json.loads(part.text)
            data_type = data.get("type")

            if data_type in validators:
                validator = validators[data_type]
                print(f"\n🎯 Routing to {data_type} validator...")

                async for result in validator(part):
                    if result.substream_name == processor.STATUS_STREAM:
                        print(f"   Status: {result.text}")
                    else:
                        status = result.metadata.get("validation_status")
                        if status == "success":
                            data = result.metadata["validated_data"]
                            print(f"   ✅ Valid {data_type}: {data}")
            else:
                print(f"\n❓ Unknown type '{data_type}', skipping...")

        except json.JSONDecodeError:
            print(f"\n⚪ Non-JSON data: {part.text[:50]}...")


async def main():
    """Run both multi-validator examples."""
    await multi_validator_pipeline()
    await conditional_validator_pattern()

    print("\n" + "=" * 60)
    print("Summary: Multi-Model Validation Patterns")
    print("=" * 60)
    print("✅ Multiple validators can be composed in pipelines")
    print("✅ Conditional routing based on data characteristics")
    print("✅ Each validator handles its specific model type")
    print("⚠️  Requires manual composition (not automatic)")
    print("🔄 v0.2.0 will include built-in multi-model support")


if __name__ == "__main__":
    asyncio.run(main())
