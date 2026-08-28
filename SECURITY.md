<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=2,3,20&height=160&section=header&text=AccessGuard%20Security%20Policy&fontSize=36&fontColor=fff&animation=fadeIn&fontAlignY=55" width="100%" />

<p>
  <img src="https://img.shields.io/badge/Security%20Policy-v5.0.0-red?style=for-the-badge&logo=shield&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Last%20Updated-2026--08--28-blue?style=for-the-badge" />
</p>

</div>

---

## 🛡️ Security Architecture Principles

AccessGuard is built under **security-first constraints** at every layer. The following principles are non-negotiable and enforced by both code and policy:

| # | Principle | Enforcement |
|---|-----------|-------------|
| 1 | **Deterministic Risk Engine** — AI does NOT calculate risk scores | Code-level isolation; AI layer sandboxed from engine |
| 2 | **Server-Side Authorization Only** — client claims never trusted | Every endpoint validates against live DB records |
| 3 | **Strict Tenant Isolation** — zero cross-tenant data leakage | `organization_id` filter enforced at ORM layer |
| 4 | **Least Privilege & ABAC/RBAC** — 7 explicit operational roles | Role enforced per-endpoint server-side |
| 5 | **HttpOnly Cookie Token Transport** — XSS cannot steal tokens | `HttpOnly`, `SameSite=Lax`, zero localStorage |
| 6 | **Read-Only Connector Boundary** — providers can never be written to | `READ=True, WRITE=False` architectural guard; write methods raise `NotImplementedError` |
| 7 | **Untrusted External Data** — all provider responses sanitized | Validated, normalized, hashed before persistence |
| 8 | **No Hardcoded Secrets** — zero credentials in source code | All secrets via environment variables only |

---

## 🔑 Authentication & Session Controls

| Subsystem | Implementation |
|-----------|---------------|
| **Password Storage** | PBKDF2-SHA256 / bcrypt — zero plaintext storage or log leakage |
| **Session Transport** | HttpOnly `SameSite=Lax` cookie — zero token in browser localStorage |
| **Session Revocation** | Server-side `UserSession` table with instant `revoked_at` invalidation on logout or password change |
| **Login Throttling** | 5 consecutive failures → 15-minute account lockout (`locked_until`) |
| **Anti-Enumeration** | Generic `"Invalid email or password"` for all failure cases (non-existent, wrong password, locked) |
| **Post-Issuance Check** | Active status and role re-verified against live DB on every authenticated request |
| **CSRF Defense** | Double-defense: `SameSite=Lax` cookie + `Origin` allowlist + `X-Requested-With` custom header |
| **Zero-Token Frontend** | Frontend stores **zero** authentication tokens in browser storage (no localStorage, no sessionStorage) |

---

## 🔒 Security Headers

Every response from the AccessGuard API includes:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: default-src 'self'; ...
Strict-Transport-Security: max-age=31536000; includeSubDomains  (production HTTPS only)
```

---

## 🔗 Provider Connector Security

The connector architecture enforces strict read-only boundaries:

```
┌─────────────────────────────────────────────────┐
│            PROVIDER CONNECTOR LAYER              │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │  READ = True   │   WRITE = False         │    │
│  │  All write methods → NotImplementedError │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  Secret Handling:                                │
│  • OAuth tokens → [REDACTED] before DB write     │
│  • Private keys → [REDACTED] before DB write     │
│  • Raw payload → SHA-256 hash stored instead     │
│                                                  │
│  Evidence Chain:                                 │
│  • payload_hash_sha256 for tamper detection      │
│  • Immutable append-only evidence records        │
└─────────────────────────────────────────────────┘
```

---

## 🤖 AI Advisory Security Boundary

The AI layer (Google Gemini) is **strictly sandboxed** from all security-critical operations:

```
┌─────────────────────────────────────────────────┐
│              AI ADVISORY LAYER                   │
│              (Isolated Subsystem)                │
│                                                  │
│  ✅ MAY: Explain findings in plain English        │
│  ✅ MAY: Suggest remediation approaches           │
│  ✅ MAY: Summarize risk posture narratively       │
│                                                  │
│  ❌ CANNOT: Calculate or modify risk scores       │
│  ❌ CANNOT: Enforce authorization decisions       │
│  ❌ CANNOT: Execute remediation actions           │
│  ❌ CANNOT: Access raw secrets or credentials     │
│  ❌ CANNOT: Be the sole source of any finding     │
│                                                  │
│  All AI outputs labeled: AI-GENERATED SUGGESTION │
│  Prompts: Bounded, sanitized, injection-protected│
└─────────────────────────────────────────────────┘
```

---

## ⚠️ Known Limitations (Development Mode)

| Limitation | Detail | Production Fix |
|-----------|--------|---------------|
| `COOKIE_SECURE=False` | Only for local HTTP development (`localhost`) | Set `COOKIE_SECURE=True` in production HTTPS |
| HS256 Symmetric Key | Shared key across services | Use asymmetric RS256/ES256 for multi-service deployments |
| SQLite Session Store | Single-file DB for development | Use PostgreSQL with row-level security in production |
| Demo Seed Credentials | `DemoPass123!` preset passwords | Replace all demo accounts with real credentials in production |

---

## 📋 Role-Based Access Control Matrix

| Capability | Super Admin | Security Admin | IT Admin | Auditor | App Owner | Data Owner | Viewer |
|------------|:-----------:|:--------------:|:--------:|:-------:|:---------:|:----------:|:------:|
| View dashboard & metrics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View findings & evidence | ✅ | ✅ | ✅ | ✅ | 🔒 own | 🔒 own | ✅ |
| Simulate remediation | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Configure connectors | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Trigger connector sync | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Run monitoring check | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage users & roles | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Disconnect connectors | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Reset demo environment | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Generate executive report | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |

---

## 🚨 Reporting Vulnerabilities

> **Please do NOT open public GitHub issues for security vulnerabilities.**

If you discover a security vulnerability in AccessGuard, please report it responsibly:

1. **Email:** `security@accessguard.io`
2. **Subject:** `[SECURITY] Brief description`
3. **Include:** Steps to reproduce, impact assessment, affected component
4. **PGP Key:** Available upon request for encrypted reports

We aim to acknowledge reports within **48 hours** and provide a fix timeline within **7 days** for critical issues.

---

## 📜 Compliance Alignment

AccessGuard's design is **inspired by and aligned with** the following frameworks. This does **not** constitute certification or formal audit compliance:

| Framework | Alignment |
|-----------|-----------|
| **NIST SP 800-161** | Supply chain risk management practices |
| **NIST SP 800-63** | Authentication & identity assurance |
| **OWASP Top 10** | Injection, broken auth, IDOR/BOLA mitigations |
| **CIS Controls v8** | Inventory, access control, audit logging |
| **ISO 27001** | Information security management principles |

> *AccessGuard references these frameworks as design guidance only. No formal third-party assessment has been conducted.*

---

<div align="center">

*AccessGuard Security Policy — v5.0.0 — Last Updated 2026-08-28*

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=2,3,20&height=80&section=footer" width="100%" />

</div>
