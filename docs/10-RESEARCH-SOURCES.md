# 10 — Research Sources
# AccessGuard: Authoritative Source Documentation

**Document Type:** Research Sources — Phase 0  
**Version:** 1.0  
**Date:** 2026-08-13  

---

## Usage Note

> These sources informed the architecture, risk model, security principles, and feature decisions of AccessGuard during Phase 0. References are to authoritative standards bodies, not secondary blogs. Where blogs or vendor documentation are cited, it is because they document specific API behaviors or technical implementation details not available elsewhere.
>
> **AccessGuard does NOT claim certification or compliance with any of these standards.** References are to design inspiration and conceptual alignment only.

---

## Primary Standards References

### S-001: NIST Special Publication 800-161 Rev. 1
**Title:** Cybersecurity Supply Chain Risk Management Practices for Systems and Organizations  
**Publisher:** National Institute of Standards and Technology (NIST)  
**Date:** May 2022 (updated November 2024 as SP 800-161r1-upd1)  
**URL:** https://csrc.nist.gov/publications/detail/sp/800-161/rev-1/final  
**Relevance:**
- Foundational framework for third-party and supply-chain risk management
- Informed AccessGuard's vendor risk model and fourth-party risk conceptualization
- Multi-level governance model informed AccessGuard's organization/vendor/application hierarchy
- Appendix F (software supply chain, 2024 update) directly relevant to SaaS connector security

**Specific application to AccessGuard:**
- C-SCRM strategy → AccessGuard's policy engine concept
- Risk assessment approach → input to the 10-factor risk model
- Multi-tier supply chain → AccessGuard's vendor/fourth-party risk distinction

---

### S-002: NIST Special Publication 800-207
**Title:** Zero Trust Architecture  
**Publisher:** National Institute of Standards and Technology (NIST)  
**Date:** August 2020  
**URL:** https://csrc.nist.gov/publications/detail/sp/800-207/final  
**Relevance:**
- "Never trust, always verify" principle applied to every authorization decision in AccessGuard
- Identity as the primary control plane → AccessGuard's identity assurance risk factor (F6)
- Policy Engine / Policy Administrator concept → AccessGuard's server-side authorization model
- Least privilege principle → core of AccessGuard's excess permission detection
- Per-request authorization evaluation → ABAC model used in AccessGuard's API layer

---

### S-003: NIST Special Publication 800-53 Rev. 5
**Title:** Security and Privacy Controls for Information Systems and Organizations  
**Publisher:** National Institute of Standards and Technology (NIST)  
**Date:** September 2020  
**URL:** https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final  
**Relevance:**
- Control families CA (Assessment, Authorization, Monitoring) → audit capability requirements
- Control AC-2 (Account Management) → orphaned authorization detection
- Control AC-6 (Least Privilege) → core functional requirement
- Control CM-8 (System Component Inventory) → application inventory requirement
- Control SI-3 (Malicious Code Protection) → dependency management guidance

---

### S-004: NIST Special Publication 800-63B
**Title:** Digital Identity Guidelines — Authentication and Lifecycle Management  
**Publisher:** National Institute of Standards and Technology (NIST)  
**Date:** June 2017 (with errata through 2019)  
**URL:** https://pages.nist.gov/800-63-3/sp800-63b.html  
**Relevance:**
- Authenticator Assurance Levels (AAL) → AccessGuard's identity assurance risk factor
- MFA requirements → MFA tracking as a risk signal
- Password requirements → AccessGuard's own authentication implementation

---

### S-005: IETF RFC 9700
**Title:** Best Current Practice for OAuth 2.0 Security  
**Publisher:** Internet Engineering Task Force (IETF)  
**Date:** January 2025  
**URL:** https://datatracker.ietf.org/doc/rfc9700/  
**Relevance:**
- PKCE requirement → AccessGuard's own OAuth implementation + connector design
- Deprecation of Implicit Grant → explicitly excluded from AccessGuard's connector framework
- Scope restriction (least privilege) → core of AccessGuard's excess permission detection
- Redirect URI validation → AccessGuard's own OAuth callback handling
- Token storage guidance → HttpOnly cookie recommendation in AccessGuard's auth implementation
- Regular auditing of OAuth grants → core use case of AccessGuard

---

### S-006: IETF RFC 6749
**Title:** The OAuth 2.0 Authorization Framework  
**Publisher:** Internet Engineering Task Force (IETF)  
**Date:** October 2012  
**URL:** https://datatracker.ietf.org/doc/html/rfc6749  
**Relevance:**
- Defines OAuth scope concept → foundation of AccessGuard's permission model
- Authorization grant types → understood to determine which grant types are safe
- Token lifetime concepts → AccessGuard's short-lived token implementation

---

### S-007: OWASP API Security Top 10 (2023)
**Title:** OWASP API Security Top 10  
**Publisher:** Open Worldwide Application Security Project (OWASP)  
**Date:** 2023  
**URL:** https://owasp.org/API-Security/editions/2023/en/0x11-t10/  
**Relevance:**
- API1:2023 — Broken Object Level Authorization (BOLA) → tenant isolation design
- API2:2023 — Broken Authentication → JWT implementation requirements
- API3:2023 — Broken Object Property Level Authorization → selective field exposure in API responses
- API5:2023 — Broken Function Level Authorization → RBAC enforcement requirements
- API8:2023 — Security Misconfiguration → API default security settings
- API10:2023 — Unsafe Consumption of APIs → connector design (treating external API responses as untrusted)

---

### S-008: OWASP Top 10 Web Application Security Risks (2021)
**Title:** OWASP Top 10  
**Publisher:** Open Worldwide Application Security Project (OWASP)  
**Date:** 2021  
**URL:** https://owasp.org/www-project-top-ten/  
**Relevance:**
- A01:2021 — Broken Access Control → server-side authorization on every endpoint
- A02:2021 — Cryptographic Failures → encryption requirements for sensitive fields
- A03:2021 — Injection → parameterized queries, Pydantic validation
- A07:2021 — Identification and Authentication Failures → JWT implementation
- A10:2021 — Server-Side Request Forgery (SSRF) → connector URL validation

---

### S-009: CIS Controls Version 8
**Title:** CIS Critical Security Controls  
**Publisher:** Center for Internet Security (CIS)  
**Date:** May 2021  
**URL:** https://www.cisecurity.org/controls/v8  
**Relevance:**
- Control 2 — Inventory and Control of Software Assets → AccessGuard's core use case (for third-party SaaS)
- Control 5 — Account Management → authorization management features
- Control 6 — Access Control Management → least privilege and permission review
- Control 18 — Penetration Testing → security testing requirements for AccessGuard itself

---

### S-010: CISA — Cybersecurity Resources for Small and Medium Businesses
**Title:** CISA SMB Resources  
**Publisher:** Cybersecurity and Infrastructure Security Agency (CISA)  
**Date:** Ongoing (current as of 2024)  
**URL:** https://www.cisa.gov/resources-tools/resources/small-and-medium-businesses  
**Relevance:**
- Confirms the problem statement is real and prioritized at national level
- Validates that inventory management and access control are priority concerns for SMBs
- Shared responsibility model for SaaS → reinforces AccessGuard's value proposition
- "You cannot protect what you do not know you have" → application inventory as foundation

---

## Secondary Technical References

### T-001: Google Workspace Admin SDK — Directory API
**URL:** https://developers.google.com/admin-sdk/directory/v1/guides  
**Relevance:** Technical reference for Google Workspace connector implementation (future Phase)

### T-002: Google Workspace Admin SDK — Reports API  
**URL:** https://developers.google.com/admin-sdk/reports/v1/guides  
**Relevance:** OAuth audit log access — list of third-party OAuth apps and their grants

### T-003: Microsoft Graph API — OAuth Permission Grants
**URL:** https://learn.microsoft.com/en-us/graph/api/oauth2permissiongrant-list  
**Relevance:** Technical reference for Microsoft 365 connector implementation

### T-004: React Flow Documentation
**URL:** https://reactflow.dev/  
**Relevance:** Graph visualization library for data-flow and attack-path visualization

### T-005: FastAPI Documentation
**URL:** https://fastapi.tiangolo.com/  
**Relevance:** Backend framework documentation; security middleware patterns

### T-006: Pydantic v2 Documentation
**URL:** https://docs.pydantic.dev/latest/  
**Relevance:** Input validation library; `ConfigDict(extra="forbid")` for strict validation

### T-007: SQLAlchemy 2.0 ORM Documentation
**URL:** https://docs.sqlalchemy.org/en/20/  
**Relevance:** ORM framework; async session patterns; tenant filtering patterns

---

## Market Research References

### M-001: SaaS Security Posture Management (SSPM) Category Analysis
**Sources consulted:** AppOmni, Adaptive Shield, Obsidian Security public documentation  
**Relevance:** Understanding the commercial SSPM market; identifying features that distinguish research-quality tools from consumer tools  
**Application:** Informed the feature matrix tier classification and competitive differentiation analysis  
**Caution:** Commercial vendor claims were treated as directional only; not accepted as factual

### M-002: Third-Party Risk Management (TPRM) Framework Landscape
**Sources consulted:** Prevalent TPRM Framework white papers, Vanta blog on NIST 800-161  
**Relevance:** Understanding how enterprise TPRM extends beyond basic vendor questionnaires  
**Application:** Informed vendor risk model and fourth-party risk conceptualization

---

## Key Findings from Research

| Finding | Source | Impact on Design |
|---|---|---|
| OAuth "over-scoping" is identified as a primary risk by RFC 9700 | RFC 9700 | Core use case validated as standards-recognized problem |
| CISA identifies inventory as the prerequisite for all security | CISA SMB | Application inventory must be foundation, not an add-on |
| Attack path analysis is standard in modern SSPM tools (2024) | Market research | Attack path + blast radius is competitive norm, not innovation |
| Implicit Grant deprecated by RFC 9700 (2025) | RFC 9700 | AccessGuard's connector must not use implicit grant |
| NIST 800-161 now covers software supply chain (2024 update) | NIST 800-161 Appx F | Vendor + application supply chain framing is standard |
| BOLA remains #1 API security risk (OWASP 2023) | OWASP API 2023 | Tenant isolation is most critical security control to implement |
| Zero Trust emphasizes per-request authorization | NIST 800-207 | Server-side authorization on every endpoint is non-negotiable |

---

*Research sources version 1.0 — All sources verified as authoritative and current as of 2026-08-13.*
