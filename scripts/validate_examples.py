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
PASS_CASES_DIR = ROOT / "examples" / "cases" / "pass"
FAIL_CASES_DIR = ROOT / "examples" / "cases" / "fail"


# ============================================================================
# Protocol constants
# ============================================================================

PROTOCOL_VERSION = "0.4.0"


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

    "audit-challenge-record":
        SCHEMAS_DIR / "audit-challenge-record.schema.json",

    "reproduction-record":
        SCHEMAS_DIR / "reproduction-record.schema.json",

    "assessment-revision-record":
        SCHEMAS_DIR / "assessment-revision-record.schema.json",
}


# ============================================================================
# Record identifier fields
# ============================================================================

ID_FIELDS = {
    "audit-case-record": "case_id",
    "audit-evidence-record": "evidence_id",
    "evidence-relationship-record": "relationship_id",
    "evidence-fusion-record": "fusion_id",
    "derivation-assessment-record": "assessment_id",
    "zk-audit-attestation": "attestation_id",
    "audit-challenge-record": "challenge_id",
    "reproduction-record": "reproduction_id",
    "assessment-revision-record": "revision_id",
}


# ============================================================================
# Typed protocol references
# ============================================================================

RECORD_TYPE_TO_SCHEMA = {
    "case": "audit-case-record",
    "evidence": "audit-evidence-record",
    "relationship": "evidence-relationship-record",
    "fusion": "evidence-fusion-record",
    "assessment": "derivation-assessment-record",
    "attestation": "zk-audit-attestation",
    "challenge": "audit-challenge-record",
    "reproduction": "reproduction-record",
    "revision": "assessment-revision-record",
}


# ============================================================================
# PASS Temporal Graph inventory
# ============================================================================

PASS_CASES = {
    "reference-case": {
        "expected_files": {
            "audit-case-record.json",

            "evidence/evidence-0001.watermark.json",
            "evidence/evidence-0002.signed-receipt.json",
            "evidence/evidence-0003.api-trace.json",
            "evidence/evidence-0004.similarity.json",
            "evidence/evidence-0005.reproduction-output.json",

            "relationships/relationship-0001.same-source.json",
            "relationships/relationship-0002.independent-corroboration.json",
            "relationships/relationship-0003.reproduction-conflict.json",

            "fusion/fusion-0001.json",
            "fusion/fusion-0002.json",

            "assessments/assessment-0001.json",
            "assessments/assessment-0002.json",

            "attestations/zk-attestation-0001.json",

            "challenges/challenge-0001.json",

            "reproductions/reproduction-0001.json",

            "revisions/revision-0001.json",
        }
    }
}


# ============================================================================
# EXPECTED-FAIL Temporal Graph inventory
# ============================================================================

FAIL_CASES = {
    "unresolved-challenge-target": {
        "expected_files": {
            "audit-case-record.json",
            "challenges/challenge-0001.json",
        },
        "expected_issue_codes": {
            "UNRESOLVED_CHALLENGE_TARGET",
        },
    },

    "orphan-reproduction-output": {
        "expected_files": {
            "audit-case-record.json",
            "evidence/evidence-0001.json",
        },
        "expected_issue_codes": {
            "ORPHAN_REPRODUCTION_OUTPUT",
        },
    },

    "broken-revision-chain": {
        "expected_files": {
            "audit-case-record.json",
            "evidence/evidence-0001.json",
            "fusion/fusion-0001.json",
            "assessments/assessment-0002.json",
            "revisions/revision-0001.json",
        },
        "expected_issue_codes": {
            "REVISION_PRIOR_UNRESOLVED",
        },
    },

    "wrong-current-assessment": {
        "expected_files": {
            "audit-case-record.json",
            "evidence/evidence-0001.json",
            "fusion/fusion-0001.json",
            "assessments/assessment-0001.json",
            "assessments/assessment-0002.json",
            "revisions/revision-0001.json",
        },
        "expected_issue_codes": {
            "CURRENT_ASSESSMENT_NOT_TERMINAL",
        },
    },

    "revision-cycle": {
        "expected_files": {
            "audit-case-record.json",
            "evidence/evidence-0001.json",
            "fusion/fusion-0001.json",
            "assessments/assessment-0001.json",
            "assessments/assessment-0002.json",
            "revisions/revision-0001.json",
            "revisions/revision-0002.json",
        },
        "expected_issue_codes": {
            "REVISION_CYCLE",
            "CURRENT_ASSESSMENT_NOT_TERMINAL",
        },
    },
}


# ============================================================================
# Graph issue
# ============================================================================

@dataclass(frozen=True)
class GraphIssue:
    code: str
    message: str


# ============================================================================
# Generic helpers
# ============================================================================

def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
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

    if path.startswith("challenges/"):
        return "audit-challenge-record"

    if path.startswith("reproductions/"):
        return "reproduction-record"

    if path.startswith("revisions/"):
        return "assessment-revision-record"

    raise RuntimeError(
        f"Cannot determine schema for case file: {path}"
    )


# ============================================================================
# Load JSON Schema validators
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

    for filename in sorted(expected - actual):
        failures += 1
        print(
            f"  [FAIL] missing schema: {filename}"
        )

    for filename in sorted(actual - expected):
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
# Case-root inventory
# ============================================================================

def verify_case_root_inventory() -> int:

    failures = 0

    print("[case root inventory]")

    expected_pass = set(PASS_CASES)
    expected_fail = set(FAIL_CASES)

    actual_pass = {
        path.name
        for path in PASS_CASES_DIR.iterdir()
        if path.is_dir()
    } if PASS_CASES_DIR.exists() else set()

    actual_fail = {
        path.name
        for path in FAIL_CASES_DIR.iterdir()
        if path.is_dir()
    } if FAIL_CASES_DIR.exists() else set()

    for name in sorted(expected_pass - actual_pass):
        failures += 1
        print(
            f"  [FAIL] missing pass case: {name}"
        )

    for name in sorted(actual_pass - expected_pass):
        failures += 1
        print(
            f"  [FAIL] unregistered pass case: {name}"
        )

    for name in sorted(expected_fail - actual_fail):
        failures += 1
        print(
            f"  [FAIL] missing fail case: {name}"
        )

    for name in sorted(actual_fail - expected_fail):
        failures += 1
        print(
            f"  [FAIL] unregistered fail case: {name}"
        )

    if failures == 0:
        print(
            "  [inventory-ok] "
            "1 PASS case and 5 EXPECTED-FAIL cases registered"
        )

    print()

    return failures


# ============================================================================
# Individual Case inventory
# ============================================================================

def verify_case_inventory(
    case_dir: Path,
    expected_files: set[str],
    label: str,
) -> int:

    failures = 0

    actual_files = {
        path.relative_to(case_dir).as_posix()
        for path in case_dir.rglob("*.json")
        if path.is_file()
    } if case_dir.exists() else set()

    missing = expected_files - actual_files
    extra = actual_files - expected_files

    for filename in sorted(missing):
        failures += 1
        print(
            f"  [FAIL] {label}: "
            f"missing file: {filename}"
        )

    for filename in sorted(extra):
        failures += 1
        print(
            f"  [FAIL] {label}: "
            f"unregistered file: {filename}"
        )

    return failures


def verify_all_case_inventories() -> int:

    failures = 0

    print("[case file inventory]")

    for case_name, config in PASS_CASES.items():

        case_failures = verify_case_inventory(
            PASS_CASES_DIR / case_name,
            config["expected_files"],
            f"pass/{case_name}",
        )

        failures += case_failures

        if case_failures == 0:
            print(
                f"  [inventory-ok] pass/{case_name}: "
                f"{len(config['expected_files'])} records"
            )

    for case_name, config in FAIL_CASES.items():

        case_failures = verify_case_inventory(
            FAIL_CASES_DIR / case_name,
            config["expected_files"],
            f"fail/{case_name}",
        )

        failures += case_failures

        if case_failures == 0:
            print(
                f"  [inventory-ok] fail/{case_name}: "
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
        tuple[str, dict[str, Any]]
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
        tuple[str, dict[str, Any]]
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
                f"expected {PROTOCOL_VERSION!r}"
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
                    f"expected {PROTOCOL_VERSION!r}"
                )

    return errors


# ============================================================================
# Schema validation
# ============================================================================

def validate_case_schemas(
    validators: dict[str, Draft202012Validator],
    records: dict[
        Path,
        tuple[str, dict[str, Any]]
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

def build_registries(
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
    global_ids: dict[str, str] = {}

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

        if record_id in global_ids:
            errors.append(
                f"{relative_path.as_posix()}: "
                f"global ID collision {record_id}; "
                f"already used by {global_ids[record_id]}"
            )
            continue

        registries[schema_name][record_id] = record
        global_ids[record_id] = schema_name

    return registries, errors


# ============================================================================
# Graph helpers
# ============================================================================

def check_ref(
    reference: str,
    expected_schema: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]]
    ],
    code: str,
    location: str,
    issues: list[GraphIssue],
) -> bool:

    if reference not in registries[expected_schema]:

        add_issue(
            issues,
            code,
            (
                f"{location}: unresolved reference "
                f"{reference!r}; "
                f"expected type={expected_schema}"
            ),
        )

        return False

    return True


def check_ref_list(
    references: list[str],
    expected_schema: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]]
    ],
    code: str,
    location: str,
    issues: list[GraphIssue],
) -> None:

    for reference in references:

        check_ref(
            reference=reference,
            expected_schema=expected_schema,
            registries=registries,
            code=code,
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
                f"outside {parent_name}: "
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
                f"{left_name} and {right_name} "
                f"must be disjoint; "
                f"overlap={sorted(overlap)}"
            ),
        )


# ============================================================================
# Temporal Audit Graph validator
# ============================================================================

def validate_audit_graph(
    registries: dict[
        str,
        dict[str, dict[str, Any]]
    ],
) -> list[GraphIssue]:

    issues: list[GraphIssue] = []

    cases = registries[
        "audit-case-record"
    ]

    # ------------------------------------------------------------------------
    # Exactly one Case
    # ------------------------------------------------------------------------

    if len(cases) != 1:

        add_issue(
            issues,
            "CASE_COUNT_INVALID",
            (
                "fixture must contain exactly one "
                f"Audit Case; found {len(cases)}"
            ),
        )

        return issues

    case_id, case = next(
        iter(cases.items())
    )

    origin_ref = case[
        "origin_ref"
    ]

    derivative_ref = case[
        "derivative_ref"
    ]

    # ------------------------------------------------------------------------
    # Case / Origin / Derivative coherence
    # ------------------------------------------------------------------------

    member_schemas = [
        "audit-evidence-record",
        "evidence-relationship-record",
        "evidence-fusion-record",
        "derivation-assessment-record",
        "zk-audit-attestation",
        "audit-challenge-record",
        "reproduction-record",
        "assessment-revision-record",
    ]

    for schema_name in member_schemas:

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
                        f"does not match {case_id!r}"
                    ),
                )

            if record.get("origin_ref") != origin_ref:

                add_issue(
                    issues,
                    "ORIGIN_MISMATCH",
                    (
                        f"{record_id}: "
                        "origin_ref does not match "
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
                        f"{derivative_ref!r}"
                    ),
                )

    # ------------------------------------------------------------------------
    # Case Registry completeness
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

        "challenge_refs":
            "audit-challenge-record",

        "reproduction_refs":
            "reproduction-record",

        "revision_refs":
            "assessment-revision-record",
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
    # Current Assessment existence
    # ------------------------------------------------------------------------

    current_assessment_ref = (
        case.get("current_assessment_ref")
    )

    if current_assessment_ref is not None:

        if (
            current_assessment_ref
            not in registries[
                "derivation-assessment-record"
            ]
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

        elif (
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
                    f"{current_assessment_ref!r} "
                    "is not registered in "
                    "assessment_refs"
                ),
            )

    # ------------------------------------------------------------------------
    # Evidence Relationships
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
            code="RELATIONSHIP_EVIDENCE_UNRESOLVED",
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

        evidence_refs = fusion.get(
            "evidence_refs",
            [],
        )

        relationship_refs = fusion.get(
            "relationship_refs",
            [],
        )

        check_ref_list(
            references=evidence_refs,
            expected_schema="audit-evidence-record",
            registries=registries,
            code="FUSION_EVIDENCE_UNRESOLVED",
            location=f"{fusion_id}.evidence_refs",
            issues=issues,
        )

        check_ref_list(
            references=relationship_refs,
            expected_schema="evidence-relationship-record",
            registries=registries,
            code="FUSION_RELATIONSHIP_UNRESOLVED",
            location=f"{fusion_id}.relationship_refs",
            issues=issues,
        )

        check_subset(
            child_values=evidence_refs,
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

        for subset_name in [
            "supporting_evidence_refs",
            "counter_evidence_refs",
            "redundant_evidence_refs",
            "effective_evidence_refs",
        ]:

            check_subset(
                child_values=fusion.get(
                    subset_name,
                    [],
                ),
                parent_values=evidence_refs,
                code="FUSION_SUBSET_INVALID",
                child_name=subset_name,
                parent_name="fusion.evidence_refs",
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
                parent_values=evidence_refs,
                code="RELATIONSHIP_OUTSIDE_FUSION",
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
    # Assessments
    # ------------------------------------------------------------------------

    assessments = registries[
        "derivation-assessment-record"
    ]

    for assessment_id, assessment in (
        assessments.items()
    ):

        evidence_refs = assessment.get(
            "evidence_refs",
            [],
        )

        fusion_refs = assessment.get(
            "fusion_refs",
            [],
        )

        check_ref_list(
            references=evidence_refs,
            expected_schema="audit-evidence-record",
            registries=registries,
            code="ASSESSMENT_EVIDENCE_UNRESOLVED",
            location=f"{assessment_id}.evidence_refs",
            issues=issues,
        )

        check_ref_list(
            references=fusion_refs,
            expected_schema="evidence-fusion-record",
            registries=registries,
            code="ASSESSMENT_FUSION_UNRESOLVED",
            location=f"{assessment_id}.fusion_refs",
            issues=issues,
        )

        check_subset(
            child_values=evidence_refs,
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
            child_values=fusion_refs,
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
            parent_values=evidence_refs,
            code="ASSESSMENT_CONFLICT_SUBSET_INVALID",
            child_name="conflicting_evidence_refs",
            parent_name="assessment.evidence_refs",
            record_id=assessment_id,
            issues=issues,
        )

        fused_evidence: set[str] = set()

        for fusion_ref in fusion_refs:

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

        unfused = (
            set(evidence_refs)
            - fused_evidence
        )

        if unfused:

            add_issue(
                issues,
                "ASSESSMENT_EVIDENCE_NOT_FUSED",
                (
                    f"{assessment_id}: "
                    "assessment contains evidence "
                    "not present in any referenced "
                    f"Fusion: {sorted(unfused)}"
                ),
            )

    # ------------------------------------------------------------------------
    # Challenge Target integrity
    # ------------------------------------------------------------------------

    challenges = registries[
        "audit-challenge-record"
    ]

    for challenge_id, challenge in (
        challenges.items()
    ):

        target_type = challenge.get(
            "target_record_type"
        )

        target_ref = challenge.get(
            "target_record_ref"
        )

        target_schema = (
            RECORD_TYPE_TO_SCHEMA.get(
                target_type
            )
        )

        if (
            target_schema is None
            or target_ref not in registries[
                target_schema
            ]
        ):

            add_issue(
                issues,
                "UNRESOLVED_CHALLENGE_TARGET",
                (
                    f"{challenge_id}: "
                    f"{target_type!r} target "
                    f"{target_ref!r} does not resolve"
                ),
            )

        check_ref_list(
            references=challenge.get(
                "related_evidence_refs",
                [],
            ),
            expected_schema="audit-evidence-record",
            registries=registries,
            code="CHALLENGE_EVIDENCE_UNRESOLVED",
            location=(
                f"{challenge_id}."
                "related_evidence_refs"
            ),
            issues=issues,
        )

    # ------------------------------------------------------------------------
    # Reproduction integrity
    # ------------------------------------------------------------------------

    reproductions = registries[
        "reproduction-record"
    ]

    for reproduction_id, reproduction in (
        reproductions.items()
    ):

        target_type = reproduction.get(
            "target_record_type"
        )

        target_ref = reproduction.get(
            "target_record_ref"
        )

        target_schema = (
            RECORD_TYPE_TO_SCHEMA.get(
                target_type
            )
        )

        if (
            target_schema is None
            or target_ref not in registries[
                target_schema
            ]
        ):

            add_issue(
                issues,
                "UNRESOLVED_REPRODUCTION_TARGET",
                (
                    f"{reproduction_id}: "
                    f"{target_type!r} target "
                    f"{target_ref!r} does not resolve"
                ),
            )

        check_ref_list(
            references=reproduction.get(
                "challenge_refs",
                [],
            ),
            expected_schema="audit-challenge-record",
            registries=registries,
            code="REPRODUCTION_CHALLENGE_UNRESOLVED",
            location=(
                f"{reproduction_id}.challenge_refs"
            ),
            issues=issues,
        )

        produced_evidence_refs = (
            reproduction.get(
                "produced_evidence_refs",
                [],
            )
        )

        check_ref_list(
            references=produced_evidence_refs,
            expected_schema="audit-evidence-record",
            registries=registries,
            code="REPRODUCTION_EVIDENCE_UNRESOLVED",
            location=(
                f"{reproduction_id}."
                "produced_evidence_refs"
            ),
            issues=issues,
        )

        check_subset(
            child_values=produced_evidence_refs,
            parent_values=case.get(
                "evidence_refs",
                [],
            ),
            code="REPRODUCTION_EVIDENCE_OUTSIDE_CASE",
            child_name="produced_evidence_refs",
            parent_name="case.evidence_refs",
            record_id=reproduction_id,
            issues=issues,
        )

    # ------------------------------------------------------------------------
    # Reproduction-output Evidence backlink
    # ------------------------------------------------------------------------

    evidence_registry = registries[
        "audit-evidence-record"
    ]

    for evidence_id, evidence in (
        evidence_registry.items()
    ):

        if (
            evidence.get("evidence_type")
            != "reproduction_output"
        ):
            continue

        reproduction_ref = evidence.get(
            "observation",
            {},
        ).get(
            "reproduction_ref"
        )

        if (
            not isinstance(reproduction_ref, str)
            or reproduction_ref
            not in reproductions
        ):

            add_issue(
                issues,
                "ORPHAN_REPRODUCTION_OUTPUT",
                (
                    f"{evidence_id}: "
                    "reproduction_output refers to "
                    f"missing reproduction "
                    f"{reproduction_ref!r}"
                ),
            )

            continue

        reproduction = reproductions[
            reproduction_ref
        ]

        if evidence_id not in reproduction.get(
            "produced_evidence_refs",
            [],
        ):

            add_issue(
                issues,
                "REPRODUCTION_BACKLINK_MISSING",
                (
                    f"{evidence_id}: "
                    f"{reproduction_ref} does not "
                    "register this evidence in "
                    "produced_evidence_refs"
                ),
            )

    # ------------------------------------------------------------------------
    # Revision integrity
    # ------------------------------------------------------------------------

    revisions = registries[
        "assessment-revision-record"
    ]

    applied_edges: dict[str, str] = {}

    for revision_id, revision in (
        revisions.items()
    ):

        prior = revision.get(
            "prior_assessment_ref"
        )

        revised = revision.get(
            "revised_assessment_ref"
        )

        prior_resolved = (
            prior in assessments
        )

        revised_resolved = (
            revised in assessments
        )

        if not prior_resolved:

            add_issue(
                issues,
                "REVISION_PRIOR_UNRESOLVED",
                (
                    f"{revision_id}: "
                    "prior_assessment_ref "
                    f"{prior!r} does not resolve"
                ),
            )

        if not revised_resolved:

            add_issue(
                issues,
                "REVISION_REVISED_UNRESOLVED",
                (
                    f"{revision_id}: "
                    "revised_assessment_ref "
                    f"{revised!r} does not resolve"
                ),
            )

        if (
            prior_resolved
            and prior not in case.get(
                "assessment_refs",
                [],
            )
        ):

            add_issue(
                issues,
                "REVISION_PRIOR_OUTSIDE_CASE",
                (
                    f"{revision_id}: "
                    f"{prior!r} is not registered "
                    "in case.assessment_refs"
                ),
            )

        if (
            revised_resolved
            and revised not in case.get(
                "assessment_refs",
                [],
            )
        ):

            add_issue(
                issues,
                "REVISION_REVISED_OUTSIDE_CASE",
                (
                    f"{revision_id}: "
                    f"{revised!r} is not registered "
                    "in case.assessment_refs"
                ),
            )

        if (
            prior_resolved
            and revised_resolved
            and prior == revised
        ):

            add_issue(
                issues,
                "REVISION_SELF_LOOP",
                (
                    f"{revision_id}: "
                    "prior and revised assessment "
                    "must differ"
                ),
            )

        check_ref_list(
            references=revision.get(
                "challenge_refs",
                [],
            ),
            expected_schema="audit-challenge-record",
            registries=registries,
            code="REVISION_CHALLENGE_UNRESOLVED",
            location=(
                f"{revision_id}.challenge_refs"
            ),
            issues=issues,
        )

        check_ref_list(
            references=revision.get(
                "reproduction_refs",
                [],
            ),
            expected_schema="reproduction-record",
            registries=registries,
            code="REVISION_REPRODUCTION_UNRESOLVED",
            location=(
                f"{revision_id}.reproduction_refs"
            ),
            issues=issues,
        )

        check_ref_list(
            references=revision.get(
                "evidence_added_refs",
                [],
            ),
            expected_schema="audit-evidence-record",
            registries=registries,
            code="REVISION_ADDED_EVIDENCE_UNRESOLVED",
            location=(
                f"{revision_id}.evidence_added_refs"
            ),
            issues=issues,
        )

        check_ref_list(
            references=revision.get(
                "evidence_removed_refs",
                [],
            ),
            expected_schema="audit-evidence-record",
            registries=registries,
            code="REVISION_REMOVED_EVIDENCE_UNRESOLVED",
            location=(
                f"{revision_id}.evidence_removed_refs"
            ),
            issues=issues,
        )

        check_ref_list(
            references=revision.get(
                "fusion_refs",
                [],
            ),
            expected_schema="evidence-fusion-record",
            registries=registries,
            code="REVISION_FUSION_UNRESOLVED",
            location=(
                f"{revision_id}.fusion_refs"
            ),
            issues=issues,
        )

        check_disjoint(
            left_values=revision.get(
                "evidence_added_refs",
                [],
            ),
            right_values=revision.get(
                "evidence_removed_refs",
                [],
            ),
            code="REVISION_EVIDENCE_ADD_REMOVE_OVERLAP",
            left_name="evidence_added_refs",
            right_name="evidence_removed_refs",
            record_id=revision_id,
            issues=issues,
        )

        # ------------------------------------------------------------
        # Revision trigger resolution
        # ------------------------------------------------------------

        trigger_type = revision.get(
            "revision_trigger"
        )

        trigger_refs = revision.get(
            "trigger_refs",
            [],
        )

        trigger_schema_map = {
            "challenge":
                "audit-challenge-record",

            "reproduction":
                "reproduction-record",

            "new_evidence":
                "audit-evidence-record",

            "new_fusion":
                "evidence-fusion-record",
        }

        if trigger_type in trigger_schema_map:

            check_ref_list(
                references=trigger_refs,
                expected_schema=(
                    trigger_schema_map[
                        trigger_type
                    ]
                ),
                registries=registries,
                code="REVISION_TRIGGER_UNRESOLVED",
                location=(
                    f"{revision_id}.trigger_refs"
                ),
                issues=issues,
            )

        # ------------------------------------------------------------
        # Revised Assessment coherence
        # ------------------------------------------------------------

        if revised_resolved:

            revised_assessment = assessments[
                revised
            ]

            revised_evidence = set(
                revised_assessment.get(
                    "evidence_refs",
                    [],
                )
            )

            added_evidence = set(
                revision.get(
                    "evidence_added_refs",
                    [],
                )
            )

            missing_added = (
                added_evidence
                - revised_evidence
            )

            if missing_added:

                add_issue(
                    issues,
                    "REVISION_ADDED_EVIDENCE_NOT_IN_REVISED_ASSESSMENT",
                    (
                        f"{revision_id}: "
                        "added evidence is absent "
                        "from revised assessment: "
                        f"{sorted(missing_added)}"
                    ),
                )

            revision_fusions = set(
                revision.get(
                    "fusion_refs",
                    [],
                )
            )

            revised_fusions = set(
                revised_assessment.get(
                    "fusion_refs",
                    [],
                )
            )

            invalid_fusions = (
                revision_fusions
                - revised_fusions
            )

            if invalid_fusions:

                add_issue(
                    issues,
                    "REVISION_FUSION_NOT_IN_REVISED_ASSESSMENT",
                    (
                        f"{revision_id}: "
                        "revision fusion is absent "
                        "from revised assessment: "
                        f"{sorted(invalid_fusions)}"
                    ),
                )

        # ------------------------------------------------------------
        # Applied revision edge
        # ------------------------------------------------------------

        if (
            revision.get("revision_state")
            == "applied"
            and prior_resolved
            and revised_resolved
        ):

            if prior in applied_edges:

                add_issue(
                    issues,
                    "REVISION_MULTIPLE_APPLIED_SUCCESSORS",
                    (
                        f"{revision_id}: "
                        f"{prior!r} already has "
                        "another applied successor"
                    ),
                )

            else:

                applied_edges[
                    prior
                ] = revised

    # ------------------------------------------------------------------------
    # Applied Revision cycle detection
    # ------------------------------------------------------------------------

    cycle_detected = False

    for start in sorted(applied_edges):

        visited: set[str] = set()
        node = start

        while node in applied_edges:

            if node in visited:

                cycle_detected = True
                break

            visited.add(node)
            node = applied_edges[node]

        if cycle_detected:
            break

    if cycle_detected:

        add_issue(
            issues,
            "REVISION_CYCLE",
            (
                "applied assessment revision "
                "chain contains a cycle"
            ),
        )

    # ------------------------------------------------------------------------
    # Current Assessment must be terminal applied revision
    # ------------------------------------------------------------------------

    if applied_edges:

        prior_nodes = set(
            applied_edges.keys()
        )

        revised_nodes = set(
            applied_edges.values()
        )

        terminal_nodes = (
            revised_nodes
            - prior_nodes
        )

        if (
            current_assessment_ref
            not in terminal_nodes
        ):

            add_issue(
                issues,
                "CURRENT_ASSESSMENT_NOT_TERMINAL",
                (
                    f"{case_id}: "
                    "current_assessment_ref "
                    f"{current_assessment_ref!r} "
                    "is not a terminal applied "
                    "revision assessment; "
                    f"terminal={sorted(terminal_nodes)}"
                ),
            )

    # ------------------------------------------------------------------------
    # ZK Attestation integrity
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

        if context_type != "other":

            context_schema = (
                RECORD_TYPE_TO_SCHEMA.get(
                    context_type
                )
            )

            if (
                context_schema is None
                or context_ref not in registries[
                    context_schema
                ]
            ):

                add_issue(
                    issues,
                    "ATTESTATION_CONTEXT_UNRESOLVED",
                    (
                        f"{attestation_id}: "
                        f"context {context_type!r} "
                        f"{context_ref!r} "
                        "does not resolve"
                    ),
                )

        meda_prefixes = (
            "CASE-",
            "EVIDENCE-",
            "REL-",
            "FUSION-",
            "ASSESSMENT-",
            "ZK-ATTESTATION-",
            "CHALLENGE-",
            "REPRODUCTION-",
            "REVISION-",
        )

        for committed_ref in attestation.get(
            "committed_inputs",
            [],
        ):

            if (
                committed_ref.startswith(
                    meda_prefixes
                )
                and committed_ref
                not in all_protocol_ids
            ):

                add_issue(
                    issues,
                    "ATTESTATION_COMMITMENT_UNRESOLVED",
                    (
                        f"{attestation_id}: "
                        "unresolved committed "
                        f"MEDA reference "
                        f"{committed_ref!r}"
                    ),
                )

    return issues


# ============================================================================
# PASS Temporal Graph validation
# ============================================================================

def validate_pass_cases(
    validators: dict[str, Draft202012Validator],
) -> int:

    failures = 0

    print("[pass temporal graph cases]")

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
            records,
            f"pass/{case_name}",
        )

        schema_errors = validate_case_schemas(
            validators,
            records,
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
            build_registries(records)
        )

        if registry_errors:

            failures += len(
                registry_errors
            )

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
            "all structural and temporal "
            "references resolve"
        )

        print(
            "    [history-ok] "
            "Assessment-0001 → Challenge → "
            "Reproduction → New Evidence → "
            "Re-Fusion → Assessment-0002 → "
            "Revision"
        )

        print(
            "    [revision-ok] "
            "current assessment is the terminal "
            "applied assessment"
        )

    print()

    return failures


# ============================================================================
# EXPECTED-FAIL Temporal Graph validation
# ============================================================================

def validate_expected_fail_cases(
    validators: dict[str, Draft202012Validator],
) -> int:

    failures = 0

    print("[expected-fail temporal graph cases]")

    for case_name, config in FAIL_CASES.items():

        case_dir = (
            FAIL_CASES_DIR
            / case_name
        )

        expected_codes = set(
            config[
                "expected_issue_codes"
            ]
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
            records,
            f"fail/{case_name}",
        )

        schema_errors = validate_case_schemas(
            validators,
            records,
        )

        # ------------------------------------------------------------
        # EXPECTED-FAIL Graphs must still be locally Schema-valid.
        # ------------------------------------------------------------

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
                "    [FAIL] fixture must be "
                "Schema-valid before Graph validation"
            )

            for error in schema_errors:
                print(
                    f"      - {error}"
                )

            continue

        registries, registry_errors = (
            build_registries(records)
        )

        if registry_errors:

            failures += len(
                registry_errors
            )

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
                "    [FAIL] temporal graph "
                "unexpectedly passed"
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

        unexpected_codes = (
            actual_codes
            - expected_codes
        )

        if missing_expected:

            failures += len(
                missing_expected
            )

            print(
                "    [FAIL] expected issue "
                "code(s) not produced:"
            )

            for code in sorted(
                missing_expected
            ):
                print(
                    f"      - {code}"
                )

        if unexpected_codes:

            failures += len(
                unexpected_codes
            )

            print(
                "    [FAIL] unexpected issue "
                "code(s) produced:"
            )

            for code in sorted(
                unexpected_codes
            ):
                print(
                    f"      - {code}"
                )

        if (
            not missing_expected
            and not unexpected_codes
        ):

            print(
                "    [schema-ok]"
            )

            print(
                "    [expected-graph-fail]"
            )

            for issue in issues:

                print(
                    f"      - "
                    f"{issue.code}: "
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
        "v0.4 Temporal Validation ==="
    )

    print()

    try:

        validators = load_validators()

        failures = 0

        failures += verify_schema_inventory()

        failures += verify_case_root_inventory()

        failures += verify_all_case_inventories()

        failures += validate_pass_cases(
            validators
        )

        failures += validate_expected_fail_cases(
            validators
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

        print(
            "[validate-pass]"
        )

        print(
            "All 9 schemas are valid. "
            "The 17-record Reference Case passed "
            "complete structural and temporal Audit "
            "Graph validation, and all 5 "
            "EXPECTED-FAIL Temporal Graph cases "
            "were rejected for exactly their "
            "intended revision-history violations."
        )

        return 0

    print(
        "[validate-fail]"
    )

    print(
        f"{failures} validation "
        "problem(s) detected."
    )

    return 1


if __name__ == "__main__":
    sys.exit(main())
