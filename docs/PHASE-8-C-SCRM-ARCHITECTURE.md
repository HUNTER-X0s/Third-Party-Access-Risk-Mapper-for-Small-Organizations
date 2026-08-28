# Phase 8 C-SCRM Architecture

**Phase:** 8 — Supplier / Vendor Risk Intelligence & Cyber Supply Chain Risk Management  
**Status:** Implemented  
**Alignment:** NIST SP 1326, NIST SP 800-161 Rev. 1, NIST CSF 2.0 (GV.SC)

---

## Architectural Separation: Access Risk vs Supplier Risk

AccessGuard enforces strict separation between two risk dimensions:

| Dimension | Engine | Scope | Never Mixed |
|---|---|---|---|
| **Access Risk** | `RiskEngine v1.5.0` (frozen) | OAuth scopes, data reachability, crown jewel proximity, attack paths | ✅ |
| **Supplier Due Diligence Risk** | `SupplierRiskEngine` (Phase 8) | FOCI, Provenance, Resilience, Cyber Practices posture | ✅ |

> Good supplier assurance **never suppresses** elevated access exposure risk. Both dimensions are independently displayed.

---

## Component Map

```
SupplierRiskEngine (services/supplier_risk_engine.py)
├── calculate_due_diligence_score()     # Deterministic NIST SP 1326 dimension scoring
├── evaluate_supplier_criticality()     # Crown jewel reachability → LOW/MEDIUM/HIGH/CRITICAL
├── calculate_concentration_risk()      # Dependency concentration across assets per vendor
├── simulate_single_supplier_failure()  # Blast radius if vendor becomes unavailable (SIMULATION ONLY)
└── get_supplier_priority_queue()       # Deterministic P0/P1/P2 review queue
```

```
API Endpoints (api/v1/endpoints/vendors.py)
├── GET  /vendors                  # List all suppliers with summary
├── GET  /vendors/priority-queue   # P0/P1/P2 review priority queue
├── GET  /vendors/concentration    # Concentration risk analysis
├── GET  /vendors/{id}             # Full supplier investigation profile
├── POST /vendors/{id}/assess      # Update NIST due diligence (SECURITY_ADMIN / IT_ADMIN only)
└── GET  /vendors/{id}/impact-analysis  # Single-supplier failure simulation

GET  /graph/supply-chain           # Multi-tier supply chain graph (Org → Vendor → Subprocessors)
```

---

## Data Models (models/vendor.py)

| Model | Purpose | Tenant Scoped |
|---|---|---|
| `SupplierProfile` | Org-scoped governance profile per vendor | ✅ `organization_id` |
| `SupplierDueDiligence` | NIST SP 1326 four-dimension assessment record | Via SupplierProfile |
| `SupplierSubprocessor` | Tier 2/3 subprocessor mapping per vendor | Via SupplierProfile |
| `SupplierAssessmentHistory` | Immutable versioned assessment audit trail | Via SupplierProfile |

---

## NIST SP 1326 Dimension Scoring

| Dimension | Max Penalty | Scoring Logic |
|---|---|---|
| FOCI | 25 pts | `ASSESSED_NO_CONCERN`=0, `POTENTIAL_CONCERN`=25, `UNKNOWN`=15, `NOT_ASSESSED`=20 |
| Provenance | 25 pts | `ASSESSED`=0, `CLAIM`=10, `UNKNOWN`=15, `DISPUTED`=25 |
| Resilience | 25 pts | `CURRENT`=0, `ASSESSED`=5, `GAP`=20, `UNKNOWN`=15 (+5 if backup not tested) |
| Foundational Cyber | 25 pts | `STRONG`=0, `PARTIAL`=10, `MINIMAL`=20, `UNKNOWN`=15 (+5 if no MFA) |

**Final score = sum of 4 dimensions, clamped to [5, 95]**

Severity thresholds: `≥80` → Critical, `≥60` → High, `≥30` → Medium, `<30` → Low

---

## Authorization Boundaries

| Endpoint Class | Required Roles |
|---|---|
| Read (`GET /vendors/*`) | SUPER_ADMIN, SECURITY_ADMIN, IT_ADMIN, AUDITOR, APP_OWNER, VIEWER |
| Write (`POST /vendors/{id}/assess`) | SUPER_ADMIN, SECURITY_ADMIN, IT_ADMIN |
| Audit Logged | All POST operations via `AuditEvent` with `SUPPLIER_ASSESSMENT_UPDATED` action |

---

## Data Integrity Rules

- All assessment writes create an **immutable `SupplierAssessmentHistory` version record** before applying changes.
- All supplier data in the demo is labeled `is_synthetic_demo=True` per AGENTS.md Rule 13.
- All external vendor claims stored as `CLAIM`, not `VERIFIED`, unless independently verified evidence exists.
- The term "aligned with NIST SP 1326" is used throughout; no compliance or certification claims are made.
