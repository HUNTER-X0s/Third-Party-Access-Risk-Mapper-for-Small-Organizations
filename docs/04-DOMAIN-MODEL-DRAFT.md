# 04 — Domain Model Specification (Hardened)
# AccessGuard: Security Data Model Concepts

**Document Type:** Domain Model Specification  
**Version:** 1.5  
**Date:** 2026-08-13  
**Status:** Hardened Architectural Specification  

---

## Design Principles

1. **Everything is scoped to an Organization** — Strict tenant isolation.
2. **Relationships & Evidence are first-class** — Every risk finding links to immutable `RawEvidence` with SHA-256 integrity hashes.
3. **Structured Validation over Free Text** — Business purposes rely on a curated `BusinessPurposeCatalog`.
4. **Data State Transparency** — All findings track explicit data freshness state (`CONFIRMED`, `INFERRED`, `UNKNOWN`, `STALE`, `CONFLICTING`).
5. **Deterministic Auditability** — Findings record `risk_engine_version` and timestamped provenance chains.

---

## Core Domain Entities (28 Entities)

### Tenant & Core Governance Entities
1. **Organization**: Root multi-tenant entity (`id`, `name`, `domain`, `settings`, `security_posture_score`).
2. **User**: Account entity (`id`, `organization_id`, `email`, `role`, `mfa_enabled`).
3. **Role**: RBAC definition (`owner`, `admin`, `analyst`, `viewer`).

### Application & Vendor Inventory Entities
4. **Application**: Shared canonical app template (`id`, `canonical_name`, `vendor_id`, `category`).
5. **ApplicationInstance**: Deployed integration (`id`, `organization_id`, `status`, `authorized_by_user_id`, `risk_score`, `data_state`).
6. **Vendor**: App publisher (`id`, `name`, `soc2_status`, `iso27001_certified`, `known_breach_history`, `trust_score`).
7. **VendorAssessment**: Periodic review (`id`, `vendor_id`, `assessed_by_user_id`, `risk_rating`).

### Permission & Scope Engine Entities
8. **Permission**: Canonical permission definition (`id`, `canonical_name`, `severity_level`, `category`).
9. **ProviderScope**: Raw scope string (`id`, `provider_type`, `raw_scope`, `permission_id`).
10. **PermissionGrant**: Granted scope on instance (`id`, `application_instance_id`, `permission_id`, `is_excess`, `data_state`).

### Structured Business Purpose Entities (Phase 0.5 Hardened)
11. **BusinessPurposeCatalog**: Curated purpose template (`id`, `purpose_code`, `display_name`, `category`, `version`).
12. **BusinessPurposeRequirement**: Mandatory/optional scopes for purpose (`id`, `purpose_id`, `permission_id`, `requirement_type`).
13. **ApplicationInstancePurpose**: Binding of app to purpose (`id`, `application_instance_id`, `purpose_id`, `approved_by_user_id`).

### Data Asset & Graph Entities
14. **DataClassification**: Taxonomy (`id`, `name`, `sensitivity_level` 1–5).
15. **DataAsset**: Named asset (`id`, `organization_id`, `name`, `classification_id`, `system_of_record`).
16. **AccessRelationship**: Graph edge (`id`, `application_instance_id`, `data_asset_id`, `access_type`).

### Evidence & Provenance Entities (Phase 0.5 Hardened)
17. **EvidenceSource**: Connector origin (`id`, `connector_type`, `api_endpoint`, `trust_level`).
18. **RawEvidence**: Un-tampered API response (`id`, `payload_hash_sha256`, `raw_payload_json`, `collected_at`, `data_freshness_status`).
19. **EvidenceTransformation**: Scope mapping record (`id`, `raw_evidence_id`, `raw_scope_string`, `canonical_permission_id`, `normalization_rule_version`).
20. **FindingEvidenceLink**: Finding-to-evidence join (`id`, `finding_id`, `raw_evidence_id`, `transformation_id`, `confidence_score`).

### Risk & Policy Engine Entities
21. **RiskFinding**: Actionable finding (`id`, `application_instance_id`, `finding_type`, `severity`, `risk_score_contribution`, `risk_engine_version`, `lifecycle_state`).
22. **RiskFactor**: Factor breakdown (`id`, `name`, `category`, `weight`, `current_value`, `normalized_value`).
23. **Policy**: Org policy rule (`id`, `name`, `rule_type`, `rule_definition`, `severity_if_violated`).
24. **PolicyViolation**: Detected violation (`id`, `policy_id`, `application_instance_id`, `detected_at`).

### Remediation, Graph Traversal & Governance
25. **Remediation**: Corrective action (`id`, `finding_id`, `action_type`, `estimated_risk_reduction`, `status`, `is_simulation`).
26. **AttackPath**: Graph traversal chain (`id`, `start_app_id`, `target_data_asset_id`, `path_steps_json`, `exploitability_score`).
27. **AuditEvent**: Append-only event log (`id`, `organization_id`, `user_id`, `event_type`, `payload_hash`).
28. **PostureSnapshot**: Daily posture record (`id`, `organization_id`, `snapshot_date`, `posture_score`).

---

*Domain Model Specification v1.5 — Hardened Architectural Blueprint.*
