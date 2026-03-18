from typing import Any, Dict, List, Optional, Tuple


def validate_intent(intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Batch 14 — Intent Validator Binding

    Deterministically validates an intent object against the canonical execution contract.
    No inference. No defaults. No side effects.

    Returns:
      {
        "valid": bool,
        "errors": [ { "path": str, "code": str, "message": str } ],
        "validated_intent": Optional[Dict]  # present only when valid
      }
    """

    errors: List[Dict[str, str]] = []

    # ---- Type guard ----
    if not isinstance(intent, dict):
        return {
            "valid": False,
            "errors": [_err("$", "TYPE", "Intent must be an object/dict")],
            "validated_intent": None
        }

    # ---- Required top-level keys (Batch 13 schema) ----
    required_keys = ["validated", "NON_EXECUTABLE_PLAN", "outputs", "security_envelope"]
    for k in required_keys:
        if k not in intent:
            errors.append(_err(f"$.{k}", "REQUIRED", f"Missing required field: {k}"))

    # If required fields missing, still continue collecting errors safely
    validated = intent.get("validated")
    non_exec = intent.get("NON_EXECUTABLE_PLAN")
    outputs = intent.get("outputs")
    envelope = intent.get("security_envelope")

    # ---- validated ----
    if "validated" in intent and not isinstance(validated, bool):
        errors.append(_err("$.validated", "TYPE", "validated must be boolean"))

    # ---- NON_EXECUTABLE_PLAN ----
    if "NON_EXECUTABLE_PLAN" in intent:
        if non_exec is not True:
            errors.append(_err("$.NON_EXECUTABLE_PLAN", "CONST", "NON_EXECUTABLE_PLAN must be true"))

    # ---- security_envelope ----
    if "security_envelope" in intent and not isinstance(envelope, dict):
        errors.append(_err("$.security_envelope", "TYPE", "security_envelope must be an object/dict"))

    # ---- outputs ----
    if "outputs" in intent:
        if not isinstance(outputs, dict):
            errors.append(_err("$.outputs", "TYPE", "outputs must be an object/dict"))
            outputs = None  # prevent downstream attribute errors
        else:
            errors.extend(_validate_outputs(outputs))

    # ---- top-level additionalProperties: false (Batch 13 intent schema) ----
    # Allowed keys at top-level (matches INTENT_SCHEMA.json)
    # Open schema: we now allow additional properties like SRS fields.
    # allowed_top_level = {
    #     "validated",
    #     "NON_EXECUTABLE_PLAN",
    #     "goal",
    #     "inputs",
    #     "constraints",
    #     "domain_tags",
    #     "outputs",
    #     "guidance",
    #     "security_envelope"
    # }

    # for k in intent.keys():
    #     if k not in allowed_top_level:
    #         errors.append(_err(f"$.{k}", "ADDITIONAL_PROPERTY", f"Unexpected top-level field: {k}"))

    # ---- inputs type (array of strings) ----
    if "inputs" in intent:
        inputs = intent.get("inputs")
        if not isinstance(inputs, list):
            errors.append(_err("$.inputs", "TYPE", "inputs must be an array"))
        elif not all(isinstance(x, str) for x in inputs):
            errors.append(_err("$.inputs", "TYPE", "All inputs elements must be strings"))

    # ---- guidance (optional) ----
    if "guidance" in intent:
        g = intent.get("guidance")
        if g is not None and not isinstance(g, dict):
            errors.append(_err("$.guidance", "TYPE", "guidance must be an object/dict or null"))

    # ---- constraints type (string or array) ----
    if "constraints" in intent:
        c = intent.get("constraints")
        if not isinstance(c, (str, list)):
            errors.append(_err("$.constraints", "TYPE", "constraints must be a string or an array"))
        if isinstance(c, list) and not all(isinstance(x, (str, int, float, bool, dict, list, type(None))) for x in c):
            # keep permissive element types; the OS only needs "array-ness"
            pass

    # ---- domain_tags type (string or array) ----
    if "domain_tags" in intent:
        dt = intent.get("domain_tags")
        if not isinstance(dt, (str, list)):
            errors.append(_err("$.domain_tags", "TYPE", "domain_tags must be a string or an array"))

    is_valid = len(errors) == 0

    if not is_valid:
        return {
            "valid": False,
            "errors": errors,
            "validated_intent": None
        }

    # IMPORTANT: no mutation of original intent
    validated_intent = dict(intent)
    validated_intent["validated"] = True

    return {
        "valid": True,
        "errors": [],
        "validated_intent": validated_intent
    }


def _validate_outputs(outputs: Dict[str, Any]) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []

    # outputs additionalProperties: false
    allowed_outputs = {"guidance", "code", "system", "platform"}
    for k in outputs.keys():
        if k not in allowed_outputs:
            errors.append(_err(f"$.outputs.{k}", "ADDITIONAL_PROPERTY", f"Unexpected outputs field: {k}"))

    # outputs.guidance
    if "guidance" in outputs and not isinstance(outputs.get("guidance"), bool):
        errors.append(_err("$.outputs.guidance", "TYPE", "outputs.guidance must be boolean"))

    # outputs.code
    if "code" in outputs:
        code = outputs.get("code")
        if not isinstance(code, dict):
            errors.append(_err("$.outputs.code", "TYPE", "outputs.code must be an object/dict"))
        else:
            # code additionalProperties: false
            allowed_code = {"enabled", "type", "bootstrap_env"}
            for k in code.keys():
                if k not in allowed_code:
                    errors.append(_err(f"$.outputs.code.{k}", "ADDITIONAL_PROPERTY", f"Unexpected code field: {k}"))

            if "enabled" in code and not isinstance(code.get("enabled"), bool):
                errors.append(_err(f"$.outputs.code.enabled", "TYPE", "outputs.code.enabled must be boolean"))
                
            if "bootstrap_env" in code and not isinstance(code.get("bootstrap_env"), bool):
                errors.append(_err(f"$.outputs.code.bootstrap_env", "TYPE", "outputs.code.bootstrap_env must be boolean"))

            if "type" in code:
                t = code.get("type")
                allowed_types = {
                    "function", "fastapi_service", "dashboard", "cli_tool", 
                    "worker_service", "analytics_service", "ai_reasoning_service", "report_service"
                }
                if t not in allowed_types:
                    errors.append(_err("$.outputs.code.type", "ENUM", f"Unsupported code type: {t}"))

    # outputs.system
    if "system" in outputs:
        system = outputs.get("system")
        if not isinstance(system, dict):
            errors.append(_err("$.outputs.system", "TYPE", "outputs.system must be an object/dict"))
        else:
            allowed_system = {"enabled", "type", "bootstrap_env", "components"}
            for k in system.keys():
                if k not in allowed_system:
                    errors.append(_err(f"$.outputs.system.{k}", "ADDITIONAL_PROPERTY", f"Unexpected system field: {k}"))

            if "enabled" in system and not isinstance(system.get("enabled"), bool):
                errors.append(_err(f"$.outputs.system.enabled", "TYPE", "outputs.system.enabled must be boolean"))

            if "bootstrap_env" in system and not isinstance(system.get("bootstrap_env"), bool):
                errors.append(_err(f"$.outputs.system.bootstrap_env", "TYPE", "outputs.system.bootstrap_env must be boolean"))

            if "type" in system and not isinstance(system.get("type"), str):
                errors.append(_err(f"$.outputs.system.type", "TYPE", "outputs.system.type must be a string"))

            if "components" in system:
                components = system.get("components")
                if not isinstance(components, list):
                    errors.append(_err("$.outputs.system.components", "TYPE", "outputs.system.components must be an array"))
                else:
                    for idx, comp in enumerate(components):
                        if not isinstance(comp, dict):
                            errors.append(_err(f"$.outputs.system.components[{idx}]", "TYPE", "Component must be an object"))
                            continue
                        if "name" not in comp:
                            errors.append(_err(f"$.outputs.system.components[{idx}].name", "REQUIRED", "Missing component name"))
                        if "type" not in comp:
                            errors.append(_err(f"$.outputs.system.components[{idx}].type", "REQUIRED", "Missing component type"))

    # outputs.platform
    if "platform" in outputs:
        platform = outputs.get("platform")
        if not isinstance(platform, dict):
            errors.append(_err("$.outputs.platform", "TYPE", "outputs.platform must be an object/dict"))
        else:
            allowed_platform = {"enabled"}
            for k in platform.keys():
                if k not in allowed_platform:
                    errors.append(_err(f"$.outputs.platform.{k}", "ADDITIONAL_PROPERTY", f"Unexpected platform field: {k}"))

            if "enabled" in platform and not isinstance(platform.get("enabled"), bool):
                errors.append(_err(f"$.outputs.platform.enabled", "TYPE", "outputs.platform.enabled must be boolean"))

    return errors


def _err(path: str, code: str, message: str) -> Dict[str, str]:
    return {"path": path, "code": code, "message": message}
