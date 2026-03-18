import json
from pathlib import Path
from typing import Dict, Any, List
from jsonschema import Draft202012Validator, ValidationError


CORE_CONTRACTS_DIR = Path("contracts/core")

SECURITY_ENVELOPE_SCHEMA = CORE_CONTRACTS_DIR / "security_envelope.schema.json"
AUDIT_LOG_SCHEMA = CORE_CONTRACTS_DIR / "audit_log.schema.json"
STATE_MACHINE_SCHEMA = CORE_CONTRACTS_DIR / "state_machine.schema.json"


class ValidationResult:
    def __init__(
        self,
        valid: bool,
        confidence: str,
        output_class: str,
        errors: List[str],
        clarifiers: List[str],
    ):
        self.valid = valid
        self.confidence = confidence
        self.output_class = output_class
        self.errors = errors
        self.clarifiers = clarifiers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "confidence": self.confidence,
            "output_class": self.output_class,
            "errors": self.errors,
            "clarifiers": self.clarifiers,
        }


def _load_schema(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _validate_against_schema(
    data: Dict[str, Any], schema_path: Path
) -> List[str]:
    schema = _load_schema(schema_path)
    validator = Draft202012Validator(schema)

    errors = []
    for err in validator.iter_errors(data):
        errors.append(err.message)

    return errors


def validate_intent(intent: Dict[str, Any]) -> ValidationResult:
    """
    Strict validator.
    Missing required fields => BLOCK + CLARIFIER.
    No inference. No defaults.
    """

    errors: List[str] = []
    clarifiers: List[str] = []

    security_envelope = intent.get("security_envelope")
    impact_class = None

    if security_envelope:
        impact_class = security_envelope.get("impact_class")

    # 1. Determine stakes (NO inference)
    if not security_envelope:
        errors.append("Missing security_envelope for intent.")
        clarifiers.append(
            "Provide a security_envelope declaring impact_class, auth, network, audit, and failsafe posture."
        )
        return ValidationResult(
            valid=False,
            confidence="LOW",
            output_class="SCAFFOLD_ONLY",
            errors=errors,
            clarifiers=clarifiers,
        )

    if not impact_class:
        errors.append("security_envelope.impact_class is missing.")
        clarifiers.append(
            "Declare impact_class to determine whether the intent is high-stakes."
        )
        return ValidationResult(
            valid=False,
            confidence="LOW",
            output_class="SCAFFOLD_ONLY",
            errors=errors,
            clarifiers=clarifiers,
        )

    # 2. Validate security envelope structure
    envelope_errors = _validate_against_schema(
        security_envelope, SECURITY_ENVELOPE_SCHEMA
    )
    if envelope_errors:
        errors.extend(envelope_errors)
        clarifiers.append(
            "Fix security_envelope to match the core Security Envelope schema."
        )

       # 3. Validate audit posture (policy block)
    audit_block = security_envelope.get("audit")
    if audit_block:
        audit_errors = _validate_against_schema(audit_block, AUDIT_LOG_SCHEMA)
        if audit_errors:
            errors.extend(audit_errors)
            clarifiers.append(
                "Audit policy does not satisfy core audit_log schema requirements."
            )
    else:
        errors.append("Missing audit block in security_envelope.")
        clarifiers.append(
            "Provide an audit block defining append-only, hash-chained logging policy."
        )


    # 4. Validate state machine reference if present
    state_machine = intent.get("state_machine")
    if state_machine:
        state_errors = _validate_against_schema(
            state_machine, STATE_MACHINE_SCHEMA
        )
        if state_errors:
            errors.extend(state_errors)
            clarifiers.append(
                "State machine definition is invalid or incomplete."
            )

    # 5. Secret handling (hard stop)
    intent_str = json.dumps(intent)
    if "secret" in intent_str.lower() and "reference" not in intent_str.lower():
        errors.append("Potential plaintext secret detected.")
        clarifiers.append(
            "Remove all plaintext secrets. Use references only."
        )
        return ValidationResult(
            valid=False,
            confidence="LOW",
            output_class="BLOCKED",
            errors=errors,
            clarifiers=clarifiers,
        )

    # Final decision
    if errors:
        return ValidationResult(
            valid=False,
            confidence="LOW",
            output_class="SCAFFOLD_ONLY",
            errors=errors,
            clarifiers=clarifiers,
        )

    # Even if valid, executable output is not allowed yet (Commit C)
    return ValidationResult(
        valid=True,
        confidence="HIGH",
        output_class="NON_EXECUTABLE_PLAN",
        errors=[],
        clarifiers=[],
    )
