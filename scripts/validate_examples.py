#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"


SCHEMA_FILES = {
    "audit-evidence-record": (
        SCHEMAS_DIR / "audit-evidence-record.schema.json"
    ),
    "derivation-assessment-record": (
        SCHEMAS_DIR / "derivation-assessment-record.schema.json"
    ),
    "zk-audit-attestation": (
        SCHEMAS_DIR / "zk-audit-attestation.schema.json"
    ),
}


PASS_EXAMPLES = {
    "audit-evidence-record.watermark.example.json":
        "audit-evidence-record",

    "derivation-assessment-record.example.json":
        "derivation-assessment-record",

    "zk-audit-attestation.example.json":
        "zk-audit-attestation",
}


FAIL_EXAMPLES = {
    "audit-evidence-record.missing-integrity.example.json":
        "audit-evidence-record",

    "derivation-assessment-record.no-evidence.example.json":
        "derivation-assessment-record",

    "zk-audit-attestation.invalid-status.example.json":
        "zk-audit-attestation",
}


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        raise RuntimeError(
            f"File not found: {path.relative_to(ROOT)}"
        ) from None

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in {path.relative_to(ROOT)}: "
            f"{exc.msg} at line {exc.lineno}, column {exc.colno}"
        ) from exc


def format_path(error: ValidationError) -> str:
    if not error.absolute_path:
        return "<root>"

    parts: list[str] = []

    for item in error.absolute_path:
        if isinstance(item, int):
            parts.append(f"[{item}]")
        else:
            if parts:
                parts.append(".")
            parts.append(str(item))

    return "".join(parts)


def validation_message(error: ValidationError) -> str:
    return (
        f"path={format_path(error)} | "
        f"validator={error.validator} | "
        f"message={error.message}"
    )


def load_validators() -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}

    print("[schemas]")

    for schema_name, schema_path in SCHEMA_FILES.items():
        schema = load_json(schema_path)

        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            raise RuntimeError(
                f"Invalid schema "
                f"{schema_path.relative_to(ROOT)}: {exc.message}"
            ) from exc

        validators[schema_name] = Draft202012Validator(schema)

        print(
            f"- {schema_name}: "
            f"{schema_path.relative_to(ROOT)}"
        )

    print()

    return validators


def validate_pass_examples(
    validators: dict[str, Draft202012Validator],
) -> int:
    failures = 0

    print("[pass examples]")

    for filename, schema_name in PASS_EXAMPLES.items():
        path = PASS_DIR / filename
        instance = load_json(path)
        validator = validators[schema_name]

        errors = sorted(
            validator.iter_errors(instance),
            key=lambda error: list(error.absolute_path),
        )

        print()
        print(f"- {path.relative_to(ROOT)}")
        print(f"  schema: {schema_name}")

        if errors:
            failures += 1
            print("  [FAIL] expected valid example")

            for error in errors:
                print(
                    f"    - {validation_message(error)}"
                )
        else:
            print("  [schema-ok]")

    print()

    return failures


def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
) -> int:
    failures = 0

    print("[fail examples]")

    for filename, schema_name in FAIL_EXAMPLES.items():
        path = FAIL_DIR / filename
        instance = load_json(path)
        validator = validators[schema_name]

        errors = sorted(
            validator.iter_errors(instance),
            key=lambda error: list(error.absolute_path),
        )

        print()
        print(f"- {path.relative_to(ROOT)}")
        print(f"  schema: {schema_name}")

        if errors:
            print("  [expected-fail]")

            for error in errors:
                print(
                    f"    - {validation_message(error)}"
                )
        else:
            failures += 1
            print(
                "  [FAIL] example unexpectedly passed validation"
            )

    print()

    return failures


def verify_example_inventory() -> int:
    failures = 0

    expected_pass = set(PASS_EXAMPLES)
    expected_fail = set(FAIL_EXAMPLES)

    actual_pass = {
        path.name
        for path in PASS_DIR.glob("*.json")
        if path.is_file()
    }

    actual_fail = {
        path.name
        for path in FAIL_DIR.glob("*.json")
        if path.is_file()
    }

    print("[inventory]")

    missing_pass = expected_pass - actual_pass
    extra_pass = actual_pass - expected_pass

    missing_fail = expected_fail - actual_fail
    extra_fail = actual_fail - expected_fail

    if missing_pass:
        failures += len(missing_pass)

        for filename in sorted(missing_pass):
            print(
                f"[FAIL] missing pass example: {filename}"
            )

    if extra_pass:
        failures += len(extra_pass)

        for filename in sorted(extra_pass):
            print(
                f"[FAIL] unregistered pass example: {filename}"
            )

    if missing_fail:
        failures += len(missing_fail)

        for filename in sorted(missing_fail):
            print(
                f"[FAIL] missing fail example: {filename}"
            )

    if extra_fail:
        failures += len(extra_fail)

        for filename in sorted(extra_fail):
            print(
                f"[FAIL] unregistered fail example: {filename}"
            )

    if failures == 0:
        print("[inventory-ok]")

    print()

    return failures


def main() -> int:
    print(
        "=== Multi-Evidence Derivation Audit Protocol "
        "v0.1 Validation ==="
    )
    print()

    try:
        validators = load_validators()

        failures = 0

        failures += verify_example_inventory()
        failures += validate_pass_examples(validators)
        failures += validate_fail_examples(validators)

    except RuntimeError as exc:
        print(f"[fatal] {exc}")
        return 1

    print("=== Validation Summary ===")

    if failures == 0:
        print("[validate-pass]")
        print(
            "All pass examples validated successfully, "
            "and all fail examples were rejected as expected."
        )
        return 0

    print("[validate-fail]")
    print(f"{failures} validation problem(s) detected.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
