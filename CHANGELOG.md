# Changelog

All notable changes to the **Multi-Evidence Derivation Audit Protocol (MEDA)** are documented in this file.

MEDA develops incrementally from evidence capture toward graph integrity, temporal revision, multi-auditor reconciliation, and external decision handoff.

---

# [0.5.0] — 2026-09-09

## Status

```text
FROZEN
CI: PASS
```

## Theme

**Multi-Auditor Reconciliation & Decision Handoff**

v0.5 extends MEDA beyond historical assessment revision into a multi-auditor audit environment.

The protocol now supports:

```text
Current Assessment
   ├─ Auditor Opinion A
   └─ Auditor Opinion B
          ↓
     Reconciliation
     ├─ agreed
     ├─ disputed
     └─ unresolved
          ↓
        Handoff
          ↓
════════ MEDA boundary ════════
 External Decision Authority
```

The core v0.5 principle is:

```text
Opinion
≠
Verdict

Reconciliation
≠
Majority Vote

Handoff
≠
Decision
```

---

## Added

### Multi-Auditor Opinion Layer

Added:

```text
schemas/auditor-opinion-record.schema.json
```

The record exposes:

```text
auditor_ref
auditor_type
organization_ref
credential_refs
assessment_ref
evidence_refs
fusion_refs
challenge_refs
reproduction_refs
position
confidence
independence_status
dependency_refs
opinion_basis
agreed_points
disputed_points
unresolved_points
limitations
effect_scope
```

Supported positions:

```text
supports
partially_supports
disputes
insufficient_basis
abstains
```

Supported independence states:

```text
independent
partially_independent
not_independent
unknown
```

Auditor identity is now explicitly preserved.

---

### Audit Reconciliation Layer

Added:

```text
schemas/audit-reconciliation-record.schema.json
```

Reconciliation now preserves:

```text
agreed_points
disputed_points
unresolved_points
```

instead of collapsing multiple opinions into a single majority result.

Supported methods include:

```text
comparative_review
independent_panel
algorithmic_summary
hybrid
other
```

Supported reconciliation states:

```text
complete
partial
blocked
```

Added hard safety constraint:

```text
majority_verdict_applied = false
```

---

### Audit Handoff Layer

Added:

```text
schemas/audit-handoff-record.schema.json
```

The handoff record transfers MEDA audit context to external decision processes.

Supported target types include:

```text
human_review
policy_engine
legal_review
royalty_assessment
external_arbitration
governance_process
other
```

Added required authority boundary:

```text
decision_authority = external
handoff_effect = transfer_only
legal_effect = none
```

A handoff may be accepted while:

```text
external_decision_ref = null
```

This formally establishes:

```text
Package Accepted
≠
Decision Issued
```

---

## Added Invariants

Added invariants A26–A33.

```text
A26 auditor_identity_visibility
A27 opinion_not_verdict
A28 no_majority_verdict
A29 disagreement_preservation
A30 reconciliation_traceability
A31 unresolved_point_preservation
A32 handoff_boundary
A33 no_autonomous_right_creation
```

---

## Changed

### Audit Case Record

Updated:

```text
schemas/audit-case-record.schema.json
```

Added registries:

```text
opinion_refs
reconciliation_refs
handoff_refs
```

Added case states:

```text
reconciling
handoff_ready
handed_off
```

A handed-off case now requires the relevant opinion, reconciliation, and handoff structure.

---

### Zero-Knowledge Audit Attestation

Updated:

```text
schemas/zk-audit-attestation.schema.json
```

Added audit context types:

```text
opinion
reconciliation
handoff
```

ZK attestation remains limited to its declared predicate.

It does not become a derivation or legal verdict.

---

### Audit Challenge

Updated:

```text
schemas/audit-challenge-record.schema.json
```

Added target record types:

```text
opinion
reconciliation
handoff
```

Added challenge scopes:

```text
auditor_independence
opinion_basis
reconciliation
handoff_scope
authority_boundary
```

Added requested actions:

```text
reconcile
review_handoff
```

---

### Assessment Revision

Updated:

```text
schemas/assessment-revision-record.schema.json
```

Added revision triggers:

```text
auditor_opinion
reconciliation
```

Historical assessments remain immutable.

---

## Reference Case

Expanded the canonical PASS case to twenty-one records.

Root:

```text
examples/cases/pass/reference-case/
```

The reference lifecycle now demonstrates:

```text
Evidence
→ Relationship
→ Fusion
→ Assessment
→ Challenge
→ Reproduction
→ New Evidence
→ Re-Fusion
→ Revised Assessment
→ Revision
→ Auditor Opinions
→ Reconciliation
→ Handoff
→ External Decision Boundary
```

---

## Expected-Fail Suite

Added six complete v0.5 EXPECTED-FAIL cases.

```text
examples/cases/fail/same-auditor-reconciliation/
examples/cases/fail/opinion-assessment-mismatch/
examples/cases/fail/unknown-unresolved-point/
examples/cases/fail/handoff-payload-incomplete/
examples/cases/fail/majority-verdict-applied/
examples/cases/fail/internal-decision-authority/
```

Each case contains twenty-one records with one controlled mutation.

Expected failures:

```text
RECONCILIATION_AUDITOR_DIVERSITY_INSUFFICIENT
RECONCILIATION_OPINION_ASSESSMENT_MISMATCH
HANDOFF_UNRESOLVED_POINT_UNKNOWN
HANDOFF_PAYLOAD_INCOMPLETE
MAJORITY_VERDICT_SCHEMA_FORBIDDEN
INTERNAL_DECISION_AUTHORITY_SCHEMA_FORBIDDEN
```

---

## Validation

Updated:

```text
scripts/validate_examples.py
```

The validator now checks:

```text
12-schema inventory
case inventory
21-record case inventory
case coherence
origin / derivative consistency
relationship references
fusion subsets
challenge targets
reproduction outputs
revision chains
current assessment integrity
ZK audit context
auditor identity
auditor diversity
opinion / assessment coherence
reconciliation point integrity
unresolved point references
handoff payload completeness
external authority boundary
hard schema safety constraints
```

Added v0.5 schema-negative classification for:

```text
MAJORITY_VERDICT_SCHEMA_FORBIDDEN
INTERNAL_DECISION_AUTHORITY_SCHEMA_FORBIDDEN
```

---

## Validation Result

v0.5 successfully passes the active repository validation workflow.

```text
12 Schemas

1 PASS Case
21 PASS Records

6 EXPECTED-FAIL Cases
126 EXPECTED-FAIL Records

147 Active Example Records
```

Final result:

```text
[validate-pass]
```

---

# [0.4.0]

## Theme

**Challenge, Reproduction & Revision**

v0.4 introduced temporal audit history.

The protocol evolved from a static audit graph into:

```text
Assessment v1
  ↓
Challenge
  ↓
Reproduction
  ↓
New Evidence
  ↓
Re-Fusion
  ↓
Assessment v2
  ↓
Revision Record
```

---

## Added

Added:

```text
schemas/audit-challenge-record.schema.json
schemas/reproduction-record.schema.json
schemas/assessment-revision-record.schema.json
```

---

## Added Invariants

Added invariants A19–A25.

```text
A19 no_destructive_revision
A20 challenge_traceability
A21 reproduction_separation
A22 revision_provenance
A23 unresolved_dispute_preservation
A24 reproduction_not_verdict
A25 revision_chain_integrity
```

---

## Historical Integrity

Established immutable assessment history.

```text
Old Assessment
→ preserved

New Assessment
→ appended

Revision Record
→ connects them
```

A revised assessment no longer replaces the previous assessment.

---

## Reproduction Semantics

A reproduction result became a distinct protocol object.

A failed reproduction may create counter-evidence but does not automatically invalidate the original evidence.

```text
Failed Reproduction
≠
Automatic Invalidation
```

---

## Reference Flow

The canonical temporal flow established:

```text
ASSESSMENT-0001
→ CHALLENGE-0001
→ REPRODUCTION-0001
→ EVIDENCE-0005
→ FUSION-0002
→ ASSESSMENT-0002
→ REVISION-0001
```

---

## Expected-Fail Validation

Added temporal integrity tests covering:

```text
unresolved challenge targets
orphan reproduction outputs
broken revision chains
incorrect current assessment
revision cycles
```

Historical v0.4 negative fixtures were later archived when the active suite moved to v0.5.

---

# [0.3.0]

## Theme

**Audit Case Graph & Cross-Record Integrity**

v0.3 introduced explicit audit-case graph validation.

The central principle became:

```text
Schema-valid
≠
Protocol-consistent
```

---

## Added

Added:

```text
schemas/audit-case-record.schema.json
```

All graph records gained:

```text
case_ref
```

and relevant records preserve:

```text
origin_ref
derivative_ref
```

---

## Added Invariants

Added invariants A12–A18.

```text
A12 case_coherence
A13 referential_integrity
A14 origin_derivative_consistency
A15 subset_integrity
A16 no_cross_case_mixing
A17 current_assessment_integrity
A18 graph_validation_required
```

---

## Graph Validation

Added validation for:

```text
reference resolution
case membership
origin consistency
derivative consistency
fusion subset integrity
current assessment integrity
typed ZK audit context
cross-case mixing
```

---

## Negative Tests

Introduced graph-level expected-fail cases for conditions including:

```text
cross-case evidence
invalid current assessment
missing references
origin mismatch
redundant / effective overlap
support / counter overlap
```

These historical v0.3 fixtures were later moved to:

```text
archive/v0.3/cases/fail/
```

---

# [0.2.0]

## Theme

**Evidence Fusion without Double Counting**

v0.2 introduced evidence relationships and evidence fusion.

The core principle became:

```text
Evidence Count
≠
Evidence Strength
```

---

## Added

Added:

```text
schemas/evidence-relationship-record.schema.json
schemas/evidence-fusion-record.schema.json
```

---

## Added Invariants

Added invariants A8–A11.

```text
A8  no_evidence_double_counting
A9  counter_evidence_preservation
A10 fusion_explainability
A11 no_universal_weight
```

---

## Evidence Dependency

Added dependency types:

```text
independent
partially_dependent
same_source
unknown
```

---

## Evidentiary Effect

Added evidentiary effects:

```text
corroborating
conflicting
neutral
unknown
```

Dependency and evidentiary effect were intentionally separated.

For example:

```text
same_source
+
corroborating
```

means two records support the same hypothesis while still sharing an underlying source.

---

## Evidence Fusion

Added fusion outputs:

```text
insufficient
weak_support
moderate_support
strong_support
conflicted
```

Fusion distinguishes:

```text
supporting evidence
counter-evidence
redundant evidence
effective evidence
```

No universal evidence-weight formula was imposed.

---

# [0.1.0]

## Theme

**Evidence → Assessment → Attestation**

v0.1 established the minimum MEDA architecture.

---

## Added

Initial schemas:

```text
schemas/audit-evidence-record.schema.json
schemas/derivation-assessment-record.schema.json
schemas/zk-audit-attestation.schema.json
```

---

## Initial Invariants

Established A1–A7.

```text
A1 evidence_not_verdict
A2 no_automatic_right_creation
A3 reproducible_assessment
A4 attestation_scope
A5 dispute_separation
A6 evidence_provenance
A7 maturity_visibility
```

---

## Assessment States

Initial assessment states:

```text
insufficient
suspected
supported
protocol_verified
disputed
```

---

## Legal Effect

Added explicit legal-effect descriptors:

```text
none
policy_dependent
human_review_required
externally_determined
```

---

## ZK Boundary

Established the term:

> **Zero-Knowledge Audit Attestation**

A verified ZK predicate does not independently establish causal derivation, liability, or royalty rights.

---

## Foundational Principle

v0.1 fixed the principle that continues through all later versions:

```text
Evidence
≠
Verdict
```

---

# Version Progression

```text
v0.1
Evidence & Assessment

      ↓

v0.2
Evidence Fusion

      ↓

v0.3
Graph Integrity

      ↓

v0.4
Temporal Revision Integrity

      ↓

v0.5
Multi-Auditor Reconciliation
& External Decision Handoff
```

---

# Current State

```text
Current Version: 0.5.0
Status: FROZEN
CI: PASS
```

MEDA v0.5 now provides an auditable path from raw signals to external decision handoff while preserving:

```text
provenance
dependency
counter-evidence
history
reproduction
auditor identity
disagreement
unresolved questions
authority boundaries
```

without converting audit machinery into an automatic verdict system.
