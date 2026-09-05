# MEDA v0.3 Archived Expected-Fail Graph Cases

This directory preserves the EXPECTED-FAIL Audit Graph fixtures used by
Multi-Evidence Derivation Audit Protocol (MEDA) v0.3.

These cases are retained as historical protocol artifacts.

They are not part of the active MEDA v0.4 validation suite and MUST NOT be
included in the v0.4 `examples/cases/fail/` inventory.

---

## Archive Metadata

- Protocol: Multi-Evidence Derivation Audit Protocol
- Protocol version: v0.3
- Archive status: Historical
- Active validation: No
- Superseded by: MEDA v0.4 Temporal Validation
- Primary purpose: Cross-record Audit Graph integrity testing

---

## Why These Cases Are Archived

MEDA v0.3 introduced validation beyond local JSON Schema correctness.

The core principle was:

```text
Schema-valid
≠
Protocol-valid

A record could be locally valid while the complete Audit Graph remained
structurally inconsistent.

The v0.3 EXPECTED-FAIL suite therefore tested cases in which individual JSON
records were Schema-valid but the connected graph violated cross-record
invariants.

MEDA v0.4 retains these design principles but extends validation into temporal
history:

v0.3
Cross-record Graph Integrity

        ↓

v0.4
Temporal Revision Integrity

The fixtures below are archived rather than deleted so that the evolution of
the protocol remains inspectable.

Archived Cases
1. cross-case-evidence
Purpose

Tests whether evidence belonging to one Audit Case can be improperly inserted
into another Audit Case.

Structural failure
CASE-A
  ↓
Evidence
  ↓
case_ref = CASE-B
Expected v0.3 issue
CASE_REF_MISMATCH
Invariant represented

A record participating in an Audit Case must declare the same case context as
the enclosing Audit Case.

This fixture primarily represented:

MEDA-A12 — case_coherence
MEDA-A16 — no_cross_case_mixing
2. invalid-current-assessment
Purpose

Tests whether an Audit Case may declare a current assessment that does not
exist in the graph.

Structural failure
CASE
  ↓
current_assessment_ref
  ↓
ASSESSMENT-MISSING
Expected v0.3 issues
CASE_REGISTRY_UNRESOLVED
CURRENT_ASSESSMENT_UNRESOLVED
Invariant represented

The current assessment must resolve to an assessment registered inside the
same Audit Case.

This fixture primarily represented:

MEDA-A17 — current_assessment_integrity
v0.4 evolution

MEDA v0.4 extends this rule.

It is no longer sufficient for the current assessment merely to exist.

When applied revisions exist, the current assessment must also be the terminal
assessment of the valid revision chain.

3. missing-reference
Purpose

Tests whether an Audit Case may contain a protocol reference whose target
record does not exist.

Structural failure
CASE
  ↓
EVIDENCE-MISSING
  ↓
no record
Expected v0.3 issue
CASE_REGISTRY_UNRESOLVED
Invariant represented

Every protocol reference must resolve to an existing record of the expected
type.

This fixture primarily represented:

MEDA-A13 — referential_integrity
MEDA-A18 — graph_validation_required
4. origin-mismatch
Purpose

Tests whether records inside the same Audit Case may silently refer to
different origins.

Structural failure
CASE
origin_ref = MODEL:origin-alpha:v1

Evidence
origin_ref = MODEL:origin-gamma:v1
Expected v0.3 issue
ORIGIN_MISMATCH
Invariant represented

All records participating in one Audit Case must remain consistent with the
declared Origin and Derivative context.

This fixture primarily represented:

MEDA-A14 — origin_derivative_consistency
5. redundant-effective-overlap
Purpose

Tests whether the same evidence can simultaneously be classified as redundant
and as effective evidence in one Fusion.

Structural failure
redundant_evidence_refs
        ∩
effective_evidence_refs
        ≠
        ∅
Expected v0.3 issue
REDUNDANT_EFFECTIVE_OVERLAP
Invariant represented

Evidence discounted as redundant must not simultaneously contribute as an
effective independent evidentiary channel.

This fixture derives from the MEDA v0.2 evidence-fusion principle:

Evidence Count
≠
Evidence Strength

and primarily reinforces:

MEDA-A8 — no_evidence_double_counting
MEDA-A10 — fusion_explainability
6. support-counter-overlap
Purpose

Tests whether the same evidence can simultaneously support and counter the
same Fusion result.

Structural failure
supporting_evidence_refs
        ∩
counter_evidence_refs
        ≠
        ∅
Expected v0.3 issue
SUPPORT_COUNTER_OVERLAP
Invariant represented

Within one Fusion evaluation, the same evidence record must not silently
occupy mutually incompatible evidentiary roles.

This fixture primarily reinforces:

MEDA-A9 — counter_evidence_preservation
MEDA-A10 — fusion_explainability
v0.3 Archived Validation Matrix
Archived Case	Primary Expected Issue
cross-case-evidence	CASE_REF_MISMATCH
invalid-current-assessment	CASE_REGISTRY_UNRESOLVED, CURRENT_ASSESSMENT_UNRESOLVED
missing-reference	CASE_REGISTRY_UNRESOLVED
origin-mismatch	ORIGIN_MISMATCH
redundant-effective-overlap	REDUNDANT_EFFECTIVE_OVERLAP
support-counter-overlap	SUPPORT_COUNTER_OVERLAP
Protocol Evolution

The archived fixtures document the transition:

MEDA v0.1
Evidence validity
    ↓
MEDA v0.2
Evidence Fusion validity
    ↓
MEDA v0.3
Cross-record Graph validity
    ↓
MEDA v0.4
Temporal Audit History validity

v0.3 established that valid records do not automatically form a valid audit.

v0.4 extends the same principle:

Valid Records
≠
Valid Graph
≠
Valid History

A temporally valid audit must preserve challenges, reproduction attempts,
re-fusions, revised assessments, and revision provenance without destructively
rewriting earlier audit states.

Archive Policy

Files under this directory are historical fixtures.

They SHOULD:

remain available for protocol archaeology and regression reference;
retain their original v0.3 semantics;
remain outside the active v0.4 case inventory;
not be silently rewritten to behave like v0.4 fixtures.

They MAY be reused when building backward-compatibility or regression test
suites.

They MUST NOT be interpreted as active v0.4 conformance examples.

Historical Principle

The v0.3 fixtures preserve one of MEDA's foundational distinctions:

A collection of individually valid audit records does not guarantee a valid
audit graph.

MEDA v0.4 builds on that foundation by adding a second distinction:

A valid audit graph does not guarantee a valid audit history.
