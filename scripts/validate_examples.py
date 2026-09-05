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
}


# ============================================================================
# Record type mappings
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
}


# ============================================================================
# Helpers
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


# ============================================================================
# Determine Schema from path
# ============================================================================

def schema_name_for_path(
    path: Path,
) -> str:

    posix = path.as_posix()

    if posix == "audit-case-record.json":
        return "audit-case-record"

    if posix.startswith("evidence/"):
        return "audit-evidence-record"

    if posix.startswith("relationships/"):
        return "evidence-relationship-record"

    if posix.startswith("fusion/"):
        return "evidence-fusion-record"

    if posix.startswith("assessments/"):
        return "derivation-assessment-record"

    if posix.startswith("attestations/"):
        return "zk-audit-attestation"

    if posix.startswith("challenges/"):
        return "audit-challenge-record"

    if posix.startswith("reproductions/"):
        return "reproduction-record"

    if posix.startswith("revisions/"):
        return "assessment-revision-record"

    raise RuntimeError(
        f"Cannot determine Schema for: "
        f"{posix}"
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

    for filename in sorted(expected - actual):
        failures += 1

        print(
            f"  [FAIL] missing schema: "
            f"{filename}"
        )

    for filename in sorted(actual - expected):
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

    records = {}

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
# Protocol version checks
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
                    f"{path.as_posix()}: "
                    f"protocol_version="
                    f"{protocol_version!r}, "
                    f"expected "
                    f"{PROTOCOL_VERSION!r}"
                )

    if failures == 0:
        print(
            "  [version-ok] all Reference Case "
            "records declare MEDA v0.4.0"
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

    registries = {
        schema_name: {}
        for schema_name in SCHEMA_FILES
    }

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
                f"duplicate ID "
                f"{record_id}"
            )
            continue

        registries[
            schema_name
        ][record_id] = record

    return registries, errors


# ============================================================================
# Graph helpers
# ============================================================================

def check_ref(
    reference: str,
    schema_name: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]]
    ],
    location: str,
    errors: list[str],
) -> None:

    if reference not in registries[
        schema_name
    ]:
        errors.append(
            f"{location}: unresolved "
            f"{schema_name} reference "
            f"{reference!r}"
        )


def check_refs(
    references: list[str],
    schema_name: str,
    registries: dict[
        str,
        dict[str, dict[str, Any]]
    ],
    location: str,
    errors: list[str],
) -> None:

    for reference in references:
        check_ref(
            reference,
            schema_name,
            registries,
            location,
            errors,
        )


def check_subset(
    child: list[str],
    parent: list[str],
    child_name: str,
    parent_name: str,
    record_id: str,
    errors: list[str],
) -> None:

    invalid = (
        set(child)
        - set(parent)
    )

    if invalid:
        errors.append(
            f"{record_id}: "
            f"{child_name} contains value(s) "
            f"outside {parent_name}: "
            f"{sorted(invalid)}"
        )


def check_disjoint(
    left: list[str],
    right: list[str],
    left_name: str,
    right_name: str,
    record_id: str,
    errors: list[str],
) -> None:

    overlap = (
        set(left)
        & set(right)
    )

    if overlap:
        errors.append(
            f"{record_id}: "
            f"{left_name} and "
            f"{right_name} overlap: "
            f"{sorted(overlap)}"
        )


# ============================================================================
# Audit Graph validation
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
    # Exactly one Audit Case
    # ------------------------------------------------------------------------

    cases = registries[
        "audit-case-record"
    ]

    if len(cases) != 1:

        print(
            "  [graph-fail] "
            "Reference Case must contain exactly "
            f"one Audit Case; found {len(cases)}"
        )

        print()

        return 1

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
    # All member records must share Case / Origin / Derivative
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
            registries[
                schema_name
            ].items()
        ):

            if record.get(
                "case_ref"
            ) != case_id:

                errors.append(
                    f"{record_id}: "
                    f"case_ref does not match "
                    f"{case_id}"
                )

            if record.get(
                "origin_ref"
            ) != origin_ref:

                errors.append(
                    f"{record_id}: "
                    "origin_ref mismatch"
                )

            if record.get(
                "derivative_ref"
            ) != derivative_ref:

                errors.append(
                    f"{record_id}: "
                    "derivative_ref mismatch"
                )

    # ------------------------------------------------------------------------
    # Case Registry completeness
    # ------------------------------------------------------------------------

    case_registry = {
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
        case_registry.items()
    ):

        declared = set(
            case.get(
                field_name,
                [],
            )
        )

        actual = set(
            registries[
                schema_name
            ].keys()
        )

        missing = (
            actual - declared
        )

        unresolved = (
            declared - actual
        )

        if missing:
            errors.append(
                f"{case_id}: "
                f"{field_name} fails to register "
                f"{sorted(missing)}"
            )

        if unresolved:
            errors.append(
                f"{case_id}: "
                f"{field_name} contains unresolved "
                f"{sorted(unresolved)}"
            )

    # ------------------------------------------------------------------------
    # Current Assessment
    # ------------------------------------------------------------------------

    current_assessment = case.get(
        "current_assessment_ref"
    )

    if current_assessment is not None:

        check_ref(
            current_assessment,
            "derivation-assessment-record",
            registries,
            f"{case_id}.current_assessment_ref",
            errors,
        )

        if current_assessment not in case.get(
            "assessment_refs",
            [],
        ):
            errors.append(
                f"{case_id}: "
                "current_assessment_ref is not "
                "registered in assessment_refs"
            )

    # ------------------------------------------------------------------------
    # Evidence Relationships
    # ------------------------------------------------------------------------

    relationships = registries[
        "evidence-relationship-record"
    ]

    for relationship_id, record in (
        relationships.items()
    ):

        evidence_refs = record.get(
            "evidence_refs",
            [],
        )

        check_refs(
            evidence_refs,
            "audit-evidence-record",
            registries,
            f"{relationship_id}.evidence_refs",
            errors,
        )

        check_subset(
            evidence_refs,
            case.get(
                "evidence_refs",
                [],
            ),
            "evidence_refs",
            "case.evidence_refs",
            relationship_id,
            errors,
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

        check_refs(
            evidence_refs,
            "audit-evidence-record",
            registries,
            f"{fusion_id}.evidence_refs",
            errors,
        )

        check_refs(
            relationship_refs,
            "evidence-relationship-record",
            registries,
            f"{fusion_id}.relationship_refs",
            errors,
        )

        check_subset(
            evidence_refs,
            case.get(
                "evidence_refs",
                [],
            ),
            "evidence_refs",
            "case.evidence_refs",
            fusion_id,
            errors,
        )

        for field_name in [
            "supporting_evidence_refs",
            "counter_evidence_refs",
            "redundant_evidence_refs",
            "effective_evidence_refs",
        ]:

            check_subset(
                fusion.get(
                    field_name,
                    [],
                ),
                evidence_refs,
                field_name,
                "fusion.evidence_refs",
                fusion_id,
                errors,
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
            "supporting_evidence_refs",
            "counter_evidence_refs",
            fusion_id,
            errors,
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
            "redundant_evidence_refs",
            "effective_evidence_refs",
            fusion_id,
            errors,
        )

        for relationship_ref in (
            relationship_refs
        ):

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
                (
                    f"{relationship_ref}."
                    "evidence_refs"
                ),
                (
                    f"{fusion_id}."
                    "evidence_refs"
                ),
                fusion_id,
                errors,
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

        check_refs(
            evidence_refs,
            "audit-evidence-record",
            registries,
            f"{assessment_id}.evidence_refs",
            errors,
        )

        check_refs(
            fusion_refs,
            "evidence-fusion-record",
            registries,
            f"{assessment_id}.fusion_refs",
            errors,
        )

        check_subset(
            assessment.get(
                "conflicting_evidence_refs",
                [],
            ),
            evidence_refs,
            "conflicting_evidence_refs",
            "assessment.evidence_refs",
            assessment_id,
            errors,
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
            errors.append(
                f"{assessment_id}: "
                "assessment references evidence "
                "not present in its Fusion(s): "
                f"{sorted(unfused)}"
            )

    # ------------------------------------------------------------------------
    # Challenge validation
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

        if target_schema is None:

            errors.append(
                f"{challenge_id}: "
                f"unsupported target type "
                f"{target_type!r}"
            )

        else:

            check_ref(
                target_ref,
                target_schema,
                registries,
                (
                    f"{challenge_id}."
                    "target_record_ref"
                ),
                errors,
            )

        related_evidence = challenge.get(
            "related_evidence_refs",
            [],
        )

        check_refs(
            related_evidence,
            "audit-evidence-record",
            registries,
            (
                f"{challenge_id}."
                "related_evidence_refs"
            ),
            errors,
        )

    # ------------------------------------------------------------------------
    # Reproduction validation
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

        if target_schema is None:

            errors.append(
                f"{reproduction_id}: "
                f"unsupported target type "
                f"{target_type!r}"
            )

        else:

            check_ref(
                target_ref,
                target_schema,
                registries,
                (
                    f"{reproduction_id}."
                    "target_record_ref"
                ),
                errors,
            )

        challenge_refs = reproduction.get(
            "challenge_refs",
            [],
        )

        check_refs(
            challenge_refs,
            "audit-challenge-record",
            registries,
            (
                f"{reproduction_id}."
                "challenge_refs"
            ),
            errors,
        )

        produced_evidence = reproduction.get(
            "produced_evidence_refs",
            [],
        )

        check_refs(
            produced_evidence,
            "audit-evidence-record",
            registries,
            (
                f"{reproduction_id}."
                "produced_evidence_refs"
            ),
            errors,
        )

        check_subset(
            produced_evidence,
            case.get(
                "evidence_refs",
                [],
            ),
            "produced_evidence_refs",
            "case.evidence_refs",
            reproduction_id,
            errors,
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
            evidence.get(
                "evidence_type"
            )
            != "reproduction_output"
        ):
            continue

        observation = evidence.get(
            "observation",
            {},
        )

        reproduction_ref = observation.get(
            "reproduction_ref"
        )

        if not reproduction_ref:
            errors.append(
                f"{evidence_id}: "
                "reproduction_output evidence "
                "must identify observation."
                "reproduction_ref"
            )
            continue

        check_ref(
            reproduction_ref,
            "reproduction-record",
            registries,
            (
                f"{evidence_id}."
                "observation.reproduction_ref"
            ),
            errors,
        )

        reproduction = reproductions.get(
            reproduction_ref
        )

        if (
            reproduction is not None
            and evidence_id not in reproduction.get(
                "produced_evidence_refs",
                [],
            )
        ):
            errors.append(
                f"{evidence_id}: "
                f"{reproduction_ref} does not "
                "register this evidence in "
                "produced_evidence_refs"
            )

    # ------------------------------------------------------------------------
    # Revision validation
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

        check_ref(
            prior,
            "derivation-assessment-record",
            registries,
            (
                f"{revision_id}."
                "prior_assessment_ref"
            ),
            errors,
        )

        check_ref(
            revised,
            "derivation-assessment-record",
            registries,
            (
                f"{revision_id}."
                "revised_assessment_ref"
            ),
            errors,
        )

        if prior == revised:
            errors.append(
                f"{revision_id}: "
                "prior_assessment_ref and "
                "revised_assessment_ref "
                "must differ"
            )

        check_refs(
            revision.get(
                "challenge_refs",
                [],
            ),
            "audit-challenge-record",
            registries,
            (
                f"{revision_id}."
                "challenge_refs"
            ),
            errors,
        )

        check_refs(
            revision.get(
                "reproduction_refs",
                [],
            ),
            "reproduction-record",
            registries,
            (
                f"{revision_id}."
                "reproduction_refs"
            ),
            errors,
        )

        check_refs(
            revision.get(
                "evidence_added_refs",
                [],
            ),
            "audit-evidence-record",
            registries,
            (
                f"{revision_id}."
                "evidence_added_refs"
            ),
            errors,
        )

        check_refs(
            revision.get(
                "evidence_removed_refs",
                [],
            ),
            "audit-evidence-record",
            registries,
            (
                f"{revision_id}."
                "evidence_removed_refs"
            ),
            errors,
        )

        check_refs(
            revision.get(
                "fusion_refs",
                [],
            ),
            "evidence-fusion-record",
            registries,
            (
                f"{revision_id}."
                "fusion_refs"
            ),
            errors,
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
            "evidence_added_refs",
            "evidence_removed_refs",
            revision_id,
            errors,
        )

        # ------------------------------------------------------------
        # Trigger validation
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

            check_refs(
                trigger_refs,
                trigger_schema_map[
                    trigger_type
                ],
                registries,
                (
                    f"{revision_id}."
                    "trigger_refs"
                ),
                errors,
            )

        # ------------------------------------------------------------
        # Applied revision chain
        # ------------------------------------------------------------

        if revision.get(
            "revision_state"
        ) == "applied":

            if prior in applied_edges:
                errors.append(
                    f"{revision_id}: "
                    f"{prior} already has another "
                    "applied successor"
                )

            else:
                applied_edges[
                    prior
                ] = revised

    # ------------------------------------------------------------------------
    # Applied revision cycles
    # ------------------------------------------------------------------------

    for start in applied_edges:

        visited: set[str] = set()

        node = start

        while node in applied_edges:

            if node in visited:
                errors.append(
                    "applied revision chain "
                    f"contains a cycle at {node}"
                )
                break

            visited.add(
                node
            )

            node = applied_edges[
                node
            ]

    # ------------------------------------------------------------------------
    # Current Assessment must be terminal applied revision
    # ------------------------------------------------------------------------

    if applied_edges:

        revised_nodes = set(
            applied_edges.values()
        )

        prior_nodes = set(
            applied_edges.keys()
        )

        terminal_nodes = (
            revised_nodes
            - prior_nodes
        )

        if (
            current_assessment
            not in terminal_nodes
        ):
            errors.append(
                f"{case_id}: "
                "current_assessment_ref "
                f"{current_assessment!r} "
                "is not the terminal revised "
                "assessment of the applied "
                f"revision chain "
                f"{sorted(terminal_nodes)}"
            )

    # ------------------------------------------------------------------------
    # ZK Audit Attestation validation
    # ------------------------------------------------------------------------

    attestations = registries[
        "zk-audit-attestation"
    ]

    all_ids: set[str] = set()

    for registry in registries.values():
        all_ids.update(
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

            if context_schema is None:

                errors.append(
                    f"{attestation_id}: "
                    "unsupported "
                    "audit_context_type "
                    f"{context_type!r}"
                )

            else:

                check_ref(
                    context_ref,
                    context_schema,
                    registries,
                    (
                        f"{attestation_id}."
                        "audit_context_ref"
                    ),
                    errors,
                )

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
                "CHALLENGE-",
                "REPRODUCTION-",
                "REVISION-",
            )

            if committed_ref.startswith(
                meda_prefixes
            ):
                if committed_ref not in all_ids:
                    errors.append(
                        f"{attestation_id}: "
                        "unresolved committed "
                        f"MEDA reference "
                        f"{committed_ref}"
                    )

    # ------------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------------

    if errors:

        for error in errors:
            print(
                f"  [graph-fail] {error}"
            )

        print()

        return len(errors)

    print(
        "  [graph-ok] all references resolve "
        "and all v0.4 cross-record "
        "invariants hold"
    )

    print(
        "  [history-ok] "
        "Assessment-0001 → Challenge → "
        "Reproduction → New Evidence → "
        "Re-Fusion → Assessment-0002 → "
        "Revision is traceable"
    )

    print(
        "  [revision-ok] "
        f"current assessment = "
        f"{current_assessment}"
    )

    print()

    return 0


# ============================================================================
# Main
# ============================================================================

def main() -> int:

    print(
        "=== Multi-Evidence Derivation Audit "
        "Protocol v0.4 Validation ==="
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

            total = sum(
                len(registry)
                for registry
                in registries.values()
            )

            print(
                f"  [registry-ok] "
                f"{total} protocol records indexed"
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

        print(
            "[validate-pass]"
        )

        print(
            "All 9 schemas are valid, "
            "all 17 Reference Case records "
            "passed Schema validation, and "
            "the complete MEDA v0.4 temporal "
            "Audit Graph passed Challenge, "
            "Reproduction, Evidence, Fusion, "
            "Assessment, and Revision-chain "
            "integrity validation."
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
