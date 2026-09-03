#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError


# ---------------------------------------------------------------------------
# Repository paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

SCHEMAS_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"


# ---------------------------------------------------------------------------
# Schema registry
# ---------------------------------------------------------------------------

SCHEMA_FILES = {
    "audit-evidence-record":
        SCHEMAS_DIR / "audit-evidence-record.schema.json",

    "evidence-relationship-record":
        SCHEMAS_DIR / "evidence-relationship-record.schema.json",

    "evidence-fusion-record":
        SCHEMAS_DIR / "evidence-fusion-record.schema.json",

    "derivation-assessment-record":
        SCHEMAS_DIR / "derivation-assessment-record.schema.json",

    "zk-audit-attestation":
        SCHEMAS_DIR / "zk-audit-attestation.schema.json",
}


# ---------------------------------------------------------------------------
# PASS examples
# ---------------------------------------------------------------------------

PASS_EXAMPLES = {
    "audit-evidence-record.watermark.example.json":
        "audit-evidence-record",

    "evidence-relationship-record.same-source.example.json":
        "evidence-relationship-record",

    "evidence-fusion-record.example.json":
        "evidence-fusion-record",

    "derivation-assessment-record.example.json":
        "derivation-assessment-record",

    "zk-audit-attestation.example.json":
        "zk-audit-attestation",
}


# ---------------------------------------------------------------------------
# FAIL examples
#
# expected_validator:
#   JSON Schema keyword that should reject the example.
#
# expected_path:
#   Instance path where the expected failure should occur.
#   "<root>" means the root object.
# ---------------------------------------------------------------------------

FAIL_EXAMPLES = {
    "audit-evidence-record.missing-integrity.example.json": {
        "schema": "audit-evidence-record",
        "expected_validator": "required",
        "expected_path": "<root>",
        "expected_message_fragment": "integrity",
    },

    "evidence-relationship-record.missing-dependency-source.example.json": {
        "schema": "evidence-relationship-record",
        "expected_validator": "required",
        "expected_path": "<root>",
        "expected_message_fragment": "dependency_source_ref",
    },

    "evidence-fusion-record.conflicted-without-counter.example.json": {
        "schema": "evidence-fusion-record",
        "expected_validator": "minItems",
        "expected_path": "counter_evidence_refs",
        "expected_message_fragment": "non-empty",
    },

    "derivation-assessment-record.no-fusion.example.json": {
        "schema": "derivation-assessment-record",
        "expected_validator": "minItems",
        "expected_path": "fusion_refs",
        "expected_message_fragment": "non-empty",
    },

    "zk-audit-attestation.invalid-status.example.json": {
        "schema": "zk-audit-attestation",
        "expected_validator": "enum",
        "expected_path": "verification_status",
        "expected_message_fragment": "accepted",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def relative(path: Path) -> str:
    """Return a repository-relative path for readable output."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    """Load a JSON file and report useful repository-level errors."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        raise RuntimeError(
            f"File not found: {relative(path)}"
        ) from None

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in {relative(path)}: "
            f"{exc.msg} at line {exc.lineno}, column {exc.colno}"
        ) from exc


def format_instance_path(error: ValidationError) -> str:
    """Convert jsonschema error path into dot/bracket notation."""
    if not error.absolute_path:
        return "<root>"

    output = ""

    for part in error.absolute_path:
        if isinstance(part, int):
            output += f"[{part}]"
        else:
            if output:
                output += "."
            output += str(part)

    return output


def format_schema_path(error: ValidationError) -> str:
    """Convert schema error path into readable notation."""
    if not error.absolute_schema_path:
        return "<root>"

    return "/".join(
        str(part)
        for part in error.absolute_schema_path
    )


def validation_message(error: ValidationError) -> str:
    """Create deterministic diagnostic output."""
    return (
        f"path={format_instance_path(error)} | "
        f"validator={error.validator} | "
        f"message={error.message}"
    )


def error_sort_key(error: ValidationError) -> tuple[str, str, str]:
    """Sort validation errors deterministically."""
    return (
        format_instance_path(error),
        str(error.validator),
        error.message,
    )


# ---------------------------------------------------------------------------
# Schema loading and validation
# ---------------------------------------------------------------------------

def load_validators() -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}

    print("[schemas]")

    for schema_name, schema_path in SCHEMA_FILES.items():
        schema = load_json(schema_path)

        try:
            Draft202012Validator.check_schema(schema)

        except SchemaError as exc:
            raise RuntimeError(
                f"Invalid schema {relative(schema_path)}: "
                f"{exc.message}"
            ) from exc

        validators[schema_name] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

        print(
            f"  [schema-ok] "
            f"{schema_name}: {relative(schema_path)}"
        )

    print()

    return validators


# ---------------------------------------------------------------------------
# Inventory validation
# ---------------------------------------------------------------------------

def verify_schema_inventory() -> int:
    failures = 0

    expected = {
        path.name
        for path in SCHEMA_FILES.values()
    }

    actual = {
        path.name
        for path in SCHEMAS_DIR.glob("*.schema.json")
        if path.is_file()
    }

    print("[schema inventory]")

    missing = expected - actual
    extra = actual - expected

    for filename in sorted(missing):
        failures += 1
        print(
            f"  [FAIL] missing schema: {filename}"
        )

    for filename in sorted(extra):
        failures += 1
        print(
            f"  [FAIL] unregistered schema: {filename}"
        )

    if failures == 0:
        print(
            f"  [inventory-ok] {len(expected)} schemas registered"
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

    print("[example inventory]")

    missing_pass = expected_pass - actual_pass
    extra_pass = actual_pass - expected_pass

    missing_fail = expected_fail - actual_fail
    extra_fail = actual_fail - expected_fail

    for filename in sorted(missing_pass):
        failures += 1
        print(
            f"  [FAIL] missing pass example: {filename}"
        )

    for filename in sorted(extra_pass):
        failures += 1
        print(
            f"  [FAIL] unregistered pass example: {filename}"
        )

    for filename in sorted(missing_fail):
        failures += 1
        print(
            f"  [FAIL] missing fail example: {filename}"
        )

    for filename in sorted(extra_fail):
        failures += 1
        print(
            f"  [FAIL] unregistered fail example: {filename}"
        )

    if failures == 0:
        print(
            f"  [inventory-ok] "
            f"{len(expected_pass)} pass + "
            f"{len(expected_fail)} fail examples registered"
        )

    print()

    return failures


# ---------------------------------------------------------------------------
# PASS validation
# ---------------------------------------------------------------------------

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
            key=error_sort_key,
        )

        print()
        print(f"  file: {relative(path)}")
        print(f"  schema: {schema_name}")

        if not errors:
            print("  [schema-ok]")
            continue

        failures += 1

        print(
            "  [FAIL] expected valid example "
            "but validation errors were found"
        )

        for error in errors:
            print(
                f"    - {validation_message(error)}"
            )
            print(
                f"      schema_path="
                f"{format_schema_path(error)}"
            )

    print()

    return failures


# ---------------------------------------------------------------------------
# FAIL validation
# ---------------------------------------------------------------------------

def matches_expected_failure(
    error: ValidationError,
    expected_validator: str,
    expected_path: str,
    expected_message_fragment: str,
) -> bool:
    actual_path = format_instance_path(error)

    return (
        error.validator == expected_validator
        and actual_path == expected_path
        and expected_message_fragment in error.message
    )


def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
) -> int:
    failures = 0

    print("[fail examples]")

    for filename, expectation in FAIL_EXAMPLES.items():
        path = FAIL_DIR / filename
        instance = load_json(path)

        schema_name = expectation["schema"]
        expected_validator = expectation["expected_validator"]
        expected_path = expectation["expected_path"]
        expected_message_fragment = expectation[
            "expected_message_fragment"
        ]

        validator = validators[schema_name]

        errors = sorted(
            validator.iter_errors(instance),
            key=error_sort_key,
        )

        print()
        print(f"  file: {relative(path)}")
        print(f"  schema: {schema_name}")
        print(
            "  expected: "
            f"validator={expected_validator}, "
            f"path={expected_path}"
        )

        if not errors:
            failures += 1

            print(
                "  [FAIL] example unexpectedly passed validation"
            )
            continue

        expected_matches = [
            error
            for error in errors
            if matches_expected_failure(
                error=error,
                expected_validator=expected_validator,
                expected_path=expected_path,
                expected_message_fragment=expected_message_fragment,
            )
        ]

        if expected_matches:
            print("  [expected-fail]")

            for error in expected_matches:
                print(
                    f"    - {validation_message(error)}"
                )

            unexpected_errors = [
                error
                for error in errors
                if error not in expected_matches
            ]

            if unexpected_errors:
                failures += 1

                print(
                    "  [FAIL] additional unexpected "
                    "validation error(s) detected"
                )

                for error in unexpected_errors:
                    print(
                        f"    - {validation_message(error)}"
                    )

        else:
            failures += 1

            print(
                "  [FAIL] example failed, but not for "
                "the expected constraint"
            )

            print("  actual error(s):")

            for error in errors:
                print(
                    f"    - {validation_message(error)}"
                )

    print()

    return failures


# ---------------------------------------------------------------------------
# Protocol-level sanity checks
# ---------------------------------------------------------------------------

def verify_protocol_versions() -> int:
    """
    Ensure all registered examples explicitly identify MEDA v0.2.0.

    JSON Schema already checks this during validation, but this separate
    preflight makes accidental v0.1 files easier to diagnose.
    """

    failures = 0

    print("[protocol version preflight]")

    paths: list[Path] = []

    paths.extend(
        PASS_DIR / filename
        for filename in PASS_EXAMPLES
    )

    paths.extend(
        FAIL_DIR / filename
        for filename in FAIL_EXAMPLES
    )

    for path in paths:
        instance = load_json(path)

        actual_version = instance.get("schema_version")

        if actual_version != "0.2.0":
            failures += 1

            print(
                f"  [FAIL] {relative(path)}: "
                f"schema_version={actual_version!r}, "
                "expected '0.2.0'"
            )

    if failures == 0:
        print(
            "  [version-ok] all registered examples "
            "declare schema_version 0.2.0"
        )

    print()

    return failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print(
        "=== Multi-Evidence Derivation Audit Protocol "
        "v0.2 Validation ==="
    )
    print()

    try:
        validators = load_validators()

        failures = 0

        failures += verify_schema_inventory()
        failures += verify_example_inventory()
        failures += verify_protocol_versions()

        failures += validate_pass_examples(validators)
        failures += validate_fail_examples(validators)

    except RuntimeError as exc:
        print(f"[fatal] {exc}")
        return 1

    print("=== Validation Summary ===")

    if failures == 0:
        print("[validate-pass]")
        print(
            "All 5 schemas are valid, "
            "all 5 pass examples were accepted, "
            "and all 5 fail examples were rejected "
            "by their expected constraints."
        )
        return 0

    print("[validate-fail]")
    print(
        f"{failures} validation problem(s) detected."
    )

    return 1


if __name__ == "__main__":
    sys.exit(main())
