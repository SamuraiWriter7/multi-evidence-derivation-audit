#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError


# ============================================================================
# Repository paths
# ============================================================================

ROOT = Path(__file__).resolve().parents[1]

SCHEMAS_DIR = ROOT / "schemas"

PASS_CASES_DIR = (
    ROOT
    / "examples"
    / "cases"
    / "pass"
)

FAIL_CASES_DIR = (
    ROOT
    / "examples"
    / "cases"
    / "fail"
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
# Record identifier fields
# ============================================================================

ID_FIELDS = {
    "audit-case-record":
        "case_id",

    "audit-evidence-record":
        "evidence_id",

    "evidence-relationship-record":
        "relationship_id",

    "evidence-fusion-record":
        "fusion_id",

    "derivation-assessment-record":
        "assessment_id",

    "zk-audit-attestation":
        "attestation_id",
}


# ============================================================================
# Audit context mapping
# ============================================================================

AUDIT_CONTEXT_TYPES = {
    "case":
        "audit-case-record",

    "evidence":
        "audit-evidence-record",

    "relationship":
        "evidence-relationship-record",

    "fusion":
        "evidence-fusion-record",

    "assessment":
        "derivation-assessment-record",
}


# ============================================================================
# PASS Case inventory
# ============================================================================

PASS_CASES = {
    "reference-case": {
        "expected_files": {
            "audit-case-record.json",

            "evidence/evidence-0001.watermark.json",
            "evidence/evidence-0002.signed-receipt.json",
            "evidence/evidence-0003.api-trace.json",
            "evidence/evidence-0004.similarity.json",

            "relationships/relationship-0001.same-source.json",
            "relationships/relationship-0002.independent-corroboration.json",

            "fusion/fusion-0001.json",

            "assessments/assessment-0001.json",

            "attestations/zk-attestation-0001.json",
        }
    }
}


# ============================================================================
# EXPECTED-FAIL Case inventory
#
# expected_issue_codes:
#   Graph Validator must produce exactly these issue codes.
#
# All JSON records in these cases must remain Schema-valid.
# ============================================================================

FAIL_CASES = {
    "cross-case-evidence": {
        "expected_files": {
            "audit-case-record.json",
            "evidence/evidence-0001.json",
        },
        "expected_issue_codes": {
            "CASE_REF_MISMATCH",
        },
    },

    "missing-reference": {
        "expected_files": {
            "audit-case-record.json",
        },
        "expected_issue_codes": {
            "CASE_REGISTRY_UNRESOLVED",
        },
    },

    "support-counter-overlap": {
        "expected_files": {
            "audit-case-record.json",
            "evidence/evidence-0001.json",
            "fusion/fusion-0001.json",
        },
        "expected_issue_codes": {
            "SUPPORT_COUNTER_OVERLAP",
        },
    },

    "redundant-effective-overlap": {
        "expected_files": {
            "audit-case-record.json",
            "evidence/evidence-0001.json",
            "fusion/fusion-0001.json",
        },
        "expected_issue_codes": {
            "REDUNDANT_EFFECTIVE_OVERLAP",
        },
    },

    "origin-mismatch": {
        "expected_files": {
            "audit-case-record.json",
            "evidence/evidence-0001.json",
        },
        "expected_issue_codes": {
            "ORIGIN_MISMATCH",
        },
    },

    "invalid-current-assessment": {
        "expected_files": {
            "audit-case-record.json",
        },
        "expected_issue_codes": {
            "CASE_REGISTRY_UNRESOLVED",
            "CURRENT_ASSESSMENT_UNRESOLVED",
        },
    },
}


# ============================================================================
# Graph issue type
# ============================================================================

@dataclass(frozen=True)
class GraphIssue:
    code: str
    message: str


# ============================================================================
# Generic helpers
# ============================================================================

def relative(path: Path) -> str:
    """Return repository-relative path for diagnostics."""

    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    """Load JSON with readable diagnostics."""

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
    """Convert jsonschema instance path into dot/bracket notation."""

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
    """Convert jsonschema schema path into readable notation."""

    if not error.absolute_schema_path:
        return "<root>"

    return "/".join(
        str(part)
        for part in error.absolute_schema_path
    )


def validation_message(
    error: ValidationError,
) -> str:
    return (
        f"path={format_instance_path(error)} | "
        f"validator={error.validator} | "
        f"message={error.message}"
    )


def error_sort_key(
    error: ValidationError,
) -> tuple[str, str, str]:
    return (
        format_instance_path(error),
        str(error.validator),
        error.message,
    )


# ============================================================================
# Determine schema from case-relative path
# ============================================================================

def schema_name_for_path(
    relative_path: Path,
) -> str:

    path = relative_path.as_posix()

    if path == "audit-case-record.json":
        return "audit-case-record"

    if path.startswith("evidence/"):
        return "audit-evidence-record"

    if path.startswith("relationships/"):
        return "evidence-relationship-record"

    if path.startswith("fusion/"):
        return "evidence-fusion-record"

    if path.startswith("assessments/"):
        return "derivation-assessment-record"

    if path.startswith("attestations/"):
        return "zk-audit-attestation"

    raise RuntimeError(
        f"Cannot determine schema for case file: {path}"
    )


# ============================================================================
# Schema loading
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
# Case inventory
# ============================================================================

def verify_case_inventory(
    case_dir: Path,
    expected_files: set[str],
    case_label: str,
) -> int:

    failures = 0

    actual_files = {
        path.relative_to(case_dir).as_posix()
        for path in case_dir.rglob("*.json")
        if path.is_file()
    }

    missing = expected_files - actual_files
    extra = actual_files - expected_files

    for filename in sorted(missing):
        failures += 1

        print(
            f"  [FAIL] {case_label}: "
            f"missing file: {filename}"
        )

    for filename in sorted(extra):
        failures += 1

        print(
            f"  [FAIL] {case_label}: "
            f"unregistered file: {filename}"
        )

    return failures


def verify_all_case_inventories() -> int:

    failures = 0

    print("[case inventory]")

    for case_name, config in PASS_CASES.items():
        case_dir = PASS_CASES_DIR / case_name

        case_failures = verify_case_inventory(
            case_dir=case_dir,
            expected_files=config["expected_files"],
            case_label=f"pass/{case_name}",
        )

        failures += case_failures

        if case_failures == 0:
            print(
                f"  [inventory-ok] "
                f"pass/{case_name}: "
                f"{len(config['expected_files'])} records"
            )

    for case_name, config in FAIL_CASES.items():
        case_dir = FAIL_CASES_DIR / case_name

        case_failures = verify_case_inventory(
            case_dir=case_dir,
            expected_files=config["expected_files"],
            case_label=f"fail/{case_name}",
        )

        failures += case_failures

        if case_failures == 0:
            print(
                f"  [inventory-ok] "
                f"fail/{case_name}: "
                f"{len(config['expected_files'])} record(s)"
            )

    print()

    return failures


# ============================================================================
# Case loading
# ============================================================================

def load_case_records(
    case_dir: Path,
) -> dict[Path, tuple[str, dict[str, Any]]]:

    records: dict[
        Path,
        tuple[str, dict[str, Any]],
    ] = {}

    for path in sorted(case_dir.rglob("*.json")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(case_dir)

        schema_name = schema_name_for_path(
            relative_path
        )

        record = load_json(path)

        if not isinstance(record, dict):
            raise RuntimeError(
                f"Case record must be a JSON object: "
                f"{relative(path)}"
            )

        records[relative_path] = (
            schema_name,
            record,
        )

    return records


# ============================================================================
# Version validation
# ============================================================================

def validate_case_versions(
    records: dict[
        Path,
        tuple[str, dict[str, Any]],
    ],
    case_label: str,
) -> list[str]:

    errors: list[str] = []

    for relative_path, (
        _schema_name,
        record,
    ) in records.items():

        schema_version = record.get(
            "schema_version"
        )

        if schema_version != PROTOCOL_VERSION:
            errors.append(
                f"{case_label}/"
                f"{relative_path.as_posix()}: "
                f"schema_version="
                f"{schema_version!r}; "
                f"expected "
                f"{PROTOCOL_VERSION!r}"
            )

        if "protocol_version" in record:
            protocol_version = record.get(
                "protocol_version"
            )

            if protocol_version != PROTOCOL_VERSION:
                errors.append(
                    f"{case_label}/"
                    f"{relative_path.as_posix()}: "
                    f"protocol_version="
                    f"{protocol_version!r}; "
                    f"expected "
                    f"{PROTOCOL_VERSION!r}"
                )

    return errors


# ============================================================================
# Schema validation for a Case
# ============================================================================

def validate_case_schemas(
    validators: dict[str, Draft202012Validator],
    records: dict[
        Path,
        tuple[str, dict[str, Any]],
    ],
) -> list[str]:

    errors: list[str] = []

    for relative_path, (
        schema_name,
        instance,
    ) in records.items():

        validator = validators[schema_name]

        schema_errors = sorted(
            validator.iter_errors(instance),
            key=error_sort_key,
        )

        for error in schema_errors:
            errors.append(
                f"{relative_path.as_posix()} | "
                f"{validation_message(error)}"
            )

    return errors


# ============================================================================
# Registry construction
# ============================================================================

def build_record_registries(
    records: dict[
        Path,
        tuple[str, dict[str, Any]],
    ],
) -> tuple[
    dict[str, dict[str, dict[str, Any]]],
    list[str],
]:

    registries: dict[
        str,
        dict[str, dict[str, Any]],
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

        registries[schema_name][record_id] = record

    return registries, errors


# ============================================================================
# Graph helpers
# ============================================================================

def add_issue(
    issues: list[GraphIssue],
    code: str,
    message: str,
) -> None:

    issues.append(
        GraphIssue(
            code=code,
            message=message,
        )
    )


def check_ref(
    reference: str,
    expected_schema: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]],
    ],
    location: str,
    issues: list[GraphIssue],
) -> None:

    if reference not in registries[expected_schema]:
        add_issue(
            issues,
            "UNRESOLVED_REFERENCE",
            (
                f"{location}: unresolved reference "
                f"{reference!r}; "
                f"expected type={expected_schema}"
            ),
        )


def check_ref_list(
    references: list[str],
    expected_schema: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]],
    ],
    location: str,
    issues: list[GraphIssue],
) -> None:

    for reference in references:
        check_ref(
            reference=reference,
            expected_schema=expected_schema,
            registries=registries,
            location=location,
            issues=issues,
        )


def check_subset(
    child_values: list[str],
    parent_values: list[str],
    code: str,
    child_name: str,
    parent_name: str,
    record_id: str,
    issues: list[GraphIssue],
) -> None:

    invalid = (
        set(child_values)
        - set(parent_values)
    )

    if invalid:
        add_issue(
            issues,
            code,
            (
                f"{record_id}: "
                f"{child_name} contains value(s) "
                f"not present in {parent_name}: "
                f"{sorted(invalid)}"
            ),
        )


def check_disjoint(
    left_values: list[str],
    right_values: list[str],
    code: str,
    left_name: str,
    right_name: str,
    record_id: str,
    issues: list[GraphIssue],
) -> None:

    overlap = (
        set(left_values)
        & set(right_values)
    )

    if overlap:
        add_issue(
            issues,
            code,
            (
                f"{record_id}: "
                f"{left_name} and "
                f"{right_name} must be disjoint; "
                f"overlap={sorted(overlap)}"
            ),
        )


# ============================================================================
# Audit Graph validation
# ============================================================================

def validate_audit_graph(
    registries: dict[
        str,
        dict[str, dict[str, Any]],
    ],
) -> list[GraphIssue]:

    issues: list[GraphIssue] = []

    cases = registries[
        "audit-case-record"
    ]

    # ------------------------------------------------------------------------
    # Exactly one case per fixture
    # ------------------------------------------------------------------------

    if len(cases) != 1:
        add_issue(
            issues,
            "CASE_COUNT_INVALID",
            (
                "fixture must contain exactly "
                f"one Audit Case; found {len(cases)}"
            ),
        )

        return issues

    case_id, case = next(
        iter(cases.items())
    )

    origin_ref = case["origin_ref"]
    derivative_ref = case["derivative_ref"]

    # ------------------------------------------------------------------------
    # Case / Origin / Derivative consistency
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
                add_issue(
                    issues,
                    "CASE_REF_MISMATCH",
                    (
                        f"{record_id}: "
                        f"case_ref="
                        f"{record.get('case_ref')!r} "
                        f"does not match "
                        f"{case_id!r}"
                    ),
                )

            if record.get("origin_ref") != origin_ref:
                add_issue(
                    issues,
                    "ORIGIN_MISMATCH",
                    (
                        f"{record_id}: "
                        "origin_ref does not match "
                        f"Audit Case origin_ref "
                        f"{origin_ref!r}"
                    ),
                )

            if (
                record.get("derivative_ref")
                != derivative_ref
            ):
                add_issue(
                    issues,
                    "DERIVATIVE_MISMATCH",
                    (
                        f"{record_id}: "
                        "derivative_ref does not match "
                        f"Audit Case derivative_ref "
                        f"{derivative_ref!r}"
                    ),
                )

    # ------------------------------------------------------------------------
    # Case registry integrity
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

        unregistered_actual = (
            actual - declared
        )

        unresolved_declared = (
            declared - actual
        )

        if unregistered_actual:
            add_issue(
                issues,
                "CASE_REGISTRY_INCOMPLETE",
                (
                    f"{case_id}: "
                    f"{field_name} does not register "
                    f"existing record(s): "
                    f"{sorted(unregistered_actual)}"
                ),
            )

        if unresolved_declared:
            add_issue(
                issues,
                "CASE_REGISTRY_UNRESOLVED",
                (
                    f"{case_id}: "
                    f"{field_name} contains unresolved "
                    f"record(s): "
                    f"{sorted(unresolved_declared)}"
                ),
            )

    # ------------------------------------------------------------------------
    # Current assessment
    # ------------------------------------------------------------------------

    current_assessment_ref = (
        case.get("current_assessment_ref")
    )

    if current_assessment_ref is not None:

        assessment_registry = registries[
            "derivation-assessment-record"
        ]

        if (
            current_assessment_ref
            not in assessment_registry
        ):
            add_issue(
                issues,
                "CURRENT_ASSESSMENT_UNRESOLVED",
                (
                    f"{case_id}: "
                    "current_assessment_ref "
                    f"{current_assessment_ref!r} "
                    "does not resolve"
                ),
            )

        if (
            current_assessment_ref
            not in case.get(
                "assessment_refs",
                [],
            )
        ):
            add_issue(
                issues,
                "CURRENT_ASSESSMENT_UNREGISTERED",
                (
                    f"{case_id}: "
                    "current_assessment_ref "
                    f"{current_assessment_ref!r} "
                    "is not registered in "
                    "assessment_refs"
                ),
            )

    # ------------------------------------------------------------------------
    # Evidence relationships
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
            expected_schema="audit-evidence-record",
            registries=registries,
            location=(
                f"{relationship_id}.evidence_refs"
            ),
            issues=issues,
        )

        check_subset(
            child_values=evidence_refs,
            parent_values=case.get(
                "evidence_refs",
                [],
            ),
            code="RELATIONSHIP_EVIDENCE_OUTSIDE_CASE",
            child_name="evidence_refs",
            parent_name="case.evidence_refs",
            record_id=relationship_id,
            issues=issues,
        )

    # ------------------------------------------------------------------------
    # Evidence Fusion
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
            expected_schema="audit-evidence-record",
            registries=registries,
            location=f"{fusion_id}.evidence_refs",
            issues=issues,
        )

        check_ref_list(
            references=relationship_refs,
            expected_schema="evidence-relationship-record",
            registries=registries,
            location=f"{fusion_id}.relationship_refs",
            issues=issues,
        )

        check_subset(
            child_values=fusion_evidence_refs,
            parent_values=case.get(
                "evidence_refs",
                [],
            ),
            code="FUSION_EVIDENCE_OUTSIDE_CASE",
            child_name="evidence_refs",
            parent_name="case.evidence_refs",
            record_id=fusion_id,
            issues=issues,
        )

        check_subset(
            child_values=relationship_refs,
            parent_values=case.get(
                "relationship_refs",
                [],
            ),
            code="FUSION_RELATIONSHIP_OUTSIDE_CASE",
            child_name="relationship_refs",
            parent_name="case.relationship_refs",
            record_id=fusion_id,
            issues=issues,
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
                code="FUSION_SUBSET_INVALID",
                child_name=subset_name,
                parent_name="evidence_refs",
                record_id=fusion_id,
                issues=issues,
            )

        check_disjoint(
            left_values=fusion.get(
                "supporting_evidence_refs",
                [],
            ),
            right_values=fusion.get(
                "counter_evidence_refs",
                [],
            ),
            code="SUPPORT_COUNTER_OVERLAP",
            left_name="supporting_evidence_refs",
            right_name="counter_evidence_refs",
            record_id=fusion_id,
            issues=issues,
        )

        check_disjoint(
            left_values=fusion.get(
                "redundant_evidence_refs",
                [],
            ),
            right_values=fusion.get(
                "effective_evidence_refs",
                [],
            ),
            code="REDUNDANT_EFFECTIVE_OVERLAP",
            left_name="redundant_evidence_refs",
            right_name="effective_evidence_refs",
            record_id=fusion_id,
            issues=issues,
        )

        # Every Relationship used by a Fusion
        # must only reference Evidence that is
        # inside that Fusion.
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
                code=(
                    "RELATIONSHIP_OUTSIDE_FUSION"
                ),
                child_name=(
                    f"{relationship_ref}.evidence_refs"
                ),
                parent_name=(
                    f"{fusion_id}.evidence_refs"
                ),
                record_id=fusion_id,
                issues=issues,
            )

    # ------------------------------------------------------------------------
    # Derivation Assessment
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
            expected_schema="audit-evidence-record",
            registries=registries,
            location=(
                f"{assessment_id}.evidence_refs"
            ),
            issues=issues,
        )

        check_ref_list(
            references=assessment_fusion_refs,
            expected_schema="evidence-fusion-record",
            registries=registries,
            location=(
                f"{assessment_id}.fusion_refs"
            ),
            issues=issues,
        )

        check_subset(
            child_values=assessment_evidence_refs,
            parent_values=case.get(
                "evidence_refs",
                [],
            ),
            code="ASSESSMENT_EVIDENCE_OUTSIDE_CASE",
            child_name="evidence_refs",
            parent_name="case.evidence_refs",
            record_id=assessment_id,
            issues=issues,
        )

        check_subset(
            child_values=assessment_fusion_refs,
            parent_values=case.get(
                "fusion_refs",
                [],
            ),
            code="ASSESSMENT_FUSION_OUTSIDE_CASE",
            child_name="fusion_refs",
            parent_name="case.fusion_refs",
            record_id=assessment_id,
            issues=issues,
        )

        check_subset(
            child_values=assessment.get(
                "conflicting_evidence_refs",
                [],
            ),
            parent_values=assessment_evidence_refs,
            code="ASSESSMENT_CONFLICT_SUBSET_INVALID",
            child_name=(
                "conflicting_evidence_refs"
            ),
            parent_name="evidence_refs",
            record_id=assessment_id,
            issues=issues,
        )

        fused_evidence: set[str] = set()

        for fusion_ref in assessment_fusion_refs:

            fusion = fusions.get(
                fusion_ref
            )

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
            add_issue(
                issues,
                "ASSESSMENT_EVIDENCE_NOT_FUSED",
                (
                    f"{assessment_id}: "
                    "assessment contains evidence "
                    "not present in any referenced "
                    f"Fusion: "
                    f"{sorted(assessment_only)}"
                ),
            )

    # ------------------------------------------------------------------------
    # ZK Audit Attestation
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
                issues=issues,
            )

        elif context_type != "other":
            add_issue(
                issues,
                "ATTESTATION_CONTEXT_TYPE_INVALID",
                (
                    f"{attestation_id}: "
                    "unsupported "
                    "audit_context_type "
                    f"{context_type!r}"
                ),
            )

        # MEDA-looking committed references
        # must resolve inside this fixture.
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
                if committed_ref not in all_protocol_ids:
                    add_issue(
                        issues,
                        "ATTESTATION_COMMITMENT_UNRESOLVED",
                        (
                            f"{attestation_id}: "
                            "unresolved protocol "
                            "committed_input "
                            f"{committed_ref!r}"
                        ),
                    )

        public_inputs = attestation.get(
            "public_inputs",
            {},
        )

        if (
            "case_ref" in public_inputs
            and public_inputs["case_ref"]
            != case_id
        ):
            add_issue(
                issues,
                "ATTESTATION_PUBLIC_CASE_MISMATCH",
                (
                    f"{attestation_id}: "
                    "public_inputs.case_ref "
                    "does not match Audit Case"
                ),
            )

        if (
            "origin_ref" in public_inputs
            and public_inputs["origin_ref"]
            != origin_ref
        ):
            add_issue(
                issues,
                "ATTESTATION_PUBLIC_ORIGIN_MISMATCH",
                (
                    f"{attestation_id}: "
                    "public_inputs.origin_ref "
                    "does not match Audit Case"
                ),
            )

        if (
            "derivative_ref" in public_inputs
            and public_inputs["derivative_ref"]
            != derivative_ref
        ):
            add_issue(
                issues,
                "ATTESTATION_PUBLIC_DERIVATIVE_MISMATCH",
                (
                    f"{attestation_id}: "
                    "public_inputs.derivative_ref "
                    "does not match Audit Case"
                ),
            )

        if (
            context_type == "fusion"
            and "fusion_ref" in public_inputs
            and public_inputs["fusion_ref"]
            != context_ref
        ):
            add_issue(
                issues,
                "ATTESTATION_PUBLIC_CONTEXT_MISMATCH",
                (
                    f"{attestation_id}: "
                    "public_inputs.fusion_ref "
                    "does not match "
                    "audit_context_ref"
                ),
            )

    return issues


# ============================================================================
# PASS Graph validation
# ============================================================================

def validate_pass_cases(
    validators: dict[str, Draft202012Validator],
) -> int:

    failures = 0

    print("[pass graph cases]")

    for case_name in PASS_CASES:

        case_dir = (
            PASS_CASES_DIR
            / case_name
        )

        print()
        print(
            f"  case: {case_name}"
        )

        records = load_case_records(
            case_dir
        )

        version_errors = validate_case_versions(
            records=records,
            case_label=f"pass/{case_name}",
        )

        schema_errors = validate_case_schemas(
            validators=validators,
            records=records,
        )

        if version_errors:
            failures += len(version_errors)

            for error in version_errors:
                print(
                    f"    [FAIL] version: {error}"
                )

        if schema_errors:
            failures += len(schema_errors)

            for error in schema_errors:
                print(
                    f"    [FAIL] schema: {error}"
                )

        if version_errors or schema_errors:
            continue

        registries, registry_errors = (
            build_record_registries(
                records
            )
        )

        if registry_errors:
            failures += len(registry_errors)

            for error in registry_errors:
                print(
                    f"    [FAIL] registry: {error}"
                )

            continue

        issues = validate_audit_graph(
            registries
        )

        if issues:
            failures += len(issues)

            for issue in issues:
                print(
                    f"    [graph-fail] "
                    f"{issue.code}: "
                    f"{issue.message}"
                )

            continue

        total_records = sum(
            len(registry)
            for registry
            in registries.values()
        )

        print(
            f"    [schema-ok] "
            f"{total_records} records"
        )

        print(
            "    [graph-ok] "
            "all references resolve and "
            "cross-record invariants hold"
        )

    print()

    return failures


# ============================================================================
# EXPECTED-FAIL Graph validation
# ============================================================================

def validate_expected_fail_cases(
    validators: dict[str, Draft202012Validator],
) -> int:

    failures = 0

    print("[expected-fail graph cases]")

    for case_name, config in FAIL_CASES.items():

        case_dir = (
            FAIL_CASES_DIR
            / case_name
        )

        expected_codes = set(
            config["expected_issue_codes"]
        )

        print()
        print(
            f"  case: {case_name}"
        )

        print(
            "    expected issue code(s): "
            + ", ".join(
                sorted(expected_codes)
            )
        )

        records = load_case_records(
            case_dir
        )

        version_errors = validate_case_versions(
            records=records,
            case_label=f"fail/{case_name}",
        )

        schema_errors = validate_case_schemas(
            validators=validators,
            records=records,
        )

        # FAIL Graph fixtures must still be valid
        # individual MEDA records.
        if version_errors:
            failures += len(version_errors)

            for error in version_errors:
                print(
                    f"    [FAIL] version: {error}"
                )

            continue

        if schema_errors:
            failures += len(schema_errors)

            print(
                "    [FAIL] expected "
                "Schema-valid fixture"
            )

            for error in schema_errors:
                print(
                    f"      - {error}"
                )

            continue

        registries, registry_errors = (
            build_record_registries(
                records
            )
        )

        if registry_errors:
            failures += len(registry_errors)

            print(
                "    [FAIL] registry construction "
                "failed before Graph validation"
            )

            for error in registry_errors:
                print(
                    f"      - {error}"
                )

            continue

        issues = validate_audit_graph(
            registries
        )

        if not issues:
            failures += 1

            print(
                "    [FAIL] graph unexpectedly passed"
            )

            continue

        actual_codes = {
            issue.code
            for issue in issues
        }

        missing_expected = (
            expected_codes
            - actual_codes
        )

        unexpected = (
            actual_codes
            - expected_codes
        )

        if missing_expected:
            failures += len(
                missing_expected
            )

            print(
                "    [FAIL] expected Graph issue "
                "was not produced:"
            )

            for code in sorted(
                missing_expected
            ):
                print(
                    f"      - {code}"
                )

        if unexpected:
            failures += len(
                unexpected
            )

            print(
                "    [FAIL] unexpected Graph "
                "issue code(s) detected:"
            )

            for code in sorted(
                unexpected
            ):
                print(
                    f"      - {code}"
                )

        if (
            not missing_expected
            and not unexpected
        ):
            print(
                "    [schema-ok]"
            )

            print(
                "    [expected-graph-fail]"
            )

            for issue in issues:
                print(
                    f"      - {issue.code}: "
                    f"{issue.message}"
                )

    print()

    return failures


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

        failures += verify_all_case_inventories()

        failures += validate_pass_cases(
            validators
        )

        failures += (
            validate_expected_fail_cases(
                validators
            )
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
            "All 6 schemas are valid. "
            "The Reference Case passed complete "
            "Audit Graph validation, and all 6 "
            "expected-fail Graph cases were rejected "
            "for their intended cross-record "
            "integrity violations."
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
