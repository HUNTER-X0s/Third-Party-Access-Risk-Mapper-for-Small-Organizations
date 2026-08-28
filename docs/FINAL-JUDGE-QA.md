# AccessGuard: Final Judge Q&A & Technical Defense Guide

**Purpose:** Rapid, rock-solid technical responses for hackathon judges evaluating AccessGuard.

---

### 1. Why is the risk score trustworthy?
The risk scoring engine (`RiskEngine v1.5.0`) is **100% deterministic pure Python CPU code** running on the server. It evaluates 5 distinct mathematical dimensions (Technical Risk, Data Exposure Risk, Business Impact Risk, Vendor Posture Risk, and Attack Path Reachability). It does NOT use any probabilistic LLM calls to compute or influence scores.

### 2. How do you prevent AI from changing the score?
By architectural separation. The AI Security Analyst is a **read-only advisory assistant** placed in a dedicated, isolated subsystem. It receives read-only context and has no write access or database mutation permissions.

### 3. How do you prevent cross-tenant data leakage?
Every database query in the application enforces mandatory `organization_id` filtering backed by server-validated JWT session claims. Cross-tenant queries return 404 / empty sets and are verified by 15+ automated tenant-isolation test suites.

### 4. What happens if the connector lies or fails?
All external data ingested from SaaS providers is treated as untrusted. Raw payloads are hashed with SHA-256 to create immutable evidence. If an upstream API returns an error or malformed payload, the connector logs the error cleanly and preserves the last known valid snapshot without corrupting the security baseline.

### 5. What happens if provider metadata contains prompt injection?
All untrusted third-party text (app descriptions, permission scopes, supplier notes) is sanitized by `AIContextBuilder` and wrapped in `<UNTRUSTED_SECURITY_DATA>` delimiter tags before prompt composition, neutralizing injection attempts.

### 6. How is blast radius calculated?
Blast radius is computed deterministically by `BlastRadiusCalculator` traversing the underlying graph of OAuth permissions, integrated systems, and sensitive data assets to calculate reachable crown jewels. Post-remediation blast radius is computed by re-evaluating the actual remaining graph state, never by proportional arithmetic.

### 7. How do you know the graph is real?
Every node and edge in the Access Graph directly maps to a persisted `ApplicationInstance`, `PermissionGrant`, `DataAsset`, or `AccessRelationship` record backed by raw SHA-256 evidence.

### 8. How is excessive permission determined?
Excessive permission is evaluated by comparing granted OAuth scopes against the baseline minimum required scopes for that application category (e.g. read-only sync vs full organizational admin write access).

### 9. How is Shadow SaaS detected?
The Continuous Monitoring engine (`SnapshotEngine`) detects newly installed applications, OAuth grants, and unapproved integrations that lack an approved organizational owner or compliance registration, automatically categorizing them as `shadow` or `unapproved`.

### 10. How do you distinguish supplier risk from access risk?
AccessGuard strictly separates **Access Risk** (technical OAuth scopes, data reachability, crown jewels) from **Supplier Risk** (NIST SP 1326 FOCI, Provenance, Resilience, Foundational Cyber Practices). Favorable supplier due diligence *never suppresses* high access exposure.

### 11. What happens if the vendor is compromised?
AccessGuard provides a Single-Supplier Failure / Compromise Simulator (`GET /vendors/{id}/impact-analysis`) that instantly models all applications, crown jewels, and business units dependent on that vendor, allowing security teams to execute targeted mitigations.

### 12. What happens if the AI is unavailable?
AccessGuard operates with 100% functionality without AI. The dashboard, risk engine, security graph, blast radius calculator, remediation optimizer, continuous monitoring, and reporting are completely independent. If Gemini returns 429 or is unreachable, the AI drawer falls back cleanly to deterministic grounding facts.

### 13. What happens if GitHub is unavailable?
AccessGuard operates seamlessly in offline demo mode using synthetic seed datasets, while live connector health checks report provider unavailability without crashing.

### 14. What happens if evidence is tampered with?
The Evidence Engine recalculates SHA-256 hashes against raw payloads. Any mismatch immediately triggers a `TAMPER_DETECTED` flag and generates an audit log entry.

### 15. What is live vs simulated?
- **Live:** GitHub OAuth/App live metadata discovery, real-time JWT authentication & RBAC, deterministic risk calculation, graph traversal, and live Gemini AI analysis.
- **Simulated:** Remediation execution (deliberately simulates revocations rather than destructive live SaaS API mutations) and single-supplier failure impact.

### 16. How does the system scale?
The core risk engine processes 1,000 risk evaluations in < 0.1ms per evaluation. Graph traversals execute in < 15ms. The modular monolith architecture is lightweight and easily containerized.

### 17. Why should a small organization use this?
Small organizations lack large dedicated SecOps teams to manually audit complex OAuth permissions and supply chain dependencies. AccessGuard provides an automated, unified view of third-party risk, actionable remediation steps, and continuous monitoring at zero enterprise complexity.

### 18. What makes this different from IAM/SSPM/CASB?
IAM manages user identity; CASB inspects network traffic; SSPM checks SaaS misconfigurations. AccessGuard uniquely maps the **transitive graph of third-party machine-to-machine access**, evaluating data reachability, attack paths, and supplier supply-chain risk in one cohesive platform.

### 19. Why is the system not simply an AI wrapper?
Over 90% of AccessGuard consists of deterministic security engines, graph algorithms, evidence pipelines, multi-tenant databases, and monitoring schedulers. The AI is strictly an advisory copilot grounded on deterministic facts.

### 20. What would you build next?
Automated pull request remediation workflows (e.g. automatically opening PRs to downgrade GitHub App permissions), bi-directional webhooks for Okta/Google Workspace, and expanded C-SCRM questionnaire automation.
