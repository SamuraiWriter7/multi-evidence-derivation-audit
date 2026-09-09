# Multi-Evidence Derivation Audit Protocol

**MEDA — Multi-Evidence Derivation Audit Protocol**

A protocol for collecting, relating, fusing, assessing, challenging, reproducing, revising, reconciling, and handing off multi-source evidence of possible model derivation — **without treating audit signals as automatic legal, royalty, or settlement verdicts.**

**Current Version:** `v0.5.0`  
**Status:** `FROZEN`

---

## Core Principle

> **Audit evidence is not a verdict.**

MEDA is designed for situations in which no single watermark, receipt, trace, similarity signal, reproduction result, or auditor opinion is sufficient to determine model derivation on its own.

The protocol separates the evidentiary process into explicit stages:

```text
Signal
  ↓
Evidence
  ↓
Relationship
  ↓
Fusion
  ↓
Assessment
  ↓
Challenge / Reproduction / Revision
  ↓
Auditor Opinion
  ↓
Reconciliation
  ↓
Handoff
────────────────────────────
External Decision Authority
```

MEDA ends at the **audit handoff boundary**.

It does not autonomously determine:

```text
copyright infringement
legal liability
license creation
royalty entitlement
royalty allocation
settlement instruction
```

---

# Why MEDA?

Model derivation may leave many different kinds of traces:

- statistical watermark signals,
- signed access receipts,
- API traces,
- dataset manifests,
- training attestations,
- behavioral similarity,
- white-box lineage evidence,
- reproduction results.

But:

```text
Evidence Count
≠
Evidence Strength
```

and:

```text
Evidence
≠
Verdict
```

Two records may come from the same underlying event.

A reproduction may conflict with an original observation.

Multiple auditors may disagree.

An external authority may need to decide questions that the audit layer cannot resolve.

MEDA preserves these distinctions instead of collapsing them into a single score.

---

# What MEDA Does

MEDA provides structures for:

- evidence provenance,
- evidence dependency,
- corroborating and conflicting evidence,
- evidence fusion,
- derivation assessment,
- challenge tracking,
- independent reproduction,
- immutable assessment revision,
- multi-auditor opinions,
- reconciliation,
- unresolved-point preservation,
- external decision handoff.

---

# What MEDA Does Not Do

MEDA is not:

- a copyright court,
- a licensing authority,
- a royalty calculator,
- a settlement engine,
- a majority-voting tribunal,
- a universal derivation detector,
- a universal evidence-weighting formula,
- a legal-liability engine.

MEDA may provide evidence to downstream systems.

It does not replace them.

---

# Protocol Boundaries

MEDA v0.5 fixes several important distinctions.

```text
Signal
≠
Evidence Conclusion

Evidence
≠
Verdict

Authenticated Access
≠
Training Incorporation

Similarity
≠
Causal Derivation

Failed Reproduction
≠
Automatic Invalidation

Zero-Knowledge Attestation
≠
Derivation Verdict

Auditor Opinion
≠
Verdict

Reconciliation
≠
Majority Vote

Handoff
≠
Decision

Audit Assessment
≠
Royalty Entitlement

Royalty Entitlement
≠
Settlement
```

---

# Protocol Evolution

MEDA has evolved layer by layer.

```text
v0.1
Evidence
→ Assessment
→ Attestation

v0.2
Evidence Relationships
→ Evidence Fusion
→ Double-Counting Protection

v0.3
Audit Case Graph
→ Cross-Record Integrity

v0.4
Challenge
→ Reproduction
→ Revision
→ Temporal History Integrity

v0.5
Multi-Auditor Opinion
→ Reconciliation
→ Decision Handoff
```

---

# v0.5 Architecture

The v0.5 audit lifecycle is:

```text
Evidence
  ↓
Relationship
  ↓
Fusion
  ↓
Assessment
  ↓
Challenge
  ↓
Reproduction
  ↓
New Evidence
  ↓
Re-Fusion
  ↓
Revised Assessment
  ↓
Revision Record
  ↓
Auditor Opinion A
Auditor Opinion B
  ↓
Reconciliation
  ├─ Agreed Points
  ├─ Disputed Points
  └─ Unresolved Points
  ↓
Handoff
  ↓
════════════════════════════
      MEDA Boundary
════════════════════════════
  ↓
External Decision Authority
```

---

# Schemas

MEDA v0.5 defines twelve JSON Schema record types.

```text
schemas/audit-case-record.schema.json
schemas/audit-evidence-record.schema.json
schemas/evidence-relationship-record.schema.json
schemas/evidence-fusion-record.schema.json
schemas/derivation-assessment-record.schema.json
schemas/zk-audit-attestation.schema.json
schemas/audit-challenge-record.schema.json
schemas/reproduction-record.schema.json
schemas/assessment-revision-record.schema.json
schemas/auditor-opinion-record.schema.json
schemas/audit-reconciliation-record.schema.json
schemas/audit-handoff-record.schema.json
```

All active v0.5 records use:

```text
schema_version = 0.5.0
```

Where applicable:

```text
protocol_version = 0.5.0
```

---

# Record Types

## Audit Case

The case record acts as the root of the audit graph.

It registers:

```text
evidence_refs
relationship_refs
fusion_refs
assessment_refs
attestation_refs
challenge_refs
reproduction_refs
revision_refs
opinion_refs
reconciliation_refs
handoff_refs
```

and maintains:

```text
current_assessment_ref
```

---

## Audit Evidence

Evidence records represent individual observations or artifacts.

Examples include:

```text
watermark
signed_receipt
api_trace
dataset_manifest
training_attestation
similarity
white_box_lineage
reproduction_output
other
```

A valid evidence record remains evidence.

It does not automatically become a derivation verdict.

---

## Evidence Relationship

Evidence relationships distinguish two separate questions:

```text
How dependent are these records?
```

and:

```text
How do they affect the hypothesis?
```

Dependency types include:

```text
independent
partially_dependent
same_source
unknown
```

Evidentiary effects include:

```text
corroborating
conflicting
neutral
unknown
```

---

## Evidence Fusion

Fusion combines evidence without losing dependency structure.

Possible results include:

```text
insufficient
weak_support
moderate_support
strong_support
conflicted
```

Fusion explicitly separates:

```text
supporting_evidence_refs
counter_evidence_refs
redundant_evidence_refs
effective_evidence_refs
```

This prevents evidence count from being mistaken for independent evidentiary strength.

---

## Derivation Assessment

Assessment records describe the protocol-level interpretation of the available audit evidence.

Assessment states include:

```text
insufficient
suspected
supported
protocol_verified
disputed
```

These are audit states, not legal judgments.

---

## Zero-Knowledge Audit Attestation

MEDA uses the term:

> **Zero-Knowledge Audit Attestation**

A ZK attestation proves a declared predicate over committed or secret inputs.

It does not independently prove:

```text
causal derivation
copyright infringement
legal liability
royalty entitlement
```

---

## Audit Challenge

A challenge records an objection to an existing audit record.

A challenge may request:

```text
reassessment
reproduction
reconciliation
handoff review
```

depending on its scope.

A challenge does not automatically invalidate its target.

---

## Reproduction

A reproduction record represents an attempt to repeat a prior audit procedure.

For example:

```text
EVIDENCE-0001
Original watermark observation

        ↓ challenge

REPRODUCTION-0001

        ↓ produces

EVIDENCE-0005
Reproduction output
```

A failed reproduction becomes counter-evidence.

It does not erase the original record.

---

## Assessment Revision

MEDA uses immutable assessment history.

```text
ASSESSMENT-0001
      ↓
Challenge
      ↓
Reproduction
      ↓
New Evidence
      ↓
Re-Fusion
      ↓
ASSESSMENT-0002
      ↓
REVISION-0001
```

The prior assessment remains preserved.

---

## Auditor Opinion

An auditor opinion records:

```text
auditor identity
auditor type
assessment target
evidence basis
position
confidence
independence status
agreed points
disputed points
unresolved points
```

Supported positions include:

```text
supports
partially_supports
disputes
insufficient_basis
abstains
```

Auditor opinions remain opinions.

---

## Audit Reconciliation

Reconciliation compares multiple auditor opinions.

It preserves:

```text
agreed_points
disputed_points
unresolved_points
```

without converting auditor count into an automatic verdict.

The protocol requires:

```text
majority_verdict_applied = false
```

---

## Audit Handoff

A handoff transfers audit context to an external authority.

Supported targets include:

```text
human_review
policy_engine
legal_review
royalty_assessment
external_arbitration
governance_process
other
```

The protocol requires:

```text
decision_authority = external
handoff_effect = transfer_only
legal_effect = none
```

A handoff package may be accepted while:

```text
external_decision_ref = null
```

Therefore:

```text
Package Accepted
≠
Decision Issued
```

---

# Protocol Invariants

MEDA v0.5 defines thirty-three invariants.

```text
A1  evidence_not_verdict
A2  no_automatic_right_creation
A3  reproducible_assessment
A4  attestation_scope
A5  dispute_separation
A6  evidence_provenance
A7  maturity_visibility

A8  no_evidence_double_counting
A9  counter_evidence_preservation
A10 fusion_explainability
A11 no_universal_weight

A12 case_coherence
A13 referential_integrity
A14 origin_derivative_consistency
A15 subset_integrity
A16 no_cross_case_mixing
A17 current_assessment_integrity
A18 graph_validation_required

A19 no_destructive_revision
A20 challenge_traceability
A21 reproduction_separation
A22 revision_provenance
A23 unresolved_dispute_preservation
A24 reproduction_not_verdict
A25 revision_chain_integrity

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

# Reference Case

The canonical PASS case is:

```text
examples/cases/pass/reference-case/
```

It contains twenty-one records.

```text
examples/cases/pass/reference-case/audit-case-record.json

examples/cases/pass/reference-case/evidence/evidence-0001.watermark.json
examples/cases/pass/reference-case/evidence/evidence-0002.signed-receipt.json
examples/cases/pass/reference-case/evidence/evidence-0003.api-trace.json
examples/cases/pass/reference-case/evidence/evidence-0004.similarity.json
examples/cases/pass/reference-case/evidence/evidence-0005.reproduction-output.json

examples/cases/pass/reference-case/relationships/relationship-0001.same-source.json
examples/cases/pass/reference-case/relationships/relationship-0002.independent-corroboration.json
examples/cases/pass/reference-case/relationships/relationship-0003.reproduction-conflict.json

examples/cases/pass/reference-case/fusion/fusion-0001.json
examples/cases/pass/reference-case/fusion/fusion-0002.json

examples/cases/pass/reference-case/assessments/assessment-0001.json
examples/cases/pass/reference-case/assessments/assessment-0002.json

examples/cases/pass/reference-case/attestations/zk-attestation-0001.json

examples/cases/pass/reference-case/challenges/challenge-0001.json

examples/cases/pass/reference-case/reproductions/reproduction-0001.json

examples/cases/pass/reference-case/revisions/revision-0001.json

examples/cases/pass/reference-case/opinions/opinion-0001.json
examples/cases/pass/reference-case/opinions/opinion-0002.json

examples/cases/pass/reference-case/reconciliations/reconciliation-0001.json

examples/cases/pass/reference-case/handoffs/handoff-0001.json
```

---

# Reference Case Story

The reference case begins with four initial evidence records.

```text
EVIDENCE-0001
Watermark detection

EVIDENCE-0002
Signed API receipt

EVIDENCE-0003
API trace

EVIDENCE-0004
Behavioral similarity
```

`EVIDENCE-0002` and `EVIDENCE-0003` originate from the same authenticated access event.

MEDA therefore records:

```text
dependency_type = same_source
```

rather than treating them as fully independent evidence.

The initial fusion becomes:

```text
FUSION-0001
fusion_result = strong_support
confidence = 0.86
```

and produces:

```text
ASSESSMENT-0001
assessment_state = supported
```

A challenge then questions the evidentiary confidence of the watermark result.

The reproduction does not reproduce that signal.

A new evidence record is added:

```text
EVIDENCE-0005
```

and the second fusion becomes:

```text
FUSION-0002
fusion_result = conflicted
confidence = 0.58
```

The new assessment becomes:

```text
ASSESSMENT-0002
assessment_state = disputed
```

The original assessment remains preserved.

---

# Multi-Auditor Reconciliation

Two auditor opinions examine the current assessment.

```text
OPINION-0001
→ partially_supports

OPINION-0002
→ disputes
```

They agree that:

```text
authenticated API access occurred
```

and that:

```text
the watermark evidence is materially contested
```

They disagree about the remaining evidentiary weight of the original watermark signal.

They also leave unresolved:

```text
whether accessed outputs were incorporated into downstream training
```

The resulting reconciliation is:

```text
RECONCILIATION-0001
reconciliation_state = partial
```

MEDA preserves the disagreement instead of voting it away.

---

# Handoff Boundary

The unresolved audit context is transferred through:

```text
HANDOFF-0001
```

to an external review process.

The handoff package contains the current assessment, opinions, reconciliation, fusion, challenge, reproduction, and revision context.

MEDA does not issue the external decision.

```text
Handoff
≠
Decision
```

---

# Expected-Fail Cases

MEDA v0.5 includes six complete EXPECTED-FAIL cases.

```text
examples/cases/fail/same-auditor-reconciliation/
examples/cases/fail/opinion-assessment-mismatch/
examples/cases/fail/unknown-unresolved-point/
examples/cases/fail/handoff-payload-incomplete/
examples/cases/fail/majority-verdict-applied/
examples/cases/fail/internal-decision-authority/
```

Each case contains the same twenty-one-record structure as the PASS reference case, with one controlled mutation.

---

## Failure Matrix

| Case | Expected Stage | Expected Issue |
|---|---|---|
| `same-auditor-reconciliation` | Graph | `RECONCILIATION_AUDITOR_DIVERSITY_INSUFFICIENT` |
| `opinion-assessment-mismatch` | Graph | `RECONCILIATION_OPINION_ASSESSMENT_MISMATCH` |
| `unknown-unresolved-point` | Graph | `HANDOFF_UNRESOLVED_POINT_UNKNOWN` |
| `handoff-payload-incomplete` | Graph | `HANDOFF_PAYLOAD_INCOMPLETE` |
| `majority-verdict-applied` | Schema | `MAJORITY_VERDICT_SCHEMA_FORBIDDEN` |
| `internal-decision-authority` | Schema | `INTERNAL_DECISION_AUTHORITY_SCHEMA_FORBIDDEN` |

---

# Hard Safety Boundaries

Two v0.5 constraints are enforced directly by schema.

```text
majority_verdict_applied = false
decision_authority = external
```

These are architectural boundaries rather than advisory conventions.

The protocol intentionally makes violations Schema-invalid.

---

# Validation

The active validator is:

```text
scripts/validate_examples.py
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run validation:

```bash
python scripts/validate_examples.py
```

A valid v0.5 repository state concludes with:

```text
[validate-pass]
```

---

# Validation Layers

MEDA validation is layered.

```text
JSON
  ↓
Schema Validation
  ↓
Schema Inventory
  ↓
Case Inventory
  ↓
Record Inventory
  ↓
Graph Integrity
  ↓
Historical Revision Integrity
  ↓
Multi-Auditor Integrity
  ↓
Reconciliation Integrity
  ↓
Handoff Boundary Integrity
```

Therefore:

```text
JSON-valid
≠
Schema-valid
≠
Graph-valid
≠
Protocol-valid
```

---

# Current v0.5 Validation State

MEDA v0.5 has passed the repository validation workflow with:

```text
12 Schemas

1 Canonical PASS Case
21 PASS Reference Records

6 EXPECTED-FAIL Cases
126 EXPECTED-FAIL Records

147 Active Example Records Total
```

Validated areas include:

```text
Schema Validation
Graph Integrity
Assessment History
Challenge / Reproduction
Revision Integrity
Multi-Auditor Identity
Reconciliation
Unresolved Point Preservation
Handoff Payload Integrity
External Decision Authority Boundary
Expected-Fail Classification
```

---

# Specification

The complete protocol specification is available at:

```text
SPEC.md
```

---

# Design Principle

MEDA is designed to preserve structure before judgment.

```text
Observe
≠
Prove

Evidence
≠
Verdict

Fusion
≠
Truth

Assessment
≠
Legal Judgment

Reproduction
≠
Automatic Invalidation

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

The protocol does not force uncertain evidence into artificial certainty.

It preserves enough provenance, disagreement, history, and authority boundaries for downstream systems or human institutions to make informed decisions.

---

# Status

```text
MEDA v0.5.0
Status: FROZEN

Schema Validation: PASS
Graph Validation: PASS
Historical Integrity: PASS
Multi-Auditor Validation: PASS
Reconciliation Validation: PASS
Handoff Boundary Validation: PASS
Expected-Fail Validation: PASS
CI: PASS
```

---

## Multi-Evidence Derivation Audit Protocol

**Audit evidence without automatic verdict.**

**Reconciliation without majority rule.**

**Handoff without authority capture.**
