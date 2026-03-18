# Dry-Run Tests (CLI)

These tests lock the observable CLI behavior of run.py before
orchestration wiring.

Rules:
- No generated code is executed.
- Validation gates compilation.
- Linter emits warnings only.
- Context is never loaded at runtime.

Each intent here should produce consistent output sections:
INTENT → VALIDATION RESULT → LINT WARNINGS → (optional) COMPILER OUTPUT.
