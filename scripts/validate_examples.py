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

PASS_ROOT = ROOT / "examples" / "cases" / "pass"
FAIL_ROOT = ROOT / "examples" / "cases" / "fail"


# ============================================================================
# Protocol
# ============================================================================

PROTOCOL_VERSION = "0.5.0"


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

    "auditor-opinion-record":
        SCHEMAS_DIR / "auditor-opinion-record.schema.json",

    "audit-reconciliation-record":
        SCHEMAS_DIR / "audit-reconciliation-record.schema.json",

    "audit-handoff-record":
        SCHEMAS_DIR / "audit-handoff-record.schema.json",
}


# ============================================================================
# ID fields
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

    "audit-challenge-record":
        "challenge_id",

    "reproduction-record":
        "reproduction_id",

    "assessment-revision-record":
        "revision_id",

    "auditor-opinion-record":
        "opinion_id",

    "audit-reconciliation-record":
        "reconciliation_id",

    "audit-handoff-record":
        "handoff_id",
}


# ============================================================================
# Typed MEDA references
# ============================================================================

RECORD_TYPE_TO_SCHEMA = {
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

    "attestation":
        "zk-audit-attestation",

    "challenge":
        "audit-challenge-record",

    "reproduction":
        "reproduction-record",

    "revision":
        "assessment-revision-record",

    "opinion":
        "auditor-opinion-record",

    "reconciliation":
        "audit-reconciliation-record",

    "handoff":
        "audit-handoff-record",
}


# ============================================================================
# Case inventory
# ============================================================================

CASE_FILES = {
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

    "opinions/opinion-0001.json",
    "opinions/opinion-0002.json",

    "reconciliations/reconciliation-0001.json",

    "handoffs/handoff-0001.json",
}


PASS_CASES = {
    "reference-case": {
        "expected_files": CASE_FILES,
    },
}


FAIL_CASES = {
    "same-auditor-reconciliation": {
        "failure_stage": "graph",
        "expected_codes": {
            "RECONCILIATION_AUDITOR_DIVERSITY_INSUFFICIENT",
        },
        "expected_files": CASE_FILES,
    },

    "opinion-assessment-mismatch": {
        "failure_stage": "graph",
        "expected_codes": {
            "RECONCILIATION_OPINION_ASSESSMENT_MISMATCH",
        },
        "expected_files": CASE_FILES,
    },

    "unknown-unresolved-point": {
        "failure_stage": "graph",
        "expected_codes": {
            "HANDOFF_UNRESOLVED_POINT_UNKNOWN",
        },
        "expected_files": CASE_FILES,
    },

    "handoff-payload-incomplete": {
        "failure_stage": "graph",
        "expected_codes": {
            "HANDOFF_PAYLOAD_INCOMPLETE",
        },
        "expected_files": CASE_FILES,
    },

    "majority-verdict-applied": {
        "failure_stage": "schema",
        "expected_codes": {
            "MAJORITY_VERDICT_SCHEMA_FORBIDDEN",
        },
        "expected_files": CASE_FILES,
    },

    "internal-decision-authority": {
        "failure_stage": "schema",
        "expected_codes": {
            "INTERNAL_DECISION_AUTHORITY_SCHEMA_FORBIDDEN",
        },
        "expected_files": CASE_FILES,
    },
}


# ============================================================================
# Issue objects
# ============================================================================

@dataclass(frozen=True)
class GraphIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SchemaIssue:
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


def add_graph_issue(
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

    if path.startswith("opinions/"):
        return "auditor-opinion-record"

    if path.startswith("reconciliations/"):
        return "audit-reconciliation-record"

    if path.startswith("handoffs/"):
        return "audit-handoff-record"

    raise RuntimeError(
        f"Cannot determine schema for case file: {path}"
    )


# ============================================================================
# Load / validate schemas
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
# Case root inventory
# ============================================================================

def child_directories(path: Path) -> set[str]:

    if not path.exists():
        return set()

    return {
        item.name
        for item in path.iterdir()
        if item.is_dir()
    }


def verify_case_root_inventory() -> int:

    failures = 0

    expected_pass = set(PASS_CASES)
    expected_fail = set(FAIL_CASES)

    actual_pass = child_directories(PASS_ROOT)
    actual_fail = child_directories(FAIL_ROOT)

    print("[case root inventory]")

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
            f"{len(expected_pass)} PASS case and "
            f"{len(expected_fail)} EXPECTED-FAIL "
            "cases registered"
        )

    print()

    return failures


# ============================================================================
# Per-case file inventory
# ============================================================================

def actual_case_files(
    case_dir: Path,
) -> set[str]:

    return {
        path.relative_to(case_dir).as_posix()
        for path in case_dir.rglob("*.json")
        if path.is_file()
    }


def verify_case_file_inventory() -> int:

    failures = 0

    print("[case file inventory]")

    for case_name, config in PASS_CASES.items():

        case_dir = PASS_ROOT / case_name

        expected = set(config["expected_files"])
        actual = actual_case_files(case_dir)

        case_failures = 0

        for filename in sorted(expected - actual):

            failures += 1
            case_failures += 1

            print(
                f"  [FAIL] pass/{case_name}: "
                f"missing file: {filename}"
            )

        for filename in sorted(actual - expected):

            failures += 1
            case_failures += 1

            print(
                f"  [FAIL] pass/{case_name}: "
                f"unregistered file: {filename}"
            )

        if case_failures == 0:

            print(
                f"  [inventory-ok] pass/{case_name}: "
                f"{len(expected)} records"
            )

    for case_name, config in FAIL_CASES.items():

        case_dir = FAIL_ROOT / case_name

        expected = set(config["expected_files"])
        actual = actual_case_files(case_dir)

        case_failures = 0

        for filename in sorted(expected - actual):

            failures += 1
            case_failures += 1

            print(
                f"  [FAIL] fail/{case_name}: "
                f"missing file: {filename}"
            )

        for filename in sorted(actual - expected):

            failures += 1
            case_failures += 1

            print(
                f"  [FAIL] fail/{case_name}: "
                f"unregistered file: {filename}"
            )

        if case_failures == 0:

            print(
                f"  [inventory-ok] fail/{case_name}: "
                f"{len(expected)} records"
            )

    print()

    return failures


# ============================================================================
# Case loading
# ============================================================================

def load_case_records(
    case_dir: Path,
) -> dict[
    Path,
    tuple[str, dict[str, Any]],
]:

    records: dict[
        Path,
        tuple[str, dict[str, Any]],
    ] = {}

    for path in sorted(case_dir.rglob("*.json")):

        if not path.is_file():
            continue

        case_relative = path.relative_to(case_dir)

        schema_name = schema_name_for_path(
            case_relative
        )

        record = load_json(path)

        if not isinstance(record, dict):
            raise RuntimeError(
                f"Case record must be a JSON object: "
                f"{relative(path)}"
            )

        records[case_relative] = (
            schema_name,
            record,
        )

    return records


# ============================================================================
# Protocol version validation
# ============================================================================

def version_issues(
    records: dict[
        Path,
        tuple[str, dict[str, Any]],
    ],
) -> list[str]:

    issues: list[str] = []

    for path, (
        _schema_name,
        record,
    ) in records.items():

        schema_version = record.get(
            "schema_version"
        )

        if schema_version != PROTOCOL_VERSION:

            issues.append(
                f"{path.as_posix()}: "
                f"schema_version="
                f"{schema_version!r}; "
                f"expected {PROTOCOL_VERSION!r}"
            )

        if "protocol_version" in record:

            protocol_version = record.get(
                "protocol_version"
            )

            if protocol_version != PROTOCOL_VERSION:

                issues.append(
                    f"{path.as_posix()}: "
                    f"protocol_version="
                    f"{protocol_version!r}; "
                    f"expected {PROTOCOL_VERSION!r}"
                )

    return issues


# ============================================================================
# Schema negative classification
# ============================================================================

def classify_schema_error(
    schema_name: str,
    error: ValidationError,
) -> str:

    path = tuple(error.absolute_path)

    if (
        schema_name == "audit-reconciliation-record"
        and path == ("majority_verdict_applied",)
        and error.validator == "const"
    ):
        return "MAJORITY_VERDICT_SCHEMA_FORBIDDEN"

    if (
        schema_name == "audit-handoff-record"
        and path == ("decision_authority",)
        and error.validator == "const"
    ):
        return "INTERNAL_DECISION_AUTHORITY_SCHEMA_FORBIDDEN"

    return "UNEXPECTED_SCHEMA_VALIDATION_ERROR"


def collect_schema_issues(
    validators: dict[str, Draft202012Validator],
    records: dict[
        Path,
        tuple[str, dict[str, Any]],
    ],
) -> list[SchemaIssue]:

    issues: list[SchemaIssue] = []

    for path, (
        schema_name,
        record,
    ) in records.items():

        validator = validators[schema_name]

        errors = sorted(
            validator.iter_errors(record),
            key=error_sort_key,
        )

        for error in errors:

            issues.append(
                SchemaIssue(
                    code=classify_schema_error(
                        schema_name,
                        error,
                    ),
                    message=(
                        f"{path.as_posix()}: "
                        f"{validation_message(error)}"
                    ),
                )
            )

    return issues


# ============================================================================
# Registry construction
# ============================================================================

def build_registries(
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

    global_ids: dict[str, str] = {}

    errors: list[str] = []

    for path, (
        schema_name,
        record,
    ) in records.items():

        id_field = ID_FIELDS[schema_name]

        record_id = record.get(id_field)

        if not isinstance(record_id, str):

            errors.append(
                f"{path.as_posix()}: "
                f"missing usable {id_field}"
            )

            continue

        if record_id in registries[schema_name]:

            errors.append(
                f"{path.as_posix()}: "
                f"duplicate {schema_name} ID "
                f"{record_id}"
            )

            continue

        if record_id in global_ids:

            errors.append(
                f"{path.as_posix()}: "
                f"global ID collision "
                f"{record_id}; already used by "
                f"{global_ids[record_id]}"
            )

            continue

        registries[
            schema_name
        ][record_id] = record

        global_ids[
            record_id
        ] = schema_name

    return registries, errors


# ============================================================================
# Graph helpers
# ============================================================================

def check_ref(
    reference: str,
    expected_schema: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]],
    ],
    code: str,
    location: str,
    issues: list[GraphIssue],
) -> bool:

    if reference not in registries[
        expected_schema
    ]:

        add_graph_issue(
            issues,
            code,
            (
                f"{location}: unresolved reference "
                f"{reference!r}; expected "
                f"type={expected_schema}"
            ),
        )

        return False

    return True


def check_ref_list(
    references: list[str],
    expected_schema: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]],
    ],
    code: str,
    location: str,
    issues: list[GraphIssue],
) -> None:

    for reference in references:

        check_ref(
            reference,
            expected_schema,
            registries,
            code,
            location,
            issues,
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

        add_graph_issue(
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

        add_graph_issue(
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
# Complete v0.5 Graph validation
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
    # Exactly one Audit Case
    # ------------------------------------------------------------------------

    if len(cases) != 1:

        add_graph_issue(
            issues,
            "CASE_COUNT_INVALID",
            (
                "Case graph must contain exactly "
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
        "auditor-opinion-record",
        "audit-reconciliation-record",
        "audit-handoff-record",
    ]

    for schema_name in member_schemas:

        for record_id, record in (
            registries[schema_name].items()
        ):

            if record.get("case_ref") != case_id:

                add_graph_issue(
                    issues,
                    "CASE_REF_MISMATCH",
                    (
                        f"{record_id}: "
                        f"case_ref does not match "
                        f"{case_id!r}"
                    ),
                )

            if record.get(
                "origin_ref"
            ) != origin_ref:

                add_graph_issue(
                    issues,
                    "ORIGIN_MISMATCH",
                    (
                        f"{record_id}: "
                        f"origin_ref does not match "
                        f"{origin_ref!r}"
                    ),
                )

            if record.get(
                "derivative_ref"
            ) != derivative_ref:

                add_graph_issue(
                    issues,
                    "DERIVATIVE_MISMATCH",
                    (
                        f"{record_id}: "
                        f"derivative_ref does not "
                        f"match {derivative_ref!r}"
                    ),
                )

    # ------------------------------------------------------------------------
    # Case Registry
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

        "opinion_refs":
            "auditor-opinion-record",

        "reconciliation_refs":
            "audit-reconciliation-record",

        "handoff_refs":
            "audit-handoff-record",
    }

    for field_name, schema_name in (
        case_registry_fields.items()
    ):

        declared = set(
            case.get(field_name, [])
        )

        actual = set(
            registries[schema_name]
        )

        missing_from_case = (
            actual - declared
        )

        unresolved_in_case = (
            declared - actual
        )

        if missing_from_case:

            add_graph_issue(
                issues,
                "CASE_REGISTRY_INCOMPLETE",
                (
                    f"{case_id}: "
                    f"{field_name} does not register "
                    f"{sorted(missing_from_case)}"
                ),
            )

        if unresolved_in_case:

            add_graph_issue(
                issues,
                "CASE_REGISTRY_UNRESOLVED",
                (
                    f"{case_id}: "
                    f"{field_name} contains unresolved "
                    f"{sorted(unresolved_in_case)}"
                ),
            )

    # ------------------------------------------------------------------------
    # Current Assessment
    # ------------------------------------------------------------------------

    assessments = registries[
        "derivation-assessment-record"
    ]

    current_assessment_ref = (
        case.get("current_assessment_ref")
    )

    if current_assessment_ref is not None:

        if current_assessment_ref not in assessments:

            add_graph_issue(
                issues,
                "CURRENT_ASSESSMENT_UNRESOLVED",
                (
                    f"{case_id}: "
                    f"current_assessment_ref "
                    f"{current_assessment_ref!r} "
                    "does not resolve"
                ),
            )

        elif current_assessment_ref not in (
            case.get("assessment_refs", [])
        ):

            add_graph_issue(
                issues,
                "CURRENT_ASSESSMENT_UNREGISTERED",
                (
                    f"{case_id}: current assessment "
                    "is not registered in "
                    "assessment_refs"
                ),
            )

    # ------------------------------------------------------------------------
    # Relationships
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
            evidence_refs,
            "audit-evidence-record",
            registries,
            "RELATIONSHIP_EVIDENCE_UNRESOLVED",
            f"{relationship_id}.evidence_refs",
            issues,
        )

        check_subset(
            evidence_refs,
            case.get("evidence_refs", []),
            "RELATIONSHIP_EVIDENCE_OUTSIDE_CASE",
            "evidence_refs",
            "case.evidence_refs",
            relationship_id,
            issues,
        )

    # ------------------------------------------------------------------------
    # Fusion
    # ------------------------------------------------------------------------

    fusions = registries[
        "evidence-fusion-record"
    ]

    for fusion_id, fusion in fusions.items():

        evidence_refs = fusion.get(
            "evidence_refs",
            [],
        )

        relationship_refs = fusion.get(
            "relationship_refs",
            [],
        )

        check_ref_list(
            evidence_refs,
            "audit-evidence-record",
            registries,
            "FUSION_EVIDENCE_UNRESOLVED",
            f"{fusion_id}.evidence_refs",
            issues,
        )

        check_ref_list(
            relationship_refs,
            "evidence-relationship-record",
            registries,
            "FUSION_RELATIONSHIP_UNRESOLVED",
            f"{fusion_id}.relationship_refs",
            issues,
        )

        for subset_name in [
            "supporting_evidence_refs",
            "counter_evidence_refs",
            "redundant_evidence_refs",
            "effective_evidence_refs",
        ]:

            check_subset(
                fusion.get(subset_name, []),
                evidence_refs,
                "FUSION_SUBSET_INVALID",
                subset_name,
                "fusion.evidence_refs",
                fusion_id,
                issues,
            )

        check_disjoint(
            fusion.get(
                "supporting_evidence_refs",
                [],
            ),
            fusion.get(
                "counter_evidence_refs",
                [],
            ),
            "SUPPORT_COUNTER_OVERLAP",
            "supporting_evidence_refs",
            "counter_evidence_refs",
            fusion_id,
            issues,
        )

        check_disjoint(
            fusion.get(
                "redundant_evidence_refs",
                [],
            ),
            fusion.get(
                "effective_evidence_refs",
                [],
            ),
            "REDUNDANT_EFFECTIVE_OVERLAP",
            "redundant_evidence_refs",
            "effective_evidence_refs",
            fusion_id,
            issues,
        )

        # Relationship evidence must be inside Fusion evidence.

        for relationship_ref in relationship_refs:

            relationship = relationships.get(
                relationship_ref
            )

            if relationship is None:
                continue

            check_subset(
                relationship.get(
                    "evidence_refs",
                    [],
                ),
                evidence_refs,
                "FUSION_RELATIONSHIP_EVIDENCE_OUTSIDE_FUSION",
                (
                    f"{relationship_ref}."
                    "evidence_refs"
                ),
                "fusion.evidence_refs",
                fusion_id,
                issues,
            )

    # ------------------------------------------------------------------------
    # Assessments
    # ------------------------------------------------------------------------

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
            evidence_refs,
            "audit-evidence-record",
            registries,
            "ASSESSMENT_EVIDENCE_UNRESOLVED",
            f"{assessment_id}.evidence_refs",
            issues,
        )

        check_ref_list(
            fusion_refs,
            "evidence-fusion-record",
            registries,
            "ASSESSMENT_FUSION_UNRESOLVED",
            f"{assessment_id}.fusion_refs",
            issues,
        )

        check_subset(
            assessment.get(
                "conflicting_evidence_refs",
                [],
            ),
            evidence_refs,
            "ASSESSMENT_CONFLICT_SUBSET_INVALID",
            "conflicting_evidence_refs",
            "assessment.evidence_refs",
            assessment_id,
            issues,
        )

        fused_evidence: set[str] = set()

        for fusion_ref in fusion_refs:

            fusion = fusions.get(fusion_ref)

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

            add_graph_issue(
                issues,
                "ASSESSMENT_EVIDENCE_NOT_FUSED",
                (
                    f"{assessment_id}: "
                    "assessment contains evidence "
                    "outside referenced Fusion(s): "
                    f"{sorted(unfused)}"
                ),
            )

    # ------------------------------------------------------------------------
    # Challenges
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

            add_graph_issue(
                issues,
                "UNRESOLVED_CHALLENGE_TARGET",
                (
                    f"{challenge_id}: "
                    f"{target_type!r} target "
                    f"{target_ref!r} does not resolve"
                ),
            )

        check_ref_list(
            challenge.get(
                "related_evidence_refs",
                [],
            ),
            "audit-evidence-record",
            registries,
            "CHALLENGE_EVIDENCE_UNRESOLVED",
            (
                f"{challenge_id}."
                "related_evidence_refs"
            ),
            issues,
        )

    # ------------------------------------------------------------------------
    # Reproductions
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

            add_graph_issue(
                issues,
                "UNRESOLVED_REPRODUCTION_TARGET",
                (
                    f"{reproduction_id}: "
                    f"{target_type!r} target "
                    f"{target_ref!r} does not resolve"
                ),
            )

        check_ref_list(
            reproduction.get(
                "challenge_refs",
                [],
            ),
            "audit-challenge-record",
            registries,
            "REPRODUCTION_CHALLENGE_UNRESOLVED",
            f"{reproduction_id}.challenge_refs",
            issues,
        )

        produced_refs = reproduction.get(
            "produced_evidence_refs",
            [],
        )

        check_ref_list(
            produced_refs,
            "audit-evidence-record",
            registries,
            "REPRODUCTION_EVIDENCE_UNRESOLVED",
            (
                f"{reproduction_id}."
                "produced_evidence_refs"
            ),
            issues,
        )

        check_subset(
            produced_refs,
            case.get("evidence_refs", []),
            "REPRODUCTION_EVIDENCE_OUTSIDE_CASE",
            "produced_evidence_refs",
            "case.evidence_refs",
            reproduction_id,
            issues,
        )

    # ------------------------------------------------------------------------
    # reproduction_output backlink
    # ------------------------------------------------------------------------

    evidence_registry = registries[
        "audit-evidence-record"
    ]

    for evidence_id, evidence in (
        evidence_registry.items()
    ):

        if evidence.get(
            "evidence_type"
        ) != "reproduction_output":
            continue

        reproduction_ref = evidence.get(
            "observation",
            {},
        ).get(
            "reproduction_ref"
        )

        if (
            not isinstance(reproduction_ref, str)
            or reproduction_ref not in reproductions
        ):

            add_graph_issue(
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

        if evidence_id not in reproductions[
            reproduction_ref
        ].get(
            "produced_evidence_refs",
            [],
        ):

            add_graph_issue(
                issues,
                "REPRODUCTION_BACKLINK_MISSING",
                (
                    f"{evidence_id}: "
                    f"{reproduction_ref} does not "
                    "register this evidence"
                ),
            )

    # ------------------------------------------------------------------------
    # Revisions
    # ------------------------------------------------------------------------

    revisions = registries[
        "assessment-revision-record"
    ]

    opinions = registries[
        "auditor-opinion-record"
    ]

    reconciliations = registries[
        "audit-reconciliation-record"
    ]

    revision_trigger_schema = {
        "challenge":
            "audit-challenge-record",

        "reproduction":
            "reproduction-record",

        "new_evidence":
            "audit-evidence-record",

        "new_fusion":
            "evidence-fusion-record",

        "auditor_opinion":
            "auditor-opinion-record",

        "reconciliation":
            "audit-reconciliation-record",
    }

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

            add_graph_issue(
                issues,
                "REVISION_PRIOR_UNRESOLVED",
                (
                    f"{revision_id}: "
                    f"prior_assessment_ref "
                    f"{prior!r} does not resolve"
                ),
            )

        if not revised_resolved:

            add_graph_issue(
                issues,
                "REVISION_REVISED_UNRESOLVED",
                (
                    f"{revision_id}: "
                    f"revised_assessment_ref "
                    f"{revised!r} does not resolve"
                ),
            )

        if (
            prior_resolved
            and revised_resolved
            and prior == revised
        ):

            add_graph_issue(
                issues,
                "REVISION_SELF_LOOP",
                (
                    f"{revision_id}: prior and "
                    "revised assessments are identical"
                ),
            )

        check_ref_list(
            revision.get(
                "challenge_refs",
                [],
            ),
            "audit-challenge-record",
            registries,
            "REVISION_CHALLENGE_UNRESOLVED",
            f"{revision_id}.challenge_refs",
            issues,
        )

        check_ref_list(
            revision.get(
                "reproduction_refs",
                [],
            ),
            "reproduction-record",
            registries,
            "REVISION_REPRODUCTION_UNRESOLVED",
            f"{revision_id}.reproduction_refs",
            issues,
        )

        check_ref_list(
            revision.get(
                "evidence_added_refs",
                [],
            ),
            "audit-evidence-record",
            registries,
            "REVISION_ADDED_EVIDENCE_UNRESOLVED",
            f"{revision_id}.evidence_added_refs",
            issues,
        )

        check_ref_list(
            revision.get(
                "evidence_removed_refs",
                [],
            ),
            "audit-evidence-record",
            registries,
            "REVISION_REMOVED_EVIDENCE_UNRESOLVED",
            f"{revision_id}.evidence_removed_refs",
            issues,
        )

        check_ref_list(
            revision.get(
                "fusion_refs",
                [],
            ),
            "evidence-fusion-record",
            registries,
            "REVISION_FUSION_UNRESOLVED",
            f"{revision_id}.fusion_refs",
            issues,
        )

        check_disjoint(
            revision.get(
                "evidence_added_refs",
                [],
            ),
            revision.get(
                "evidence_removed_refs",
                [],
            ),
            "REVISION_EVIDENCE_ADD_REMOVE_OVERLAP",
            "evidence_added_refs",
            "evidence_removed_refs",
            revision_id,
            issues,
        )

        trigger_type = revision.get(
            "revision_trigger"
        )

        if trigger_type in revision_trigger_schema:

            check_ref_list(
                revision.get(
                    "trigger_refs",
                    [],
                ),
                revision_trigger_schema[
                    trigger_type
                ],
                registries,
                "REVISION_TRIGGER_UNRESOLVED",
                f"{revision_id}.trigger_refs",
                issues,
            )

        # Revised Assessment coherence.

        if revised_resolved:

            revised_assessment = assessments[
                revised
            ]

            check_subset(
                revision.get(
                    "evidence_added_refs",
                    [],
                ),
                revised_assessment.get(
                    "evidence_refs",
                    [],
                ),
                "REVISION_ADDED_EVIDENCE_NOT_IN_REVISED_ASSESSMENT",
                "evidence_added_refs",
                (
                    f"{revised}."
                    "evidence_refs"
                ),
                revision_id,
                issues,
            )

            check_subset(
                revision.get(
                    "fusion_refs",
                    [],
                ),
                revised_assessment.get(
                    "fusion_refs",
                    [],
                ),
                "REVISION_FUSION_NOT_IN_REVISED_ASSESSMENT",
                "fusion_refs",
                (
                    f"{revised}."
                    "fusion_refs"
                ),
                revision_id,
                issues,
            )

        if (
            revision.get(
                "revision_state"
            ) == "applied"
            and prior_resolved
            and revised_resolved
        ):

            if prior in applied_edges:

                add_graph_issue(
                    issues,
                    "REVISION_MULTIPLE_APPLIED_SUCCESSORS",
                    (
                        f"{prior!r} has multiple "
                        "applied successors"
                    ),
                )

            else:

                applied_edges[
                    prior
                ] = revised

    # Revision cycle.

    cycle_detected = False

    for start in applied_edges:

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

        add_graph_issue(
            issues,
            "REVISION_CYCLE",
            (
                "applied assessment revision "
                "chain contains a cycle"
            ),
        )

    # Current Assessment must be terminal.

    if applied_edges:

        prior_nodes = set(
            applied_edges.keys()
        )

        revised_nodes = set(
            applied_edges.values()
        )

        terminal_nodes = (
            revised_nodes - prior_nodes
        )

        if (
            current_assessment_ref
            not in terminal_nodes
        ):

            add_graph_issue(
                issues,
                "CURRENT_ASSESSMENT_NOT_TERMINAL",
                (
                    f"{case_id}: "
                    f"current_assessment_ref "
                    f"{current_assessment_ref!r} "
                    "is not a terminal applied "
                    "revision assessment; "
                    f"terminal="
                    f"{sorted(terminal_nodes)}"
                ),
            )

    # ========================================================================
    # v0.5 — Auditor Opinions
    # ========================================================================

    for opinion_id, opinion in (
        opinions.items()
    ):

        assessment_ref = opinion.get(
            "assessment_ref"
        )

        if assessment_ref not in assessments:

            add_graph_issue(
                issues,
                "OPINION_ASSESSMENT_UNRESOLVED",
                (
                    f"{opinion_id}: "
                    f"assessment_ref "
                    f"{assessment_ref!r} "
                    "does not resolve"
                ),
            )

            continue

        assessment = assessments[
            assessment_ref
        ]

        opinion_evidence = opinion.get(
            "evidence_refs",
            [],
        )

        opinion_fusions = opinion.get(
            "fusion_refs",
            [],
        )

        check_ref_list(
            opinion_evidence,
            "audit-evidence-record",
            registries,
            "OPINION_EVIDENCE_UNRESOLVED",
            f"{opinion_id}.evidence_refs",
            issues,
        )

        check_subset(
            opinion_evidence,
            assessment.get(
                "evidence_refs",
                [],
            ),
            "OPINION_EVIDENCE_OUTSIDE_ASSESSMENT",
            "evidence_refs",
            (
                f"{assessment_ref}."
                "evidence_refs"
            ),
            opinion_id,
            issues,
        )

        check_ref_list(
            opinion_fusions,
            "evidence-fusion-record",
            registries,
            "OPINION_FUSION_UNRESOLVED",
            f"{opinion_id}.fusion_refs",
            issues,
        )

        check_subset(
            opinion_fusions,
            assessment.get(
                "fusion_refs",
                [],
            ),
            "OPINION_FUSION_OUTSIDE_ASSESSMENT",
            "fusion_refs",
            (
                f"{assessment_ref}."
                "fusion_refs"
            ),
            opinion_id,
            issues,
        )

        check_ref_list(
            opinion.get(
                "challenge_refs",
                [],
            ),
            "audit-challenge-record",
            registries,
            "OPINION_CHALLENGE_UNRESOLVED",
            f"{opinion_id}.challenge_refs",
            issues,
        )

        check_ref_list(
            opinion.get(
                "reproduction_refs",
                [],
            ),
            "reproduction-record",
            registries,
            "OPINION_REPRODUCTION_UNRESOLVED",
            f"{opinion_id}.reproduction_refs",
            issues,
        )

        if not opinion.get("auditor_ref"):

            add_graph_issue(
                issues,
                "OPINION_AUDITOR_MISSING",
                (
                    f"{opinion_id}: "
                    "auditor identity is missing"
                ),
            )

        if (
            opinion.get(
                "independence_status"
            ) == "independent"
            and opinion.get(
                "dependency_refs",
                [],
            )
        ):

            add_graph_issue(
                issues,
                "OPINION_INDEPENDENCE_CONFLICT",
                (
                    f"{opinion_id}: "
                    "independence_status is "
                    "independent but dependency_refs "
                    "is non-empty"
                ),
            )

        if opinion.get(
            "effect_scope"
        ) != "audit_only":

            add_graph_issue(
                issues,
                "OPINION_EFFECT_SCOPE_INVALID",
                (
                    f"{opinion_id}: "
                    "effect_scope must remain "
                    "audit_only"
                ),
            )

    # ========================================================================
    # v0.5 — Reconciliation
    # ========================================================================

    unresolved_point_registry: dict[
        str,
        str,
    ] = {}

    for reconciliation_id, reconciliation in (
        reconciliations.items()
    ):

        assessment_refs = reconciliation.get(
            "assessment_refs",
            [],
        )

        opinion_refs = reconciliation.get(
            "opinion_refs",
            [],
        )

        evidence_refs = reconciliation.get(
            "evidence_refs",
            [],
        )

        fusion_refs = reconciliation.get(
            "fusion_refs",
            [],
        )

        check_ref_list(
            assessment_refs,
            "derivation-assessment-record",
            registries,
            "RECONCILIATION_ASSESSMENT_UNRESOLVED",
            (
                f"{reconciliation_id}."
                "assessment_refs"
            ),
            issues,
        )

        check_ref_list(
            opinion_refs,
            "auditor-opinion-record",
            registries,
            "RECONCILIATION_OPINION_UNRESOLVED",
            (
                f"{reconciliation_id}."
                "opinion_refs"
            ),
            issues,
        )

        check_ref_list(
            evidence_refs,
            "audit-evidence-record",
            registries,
            "RECONCILIATION_EVIDENCE_UNRESOLVED",
            (
                f"{reconciliation_id}."
                "evidence_refs"
            ),
            issues,
        )

        check_ref_list(
            fusion_refs,
            "evidence-fusion-record",
            registries,
            "RECONCILIATION_FUSION_UNRESOLVED",
            (
                f"{reconciliation_id}."
                "fusion_refs"
            ),
            issues,
        )

        check_ref_list(
            reconciliation.get(
                "challenge_refs",
                [],
            ),
            "audit-challenge-record",
            registries,
            "RECONCILIATION_CHALLENGE_UNRESOLVED",
            (
                f"{reconciliation_id}."
                "challenge_refs"
            ),
            issues,
        )

        check_ref_list(
            reconciliation.get(
                "reproduction_refs",
                [],
            ),
            "reproduction-record",
            registries,
            "RECONCILIATION_REPRODUCTION_UNRESOLVED",
            (
                f"{reconciliation_id}."
                "reproduction_refs"
            ),
            issues,
        )

        # ------------------------------------------------------------
        # Opinion → Assessment coherence
        # ------------------------------------------------------------

        auditor_refs: set[str] = set()

        for opinion_ref in opinion_refs:

            opinion = opinions.get(
                opinion_ref
            )

            if opinion is None:
                continue

            opinion_assessment = opinion.get(
                "assessment_ref"
            )

            if opinion_assessment not in assessment_refs:

                add_graph_issue(
                    issues,
                    "RECONCILIATION_OPINION_ASSESSMENT_MISMATCH",
                    (
                        f"{reconciliation_id}: "
                        f"{opinion_ref} concerns "
                        f"{opinion_assessment!r}, "
                        "which is absent from "
                        "reconciliation assessment_refs"
                    ),
                )

            auditor_ref = opinion.get(
                "auditor_ref"
            )

            if isinstance(auditor_ref, str):

                auditor_refs.add(
                    auditor_ref
                )

        # Multiple Opinion records do not imply multiple auditors.

        if len(auditor_refs) < 2:

            add_graph_issue(
                issues,
                "RECONCILIATION_AUDITOR_DIVERSITY_INSUFFICIENT",
                (
                    f"{reconciliation_id}: "
                    "fewer than two distinct "
                    "auditor_ref values are represented"
                ),
            )

        # Defense in depth:
        # Schema already fixes this to false.

        if reconciliation.get(
            "majority_verdict_applied"
        ) is not False:

            add_graph_issue(
                issues,
                "MAJORITY_VERDICT_FORBIDDEN",
                (
                    f"{reconciliation_id}: "
                    "majority_verdict_applied "
                    "must remain false"
                ),
            )

        if reconciliation.get(
            "effect_scope"
        ) != "audit_only":

            add_graph_issue(
                issues,
                "RECONCILIATION_EFFECT_SCOPE_INVALID",
                (
                    f"{reconciliation_id}: "
                    "effect_scope must remain "
                    "audit_only"
                ),
            )

        # ------------------------------------------------------------
        # Reconciliation point integrity
        # ------------------------------------------------------------

        point_ids: set[str] = set()

        def register_point(
            point_id: Any,
            point_type: str,
        ) -> None:

            if not isinstance(point_id, str):
                return

            if point_id in point_ids:

                add_graph_issue(
                    issues,
                    "RECONCILIATION_POINT_ID_DUPLICATE",
                    (
                        f"{reconciliation_id}: "
                        f"duplicate point_id "
                        f"{point_id!r}"
                    ),
                )

            else:

                point_ids.add(
                    point_id
                )

            if point_type == "unresolved":

                if (
                    point_id
                    in unresolved_point_registry
                ):

                    add_graph_issue(
                        issues,
                        "UNRESOLVED_POINT_ID_COLLISION",
                        (
                            f"{point_id!r} appears "
                            "in multiple reconciliation "
                            "records"
                        ),
                    )

                else:

                    unresolved_point_registry[
                        point_id
                    ] = reconciliation_id

        # Agreement points.

        for point in reconciliation.get(
            "agreed_points",
            [],
        ):

            register_point(
                point.get("point_id"),
                "agreed",
            )

            check_subset(
                point.get(
                    "supporting_opinion_refs",
                    [],
                ),
                opinion_refs,
                "AGREEMENT_OPINION_OUTSIDE_RECONCILIATION",
                "supporting_opinion_refs",
                "reconciliation.opinion_refs",
                reconciliation_id,
                issues,
            )

            check_subset(
                point.get(
                    "evidence_refs",
                    [],
                ),
                evidence_refs,
                "AGREEMENT_EVIDENCE_OUTSIDE_RECONCILIATION",
                "evidence_refs",
                "reconciliation.evidence_refs",
                reconciliation_id,
                issues,
            )

            check_subset(
                point.get(
                    "assessment_refs",
                    [],
                ),
                assessment_refs,
                "AGREEMENT_ASSESSMENT_OUTSIDE_RECONCILIATION",
                "assessment_refs",
                "reconciliation.assessment_refs",
                reconciliation_id,
                issues,
            )

        # Disputed points.

        for point in reconciliation.get(
            "disputed_points",
            [],
        ):

            register_point(
                point.get("point_id"),
                "disputed",
            )

            position_labels: set[str] = set()

            for position in point.get(
                "positions",
                [],
            ):

                label = position.get(
                    "position"
                )

                if isinstance(label, str):

                    if label in position_labels:

                        add_graph_issue(
                            issues,
                            "DISPUTE_POSITION_DUPLICATE",
                            (
                                f"{reconciliation_id}: "
                                "duplicate dispute "
                                f"position {label!r}"
                            ),
                        )

                    else:

                        position_labels.add(
                            label
                        )

                check_subset(
                    position.get(
                        "opinion_refs",
                        [],
                    ),
                    opinion_refs,
                    "DISPUTE_OPINION_OUTSIDE_RECONCILIATION",
                    "position.opinion_refs",
                    "reconciliation.opinion_refs",
                    reconciliation_id,
                    issues,
                )

            check_subset(
                point.get(
                    "evidence_refs",
                    [],
                ),
                evidence_refs,
                "DISPUTE_EVIDENCE_OUTSIDE_RECONCILIATION",
                "evidence_refs",
                "reconciliation.evidence_refs",
                reconciliation_id,
                issues,
            )

            check_subset(
                point.get(
                    "assessment_refs",
                    [],
                ),
                assessment_refs,
                "DISPUTE_ASSESSMENT_OUTSIDE_RECONCILIATION",
                "assessment_refs",
                "reconciliation.assessment_refs",
                reconciliation_id,
                issues,
            )

        # Unresolved points.

        for point in reconciliation.get(
            "unresolved_points",
            [],
        ):

            register_point(
                point.get("point_id"),
                "unresolved",
            )

            check_subset(
                point.get(
                    "opinion_refs",
                    [],
                ),
                opinion_refs,
                "UNRESOLVED_OPINION_OUTSIDE_RECONCILIATION",
                "opinion_refs",
                "reconciliation.opinion_refs",
                reconciliation_id,
                issues,
            )

            check_subset(
                point.get(
                    "evidence_refs",
                    [],
                ),
                evidence_refs,
                "UNRESOLVED_EVIDENCE_OUTSIDE_RECONCILIATION",
                "evidence_refs",
                "reconciliation.evidence_refs",
                reconciliation_id,
                issues,
            )

            check_subset(
                point.get(
                    "assessment_refs",
                    [],
                ),
                assessment_refs,
                "UNRESOLVED_ASSESSMENT_OUTSIDE_RECONCILIATION",
                "assessment_refs",
                "reconciliation.assessment_refs",
                reconciliation_id,
                issues,
            )

    # ========================================================================
    # v0.5 — Handoff
    # ========================================================================

    handoffs = registries[
        "audit-handoff-record"
    ]

    all_protocol_ids: set[str] = set()

    for registry in registries.values():

        all_protocol_ids.update(
            registry.keys()
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
        "OPINION-",
        "RECONCILIATION-",
        "HANDOFF-",
    )

    for handoff_id, handoff in (
        handoffs.items()
    ):

        handoff_assessments = handoff.get(
            "assessment_refs",
            [],
        )

        handoff_opinions = handoff.get(
            "opinion_refs",
            [],
        )

        handoff_reconciliations = handoff.get(
            "reconciliation_refs",
            [],
        )

        handoff_challenges = handoff.get(
            "challenge_refs",
            [],
        )

        handoff_reproductions = handoff.get(
            "reproduction_refs",
            [],
        )

        handoff_revisions = handoff.get(
            "revision_refs",
            [],
        )

        check_ref_list(
            handoff_assessments,
            "derivation-assessment-record",
            registries,
            "HANDOFF_ASSESSMENT_UNRESOLVED",
            f"{handoff_id}.assessment_refs",
            issues,
        )

        check_ref_list(
            handoff_opinions,
            "auditor-opinion-record",
            registries,
            "HANDOFF_OPINION_UNRESOLVED",
            f"{handoff_id}.opinion_refs",
            issues,
        )

        check_ref_list(
            handoff_reconciliations,
            "audit-reconciliation-record",
            registries,
            "HANDOFF_RECONCILIATION_UNRESOLVED",
            f"{handoff_id}.reconciliation_refs",
            issues,
        )

        check_ref_list(
            handoff_challenges,
            "audit-challenge-record",
            registries,
            "HANDOFF_CHALLENGE_UNRESOLVED",
            f"{handoff_id}.challenge_refs",
            issues,
        )

        check_ref_list(
            handoff_reproductions,
            "reproduction-record",
            registries,
            "HANDOFF_REPRODUCTION_UNRESOLVED",
            f"{handoff_id}.reproduction_refs",
            issues,
        )

        check_ref_list(
            handoff_revisions,
            "assessment-revision-record",
            registries,
            "HANDOFF_REVISION_UNRESOLVED",
            f"{handoff_id}.revision_refs",
            issues,
        )

        # ------------------------------------------------------------
        # Handoff payload resolution
        # ------------------------------------------------------------

        payload_refs = handoff.get(
            "payload_refs",
            [],
        )

        for payload_ref in payload_refs:

            if (
                payload_ref.startswith(
                    meda_prefixes
                )
                and payload_ref
                not in all_protocol_ids
            ):

                add_graph_issue(
                    issues,
                    "HANDOFF_PAYLOAD_UNRESOLVED",
                    (
                        f"{handoff_id}: "
                        "payload_refs contains "
                        "unresolved MEDA record "
                        f"{payload_ref!r}"
                    ),
                )

        # Every explicitly linked audit record must
        # actually appear in the transferred payload.

        required_payload_refs = (
            set(handoff_assessments)
            | set(handoff_opinions)
            | set(handoff_reconciliations)
            | set(handoff_challenges)
            | set(handoff_reproductions)
            | set(handoff_revisions)
        )

        missing_payload = (
            required_payload_refs
            - set(payload_refs)
        )

        if missing_payload:

            add_graph_issue(
                issues,
                "HANDOFF_PAYLOAD_INCOMPLETE",
                (
                    f"{handoff_id}: "
                    "linked audit records are absent "
                    "from payload_refs: "
                    f"{sorted(missing_payload)}"
                ),
            )

        # ------------------------------------------------------------
        # Unresolved-point references
        # ------------------------------------------------------------

        referenced_reconciliation_set = set(
            handoff_reconciliations
        )

        for point_ref in handoff.get(
            "unresolved_point_refs",
            [],
        ):

            reconciliation_ref = (
                unresolved_point_registry.get(
                    point_ref
                )
            )

            if reconciliation_ref is None:

                add_graph_issue(
                    issues,
                    "HANDOFF_UNRESOLVED_POINT_UNKNOWN",
                    (
                        f"{handoff_id}: "
                        f"unresolved point "
                        f"{point_ref!r} does not exist"
                    ),
                )

            elif reconciliation_ref not in (
                referenced_reconciliation_set
            ):

                add_graph_issue(
                    issues,
                    "HANDOFF_UNRESOLVED_POINT_OUTSIDE_RECONCILIATION",
                    (
                        f"{handoff_id}: "
                        f"{point_ref!r} belongs to "
                        f"{reconciliation_ref}, "
                        "which is not referenced "
                        "by this handoff"
                    ),
                )

        # ------------------------------------------------------------
        # MEDA authority boundary
        # ------------------------------------------------------------

        if handoff.get(
            "decision_authority"
        ) != "external":

            add_graph_issue(
                issues,
                "HANDOFF_AUTHORITY_BOUNDARY_VIOLATION",
                (
                    f"{handoff_id}: "
                    "decision_authority must "
                    "remain external"
                ),
            )

        if handoff.get(
            "handoff_effect"
        ) != "transfer_only":

            add_graph_issue(
                issues,
                "HANDOFF_EFFECT_BOUNDARY_VIOLATION",
                (
                    f"{handoff_id}: "
                    "handoff_effect must remain "
                    "transfer_only"
                ),
            )

        if handoff.get(
            "legal_effect"
        ) != "none":

            add_graph_issue(
                issues,
                "HANDOFF_LEGAL_EFFECT_VIOLATION",
                (
                    f"{handoff_id}: "
                    "MEDA handoff cannot create "
                    "legal effect"
                ),
            )

    # ------------------------------------------------------------------------
    # Case state = handed_off requires actual transfer
    # ------------------------------------------------------------------------

    if case.get(
        "case_state"
    ) == "handed_off":

        transferred = [
            handoff
            for handoff in handoffs.values()
            if handoff.get(
                "handoff_status"
            ) in {
                "transmitted",
                "accepted",
            }
        ]

        if not transferred:

            add_graph_issue(
                issues,
                "CASE_HANDED_OFF_WITHOUT_TRANSFER",
                (
                    f"{case_id}: "
                    "case_state is handed_off but "
                    "no handoff is transmitted "
                    "or accepted"
                ),
            )

    # ========================================================================
    # ZK Attestations
    # ========================================================================

    attestations = registries[
        "zk-audit-attestation"
    ]

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

                add_graph_issue(
                    issues,
                    "ATTESTATION_CONTEXT_UNRESOLVED",
                    (
                        f"{attestation_id}: "
                        f"context {context_type!r} "
                        f"{context_ref!r} "
                        "does not resolve"
                    ),
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

                add_graph_issue(
                    issues,
                    "ATTESTATION_COMMITMENT_UNRESOLVED",
                    (
                        f"{attestation_id}: "
                        "unresolved MEDA committed "
                        f"input {committed_ref!r}"
                    ),
                )

    return issues


# ============================================================================
# PASS cases
# ============================================================================

def validate_pass_cases(
    validators: dict[str, Draft202012Validator],
) -> int:

    failures = 0

    print("[pass graph cases]")

    for case_name in PASS_CASES:

        print(f"  case: {case_name}")

        case_dir = PASS_ROOT / case_name

        records = load_case_records(
            case_dir
        )

        versions = version_issues(
            records
        )

        if versions:

            failures += len(versions)

            for issue in versions:
                print(
                    f"    [FAIL] version: {issue}"
                )

            continue

        schema_issues = collect_schema_issues(
            validators,
            records,
        )

        if schema_issues:

            failures += len(schema_issues)

            for issue in schema_issues:

                print(
                    f"    [FAIL] schema "
                    f"{issue.code}: "
                    f"{issue.message}"
                )

            continue

        print(
            f"    [schema-ok] "
            f"{len(records)} records"
        )

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

        print(
            "    [graph-ok] all structural "
            "references resolve"
        )

        print(
            "    [history-ok] Assessment-0001 "
            "→ Challenge → Reproduction → "
            "New Evidence → Re-Fusion → "
            "Assessment-0002 → Revision"
        )

        print(
            "    [multi-auditor-ok] "
            "independent auditor identities "
            "remain explicit"
        )

        print(
            "    [reconciliation-ok] "
            "agreement, disagreement, and "
            "unresolved points are preserved "
            "without majority verdict"
        )

        print(
            "    [handoff-ok] MEDA transfers "
            "audit context while external "
            "authority retains decision power"
        )

    print()

    return failures


# ============================================================================
# EXPECTED-FAIL cases
# ============================================================================

def validate_expected_fail_cases(
    validators: dict[str, Draft202012Validator],
) -> int:

    failures = 0

    print("[expected-fail cases]")

    for case_name, config in FAIL_CASES.items():

        print(f"  case: {case_name}")

        failure_stage = config[
            "failure_stage"
        ]

        expected_codes = set(
            config["expected_codes"]
        )

        print(
            "    expected stage: "
            f"{failure_stage}"
        )

        print(
            "    expected issue code(s): "
            + ", ".join(
                sorted(expected_codes)
            )
        )

        case_dir = FAIL_ROOT / case_name

        records = load_case_records(
            case_dir
        )

        versions = version_issues(
            records
        )

        if versions:

            failures += len(versions)

            for issue in versions:

                print(
                    f"    [FAIL] version: {issue}"
                )

            continue

        schema_issues = collect_schema_issues(
            validators,
            records,
        )

        # --------------------------------------------------------------------
        # Expected Schema Failure
        # --------------------------------------------------------------------

        if failure_stage == "schema":

            actual_codes = {
                issue.code
                for issue in schema_issues
            }

            missing = (
                expected_codes - actual_codes
            )

            unexpected = (
                actual_codes - expected_codes
            )

            if missing:

                failures += len(missing)

                print(
                    "    [FAIL] expected schema "
                    "issue code(s) not produced:"
                )

                for code in sorted(missing):

                    print(
                        f"      - {code}"
                    )

            if unexpected:

                failures += len(unexpected)

                print(
                    "    [FAIL] unexpected schema "
                    "issue code(s) produced:"
                )

                for code in sorted(unexpected):

                    print(
                        f"      - {code}"
                    )

            if not schema_issues:

                failures += 1

                print(
                    "    [FAIL] case unexpectedly "
                    "passed Schema validation"
                )

            elif not missing and not unexpected:

                print(
                    "    [expected-schema-fail]"
                )

                for issue in schema_issues:

                    print(
                        f"      - {issue.code}: "
                        f"{issue.message}"
                    )

            continue

        # --------------------------------------------------------------------
        # Expected Graph Failure
        # --------------------------------------------------------------------

        if failure_stage != "graph":

            failures += 1

            print(
                f"    [FAIL] unknown "
                f"failure_stage={failure_stage!r}"
            )

            continue

        # Graph-negative fixtures MUST remain Schema-valid.

        if schema_issues:

            failures += len(schema_issues)

            print(
                "    [FAIL] graph-negative case "
                "must be Schema-valid"
            )

            for issue in schema_issues:

                print(
                    f"      - {issue.code}: "
                    f"{issue.message}"
                )

            continue

        print("    [schema-ok]")

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

        graph_issues = validate_audit_graph(
            registries
        )

        actual_codes = {
            issue.code
            for issue in graph_issues
        }

        missing = (
            expected_codes - actual_codes
        )

        unexpected = (
            actual_codes - expected_codes
        )

        if missing:

            failures += len(missing)

            print(
                "    [FAIL] expected graph "
                "issue code(s) not produced:"
            )

            for code in sorted(missing):

                print(
                    f"      - {code}"
                )

        if unexpected:

            failures += len(unexpected)

            print(
                "    [FAIL] unexpected graph "
                "issue code(s) produced:"
            )

            for code in sorted(unexpected):

                print(
                    f"      - {code}"
                )

        if not graph_issues:

            failures += 1

            print(
                "    [FAIL] case unexpectedly "
                "passed Graph validation"
            )

        elif not missing and not unexpected:

            print(
                "    [expected-graph-fail]"
            )

            for issue in graph_issues:

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
        "v0.5 Validation ==="
    )

    print()

    try:

        validators = load_validators()

        failures = 0

        failures += verify_schema_inventory()

        failures += (
            verify_case_root_inventory()
        )

        failures += (
            verify_case_file_inventory()
        )

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
            "All 12 schemas are valid."
        )

        print(
            "The 21-record MEDA v0.5 Reference "
            "Case passed Schema, Graph, history, "
            "multi-auditor, reconciliation, and "
            "handoff-boundary validation."
        )

        print(
            "All 6 EXPECTED-FAIL cases were "
            "rejected exactly as intended:"
        )

        print(
            "  - 4 Schema-valid / Graph-invalid "
            "cross-record cases"
        )

        print(
            "  - 2 Schema-invalid hard-boundary "
            "cases"
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
