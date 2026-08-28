<div align="center">

<!-- Animated Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,12,20&height=220&section=header&text=AccessGuard&fontSize=72&fontColor=fff&animation=fadeIn&fontAlignY=38&desc=Third-Party%20Access%20Risk%20Intelligence%20Platform&descAlignY=58&descSize=20" width="100%" />

<!-- Badges -->
<p>
  <img src="https://img.shields.io/badge/Risk%20Engine-v1.5.0%20Deterministic-blue?style=for-the-badge&logo=shield&logoColor=white" />
  <img src="https://img.shields.io/badge/Test%20Suite-102%2F102%20PASSED-success?style=for-the-badge&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/Security-Production%20Grade-red?style=for-the-badge&logo=security&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React%2018-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
</p>

<p>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" />
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square" />
  <img src="https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-red?style=flat-square" />
  <img src="https://img.shields.io/badge/SIH%202026-Hackathon%20Project-purple?style=flat-square" />
</p>

<br/>

> **🛡️ The only open-source platform that maps, scores, and monitors every third-party SaaS access risk for small organizations — in real time.**

<br/>

</div>

---

## 📖 Table of Contents

<details open>
<summary><b>Click to expand</b></summary>

- [🔥 What is AccessGuard?](#-what-is-accessguard)
- [🎯 The Problem We Solve](#-the-problem-we-solve)
- [⚡ Key Features](#-key-features)
- [🖥️ Platform Screenshots](#️-platform-screenshots)
- [🏗️ System Architecture](#️-system-architecture)
- [🚀 Quick Start](#-quick-start)
- [🔐 Security & Role Matrix](#-security--role-matrix)
- [📊 Live Metrics](#-live-metrics)
- [🧩 Technology Stack](#-technology-stack)
- [📁 Project Structure](#-project-structure)
- [🗺️ Roadmap](#️-roadmap)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)

</details>

---

## 🔥 What is AccessGuard?

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════╗
║   Small organizations connect dozens of SaaS apps every year.        ║
║   Each OAuth grant is a door into your most sensitive data.          ║
║   Most organizations have NO idea who has access to what.            ║
║                                                                      ║
║   AccessGuard changes that.                                          ║
╚══════════════════════════════════════════════════════════════════════╝
```

</div>

**AccessGuard** is a **deterministic, open-source third-party access risk intelligence platform** built specifically for small and mid-sized organizations. It provides complete, real-time visibility into every external SaaS application, vendor integration, and OAuth delegation that can reach your organizational data — and translates that visibility into **prioritized, evidence-backed security decisions**.

Unlike AI-generated risk scores that are opaque and unpredictable, AccessGuard uses a **transparent, auditable, deterministic risk engine** (`v1.5.0`) — every score can be explained, verified, and reproduced.

---

## 🎯 The Problem We Solve

<table>
<tr>
<td width="50%">

### 😰 Before AccessGuard
- ❌ No visibility into which SaaS apps have OAuth access
- ❌ Shadow IT running undetected for months
- ❌ No way to prioritize which access risks to fix first
- ❌ Security teams spending weeks on manual audits
- ❌ No proof of what changed and when
- ❌ Supply chain risks invisible until breach

</td>
<td width="50%">

### ✅ After AccessGuard
- ✅ Complete real-time third-party access inventory
- ✅ Shadow SaaS detected within seconds of sync
- ✅ Deterministic risk scores with full evidence trail
- ✅ Automated attack path discovery via graph engine
- ✅ Immutable SHA-256 evidence chain for every finding
- ✅ C-SCRM supplier risk matrix with concentration analysis

</td>
</tr>
</table>

---

## ⚡ Key Features

<div align="center">

| 🔍 **Discover** | 📊 **Score** | 🗺️ **Visualize** | 🔔 **Monitor** |
|:---:|:---:|:---:|:---:|
| Every SaaS integration | Deterministic risk engine v1.5.0 | Interactive attack graph | Real-time change detection |
| Shadow IT & rogue apps | Blast radius calculation | Crown jewel reachability | Security incident correlation |
| OAuth permission scopes | Permission excess detection | Delta mode topology | In-app notification center |
| Vendor supply chain | C-SCRM supplier scoring | Evidence provenance | Continuous monitoring scheduler |

</div>

<br/>

### 🎨 Core Capabilities

<details>
<summary><b>🔴 Deterministic Risk Scoring Engine</b></summary>

AccessGuard's risk engine is **100% deterministic** — no AI, no black box. Every score is calculated from explicit formulas documented in [`docs/05-RISK-MODEL-DRAFT.md`](./docs/05-RISK-MODEL-DRAFT.md).

- **Composite Risk Score** = Base Risk + Permission Excess + Crown Jewel Exposure + Shadow Penalty + Concentration Bonus
- **Blast Radius Calculator** — quantifies the damage a compromised third-party can cause
- **Minimum Effective Remediation Optimizer v2.1.0** — finds the smallest set of revocations that bring risk below threshold
- Every finding records `risk_engine_version` for full auditability

</details>

<details>
<summary><b>🟡 Attack Path Graph Engine</b></summary>

Visualizes the complete access topology as an interactive graph:
- **DELTA Mode** — highlights new, changed, and removed edges since last snapshot
- **Crown Jewel Reachability** — which third-party apps have a path to your most sensitive data
- **Attack Path Discovery** — automated identification of exploitable permission chains
- Powered by **ReactFlow** with force-directed layout

</details>

<details>
<summary><b>🟢 Continuous Monitoring & Change Detection</b></summary>

- **DiffEngine** — deterministic diff between access snapshots, detecting permission escalations in real time
- **Security Incident Correlator** — groups related changes into security incidents
- **In-App Notification Center** — severity-classified alerts with deduplication
- **Background Scheduler** — automated monitoring cycles, configurable interval

</details>

<details>
<summary><b>🔵 Provider Connectors (Read-Only)</b></summary>

- **GitHub App Connector** — RS256 JWT auth, paginated discovery, rate-limit backoff, `2022-11-28` API pinning
- **Provider Permission Normalization** — raw scopes (`contents:write`) → canonical (`WRITE`, `ADMIN`, `UNKNOWN`)
- **Architectural Guard**: `READ=True, WRITE=False` enforced at the connector layer
- **Zero secret persistence** — tokens redacted to `[REDACTED]` before any database write

</details>

<details>
<summary><b>🟣 AI Security Analyst (Advisory Only)</b></summary>

- Powered by **Google Gemini** — strictly sandboxed, read-only advisory role
- Explains risk findings in plain English
- **AI cannot**: calculate scores, make authorization decisions, or modify findings
- All AI outputs are labeled `AI-GENERATED SUGGESTION`
- Bounded, sanitized prompts — protected against prompt injection

</details>

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                 │
│          React 18 + TypeScript + Vite + TailwindCSS         │
│   • AccessGuard SecOps Design System                        │
│   • Lazy-loaded page chunks (fast initial load)             │
│   • All data from authenticated REST API only               │
└───────────────────────┬─────────────────────────────────────┘
                        │  HTTPS + HttpOnly JWT Cookie
┌───────────────────────▼─────────────────────────────────────┐
│                  FASTAPI BACKEND                            │
│   • RS256/HS256 JWT authentication                          │
│   • CSRF double-defense (SameSite + X-Requested-With)       │
│   • Pydantic input validation & sanitization                │
│   • Rate limiting & login throttling (5 attempts → 15min)   │
└──────────┬────────────────────────────────┬─────────────────┘
           │                                │
┌──────────▼──────────┐        ┌────────────▼────────────────┐
│   RISK ENGINE       │        │   AI ADVISORY LAYER         │
│   Deterministic     │        │   Google Gemini (isolated)  │
│   No AI influence   │        │   Sandboxed, read-only      │
│   SHA-256 evidence  │        │   Labels all AI output      │
└──────────┬──────────┘        └────────────▬────────────────┘
           │                                
┌──────────▼──────────────────────────────────────────────────┐
│                  DATABASE (SQLite → PostgreSQL)             │
│   • Organization-scoped tenant isolation on every query     │
│   • Append-only evidence & audit log tables                 │
│   • Encrypted sensitive fields                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
Python 3.11+
Node.js 18+
npm 9+
```

### 1️⃣ Clone & Setup Backend

```powershell
# Clone the repository
git clone https://github.com/your-org/accessguard.git
cd accessguard

# Create & activate virtual environment
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Configure Environment

```powershell
# Copy environment template
cp .env.example backend/.env

# Edit backend/.env — set your secret key
# Never commit .env to version control!
```

### 3️⃣ Start Backend

```powershell
# From project root
$env:PYTHONPATH = "backend"
.\backend\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4️⃣ Start Frontend

```powershell
# In a new terminal
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### 5️⃣ Login

```
URL:      http://localhost:5173
Email:    admin@anurag.tech
Password: DemoPass123!
```

> 💡 The platform auto-seeds all demo data on first startup. No external services required.

### 🧪 Run the Test Suite

```powershell
$env:PYTHONPATH = "backend"

# Full test suite (102 tests)
.\backend\venv\Scripts\pytest backend/tests/ -v

# Acceptance scenario (20 steps)
.\backend\venv\Scripts\python backend/tests/verify_acceptance_scenario.py

# Phase 2 & 3 demo scenario
.\backend\venv\Scripts\python backend/tests/verify_phase2_demo_scenario.py
```

---

## 🔐 Security & Role Matrix

AccessGuard implements production-grade authentication with 7 operational roles:

| Role | Email | Capabilities |
|------|-------|-------------|
| 🔴 **Super Admin** | `superadmin@anurag.tech` | User management, connector disconnect, system reset |
| 🟠 **Security Admin** | `admin@anurag.tech` | Full SecOps access, connector config & sync, remediation |
| 🟡 **IT Admin** | *(create via User Management)* | Connector management, application registration |
| 🔵 **Auditor** | `auditor@anurag.tech` | Read-only findings, evidence SHA-256 verification |
| 🟢 **App Owner** | `devops@anurag.tech` | Restricted to assigned application instances only |
| ⚪ **Data Owner** | *(create via User Management)* | Restricted to assigned data assets only |
| ⬜ **Viewer** | `viewer@anurag.tech` | Read-only dashboard summaries & connector health |

**All passwords for demo accounts:** `DemoPass123!`

### Security Controls

```
✅ HttpOnly cookie JWT transport (zero localStorage tokens)
✅ PBKDF2-SHA256 / bcrypt password hashing
✅ CSRF double-defense (SameSite=Lax + X-Requested-With)
✅ Login throttling: 5 failures → 15-minute lockout
✅ Server-side session revocation table
✅ Organization-scoped tenant isolation on every DB query
✅ SHA-256 tamper-evident evidence chain
✅ Security headers: CSP, X-Frame-Options, HSTS, nosniff
✅ Read-Only connector guard: READ=True, WRITE=False
✅ Credential redaction before any database write
```

---

## 📊 Live Metrics

> Authoritative values from the clean seeded demo environment.

| Metric | Value | Status |
|--------|-------|--------|
| Security Posture Score | `62.4 / 100` | 🟡 Medium Risk |
| GitHub App Risk Score | `94.5 / 100` | 🔴 Critical |
| Blast Radius | `75.0 / 100` | 🟠 High |
| Post-Remediation Blast Radius | `50.0 / 100` | 🟡 Medium |
| Blast Radius Reduction | `25.0 pts` | ✅ |
| Simulated Residual Risk | `53.6` (Target ≤ 55.0) | ✅ |
| Evidence Integrity | `VERIFIED_INTACT` (SHA-256) | ✅ |
| Test Suite | `102 / 102 PASSED` | ✅ 100% |

---

## 🧩 Technology Stack

<div align="center">

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + TypeScript | UI Framework |
| **Styling** | TailwindCSS v4 | Design System |
| **Graph** | ReactFlow (@xyflow/react) | Access topology visualization |
| **Build** | Vite 5 + esbuild | Bundler & minifier |
| **Backend** | FastAPI + Uvicorn | REST API server |
| **ORM** | SQLAlchemy + Alembic | Database layer |
| **Auth** | python-jose (JWT) + passlib | Authentication |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Persistence |
| **AI Advisory** | Google Gemini API | Advisory copilot (sandboxed) |
| **Testing** | pytest + httpx | 102-test security suite |
| **Icons** | Lucide React | UI icons |
| **Fonts** | Inter + JetBrains Mono | Typography |

</div>

---

## 📁 Project Structure

```
accessguard/
├── 📁 backend/                    # FastAPI application
│   ├── 📁 app/
│   │   ├── 📄 main.py             # Application entrypoint & middleware
│   │   ├── 📁 routers/            # API route handlers
│   │   │   ├── auth.py            # Authentication & session management
│   │   │   ├── dashboard.py       # Dashboard summary & metrics
│   │   │   ├── applications.py    # Application inventory
│   │   │   ├── findings.py        # Risk findings & evidence
│   │   │   ├── graph.py           # Access topology graph
│   │   │   ├── monitoring.py      # Continuous monitoring
│   │   │   ├── connectors.py      # Provider connector management
│   │   │   └── vendors.py         # Supplier C-SCRM
│   │   ├── 📁 engine/
│   │   │   ├── risk_engine.py     # Deterministic risk scoring v1.5.0
│   │   │   ├── graph_engine.py    # Attack path discovery
│   │   │   ├── blast_radius.py    # Blast radius calculator
│   │   │   ├── diff_engine.py     # Change detection engine
│   │   │   └── remediation.py     # Optimizer v2.1.0
│   │   ├── 📁 connectors/         # Provider integrations (read-only)
│   │   └── 📁 models/             # SQLAlchemy ORM models
│   ├── 📁 tests/                  # 102-test security suite
│   └── 📄 requirements.txt
│
├── 📁 frontend/                   # React application
│   ├── 📁 src/
│   │   ├── 📁 app/                # App root & routing
│   │   ├── 📁 pages/              # Page components
│   │   │   ├── DashboardPage.tsx  # Overview & KPIs
│   │   │   ├── ApplicationsPage.tsx  # App inventory
│   │   │   ├── FindingsPage.tsx   # Security findings
│   │   │   ├── MonitoringPage.tsx # Continuous monitoring
│   │   │   ├── VendorsPage.tsx    # C-SCRM suppliers
│   │   │   └── ConnectorsPage.tsx # Provider connectors
│   │   ├── 📁 components/         # Shared UI components
│   │   │   ├── AccessGraphView.tsx  # ReactFlow graph
│   │   │   ├── Sidebar.tsx        # Navigation (responsive)
│   │   │   ├── Navbar.tsx         # Top bar (responsive)
│   │   │   └── AIAnalystDrawer.tsx  # AI advisory copilot
│   │   └── 📁 services/           # API client
│   ├── 📄 index.html              # SEO-optimized entry
│   └── 📄 vite.config.ts          # Build optimization
│
├── 📁 docs/                       # Technical documentation
├── 📄 README.md                   # This file
├── 📄 SECURITY.md                 # Security policy
└── 📄 .env.example                # Environment template
```

---

## ✅ Feature Implementation Status

| Feature | Status |
|---------|--------|
| Deterministic Risk Engine `v1.5.0` | ✅ **COMPLETE & VERIFIED** |
| Graph Engine & Attack Path Discovery | ✅ **COMPLETE & VERIFIED** |
| Graph Delta Visualization (DELTA Mode) | ✅ **COMPLETE & VERIFIED** |
| Blast Radius Calculator (`75.0 → 50.0`) | ✅ **SINGLE-SOURCE VERIFIED** |
| Remediation Optimizer `v2.1.0` | ✅ **MATHEMATICALLY VERIFIED** |
| SecOps Priority Queue (P0/P1/P2) | ✅ **COMPLETE & VERIFIED** |
| Continuous Change Detection (DiffEngine) | ✅ **COMPLETE & VERIFIED** |
| Shadow SaaS Detection & Baseline Governance | ✅ **COMPLETE & VERIFIED** |
| Security Incident Correlation Engine | ✅ **COMPLETE & VERIFIED** |
| In-App Notification Center & Deduplication | ✅ **COMPLETE & VERIFIED** |
| AI Security Analyst Advisory (Gemini) | ✅ **COMPLETE & GUARDRAILED** |
| Read-Only GitHub App Live Connector | ✅ **COMPLETE & SECURED** |
| Executive Security Summary Report Generator | ✅ **COMPLETE & VERIFIED** |
| Security Snapshots & Delta Analysis | ✅ **COMPLETE & VERIFIED** |
| Supplier C-SCRM Risk Matrix | ✅ **COMPLETE & VERIFIED** |
| Responsive UI (Mobile, Tablet, Desktop) | ✅ **COMPLETE** |
| SEO & Performance Optimization | ✅ **COMPLETE** |
| Remediation Simulation | ⚡ **SIMULATION ONLY** — No provider changes |
| OAuth Live Connectors (Google, M365) | 🗺️ **ROADMAP** |

---

## 🗺️ Roadmap

```
v1.0 ████████████████████ CURRENT
  ├── ✅ Deterministic risk engine
  ├── ✅ GitHub App connector
  ├── ✅ Attack graph visualization
  ├── ✅ Continuous monitoring
  └── ✅ AI advisory copilot

v2.0 ░░░░░░░░░░░░░░░░░░░░ NEXT
  ├── 🗺️ Google Workspace OAuth connector
  ├── 🗺️ Microsoft 365 connector
  ├── 🗺️ Slack workspace connector
  └── 🗺️ Automated remediation (with approval workflow)

v3.0 ░░░░░░░░░░░░░░░░░░░░ FUTURE
  ├── 🗺️ Multi-tenant SaaS deployment
  ├── 🗺️ SSO / SAML 2.0 / Okta integration
  ├── 🗺️ Compliance report export (SOC 2, ISO 27001)
  └── 🗺️ API-first integrations (Webhook + REST)
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`docs/DEMO-RUNBOOK.md`](./docs/DEMO-RUNBOOK.md) | Step-by-step presentation runbook |
| [`docs/FINAL-JUDGE-QA.md`](./docs/FINAL-JUDGE-QA.md) | 20-question hostile jury Q&A |
| [`docs/BLAST-RADIUS-MODEL.md`](./docs/BLAST-RADIUS-MODEL.md) | Blast radius scoring specification |
| [`docs/REMEDIATION-OPTIMIZATION.md`](./docs/REMEDIATION-OPTIMIZATION.md) | Remediation optimizer specification |
| [`docs/SIH-JUDGE-DEFENSIBILITY.md`](./docs/SIH-JUDGE-DEFENSIBILITY.md) | SIH judge defensibility document |
| [`SECURITY.md`](./SECURITY.md) | Security policy & vulnerability disclosure |
| [`frontend/README.md`](./frontend/README.md) | Frontend architecture & page guide |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. **Fork** the repository
2. **Create** your feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

Please read [`SECURITY.md`](./SECURITY.md) before contributing security-sensitive changes.

---

## 📄 License

This project is licensed under the **MIT License** — see the [`LICENSE`](./LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for Smart India Hackathon 2026**

*Protecting small organizations from third-party access risks — one permission at a time.*

<br/>

⭐ **If AccessGuard helps you, please give it a star!** ⭐

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,12,20&height=100&section=footer" width="100%" />

</div>
