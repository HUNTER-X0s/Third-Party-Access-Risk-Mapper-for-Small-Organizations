# AccessGuard Phase 9: Complete System Inventory

**Product:** AccessGuard — Third-Party Access Risk Mapper & C-SCRM Intelligence Platform  
**Architecture:** Modular Monolith (FastAPI Backend + React/TypeScript Frontend)  
**Status:** Frozen & Hardened for Competition

---

## Subsystem Inventory Matrix

| Subsystem | Entry Points | Dependencies | Data Stores | Security Boundary | Failure Behavior | Test Coverage |
|---|---|---|---|---|---|---|
| **Authentication** | `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` | JWT (RS256/HS256), `bcrypt` | `users`, `user_sessions` | HttpOnly Cookie, SameSite=Strict, CSRF origin check | Fail Closed (401 Unauthorized) | `test_phase42_csrf_cookie_production_gate.py`, `test_phase9_redteam_security.py` |
| **RBAC / Authorization** | `require_role(roles)` dependency | Session claims, DB user status | `users`, `organization_memberships` | Server-side role enforcement on every route | Fail Closed (403 Forbidden) | `test_phase8_security_rbac.py`, `test_phase9_redteam_security.py` |
| **Tenant Isolation** | `get_current_org_id` dependency | User primary org / memberships | All tables (`organization_id`) | Strict ORM query filter on every SQL read/write | Empty set / 404 Not Found (Cross-tenant leak impossible) | `test_tenant_isolation.py`, `test_supplier_risk_isolation.py` |
| **Deterministic Risk Engine** | `calculate_risk()` (`services/risk_engine.py`) | Pure Python formulas (v1.5.0) | None (Stateless CPU calculation) | Absolute isolation from AI; strictly deterministic | Clamped [0, 100], deterministic error fallback | `test_risk_calibration.py`, `test_phase9_cross_module_truth.py` |
| **Security Graph Engine** | `GraphEngine` (`services/graph_engine.py`) | Graph traversal, path discovery | `access_relationships`, `data_assets` | Organization-scoped graph queries | Cycle-safe traversal, graceful empty response | `test_graph_engine.py`, `test_phase9_cross_module_truth.py` |
| **Blast Radius Calculator** | `BlastRadiusCalculator` (`services/blast_radius_engine.py`) | Multi-hop scope expansion | `data_assets`, `access_relationships` | Server-side evaluation | Clamped [0, 100], fallback to direct reachability | `test_blast_radius_engine.py` |
| **Evidence Engine** | `compute_payload_hash()`, `verify_payload_hash()` | SHA-256 canonical JSON hash | `raw_evidence`, `evidence_sources` | Immutability check; tamper-evident logs | `TAMPER_DETECTED` flag, audit logged | `test_evidence_engine.py`, `test_phase9_ai_connector_safety.py` |
| **Remediation Optimizer** | `RemediationOptimizer` (`services/remediation_optimizer.py`) | Deterministic scope power-set evaluator | `permission_grants`, `data_assets` | Simulation Only; zero provider write operations | Returns `is_target_achieved=False` if unachievable | `test_remediation_optimizer.py`, `test_phase9_cross_module_truth.py` |
| **Continuous Monitoring** | `POST /monitoring/run`, `GET /monitoring/timeline` | `SecurityDiffEngine`, `IncidentEngine` | `security_snapshots`, `security_changes`, `security_incidents` | Snapshot diffing, version tracking | Fail-safe rollback, deduplicated alerts | `test_monitoring_tenant_isolation.py`, `test_incident_correlation.py` |
| **Notification Center** | `GET /monitoring/notifications`, `PATCH .../read` | `NotificationEngine` | `security_notifications` | Organization-scoped alert queue | Deduplicated fingerprinting | `test_phase71_security.py` |
| **Shadow SaaS Intelligence** | `GET /monitoring/shadow-saas` | App catalog classification | `applications`, `application_instances` | Catalog status tagging (`shadow`, `unapproved`) | Auto-tags `shadow` status upon unmanaged discovery | `test_shadow_saas.py` |
| **Supplier Risk & C-SCRM** | `SupplierRiskEngine` (`services/supplier_risk_engine.py`) | NIST SP 1326 four-domain scoring | `supplier_profiles`, `supplier_due_diligence`, `supplier_subprocessors` | Access Risk strictly separated from Supplier Posture | Deterministic scoring; clamps [5, 95] | `test_vendor_model.py`, `test_nist_due_diligence.py`, `test_phase81_csrm_validation.py` |
| **Supply Chain Graph** | `GET /graph/supply-chain` | Multi-tier node generation | `supplier_subprocessors`, `vendors` | Verified vs Declared boundary modeling | Degrades to Tier-1 direct vendor tree | `test_supply_chain_graph.py` |
| **AI Security Analyst** | `AISecurityAnalystService` (`app/ai/service.py`) | Gemini 2.5 Flash / offline fallback | Grounding facts & evidence anchors | Advisory only; untrusted text bounded & sanitized | Offline deterministic fallback if provider 429/500 | `test_ai_authorization.py`, `test_phase9_ai_connector_safety.py` |
| **Connector Framework** | `BaseConnector`, `GitHubConnector` | Provider REST/GraphQL APIs | `provider_connectors`, `raw_evidence` | Architectural Read Guard (`READ=True, WRITE=False`) | Safe error recording; no credentials leaked | `test_phase5_connector_framework.py`, `test_phase9_ai_connector_safety.py` |
| **Audit Logging** | `AuditEvent` (`models/audit.py`) | Database append-only table | `audit_events` | Immutable audit log | Transactional integrity | `test_audit_trail.py` |
