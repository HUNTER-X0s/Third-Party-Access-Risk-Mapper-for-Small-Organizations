# EVIDENCE & PROVENANCE DOMAIN MODEL
# AccessGuard: Formal Evidence Chain & Audit Verification Architecture

**Document Type:** Domain Model Specification  
**Version:** 1.0  
**Date:** 2026-08-13  
**Status:** Approved Security Architecture  

---

## 1. Concept Statement

In AccessGuard, **no high-confidence security finding or risk score may exist without underlying immutable evidence**. 

Security auditors and CISOs reject "black box" claims. A finding that flags an application for excessive permissions must explicitly trace to:
1. The exact raw response received from the third-party OAuth provider
2. The collection timestamp and connector ID
3. The exact normalization rule applied
4. The policy or least-privilege rule violated

---

## 2. The Evidence Provenance Chain

Every finding follows a strict 7-stage deterministic provenance chain:

```
┌─────────────────┐
│  EVIDENCE SOURCE│ (e.g. Google Workspace Admin SDK API)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RAW EVIDENCE  │ (Raw JSON scope payload + HTTP response headers)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ NORMALIZATION   │ (ProviderScope map -> CanonicalPermission)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RULE EVALUATION │ (Comparison against BusinessPurpose requirement)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RISK FINDING   │ (Deterministic score + severity calculation)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ REMEDIATION SPEC│ (Simulated or recommended action)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  VERIFICATION   │ (Post-remediation state resync & hash verification)
└─────────────────┘
```

---

## 3. Domain Entities

### 3.1 `EvidenceSource`
Represents the origin of data.

```python
class EvidenceSource(Base):
    id: UUID
    organization_id: UUID
    connector_type: Enum  # GOOGLE_WORKSPACE, MS_365, MANUAL_AUDIT, DEMO_SEED
    connector_instance_id: UUID
    api_endpoint: str
    authenticated_identity: str # Service Account or Admin User email
    trust_level: Enum # VERIFIED_API, UNVERIFIED_IMPORT, MANUAL_ENTRY
    created_at: datetime
```

### 3.2 `RawEvidence`
Immutable storage of un-tampered raw payloads.

```python
class RawEvidence(Base):
    id: UUID
    organization_id: UUID
    evidence_source_id: UUID (FK -> EvidenceSource)
    payload_hash_sha256: str # SHA-256 hash of raw_payload to guarantee immutability
    raw_payload_json: JSONB  # Raw API response body
    collected_at: datetime
    data_freshness_status: Enum # CONFIRMED, STALE, CONFLICTING
```

### 3.3 `EvidenceTransformation`
Records how raw provider scopes were converted into AccessGuard normalized permissions.

```python
class EvidenceTransformation(Base):
    id: UUID
    raw_evidence_id: UUID (FK -> RawEvidence)
    normalization_rule_version: str # e.g. "v1.4.0"
    raw_scope_string: str           # "https://www.googleapis.com/auth/gmail.readonly"
    canonical_permission_id: UUID   # Maps to Canonical Permission "read_email"
    transformation_status: Enum     # EXACT_MATCH, PATTERN_MATCH, UNKNOWN_FALLBACK
```

### 3.4 `FindingEvidenceLink`
Joins a `RiskFinding` or `PermissionGrant` to its supporting evidence chain.

```python
class FindingEvidenceLink(Base):
    id: UUID
    finding_id: UUID (FK -> RiskFinding)
    raw_evidence_id: UUID (FK -> RawEvidence)
    transformation_id: UUID (FK -> EvidenceTransformation)
    confidence_score: float # 0.0 to 1.0 based on source trust & freshness
```

---

## 4. UI Provenance Display Specification

When a user clicks on a `RiskFinding` in the inspection drawer, the UI renders the **Provenance Inspector Panel**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ PROVENANCE & EVIDENCE INSPECTOR                                        │
├────────────────────────────────────────────────────────────────────────┤
│ Finding ID: FND-8942                                                   │
│ Finding Type: EXCESSIVE_PERMISSION_GRANTED                             │
│ Risk Contribution: +35.0 to App Risk Score                             │
├────────────────────────────────────────────────────────────────────────┤
│ 1. SOURCE OBSERVATION                                                  │
│    Connector: Google Workspace Admin SDK (ID: conn-gw-01)              │
│    Timestamp: 2026-08-13 14:22:05 UTC (Freshness: CONFIRMED - 18m ago) │
│    Raw Payload SHA256: 8f9a2b...e411                                 │
│                                                                        │
│ 2. RAW SCOPE                                                           │
│    `https://www.googleapis.com/auth/gmail.readonly`                    │
│                                                                        │
│ 3. NORMALIZATION RULE (Rule Engine v1.4)                               │
│    Mapped to -> Canonical Permission: `read_email` (Severity: HIGH)    │
│                                                                        │
│ 4. BUSINESS PURPOSE CONFLICT                                           │
│    Declared Purpose: "Marketing Newsletter Sender"                     │
│    Required Permission: `send_email`                                   │
│    Excess Scope Identified: `read_email` is NOT required for sending.  │
└────────────────────────────────────────────────────────────────────────┘
```

---

*Evidence Provenance Model v1.0 — Approved Domain Architecture.*
