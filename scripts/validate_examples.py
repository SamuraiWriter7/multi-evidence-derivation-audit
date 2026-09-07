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

REFERENCE_CASE_DIR = (
    ROOT
    / "examples"
    / "cases"
    / "pass"
    / "reference-case"
)


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
# Reference Case inventory
# ============================================================================

REFERENCE_CASE_FILES = {
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
# Determine schema from relative path
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
# Load schemas
# ============================================================================

def load_validators() -> dict[str, Draft202012Validator]:

    validators: dict[str, Draft202012Validator] = {}

    print("[schemas]")

    for schema_name, schema_path in SCHEMA_FILES.items():

        schema = load_json(schema_path)

        try:
            Draft202012Validator.check_schema(
                schema
            )

        except SchemaError as exc:
            raise RuntimeError(
                f"Invalid schema "
                f"{relative(schema_path)}: "
                f"{exc.message}"
            ) from exc

        validators[schema_name] = (
            Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            )
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
        for path in SCHEMAS_DIR.glob(
            "*.schema.json"
        )
        if path.is_file()
    }

    print("[schema inventory]")

    for filename in sorted(
        expected - actual
    ):
        failures += 1

        print(
            f"  [FAIL] missing schema: "
            f"{filename}"
        )

    for filename in sorted(
        actual - expected
    ):
        failures += 1

        print(
            f"  [FAIL] unregistered schema: "
            f"{filename}"
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

    actual = {
        path.relative_to(
            REFERENCE_CASE_DIR
        ).as_posix()
        for path in REFERENCE_CASE_DIR.rglob(
            "*.json"
        )
        if path.is_file()
    }

    print("[reference case inventory]")

    for filename in sorted(
        REFERENCE_CASE_FILES - actual
    ):
        failures += 1

        print(
            f"  [FAIL] missing record: "
            f"{filename}"
        )

    for filename in sorted(
        actual - REFERENCE_CASE_FILES
    ):
        failures += 1

        print(
            f"  [FAIL] unregistered record: "
            f"{filename}"
        )

    if failures == 0:
        print(
            f"  [inventory-ok] "
            f"{len(REFERENCE_CASE_FILES)} "
            "Reference Case records registered"
        )

    print()

    return failures


# ============================================================================
# Load Reference Case
# ============================================================================

def load_reference_case_records(
) -> dict[
    Path,
    tuple[str, dict[str, Any]]
]:

    records: dict[
        Path,
        tuple[str, dict[str, Any]]
    ] = {}

    for path in sorted(
        REFERENCE_CASE_DIR.rglob("*.json")
    ):

        if not path.is_file():
            continue

        case_relative = path.relative_to(
            REFERENCE_CASE_DIR
        )

        schema_name = schema_name_for_path(
            case_relative
        )

        record = load_json(path)

        if not isinstance(record, dict):
            raise RuntimeError(
                "Reference Case records must be "
                f"JSON objects: {relative(path)}"
            )

        records[case_relative] = (
            schema_name,
            record,
        )

    return records


# ============================================================================
# Version checks
# ============================================================================

def verify_protocol_versions(
    records: dict[
        Path,
        tuple[str, dict[str, Any]]
    ],
) -> int:

    failures = 0

    print("[protocol version preflight]")

    for path, (
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
                f"{path.as_posix()}: "
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

                failures += 1

                print(
                    f"  [FAIL] "
                    f"{path.as_posix()}: "
                    f"protocol_version="
                    f"{protocol_version!r}; "
                    f"expected "
                    f"{PROTOCOL_VERSION!r}"
                )

    if failures == 0:

        print(
            "  [version-ok] all Reference Case "
            "records declare MEDA v0.5.0"
        )

    print()

    return failures


# ============================================================================
# Schema validation
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

    for path, (
        schema_name,
        record,
    ) in records.items():

        validator = validators[
            schema_name
        ]

        errors = sorted(
            validator.iter_errors(record),
            key=error_sort_key,
        )

        if errors:

            failures += 1

            print(
                f"  [FAIL] "
                f"{path.as_posix()}"
            )

            for error in errors:

                print(
                    f"    - "
                    f"{validation_message(error)}"
                )

        else:

            print(
                f"  [schema-ok] "
                f"{path.as_posix()}"
            )

    print()

    return failures


# ============================================================================
# Record Registry
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

    global_ids: dict[str, str] = {}

    errors: list[str] = []

    for path, (
        schema_name,
        record,
    ) in records.items():

        id_field = ID_FIELDS[
            schema_name
        ]

        record_id = record.get(
            id_field
        )

        if not isinstance(record_id, str):

            errors.append(
                f"{path.as_posix()}: "
                f"missing usable {id_field}"
            )

            continue

        if record_id in registries[
            schema_name
        ]:

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
        dict[str, dict[str, Any]]
    ],
    code: str,
    location: str,
    issues: list[GraphIssue],
) -> bool:

    if reference not in registries[
        expected_schema
    ]:

        add_issue(
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
# Complete v0.5 Audit Graph validation
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
                "Reference Case must contain "
                f"exactly one Audit Case; "
                f"found {len(cases)}"
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
        "auditor-opinion-record",
        "audit-reconciliation-record",
        "audit-handoff-record",
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
                        "case_ref does not match "
                        f"{case_id!r}"
                    ),
                )

            if record.get(
                "origin_ref"
            ) != origin_ref:

                add_issue(
                    issues,
                    "ORIGIN_MISMATCH",
                    (
                        f"{record_id}: "
                        "origin_ref does not match "
                        f"{origin_ref!r}"
                    ),
                )

            if record.get(
                "derivative_ref"
            ) != derivative_ref:

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
            registries[schema_name].keys()
        )

        missing_from_case = (
            actual - declared
        )

        unresolved_in_case = (
            declared - actual
        )

        if missing_from_case:

            add_issue(
                issues,
                "CASE_REGISTRY_INCOMPLETE",
                (
                    f"{case_id}: "
                    f"{field_name} does not register "
                    f"{sorted(missing_from_case)}"
                ),
            )

        if unresolved_in_case:

            add_issue(
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

            add_issue(
                issues,
                "CURRENT_ASSESSMENT_UNRESOLVED",
                (
                    f"{case_id}: "
                    f"{current_assessment_ref!r} "
                    "does not resolve"
                ),
            )

        elif current_assessment_ref not in case.get(
            "assessment_refs",
            [],
        ):

            add_issue(
                issues,
                "CURRENT_ASSESSMENT_UNREGISTERED",
                (
                    f"{case_id}: "
                    "current assessment is not "
                    "registered in assessment_refs"
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
                fusion.get(
                    subset_name,
                    [],
                ),
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
                    "outside its referenced Fusion(s): "
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

            add_issue(
                issues,
                "UNRESOLVED_CHALLENGE_TARGET",
                (
                    f"{challenge_id}: "
                    f"{target_type!r} target "
                    f"{target_ref!r} does not resolve"
                ),
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

        check_ref_list(
            reproduction.get(
                "produced_evidence_refs",
                [],
            ),
            "audit-evidence-record",
            registries,
            "REPRODUCTION_EVIDENCE_UNRESOLVED",
            (
                f"{reproduction_id}."
                "produced_evidence_refs"
            ),
            issues,
        )

    # ------------------------------------------------------------------------
    # Reproduction-output backlink
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

            add_issue(
                issues,
                "ORPHAN_REPRODUCTION_OUTPUT",
                (
                    f"{evidence_id}: "
                    "reproduction output points to "
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

            add_issue(
                issues,
                "REPRODUCTION_BACKLINK_MISSING",
                (
                    f"{evidence_id}: "
                    f"{reproduction_ref} does not "
                    "register this evidence"
                ),
            )

    # ------------------------------------------------------------------------
    # Revision chain
    # ------------------------------------------------------------------------

    revisions = registries[
        "assessment-revision-record"
    ]

    applied_edges: dict[str, str] = {}

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
                    f"{prior!r} does not resolve"
                ),
            )

        if not revised_resolved:

            add_issue(
                issues,
                "REVISION_REVISED_UNRESOLVED",
                (
                    f"{revision_id}: "
                    f"{revised!r} does not resolve"
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
                "fusion_refs",
                [],
            ),
            "evidence-fusion-record",
            registries,
            "REVISION_FUSION_UNRESOLVED",
            f"{revision_id}.fusion_refs",
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

        if (
            revision.get(
                "revision_state"
            ) == "applied"
            and prior_resolved
            and revised_resolved
        ):

            if prior in applied_edges:

                add_issue(
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

    # Cycle detection

    revision_cycle = False

    for start in applied_edges:

        visited: set[str] = set()

        node = start

        while node in applied_edges:

            if node in visited:
                revision_cycle = True
                break

            visited.add(node)

            node = applied_edges[
                node
            ]

        if revision_cycle:
            break

    if revision_cycle:

        add_issue(
            issues,
            "REVISION_CYCLE",
            "applied revision graph contains a cycle",
        )

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
                    f"{case_id}: current assessment "
                    f"{current_assessment_ref!r} "
                    "is not terminal; "
                    f"terminal={sorted(terminal_nodes)}"
                ),
            )

    # ========================================================================
    # v0.5 — Auditor Opinions
    # ========================================================================

    opinions = registries[
        "auditor-opinion-record"
    ]

    for opinion_id, opinion in (
        opinions.items()
    ):

        assessment_ref = opinion.get(
            "assessment_ref"
        )

        if assessment_ref not in assessments:

            add_issue(
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

        # Opinion Evidence must belong to its Assessment.

        opinion_evidence = opinion.get(
            "evidence_refs",
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

        # Opinion Fusion must belong to its Assessment.

        opinion_fusions = opinion.get(
            "fusion_refs",
            [],
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

        if not opinion.get(
            "auditor_ref"
        ):

            add_issue(
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

            add_issue(
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

            add_issue(
                issues,
                "OPINION_EFFECT_SCOPE_INVALID",
                (
                    f"{opinion_id}: "
                    "opinion must remain audit_only"
                ),
            )

    # ========================================================================
    # v0.5 — Reconciliation
    # ========================================================================

    reconciliations = registries[
        "audit-reconciliation-record"
    ]

    unresolved_point_registry: dict[
        str,
        str
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

        # All Opinions must concern an Assessment represented
        # by the Reconciliation.

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

                add_issue(
                    issues,
                    "RECONCILIATION_OPINION_ASSESSMENT_MISMATCH",
                    (
                        f"{reconciliation_id}: "
                        f"{opinion_ref} concerns "
                        f"{opinion_assessment!r}, "
                        "which is absent from "
                        "assessment_refs"
                    ),
                )

            auditor_ref = opinion.get(
                "auditor_ref"
            )

            if isinstance(
                auditor_ref,
                str,
            ):
                auditor_refs.add(
                    auditor_ref
                )

        # Reconciliation is explicitly multi-auditor.

        if len(auditor_refs) < 2:

            add_issue(
                issues,
                "RECONCILIATION_AUDITOR_DIVERSITY_INSUFFICIENT",
                (
                    f"{reconciliation_id}: "
                    "fewer than two distinct "
                    "auditors are represented"
                ),
            )

        if reconciliation.get(
            "majority_verdict_applied"
        ) is not False:

            add_issue(
                issues,
                "MAJORITY_VERDICT_FORBIDDEN",
                (
                    f"{reconciliation_id}: "
                    "majority_verdict_applied "
                    "must be false"
                ),
            )

        if reconciliation.get(
            "effect_scope"
        ) != "audit_only":

            add_issue(
                issues,
                "RECONCILIATION_EFFECT_SCOPE_INVALID",
                (
                    f"{reconciliation_id}: "
                    "reconciliation must remain "
                    "audit_only"
                ),
            )

        # ------------------------------------------------------------
        # Point-level integrity
        # ------------------------------------------------------------

        point_ids: set[str] = set()

        def register_point_id(
            point_id: Any,
            point_type: str,
        ) -> None:

            if not isinstance(
                point_id,
                str,
            ):
                return

            if point_id in point_ids:

                add_issue(
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

                if point_id in unresolved_point_registry:

                    add_issue(
                        issues,
                        "UNRESOLVED_POINT_ID_COLLISION",
                        (
                            f"{point_id!r} appears in "
                            "multiple reconciliations"
                        ),
                    )

                else:

                    unresolved_point_registry[
                        point_id
                    ] = reconciliation_id

        # Agreement points

        for point in reconciliation.get(
            "agreed_points",
            [],
        ):

            register_point_id(
                point.get("point_id"),
                "agreed",
            )

            supporting = point.get(
                "supporting_opinion_refs",
                [],
            )

            check_subset(
                supporting,
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

        # Disputed points

        for point in reconciliation.get(
            "disputed_points",
            [],
        ):

            register_point_id(
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

                        add_issue(
                            issues,
                            "DISPUTE_POSITION_DUPLICATE",
                            (
                                f"{reconciliation_id}: "
                                f"duplicate dispute "
                                f"position {label!r}"
                            ),
                        )

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

        # Unresolved points

        for point in reconciliation.get(
            "unresolved_points",
            [],
        ):

            register_point_id(
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
    # v0.5 — Handoff Boundary
    # ========================================================================

    handoffs = registries[
        "audit-handoff-record"
    ]

    # All top-level MEDA IDs for heterogeneous payload validation.

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
            (
                f"{handoff_id}."
                "reconciliation_refs"
            ),
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
        # Payload reference resolution
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

                add_issue(
                    issues,
                    "HANDOFF_PAYLOAD_UNRESOLVED",
                    (
                        f"{handoff_id}: "
                        "payload contains unresolved "
                        f"MEDA record "
                        f"{payload_ref!r}"
                    ),
                )

        # All explicitly linked MEDA records should be represented
        # in the transferred payload.

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

            add_issue(
                issues,
                "HANDOFF_PAYLOAD_INCOMPLETE",
                (
                    f"{handoff_id}: "
                    "linked audit records absent "
                    "from payload_refs: "
                    f"{sorted(missing_payload)}"
                ),
            )

        # ------------------------------------------------------------
        # Unresolved reconciliation-point preservation
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

                add_issue(
                    issues,
                    "HANDOFF_UNRESOLVED_POINT_UNKNOWN",
                    (
                        f"{handoff_id}: "
                        "unresolved point "
                        f"{point_ref!r} does not exist"
                    ),
                )

            elif reconciliation_ref not in (
                referenced_reconciliation_set
            ):

                add_issue(
                    issues,
                    "HANDOFF_UNRESOLVED_POINT_OUTSIDE_RECONCILIATION",
                    (
                        f"{handoff_id}: "
                        f"{point_ref!r} belongs to "
                        f"{reconciliation_ref}, which "
                        "is not referenced by handoff"
                    ),
                )

        # ------------------------------------------------------------
        # Authority boundary
        # ------------------------------------------------------------

        if handoff.get(
            "decision_authority"
        ) != "external":

            add_issue(
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

            add_issue(
                issues,
                "HANDOFF_EFFECT_BOUNDARY_VIOLATION",
                (
                    f"{handoff_id}: "
                    "handoff_effect must be "
                    "transfer_only"
                ),
            )

        if handoff.get(
            "legal_effect"
        ) != "none":

            add_issue(
                issues,
                "HANDOFF_LEGAL_EFFECT_VIOLATION",
                (
                    f"{handoff_id}: "
                    "MEDA handoff cannot create "
                    "legal effect"
                ),
            )

    # ------------------------------------------------------------------------
    # Case state = handed_off must correspond to a real transfer
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

            add_issue(
                issues,
                "CASE_HANDED_OFF_WITHOUT_TRANSFER",
                (
                    f"{case_id}: "
                    "case_state is handed_off but "
                    "no handoff has been transmitted "
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
                        "unresolved MEDA committed "
                        f"input {committed_ref!r}"
                    ),
                )

    return issues


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
                validators,
                records,
            )
        )

        registries, registry_errors = (
            build_registries(
                records
            )
        )

        print("[record registry]")

        if registry_errors:

            failures += len(
                registry_errors
            )

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

            issues = validate_audit_graph(
                registries
            )

            print(
                "[audit graph validation]"
            )

            if issues:

                failures += len(
                    issues
                )

                for issue in issues:

                    print(
                        f"  [graph-fail] "
                        f"{issue.code}: "
                        f"{issue.message}"
                    )

            else:

                print(
                    "  [graph-ok] "
                    "all structural references resolve"
                )

                print(
                    "  [history-ok] "
                    "Challenge → Reproduction → "
                    "Revision history is valid"
                )

                print(
                    "  [multi-auditor-ok] "
                    "Opinions remain independently "
                    "identified and non-binding"
                )

                print(
                    "  [reconciliation-ok] "
                    "agreement, disagreement, and "
                    "unresolved points are preserved "
                    "without majority verdict"
                )

                print(
                    "  [handoff-ok] "
                    "audit context crosses the MEDA "
                    "boundary as transfer-only with "
                    "external decision authority"
                )

        print()

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
            "All 12 schemas are valid, all 21 "
            "Reference Case records passed Schema "
            "validation, and the complete MEDA v0.5 "
            "Audit Graph passed structural, temporal, "
            "multi-auditor, reconciliation, and "
            "external-handoff boundary validation."
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
