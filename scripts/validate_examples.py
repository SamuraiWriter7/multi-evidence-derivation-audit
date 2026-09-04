#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError


# ============================================================================
# Repository paths
# ============================================================================

ROOT = Path(__file__).resolve().parents[1]

SCHEMAS_DIR = ROOT / "schemas"

REFERENCE_CASE_DIR = (
    ROOT
    / "examples"
    / "cases"
    / "pass"
    / "reference-case"
)


# ============================================================================
# Protocol constants
# ============================================================================

PROTOCOL_VERSION = "0.3.0"


# ============================================================================
# Schema registry
# ============================================================================

SCHEMA_FILES = {
    "audit-case-record":
        SCHEMAS_DIR / "audit-case-record.schema.json",

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


# ============================================================================
# Reference Case inventory
#
# Each file is explicitly mapped to its expected schema.
# ============================================================================

REFERENCE_CASE_FILES = {
    Path("audit-case-record.json"):
        "audit-case-record",

    Path("evidence/evidence-0001.watermark.json"):
        "audit-evidence-record",

    Path("evidence/evidence-0002.signed-receipt.json"):
        "audit-evidence-record",

    Path("evidence/evidence-0003.api-trace.json"):
        "audit-evidence-record",

    Path("evidence/evidence-0004.similarity.json"):
        "audit-evidence-record",

    Path(
        "relationships/"
        "relationship-0001.same-source.json"
    ):
        "evidence-relationship-record",

    Path(
        "relationships/"
        "relationship-0002.independent-corroboration.json"
    ):
        "evidence-relationship-record",

    Path("fusion/fusion-0001.json"):
        "evidence-fusion-record",

    Path("assessments/assessment-0001.json"):
        "derivation-assessment-record",

    Path("attestations/zk-attestation-0001.json"):
        "zk-audit-attestation",
}


# ============================================================================
# Record identifiers
# ============================================================================

ID_FIELDS = {
    "audit-case-record": "case_id",
    "audit-evidence-record": "evidence_id",
    "evidence-relationship-record": "relationship_id",
    "evidence-fusion-record": "fusion_id",
    "derivation-assessment-record": "assessment_id",
    "zk-audit-attestation": "attestation_id",
}


# ============================================================================
# Audit context mapping
# ============================================================================

AUDIT_CONTEXT_TYPES = {
    "case": "audit-case-record",
    "evidence": "audit-evidence-record",
    "relationship": "evidence-relationship-record",
    "fusion": "evidence-fusion-record",
    "assessment": "derivation-assessment-record",
}


# ============================================================================
# Helpers
# ============================================================================

def relative(path: Path) -> str:
    """Return a repository-relative path for diagnostics."""

    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    """Load JSON and return useful errors on malformed files."""

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
            f"{exc.msg} at line {exc.lineno}, "
            f"column {exc.colno}"
        ) from exc


def format_instance_path(
    error: ValidationError,
) -> str:
    """Convert jsonschema path into readable notation."""

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


def format_schema_path(
    error: ValidationError,
) -> str:
    """Convert schema path into readable notation."""

    if not error.absolute_schema_path:
        return "<root>"

    return "/".join(
        str(part)
        for part in error.absolute_schema_path
    )


def validation_message(
    error: ValidationError,
) -> str:
    """Create deterministic schema error output."""

    return (
        f"path={format_instance_path(error)} | "
        f"validator={error.validator} | "
        f"message={error.message}"
    )


def error_sort_key(
    error: ValidationError,
) -> tuple[str, str, str]:
    """Sort schema errors deterministically."""

    return (
        format_instance_path(error),
        str(error.validator),
        error.message,
    )


# ============================================================================
# Load and validate schemas
# ============================================================================

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
                f"{relative(schema_path)}: "
                f"{exc.message}"
            ) from exc

        validators[schema_name] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

        print(
            f"  [schema-ok] "
            f"{schema_name}: "
            f"{relative(schema_path)}"
        )

    print()

    return validators


# ============================================================================
# Schema inventory
# ============================================================================

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
            f"  [inventory-ok] "
            f"{len(expected)} schemas registered"
        )

    print()

    return failures


# ============================================================================
# Reference Case inventory
# ============================================================================

def verify_reference_case_inventory() -> int:
    failures = 0

    expected = {
        path.as_posix()
        for path in REFERENCE_CASE_FILES
    }

    actual = {
        path.relative_to(
            REFERENCE_CASE_DIR
        ).as_posix()
        for path in REFERENCE_CASE_DIR.rglob("*.json")
        if path.is_file()
    }

    print("[reference case inventory]")

    missing = expected - actual
    extra = actual - expected

    for filename in sorted(missing):
        failures += 1
        print(
            f"  [FAIL] missing reference-case file: "
            f"{filename}"
        )

    for filename in sorted(extra):
        failures += 1
        print(
            f"  [FAIL] unregistered reference-case file: "
            f"{filename}"
        )

    if failures == 0:
        print(
            f"  [inventory-ok] "
            f"{len(expected)} reference-case records registered"
        )

    print()

    return failures


# ============================================================================
# Load Reference Case records
# ============================================================================

def load_reference_case_records(
) -> dict[Path, tuple[str, dict[str, Any]]]:

    records: dict[
        Path,
        tuple[str, dict[str, Any]]
    ] = {}

    for relative_path, schema_name in (
        REFERENCE_CASE_FILES.items()
    ):
        path = REFERENCE_CASE_DIR / relative_path

        record = load_json(path)

        if not isinstance(record, dict):
            raise RuntimeError(
                f"Reference-case record must be "
                f"a JSON object: {relative(path)}"
            )

        records[relative_path] = (
            schema_name,
            record,
        )

    return records


# ============================================================================
# Schema validation of Reference Case
# ============================================================================

def validate_reference_case_schemas(
    validators: dict[str, Draft202012Validator],
    records: dict[
        Path,
        tuple[str, dict[str, Any]]
    ],
) -> int:

    failures = 0

    print("[reference case schema validation]")

    for relative_path, (
        schema_name,
        instance,
    ) in records.items():

        validator = validators[schema_name]

        errors = sorted(
            validator.iter_errors(instance),
            key=error_sort_key,
        )

        print()
        print(
            f"  file: "
            f"{relative(REFERENCE_CASE_DIR / relative_path)}"
        )
        print(
            f"  schema: {schema_name}"
        )

        if not errors:
            print("  [schema-ok]")
            continue

        failures += 1

        print(
            "  [FAIL] schema validation failed"
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


# ============================================================================
# Version preflight
# ============================================================================

def verify_protocol_versions(
    records: dict[
        Path,
        tuple[str, dict[str, Any]]
    ],
) -> int:

    failures = 0

    print("[protocol version preflight]")

    for relative_path, (
        _schema_name,
        record,
    ) in records.items():

        schema_version = record.get(
            "schema_version"
        )

        if schema_version != PROTOCOL_VERSION:
            failures += 1

            print(
                f"  [FAIL] "
                f"{relative_path.as_posix()}: "
                f"schema_version="
                f"{schema_version!r}, "
                f"expected "
                f"{PROTOCOL_VERSION!r}"
            )

        if "protocol_version" in record:
            protocol_version = record.get(
                "protocol_version"
            )

            if protocol_version != PROTOCOL_VERSION:
                failures += 1

                print(
                    f"  [FAIL] "
                    f"{relative_path.as_posix()}: "
                    f"protocol_version="
                    f"{protocol_version!r}, "
                    f"expected "
                    f"{PROTOCOL_VERSION!r}"
                )

    if failures == 0:
        print(
            "  [version-ok] "
            "all reference-case records "
            f"declare MEDA v{PROTOCOL_VERSION}"
        )

    print()

    return failures


# ============================================================================
# Registry construction
# ============================================================================

def build_record_registries(
    records: dict[
        Path,
        tuple[str, dict[str, Any]]
    ],
) -> tuple[
    dict[str, dict[str, dict[str, Any]]],
    list[str],
]:

    registries: dict[
        str,
        dict[str, dict[str, Any]]
    ] = {
        schema_name: {}
        for schema_name in SCHEMA_FILES
    }

    errors: list[str] = []

    for relative_path, (
        schema_name,
        record,
    ) in records.items():

        id_field = ID_FIELDS[schema_name]

        record_id = record.get(id_field)

        if not isinstance(record_id, str):
            errors.append(
                f"{relative_path.as_posix()}: "
                f"missing usable {id_field}"
            )
            continue

        if record_id in registries[schema_name]:
            errors.append(
                f"{relative_path.as_posix()}: "
                f"duplicate {schema_name} ID "
                f"{record_id}"
            )
            continue

        registries[schema_name][record_id] = (
            record
        )

    return registries, errors


# ============================================================================
# Generic graph helpers
# ============================================================================

def check_ref(
    reference: str,
    expected_schema: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]]
    ],
    location: str,
    errors: list[str],
) -> None:

    registry = registries[expected_schema]

    if reference not in registry:
        errors.append(
            f"{location}: unresolved reference "
            f"{reference!r}; "
            f"expected type={expected_schema}"
        )


def check_ref_list(
    references: list[str],
    expected_schema: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]]
    ],
    location: str,
    errors: list[str],
) -> None:

    for reference in references:
        check_ref(
            reference=reference,
            expected_schema=expected_schema,
            registries=registries,
            location=location,
            errors=errors,
        )


def check_subset(
    child_values: list[str],
    parent_values: list[str],
    child_name: str,
    parent_name: str,
    record_id: str,
    errors: list[str],
) -> None:

    child = set(child_values)
    parent = set(parent_values)

    invalid = child - parent

    if invalid:
        errors.append(
            f"{record_id}: "
            f"{child_name} contains value(s) "
            f"not present in {parent_name}: "
            f"{sorted(invalid)}"
        )


def check_disjoint(
    left_values: list[str],
    right_values: list[str],
    left_name: str,
    right_name: str,
    record_id: str,
    errors: list[str],
) -> None:

    overlap = (
        set(left_values)
        & set(right_values)
    )

    if overlap:
        errors.append(
            f"{record_id}: "
            f"{left_name} and {right_name} "
            f"must be disjoint; "
            f"overlap={sorted(overlap)}"
        )


# ============================================================================
# Graph validation
# ============================================================================

def validate_audit_graph(
    registries: dict[
        str,
        dict[str, dict[str, Any]]
    ],
) -> int:

    errors: list[str] = []

    print("[audit graph validation]")

    # ------------------------------------------------------------------------
    # Exactly one Audit Case is expected in the reference graph.
    # ------------------------------------------------------------------------

    cases = registries[
        "audit-case-record"
    ]

    if len(cases) != 1:
        errors.append(
            "reference-case must contain exactly "
            f"one Audit Case; found {len(cases)}"
        )

        for error in errors:
            print(f"  [FAIL] {error}")

        print()
        return len(errors)

    case_id, case = next(
        iter(cases.items())
    )

    origin_ref = case["origin_ref"]
    derivative_ref = case["derivative_ref"]

    # ------------------------------------------------------------------------
    # Case membership / Origin / Derivative consistency
    # ------------------------------------------------------------------------

    member_types = [
        "audit-evidence-record",
        "evidence-relationship-record",
        "evidence-fusion-record",
        "derivation-assessment-record",
        "zk-audit-attestation",
    ]

    for schema_name in member_types:
        for record_id, record in (
            registries[schema_name].items()
        ):

            if record.get("case_ref") != case_id:
                errors.append(
                    f"{record_id}: "
                    f"case_ref={record.get('case_ref')!r} "
                    f"does not match {case_id!r}"
                )

            if record.get("origin_ref") != origin_ref:
                errors.append(
                    f"{record_id}: "
                    "origin_ref does not match "
                    f"Audit Case origin_ref "
                    f"{origin_ref!r}"
                )

            if (
                record.get("derivative_ref")
                != derivative_ref
            ):
                errors.append(
                    f"{record_id}: "
                    "derivative_ref does not match "
                    f"Audit Case derivative_ref "
                    f"{derivative_ref!r}"
                )

    # ------------------------------------------------------------------------
    # Case registry integrity
    #
    # The Reference Case is intended to be complete, so its registered refs
    # must exactly match the actual graph nodes.
    # ------------------------------------------------------------------------

    case_registry_fields = {
        "evidence_refs":
            "audit-evidence-record",

        "relationship_refs":
            "evidence-relationship-record",

        "fusion_refs":
            "evidence-fusion-record",

        "assessment_refs":
            "derivation-assessment-record",

        "attestation_refs":
            "zk-audit-attestation",
    }

    for field_name, schema_name in (
        case_registry_fields.items()
    ):
        declared = set(
            case.get(field_name, [])
        )

        actual = set(
            registries[schema_name].keys()
        )

        missing_from_case = (
            actual - declared
        )

        unresolved_in_case = (
            declared - actual
        )

        if missing_from_case:
            errors.append(
                f"{case_id}: "
                f"{field_name} does not register "
                f"existing record(s): "
                f"{sorted(missing_from_case)}"
            )

        if unresolved_in_case:
            errors.append(
                f"{case_id}: "
                f"{field_name} contains unresolved "
                f"record(s): "
                f"{sorted(unresolved_in_case)}"
            )

    # ------------------------------------------------------------------------
    # Current assessment integrity
    # ------------------------------------------------------------------------

    current_assessment_ref = (
        case.get("current_assessment_ref")
    )

    if current_assessment_ref is not None:

        check_ref(
            reference=current_assessment_ref,
            expected_schema=(
                "derivation-assessment-record"
            ),
            registries=registries,
            location=(
                f"{case_id}.current_assessment_ref"
            ),
            errors=errors,
        )

        if (
            current_assessment_ref
            not in case.get(
                "assessment_refs",
                [],
            )
        ):
            errors.append(
                f"{case_id}: "
                "current_assessment_ref "
                f"{current_assessment_ref!r} "
                "is not registered in "
                "assessment_refs"
            )

    # ------------------------------------------------------------------------
    # Evidence Relationship integrity
    # ------------------------------------------------------------------------

    relationships = registries[
        "evidence-relationship-record"
    ]

    for relationship_id, relationship in (
        relationships.items()
    ):

        evidence_refs = relationship.get(
            "evidence_refs",
            [],
        )

        check_ref_list(
            references=evidence_refs,
            expected_schema=(
                "audit-evidence-record"
            ),
            registries=registries,
            location=(
                f"{relationship_id}.evidence_refs"
            ),
            errors=errors,
        )

        check_subset(
            child_values=evidence_refs,
            parent_values=case.get(
                "evidence_refs",
                [],
            ),
            child_name="evidence_refs",
            parent_name="case.evidence_refs",
            record_id=relationship_id,
            errors=errors,
        )

    # ------------------------------------------------------------------------
    # Evidence Fusion integrity
    # ------------------------------------------------------------------------

    fusions = registries[
        "evidence-fusion-record"
    ]

    for fusion_id, fusion in (
        fusions.items()
    ):

        fusion_evidence_refs = fusion.get(
            "evidence_refs",
            [],
        )

        relationship_refs = fusion.get(
            "relationship_refs",
            [],
        )

        check_ref_list(
            references=fusion_evidence_refs,
            expected_schema=(
                "audit-evidence-record"
            ),
            registries=registries,
            location=(
                f"{fusion_id}.evidence_refs"
            ),
            errors=errors,
        )

        check_ref_list(
            references=relationship_refs,
            expected_schema=(
                "evidence-relationship-record"
            ),
            registries=registries,
            location=(
                f"{fusion_id}.relationship_refs"
            ),
            errors=errors,
        )

        check_subset(
            child_values=fusion_evidence_refs,
            parent_values=case.get(
                "evidence_refs",
                [],
            ),
            child_name="evidence_refs",
            parent_name="case.evidence_refs",
            record_id=fusion_id,
            errors=errors,
        )

        check_subset(
            child_values=relationship_refs,
            parent_values=case.get(
                "relationship_refs",
                [],
            ),
            child_name="relationship_refs",
            parent_name="case.relationship_refs",
            record_id=fusion_id,
            errors=errors,
        )

        evidence_subsets = [
            "supporting_evidence_refs",
            "counter_evidence_refs",
            "redundant_evidence_refs",
            "effective_evidence_refs",
        ]

        for subset_name in evidence_subsets:
            check_subset(
                child_values=fusion.get(
                    subset_name,
                    [],
                ),
                parent_values=fusion_evidence_refs,
                child_name=subset_name,
                parent_name="evidence_refs",
                record_id=fusion_id,
                errors=errors,
            )

        # A redundant record cannot simultaneously
        # be treated as an effective independent channel.
        check_disjoint(
            left_values=fusion.get(
                "redundant_evidence_refs",
                [],
            ),
            right_values=fusion.get(
                "effective_evidence_refs",
                [],
            ),
            left_name="redundant_evidence_refs",
            right_name="effective_evidence_refs",
            record_id=fusion_id,
            errors=errors,
        )

        # The same evidence cannot simultaneously
        # support and counter the same fusion result.
        check_disjoint(
            left_values=fusion.get(
                "supporting_evidence_refs",
                [],
            ),
            right_values=fusion.get(
                "counter_evidence_refs",
                [],
            ),
            left_name="supporting_evidence_refs",
            right_name="counter_evidence_refs",
            record_id=fusion_id,
            errors=errors,
        )

        # Every referenced relationship must operate
        # entirely inside this Fusion evidence set.
        for relationship_ref in relationship_refs:

            relationship = relationships.get(
                relationship_ref
            )

            if relationship is None:
                continue

            check_subset(
                child_values=relationship.get(
                    "evidence_refs",
                    [],
                ),
                parent_values=fusion_evidence_refs,
                child_name=(
                    f"{relationship_ref}."
                    "evidence_refs"
                ),
                parent_name=(
                    f"{fusion_id}.evidence_refs"
                ),
                record_id=fusion_id,
                errors=errors,
            )

    # ------------------------------------------------------------------------
    # Derivation Assessment integrity
    # ------------------------------------------------------------------------

    assessments = registries[
        "derivation-assessment-record"
    ]

    for assessment_id, assessment in (
        assessments.items()
    ):

        assessment_evidence_refs = (
            assessment.get(
                "evidence_refs",
                [],
            )
        )

        assessment_fusion_refs = (
            assessment.get(
                "fusion_refs",
                [],
            )
        )

        check_ref_list(
            references=assessment_evidence_refs,
            expected_schema=(
                "audit-evidence-record"
            ),
            registries=registries,
            location=(
                f"{assessment_id}.evidence_refs"
            ),
            errors=errors,
        )

        check_ref_list(
            references=assessment_fusion_refs,
            expected_schema=(
                "evidence-fusion-record"
            ),
            registries=registries,
            location=(
                f"{assessment_id}.fusion_refs"
            ),
            errors=errors,
        )

        check_subset(
            child_values=assessment_evidence_refs,
            parent_values=case.get(
                "evidence_refs",
                [],
            ),
            child_name="evidence_refs",
            parent_name="case.evidence_refs",
            record_id=assessment_id,
            errors=errors,
        )

        check_subset(
            child_values=assessment_fusion_refs,
            parent_values=case.get(
                "fusion_refs",
                [],
            ),
            child_name="fusion_refs",
            parent_name="case.fusion_refs",
            record_id=assessment_id,
            errors=errors,
        )

        check_subset(
            child_values=assessment.get(
                "conflicting_evidence_refs",
                [],
            ),
            parent_values=assessment_evidence_refs,
            child_name=(
                "conflicting_evidence_refs"
            ),
            parent_name="evidence_refs",
            record_id=assessment_id,
            errors=errors,
        )

        # Assessment evidence must come from at least
        # one of the Fusion records it references.
        fused_evidence: set[str] = set()

        for fusion_ref in assessment_fusion_refs:
            fusion = fusions.get(fusion_ref)

            if fusion is not None:
                fused_evidence.update(
                    fusion.get(
                        "evidence_refs",
                        [],
                    )
                )

        assessment_only = (
            set(assessment_evidence_refs)
            - fused_evidence
        )

        if assessment_only:
            errors.append(
                f"{assessment_id}: "
                "assessment contains evidence "
                "not present in any referenced "
                f"Fusion: {sorted(assessment_only)}"
            )

    # ------------------------------------------------------------------------
    # ZK Audit Attestation integrity
    # ------------------------------------------------------------------------

    attestations = registries[
        "zk-audit-attestation"
    ]

    all_protocol_ids: set[str] = set()

    for registry in registries.values():
        all_protocol_ids.update(
            registry.keys()
        )

    for attestation_id, attestation in (
        attestations.items()
    ):

        context_type = attestation.get(
            "audit_context_type"
        )

        context_ref = attestation.get(
            "audit_context_ref"
        )

        if context_type in AUDIT_CONTEXT_TYPES:

            expected_schema = (
                AUDIT_CONTEXT_TYPES[
                    context_type
                ]
            )

            check_ref(
                reference=context_ref,
                expected_schema=expected_schema,
                registries=registries,
                location=(
                    f"{attestation_id}."
                    "audit_context_ref"
                ),
                errors=errors,
            )

        # "other" is intentionally allowed to point
        # outside the MEDA protocol graph.
        elif context_type != "other":
            errors.append(
                f"{attestation_id}: "
                "unsupported audit_context_type "
                f"{context_type!r}"
            )

        # committed_inputs may contain either protocol
        # record IDs or opaque external commitments.
        #
        # Known MEDA-style IDs must resolve.
        for committed_ref in attestation.get(
            "committed_inputs",
            [],
        ):

            meda_prefixes = (
                "CASE-",
                "EVIDENCE-",
                "REL-",
                "FUSION-",
                "ASSESSMENT-",
                "ZK-ATTESTATION-",
            )

            if committed_ref.startswith(
                meda_prefixes
            ):
                if (
                    committed_ref
                    not in all_protocol_ids
                ):
                    errors.append(
                        f"{attestation_id}: "
                        "unresolved protocol "
                        "committed_input "
                        f"{committed_ref!r}"
                    )

        # If standard public context keys are exposed,
        # they must agree with the enclosing Audit Case.
        public_inputs = attestation.get(
            "public_inputs",
            {},
        )

        if (
            "case_ref" in public_inputs
            and public_inputs["case_ref"]
            != case_id
        ):
            errors.append(
                f"{attestation_id}: "
                "public_inputs.case_ref "
                "does not match Audit Case"
            )

        if (
            "origin_ref" in public_inputs
            and public_inputs["origin_ref"]
            != origin_ref
        ):
            errors.append(
                f"{attestation_id}: "
                "public_inputs.origin_ref "
                "does not match Audit Case"
            )

        if (
            "derivative_ref" in public_inputs
            and public_inputs["derivative_ref"]
            != derivative_ref
        ):
            errors.append(
                f"{attestation_id}: "
                "public_inputs.derivative_ref "
                "does not match Audit Case"
            )

        if (
            context_type == "fusion"
            and "fusion_ref" in public_inputs
            and public_inputs["fusion_ref"]
            != context_ref
        ):
            errors.append(
                f"{attestation_id}: "
                "public_inputs.fusion_ref "
                "does not match "
                "audit_context_ref"
            )

    # ------------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------------

    if errors:
        for error in errors:
            print(
                f"  [graph-fail] {error}"
            )

        print()
        return len(errors)

    print(
        "  [graph-ok] "
        "all references resolve and "
        "cross-record invariants hold"
    )

    print(
        "  [case-ok] "
        f"{case_id}: "
        f"{len(registries['audit-evidence-record'])} evidence, "
        f"{len(registries['evidence-relationship-record'])} relationships, "
        f"{len(registries['evidence-fusion-record'])} fusion, "
        f"{len(registries['derivation-assessment-record'])} assessment, "
        f"{len(registries['zk-audit-attestation'])} attestation"
    )

    print()

    return 0


# ============================================================================
# Main
# ============================================================================

def main() -> int:

    print(
        "=== Multi-Evidence Derivation Audit Protocol "
        "v0.3 Validation ==="
    )
    print()

    try:
        validators = load_validators()

        failures = 0

        failures += verify_schema_inventory()

        failures += (
            verify_reference_case_inventory()
        )

        records = (
            load_reference_case_records()
        )

        failures += verify_protocol_versions(
            records
        )

        failures += (
            validate_reference_case_schemas(
                validators=validators,
                records=records,
            )
        )

        registries, registry_errors = (
            build_record_registries(
                records
            )
        )

        print("[record registry]")

        if registry_errors:
            failures += len(registry_errors)

            for error in registry_errors:
                print(
                    f"  [FAIL] {error}"
                )
        else:
            total_records = sum(
                len(registry)
                for registry
                in registries.values()
            )

            print(
                f"  [registry-ok] "
                f"{total_records} protocol "
                "records indexed"
            )

        print()

        if not registry_errors:
            failures += validate_audit_graph(
                registries
            )

    except RuntimeError as exc:
        print(
            f"[fatal] {exc}"
        )
        return 1

    print(
        "=== Validation Summary ==="
    )

    if failures == 0:
        print("[validate-pass]")
        print(
            "All 6 schemas are valid, "
            "all 10 Reference Case records "
            "passed schema validation, "
            "and the complete MEDA v0.3 "
            "Audit Case Graph passed "
            "cross-record integrity validation."
        )
        return 0

    print("[validate-fail]")
    print(
        f"{failures} validation "
        "problem(s) detected."
    )

    return 1


if __name__ == "__main__":
    sys.exit(main())
