# Multi-Evidence Derivation Audit Protocol Specification

**Protocol Name:** Multi-Evidence Derivation Audit Protocol  
**Abbreviation:** MEDA  
**Version:** 0.5.0  
**Status:** FROZEN  
**Specification Layer:** Audit / Evidence / Assessment / Reconciliation / Handoff  
**Legal Effect:** None by default

---

## 1. Overview

The Multi-Evidence Derivation Audit Protocol (MEDA) is a protocol for collecting, relating, fusing, assessing, challenging, reproducing, revising, reconciling, and handing off multi-source evidence concerning possible model derivation.

MEDA is designed around one central principle:

> **Audit evidence is not a verdict.**

A watermark signal, API trace, signed receipt, behavioral similarity result, reproduction result, zero-knowledge attestation, auditor opinion, or reconciliation record may contribute to an evidentiary assessment.

None of these records, individually or collectively, automatically establish:

- model derivation as legal fact,
- copyright infringement,
- legal liability,
- license creation,
- royalty entitlement,
- royalty allocation,
- settlement obligation.

MEDA therefore separates:

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

The MEDA boundary ends at **audit-context handoff**.

Final legal, policy, royalty, governance, or settlement decisions remain outside MEDA.

---

# 2. Purpose

MEDA exists to make derivation-related audit processes:

- explicit,
- traceable,
- reproducible,
- revision-safe,
- multi-auditor aware,
- resistant to evidence double counting,
- capable of preserving disagreement,
- capable of transferring unresolved audit context without converting it into an automatic verdict.

The protocol is intended to support systems in which model lineage or derivation cannot be reliably established from a single signal.

Instead of asking:

> “Did one detector say derivation occurred?”

MEDA asks:

> “What evidence exists, how are those evidence records related, how were they fused, what assessment was produced, what challenges were raised, what could be reproduced, how did the assessment change, where do auditors agree or disagree, and what context must be handed to an external authority?”

---

# 3. Non-Goals

MEDA is not:

- a copyright court,
- a royalty calculator,
- a settlement engine,
- a licensing authority,
- a majority-voting tribunal,
- a universal derivation detector,
- a universal evidence-weighting system,
- a causal inference oracle,
- a legal-liability engine.

MEDA MUST NOT autonomously create, modify, or extinguish rights or obligations.

---

# 4. Position in a Larger Value Flow

MEDA may operate inside a larger architecture such as:

```text
Origin
  ↓
Trace
  ↓
Evidence
  ↓
Assessment
  ↓
Policy
  ↓
Contribution
  ↓
Allocation
  ↓
Settlement
```

MEDA primarily occupies the following region:

```text
Trace
  ↓
Evidence
  ↓
Assessment
  ↓
Audit Reconciliation
  ↓
Decision Handoff
```

MEDA does not itself perform downstream allocation or settlement.

---

# 5. Core Distinctions

MEDA preserves several strict semantic boundaries.

## 5.1 Evidence ≠ Verdict

A valid evidence record only establishes that an observation or artifact was recorded under a declared method and context.

For example:

```text
watermark z-score > threshold
```

may produce:

```text
watermark evidence = detected
```

It MUST NOT automatically produce:

```text
derivation = true
```

or:

```text
royalty entitlement = true
```

---

## 5.2 Access ≠ Training Incorporation

A signed receipt or API trace may establish that authenticated access occurred.

It does not establish that accessed outputs entered downstream training.

Therefore:

```text
Authenticated Access
≠
Training Incorporation
≠
Derivation
```

---

## 5.3 Similarity ≠ Causal Derivation

Behavioral similarity may support a hypothesis.

Similarity alone does not uniquely identify causal lineage.

---

## 5.4 Reproduction Failure ≠ Automatic Invalidation

A failed reproduction may become counter-evidence.

It does not automatically erase or invalidate the original evidence.

Therefore:

```text
Original Evidence
+
Failed Reproduction
→
Conflicted Evidence State
```

rather than:

```text
Failed Reproduction
→
Original Evidence Deleted
```

---

## 5.5 Zero-Knowledge Proof ≠ Derivation Verdict

A Zero-Knowledge Audit Attestation proves only the declared predicate over committed or secret inputs.

It does not prove:

- causal derivation,
- copyright infringement,
- legal liability,
- royalty entitlement.

A MEDA ZK record is therefore called:

> **Zero-Knowledge Audit Attestation**

rather than a derivation proof.

---

## 5.6 Auditor Opinion ≠ Verdict

An auditor opinion records an auditor's position and basis.

It does not create a binding decision.

---

## 5.7 Reconciliation ≠ Majority Vote

Reconciliation identifies:

- agreed points,
- disputed points,
- unresolved points.

It MUST NOT turn numerical majority into a protocol verdict.

---

## 5.8 Handoff ≠ Decision

A handoff transfers audit context to another authority.

Even:

```text
handoff_status = accepted
```

does not mean:

```text
external decision issued
```

A package may be accepted while:

```text
external_decision_ref = null
```

---

# 6. Protocol Evolution

MEDA evolved through five protocol stages.

```text
v0.1
Evidence
→ Assessment
→ Attestation

v0.2
Evidence
→ Relationship
→ Fusion
→ Assessment

v0.3
Audit Case Graph
→ Cross-Record Integrity

v0.4
Challenge
→ Reproduction
→ Revision
→ Historical Integrity

v0.5
Multi-Auditor Opinion
→ Reconciliation
→ Decision Handoff
```

Each version extends the audit graph without collapsing earlier semantic boundaries.

---

# 7. Protocol Invariants

MEDA v0.5 defines thirty-three protocol invariants.

---

## A1 — evidence_not_verdict

Evidence records MUST NOT be treated as automatic verdicts.

---

## A2 — no_automatic_right_creation

Audit records MUST NOT autonomously create legal, licensing, royalty, allocation, or settlement rights.

---

## A3 — reproducible_assessment

Assessment outputs MUST preserve sufficient references and basis information to allow later review.

---

## A4 — attestation_scope

An attestation MUST explicitly define what predicate or audit context it proves.

---

## A5 — dispute_separation

Disputes MUST remain distinguishable from ordinary evidence and assessment records.

---

## A6 — evidence_provenance

Evidence MUST preserve origin, collection context, and integrity-related metadata.

---

## A7 — maturity_visibility

Evidence maturity MUST remain explicit.

Supported maturity states include:

```text
established
emerging
experimental
```

---

## A8 — no_evidence_double_counting

Evidence records derived from the same underlying source MUST NOT automatically be counted as independent evidence.

---

## A9 — counter_evidence_preservation

Counter-evidence MUST remain explicitly represented.

It MUST NOT be silently discarded because supporting evidence exists.

---

## A10 — fusion_explainability

Fusion results MUST expose the evidence and relationships used to produce the result.

---

## A11 — no_universal_weight

MEDA MUST NOT define one universal evidence-weighting formula for every implementation or domain.

---

## A12 — case_coherence

Records participating in the same audit graph MUST belong to the same audit case.

---

## A13 — referential_integrity

Declared protocol references MUST resolve to known records when required by the protocol.

---

## A14 — origin_derivative_consistency

Records within one audit case MUST preserve consistent origin and derivative identities.

---

## A15 — subset_integrity

Referenced supporting, counter, redundant, effective, or related evidence subsets MUST remain valid subsets of the relevant parent record.

---

## A16 — no_cross_case_mixing

Records from different audit cases MUST NOT be silently combined into one graph.

---

## A17 — current_assessment_integrity

The current assessment reference MUST resolve to a valid assessment registered in the case.

---

## A18 — graph_validation_required

Schema validity alone is insufficient.

A protocol case MUST also satisfy graph-level integrity.

Therefore:

```text
Schema-valid
≠
Protocol-consistent
```

---

## A19 — no_destructive_revision

A revised assessment MUST NOT delete or overwrite the prior assessment.

---

## A20 — challenge_traceability

Challenges MUST identify the record being challenged and preserve their basis.

---

## A21 — reproduction_separation

A reproduction record MUST remain distinct from both the original evidence and the resulting reproduction-output evidence.

---

## A22 — revision_provenance

Assessment revisions MUST preserve:

- prior assessment,
- revised assessment,
- revision trigger,
- evidence changes,
- fusion context.

---

## A23 — unresolved_dispute_preservation

Unresolved disputes MUST remain visible after reassessment or revision.

---

## A24 — reproduction_not_verdict

A reproduction result MUST NOT independently become a final derivation verdict.

---

## A25 — revision_chain_integrity

Assessment revision chains MUST remain resolvable and free from invalid cycles or broken predecessor relationships.

---

## A26 — auditor_identity_visibility

Auditor identity or auditor reference MUST remain visible in auditor opinions.

---

## A27 — opinion_not_verdict

An auditor opinion MUST NOT be treated as a final protocol verdict.

---

## A28 — no_majority_verdict

MEDA reconciliation MUST NOT convert auditor majority into an automatic verdict.

The protocol requires:

```text
majority_verdict_applied = false
```

---

## A29 — disagreement_preservation

Auditor disagreement MUST remain represented rather than being flattened into one consensus value.

---

## A30 — reconciliation_traceability

A reconciliation record MUST retain references to the opinions and assessments it reconciles.

---

## A31 — unresolved_point_preservation

Unresolved reconciliation points MUST remain explicitly identifiable and transferable.

---

## A32 — handoff_boundary

MEDA handoff MUST transfer audit context without assuming external decision authority.

---

## A33 — no_autonomous_right_creation

Multi-auditor reconciliation or handoff MUST NOT autonomously create:

- derivation verdicts,
- copyright findings,
- legal liability,
- licenses,
- royalty entitlement,
- royalty allocation,
- settlement instructions.

---

# 8. Record Model

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

# 9. Audit Case Record

The audit case record acts as the graph root.

It registers the records belonging to a case.

Core fields include:

```text
case_id
origin_ref
derivative_ref
case_state

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

current_assessment_ref
case_policy_ref
protocol_version
created_at
updated_at
```

Supported case states include:

```text
open
collecting_evidence
fusion_ready
assessed
under_challenge
reproducing
revision_pending
disputed
reconciling
handoff_ready
handed_off
closed
```

A case in:

```text
handed_off
```

MUST contain the required reconciliation and handoff structure.

---

# 10. Audit Evidence Record

An audit evidence record represents one evidentiary observation.

Supported evidence classes include:

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

An evidence record may include:

```text
evidence_id
evidence_type
origin_ref
derivative_ref
method
maturity
observation
statistic
threshold
calibration_ref
source_event_ref
source_artifact_refs
assumptions
limitations
artifact_refs
collected_at
collected_by
integrity
challenge_status
```

Evidence MUST remain an evidentiary object rather than a final determination.

---

# 11. Evidence Relationship Record

The relationship record expresses structural dependence or evidentiary interaction between evidence records.

Supported dependency types include:

```text
independent
partially_dependent
same_source
unknown
```

Supported evidentiary effects include:

```text
corroborating
conflicting
neutral
unknown
```

These two concepts MUST remain separate.

For example:

```text
dependency_type = same_source
evidentiary_effect = corroborating
```

means:

> two records corroborate the same hypothesis but arise from the same underlying source and therefore must not be treated as fully independent.

---

# 12. Evidence Fusion Record

A fusion record combines evidence while preserving evidence relationships and counter-evidence.

Important fields include:

```text
evidence_refs
relationship_refs
supporting_evidence_refs
counter_evidence_refs
redundant_evidence_refs
effective_evidence_refs
evidence_diversity
fusion_result
confidence
basis
uncertainty_factors
limitations
fusion_policy_ref
```

Supported fusion results include:

```text
insufficient
weak_support
moderate_support
strong_support
conflicted
```

The protocol principle is:

```text
Evidence Count
≠
Evidence Strength
```

A large number of same-source records MUST NOT automatically increase evidence diversity.

---

# 13. Derivation Assessment Record

An assessment records the protocol-level interpretation of the available fusion and evidence state.

Supported assessment states include:

```text
insufficient
suspected
supported
protocol_verified
disputed
```

These are audit states.

They are not legal judgments.

Legal-effect descriptors include:

```text
none
policy_dependent
human_review_required
externally_determined
```

The assessment record may include:

```text
assessment_id
evidence_refs
fusion_refs
assessment_state
confidence
assessment_basis
conflicting_evidence_refs
limitations
assessment_policy_ref
legal_effect
protocol_version
created_at
```

---

# 14. Zero-Knowledge Audit Attestation

The ZK attestation records verification of a declared audit predicate.

Supported audit contexts may include:

```text
evidence
relationship
fusion
assessment
challenge
reproduction
revision
opinion
reconciliation
handoff
```

A ZK attestation may prove:

```text
"The committed records were processed under predicate P."
```

It MUST NOT be interpreted as:

```text
"The derivative model was legally derived from the origin model."
```

Verification statuses include:

```text
verified
failed
not_verified
```

Every attestation MUST include a scope note.

---

# 15. Audit Challenge Record

A challenge records a formal objection to an existing audit record.

Possible target record types include:

```text
evidence
relationship
fusion
assessment
attestation
opinion
reconciliation
handoff
```

Challenge scope may include matters such as:

```text
method
confidence
evidence_quality
evidence_dependency
auditor_independence
opinion_basis
reconciliation
handoff_scope
authority_boundary
```

A challenge MUST identify:

```text
target_record_type
target_record_ref
challenge_basis
requested_action
challenge_status
```

A challenge may trigger further audit action but does not itself invalidate the target.

---

# 16. Reproduction Record

A reproduction record represents an attempt to independently or operationally repeat a prior audit procedure.

Typical targets include:

```text
evidence
relationship
fusion
assessment
attestation
```

A reproduction may produce new evidence through:

```text
produced_evidence_refs
```

The reproduction itself remains distinct from its output evidence.

For example:

```text
REPRODUCTION-0001
  ↓
produces
  ↓
EVIDENCE-0005
```

The reproduction result may be:

```text
reproduced
partially_reproduced
not_reproduced
inconclusive
```

A failed reproduction becomes evidence relevant to reassessment.

It is not an automatic invalidation command.

---

# 17. Assessment Revision Record

The revision record connects historical assessments.

The intended structure is:

```text
ASSESSMENT-0001
      ↓
CHALLENGE-0001
      ↓
REPRODUCTION-0001
      ↓
EVIDENCE-0005
      ↓
FUSION-0002
      ↓
ASSESSMENT-0002
      ↓
REVISION-0001
```

A revision record MUST preserve:

```text
prior_assessment_ref
revised_assessment_ref
revision_trigger
trigger_refs
challenge_refs
reproduction_refs
evidence_added_refs
evidence_removed_refs
fusion_refs
revision_basis
change_summary
revision_state
```

MEDA uses immutable assessment history.

Therefore:

```text
Old Assessment
→ preserved

New Assessment
→ appended

Revision
→ links them
```

---

# 18. Auditor Opinion Record

An auditor opinion records an auditor-specific interpretation of a current assessment.

Core fields include:

```text
opinion_id
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
created_at
```

Supported auditor types include:

```text
human
organization
automated_system
hybrid
other
```

Supported positions include:

```text
supports
partially_supports
disputes
insufficient_basis
abstains
```

Supported independence states include:

```text
independent
partially_independent
not_independent
unknown
```

If an auditor is:

```text
partially_independent
```

or:

```text
not_independent
```

the dependency must be made visible.

The protocol does not treat auditor confidence as a final truth score.

---

# 19. Audit Reconciliation Record

The reconciliation record compares multiple auditor opinions without converting them into a majority verdict.

A valid reconciliation requires at least two opinion references.

The reconciliation structure contains:

```text
assessment_refs
opinion_refs
evidence_refs
fusion_refs
challenge_refs
reproduction_refs

reconciliation_method
method_ref

majority_verdict_applied

agreed_points
disputed_points
unresolved_points

reconciliation_state
basis
limitations
effect_scope
created_at
```

Supported reconciliation methods include:

```text
comparative_review
independent_panel
algorithmic_summary
hybrid
other
```

Supported reconciliation states include:

```text
complete
partial
blocked
```

The protocol requires:

```text
majority_verdict_applied = false
```

This is a hard safety boundary.

---

## 19.1 Agreed Points

An agreed point represents a statement jointly supported by multiple opinions.

It may reference:

```text
supporting_opinion_refs
evidence_refs
assessment_refs
```

Agreement does not convert the statement into a legal verdict.

---

## 19.2 Disputed Points

A disputed point preserves competing positions.

For example:

```text
Point:
Residual weight of original watermark evidence

Position A:
retain limited evidentiary weight

Position B:
treat the watermark component as insufficiently stable
```

MEDA preserves both positions.

---

## 19.3 Unresolved Points

An unresolved point explicitly records a question that the available audit graph cannot resolve.

Example:

```text
Whether authenticated API outputs were incorporated
into downstream model training.
```

This distinction is essential because:

```text
Access
≠
Training Incorporation
```

---

# 20. Audit Handoff Record

The audit handoff record transfers MEDA audit context to an authority outside MEDA.

Core fields include:

```text
assessment_refs
opinion_refs
reconciliation_refs
challenge_refs
reproduction_refs
revision_refs

handoff_target
handoff_scope
payload_refs
unresolved_point_refs

handoff_reason
limitations
excluded_decisions

handoff_status
decision_authority
handoff_effect
legal_effect

external_process_ref
external_decision_ref
response_note

created_at
transmitted_at
responded_at
```

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

Supported handoff scopes include:

```text
audit_context
evidence_review
assessment_review
dispute_review
policy_review
legal_review
royalty_eligibility_review
governance_review
other
```

Supported handoff statuses include:

```text
prepared
transmitted
accepted
rejected
withdrawn
```

The handoff MUST preserve:

```text
decision_authority = external
handoff_effect = transfer_only
legal_effect = none
```

---

# 21. Explicitly Excluded Decisions

A MEDA handoff may explicitly declare that it does not perform the following decisions:

```text
derivation_verdict
copyright_infringement
legal_liability
license_creation
royalty_entitlement
royalty_allocation
settlement_instruction
```

These exclusions protect the boundary between audit evidence and external authority.

---

# 22. Reference Case

The canonical v0.5 reference case is located at:

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

The reference case demonstrates the full v0.5 lifecycle.

---

# 23. Reference Case Flow

The canonical case begins with four initial evidence records.

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

`EVIDENCE-0002` and `EVIDENCE-0003` come from the same authenticated event.

Therefore:

```text
REL-0001
dependency_type = same_source
```

prevents them from being treated as two fully independent channels.

The first fusion produces:

```text
FUSION-0001
fusion_result = strong_support
confidence = 0.86
```

This leads to:

```text
ASSESSMENT-0001
assessment_state = supported
```

A challenge is then raised concerning the evidentiary confidence of the watermark evidence.

```text
CHALLENGE-0001
```

The challenge triggers:

```text
REPRODUCTION-0001
```

The reproduction does not reproduce the original watermark signal.

It produces:

```text
EVIDENCE-0005
```

which is preserved as counter-evidence.

A conflicting relationship is recorded:

```text
REL-0003
EVIDENCE-0001
↔
EVIDENCE-0005
```

The second fusion becomes:

```text
FUSION-0002
fusion_result = conflicted
confidence = 0.58
```

A new assessment is created:

```text
ASSESSMENT-0002
assessment_state = disputed
```

The old assessment is not deleted.

Instead:

```text
REVISION-0001
```

connects the historical assessments.

---

# 24. Multi-Auditor Reference Flow

Two independent auditor opinions are created.

```text
OPINION-0001
→ partially_supports

OPINION-0002
→ disputes
```

Both agree that:

```text
authenticated API access occurred
```

and:

```text
watermark evidence is materially contested
```

They disagree about the residual weight of the original watermark evidence.

Both leave unresolved:

```text
whether accessed outputs entered downstream training
```

The reconciliation record therefore becomes:

```text
RECONCILIATION-0001
reconciliation_state = partial
```

It preserves:

```text
agreed_points
disputed_points
unresolved_points
```

without majority verdict.

---

# 25. Handoff Reference Flow

Because the current assessment remains disputed and one causal question remains unresolved, MEDA produces:

```text
HANDOFF-0001
```

The handoff target is an external human review process.

The package includes:

```text
ASSESSMENT-0002
OPINION-0001
OPINION-0002
RECONCILIATION-0001
FUSION-0002
CHALLENGE-0001
REPRODUCTION-0001
REVISION-0001
```

The handoff preserves the unresolved point.

The external process accepts the package.

However:

```text
external_decision_ref = null
```

This demonstrates:

```text
Package Accepted
≠
Decision Issued
```

---

# 26. Validation Model

MEDA validation operates at multiple layers.

```text
JSON
  ↓
Schema Validation
  ↓
Record Inventory Validation
  ↓
Graph Validation
  ↓
Historical / Revision Validation
  ↓
Multi-Auditor Validation
  ↓
Reconciliation Validation
  ↓
Handoff Boundary Validation
```

A record may be valid JSON and valid against its schema while still violating the protocol graph.

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

# 27. Validator

The active validator is:

```text
scripts/validate_examples.py
```

The validator checks the active v0.5 schema and case inventory.

The active schema inventory contains twelve schemas.

The canonical PASS case contains twenty-one records.

Each active EXPECTED-FAIL case also contains the complete twenty-one-record graph, with one controlled mutation designed to trigger a specific protocol failure.

---

# 28. Expected-Fail Cases

The active v0.5 expected-fail cases are:

```text
examples/cases/fail/same-auditor-reconciliation/
examples/cases/fail/opinion-assessment-mismatch/
examples/cases/fail/unknown-unresolved-point/
examples/cases/fail/handoff-payload-incomplete/
examples/cases/fail/majority-verdict-applied/
examples/cases/fail/internal-decision-authority/
```

Each case contains twenty-one records.

Only the intended mutation differs from the reference case.

---

## 28.1 Same Auditor Reconciliation

Path:

```text
examples/cases/fail/same-auditor-reconciliation/
```

Controlled failure:

Two auditor opinions resolve to the same `auditor_ref`.

Expected graph issue:

```text
RECONCILIATION_AUDITOR_DIVERSITY_INSUFFICIENT
```

Purpose:

A reconciliation involving multiple opinion records must not pretend to represent multiple independent auditors when the auditor identity is the same.

---

## 28.2 Opinion Assessment Mismatch

Path:

```text
examples/cases/fail/opinion-assessment-mismatch/
```

Controlled failure:

One opinion concerns:

```text
ASSESSMENT-0001
```

while the reconciliation declares only:

```text
ASSESSMENT-0002
```

Expected graph issue:

```text
RECONCILIATION_OPINION_ASSESSMENT_MISMATCH
```

Purpose:

A reconciliation must not silently reconcile opinions concerning different assessment contexts.

---

## 28.3 Unknown Unresolved Point

Path:

```text
examples/cases/fail/unknown-unresolved-point/
```

Controlled failure:

The handoff references a reconciliation unresolved point that does not exist.

Expected graph issue:

```text
HANDOFF_UNRESOLVED_POINT_UNKNOWN
```

Purpose:

A handoff may transfer only explicitly registered unresolved reconciliation points.

---

## 28.4 Incomplete Handoff Payload

Path:

```text
examples/cases/fail/handoff-payload-incomplete/
```

Controlled failure:

The handoff declares a linked reconciliation record but omits that record from `payload_refs`.

Expected graph issue:

```text
HANDOFF_PAYLOAD_INCOMPLETE
```

Purpose:

A handoff must not claim to transfer audit context while omitting a required linked record from the transferred package.

---

## 28.5 Majority Verdict Applied

Path:

```text
examples/cases/fail/majority-verdict-applied/
```

Controlled failure:

```text
majority_verdict_applied = true
```

Expected schema issue:

```text
MAJORITY_VERDICT_SCHEMA_FORBIDDEN
```

Purpose:

MEDA reconciliation is not a majority-voting verdict mechanism.

This boundary is enforced directly at schema level.

---

## 28.6 Internal Decision Authority

Path:

```text
examples/cases/fail/internal-decision-authority/
```

Controlled failure:

```text
decision_authority = internal
```

Expected schema issue:

```text
INTERNAL_DECISION_AUTHORITY_SCHEMA_FORBIDDEN
```

Purpose:

MEDA may prepare and transfer audit context.

MEDA MUST NOT assume downstream legal, policy, royalty, governance, or settlement authority.

---

# 29. Hard Safety Boundaries

Two v0.5 boundaries are intentionally enforced by JSON Schema rather than graph-only validation.

```text
majority_verdict_applied = false
decision_authority = external
```

These are not merely preferred practices.

They define architectural boundaries of MEDA.

Therefore invalid values MUST remain Schema-invalid.

---

# 30. Auditor Independence

MEDA requires auditor identity visibility but does not assume that every auditor is fully independent.

Independence must be declared.

```text
independent
partially_independent
not_independent
unknown
```

A reconciliation may reason about multiple opinions only when their identity and dependency context remain visible.

Multiple opinion records do not necessarily imply multiple independent epistemic sources.

Therefore:

```text
Opinion Count
≠
Auditor Diversity
```

---

# 31. Reconciliation Semantics

MEDA reconciliation is descriptive and structural.

It may state:

```text
Auditors agree on X.
Auditors disagree on Y.
Z remains unresolved.
```

It MUST NOT transform this into:

```text
2 of 3 auditors voted for derivation
therefore derivation = true
```

MEDA intentionally preserves epistemic plurality where the evidence remains contested.

---

# 32. Decision Boundary

The final MEDA structure is:

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
══════════════════════════════
        MEDA Boundary
══════════════════════════════
          ↓
External Human / Policy /
Legal / Royalty / Governance
Decision Authority
```

The boundary is intentional.

MEDA answers:

> “What audit context should be carried forward?”

MEDA does not answer:

> “What legally binding outcome must occur?”

---

# 33. Relationship to Royalty Systems

MEDA can provide upstream evidence to a royalty or attribution system.

However:

```text
MEDA Assessment
≠
Royalty Entitlement
```

and:

```text
MEDA Handoff
≠
Settlement Instruction
```

A downstream system may consume MEDA records as one input among other legal, contractual, policy, attribution, and entitlement records.

That downstream process remains outside MEDA.

---

# 34. Implementation Guidance

Implementations SHOULD preserve:

- immutable record identifiers,
- append-only assessment history,
- evidence provenance,
- dependency relationships,
- counter-evidence,
- auditor identity,
- auditor independence status,
- reconciliation disagreements,
- unresolved points,
- handoff payload completeness,
- external decision authority.

Implementations SHOULD NOT silently collapse multiple records into one untraceable score.

Implementations SHOULD expose enough structure for independent graph validation.

---

# 35. Conformance

A MEDA v0.5 conforming implementation SHOULD satisfy:

```text
Schema Conformance
+
Record Inventory Integrity
+
Reference Integrity
+
Case Coherence
+
Origin / Derivative Coherence
+
Fusion Subset Integrity
+
Historical Revision Integrity
+
Auditor Identity Integrity
+
Reconciliation Integrity
+
Handoff Boundary Integrity
```

A system is not protocol-conformant merely because its individual JSON documents pass schema validation.

---

# 36. Canonical Validation Command

The canonical local validation command is:

```bash
python scripts/validate_examples.py
```

The active CI configuration is expected to execute the same validator.

A successful v0.5 validation must conclude with:

```text
[validate-pass]
```

---

# 37. v0.5 Completion State

MEDA v0.5 establishes a full audit lifecycle from raw evidence to external-decision handoff.

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
Multiple Auditor Opinions
  ↓
Reconciliation
  ↓
Handoff
  ↓
External Decision Authority
```

The protocol now preserves not only evidence and assessment, but also:

- evidence dependency,
- counter-evidence,
- historical revision,
- reproduction,
- auditor plurality,
- disagreement,
- unresolved questions,
- decision-authority boundaries.

---

# 38. Final Protocol Principle

MEDA v0.5 is built around the following sequence:

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

Audit
≠
Royalty Entitlement

Royalty Entitlement
≠
Settlement
```

The purpose of MEDA is not to force uncertain evidence into certainty.

Its purpose is to preserve enough structure that uncertainty, disagreement, revision, provenance, and authority boundaries remain inspectable.

---

## Status

```text
MEDA v0.5.0
Status: FROZEN

12 Schemas
1 Canonical PASS Case
21 Reference Records
6 EXPECTED-FAIL Cases
126 EXPECTED-FAIL Records

Schema Validation: PASS
Graph Validation: PASS
Historical Integrity Validation: PASS
Multi-Auditor Validation: PASS
Reconciliation Validation: PASS
Handoff Boundary Validation: PASS
CI Validation: PASS
```

---

**Multi-Evidence Derivation Audit Protocol v0.5.0**  
**Audit evidence without automatic verdict.**  
**Reconciliation without majority rule.**  
**Handoff without authority capture.**
