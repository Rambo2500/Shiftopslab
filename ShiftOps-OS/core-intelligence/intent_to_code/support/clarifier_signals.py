
"""
Clarifier signals (non-executing).

This module defines explanatory messages that may be returned when
validation fails.

Clarifiers do not ask questions.
Clarifiers do not modify input.
Clarifiers do not trigger retries.

They exist only to explain why execution stopped.
"""

def validation_failure(reason: str) -> str:
    return f"Validation failed: {reason}"

