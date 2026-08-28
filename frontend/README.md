# AccessGuard Frontend: Complete Technical Manual & Judge Presentation Guide

> **AccessGuard** · Third-Party Access Risk Mapper & Cyber Supply Chain Risk Intelligence Platform  
> **Institution:** Government College of Engineering, Kalahandi (GCEK) — Smart India Hackathon (SIH) 2026

---

## 📑 Table of Contents
1. [Overview & Visual Design System](#1-overview--visual-design-system)
2. [How to Run the Live Frontend & Backend](#2-how-to-run-the-live-frontend--backend)
3. [Step-by-Step Live Demo Presentation Guide (For Hackathon Judges)](#3-step-by-step-live-demo-presentation-guide-for-hackathon-judges)
4. [Exhaustive Page-by-Page & Feature Reference](#4-exhaustive-page-by-page--feature-reference)
   - [4.1. Top Navigation Bar (Navbar)](#41-top-navigation-bar-navbar)
   - [4.2. Login Page & Quick Role Switcher](#42-login-page--quick-role-switcher)
   - [4.3. Main Dashboard (Executive Overview)](#43-main-dashboard-executive-overview)
   - [4.4. Applications & Inventory Page](#44-applications--inventory-page)
   - [4.5. Security Findings & Live Remediation Simulator](#45-security-findings--live-remediation-simulator)
   - [4.6. Suppliers / Vendors & C-SCRM Due Diligence](#46-suppliers--vendors--c-scrm-due-diligence)
   - [4.7. Cloud Connectors Gateway](#47-cloud-connectors-gateway)
   - [4.8. Continuous Monitoring & Shadow SaaS Page](#48-continuous-monitoring--shadow-saas-page)
5. [Drawers, Modals & Global Floating Tools](#5-drawers-modals--global-floating-tools)
   - [5.1. Application Investigation Drawer](#51-application-investigation-drawer)
   - [5.2. Finding Detail & Proof Drawer](#52-finding-detail--proof-drawer)
   - [5.3. AI Security Analyst (Google Gemini Sandbox)](#53-ai-security-analyst-google-gemini-sandbox)
   - [5.4. In-App Notification Center](#54-in-app-notification-center)
   - [5.5. Executive Report Generator Modal](#55-executive-report-generator-modal)
   - [5.6. User & RBAC Administration Modal](#56-user--rbac-administration-modal)
   - [5.7. Snapshot Graph Comparison Drawer](#57-snapshot-graph-comparison-drawer)
6. [Frontend State Management & Security Architecture](#6-frontend-state-management--security-architecture)
7. [Directory Tree & File Reference](#7-directory-tree--file-reference)

---

## 🎨 1. Overview & Visual Design System

The AccessGuard frontend is a high-performance **React 18 + TypeScript + Vite** Single Page Application (SPA). It is built specifically for SecOps engineers, compliance officers, and IT administrators to replace passive permission spreadsheets with active graph intelligence.

### The Light Enterprise SecOps Design Standard
- **Clean Light Canvas (`#F8F9FB`):** Replaces dark, eye-straining cyberpunk tropes with a modern enterprise workspace look (similar to Datadog, Stripe, or GitHub Enterprise).
- **Crisp White Card Surfaces (`#FFFFFF`):** High contrast, subtle 1px border (`#E5E7EB`), and zero excessive drop-shadows or blurred glassmorphism cards.
- **High Information Density & Scannability:** Standard typography using **Inter** for readable text and **JetBrains Mono** for technical IDs, OAuth scopes, and cryptographic SHA-256 hashes.
- **Restrained Semantic Status Palette:**
  - 🔴 **Critical Severity:** `#DC2626` (Red) / Background `#FEF2F2`
  - 🟠 **High Severity:** `#D97706` (Amber) / Background `#FFFBEB`
  - 🟡 **Medium Severity:** `#CA8A04` (Yellow) / Background `#FEFCE8`
  - 🟢 **Low / Clean:** `#059669` (Emerald) / Background `#ECFDF5`
  - 🔵 **Primary Tech Action:** `#2563EB` (Royal Blue) / Background `#EFF6FF`
  - 🟣 **Advisory AI / Optimizer:** `#7C3AED` (Purple) / Background `#F5F3FF`

---

## 🚀 2. How to Run the Live Frontend & Backend

### Prerequisites
- Node.js (v18+ or v20+)
- Python 3.11 with Virtual Environment (`.\venv`)

### 1. Start the Backend Server (Terminal 1)
```powershell
cd "z:\Third-Party Access Risk Mapper for Small Organizations\backend"
.\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
```
- *Backend is live at:* `http://127.0.0.1:8000`
- *API Docs (Swagger UI):* `http://127.0.0.1:8000/docs`

### 2. Start the Frontend Dev Server (Terminal 2)
```powershell
cd "z:\Third-Party Access Risk Mapper for Small Organizations\frontend"
npm run dev
```
- *Frontend is live at:* `http://localhost:5173`

---

## 🏆 3. Step-by-Step Live Demo Presentation Guide (For Hackathon Judges)

Follow this exact 5-minute sequence during jury evaluation for maximum impact:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              5-MINUTE LIVE DEMO SEQUENCE                               │
├─────────┬──────────────────────┬───────────────────────────────────────────────────────┤
│ Minute  │ Page to Show         │ Action & What to Say to the Judges                    │
├─────────┼──────────────────────┼───────────────────────────────────────────────────────┤
│ 0:00    │ Login Page           │ Click "Pradyumna Biswal (Security Admin)" to login    │
│ 0:45    │ Main Dashboard       │ Explain Posture Score (62.4), 9 Apps & Critical Alert │
│ 1:30    │ Applications Page    │ Click "GitHub Production Sync" → Show Blast Radius    │
│ 2:30    │ Findings Page        │ Open GitHub Finding → Run Remediation Simulator (-31) │
│ 3:30    │ Continuous Monitoring│ Show Shadow SaaS (Canva/Zapier/AI) & 1-Click Approve  │
│ 4:15    │ Suppliers & C-SCRM   │ Show NIST SP 1326 Due Diligence & Priority P0 Queue   │
│ 4:45    │ AI Analyst & Report  │ Trigger AI plain-English summary & Executive Report   │
└─────────┴──────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 🖥️ 4. Exhaustive Page-by-Page & Feature Reference

---

### 4.1. Top Navigation Bar (Navbar)
Located at the top of every screen:

```
[🛡️ AccessGuard] [Anurag Technologies]  [Dashboard] [Applications] [Findings] [Suppliers] [Connectors] [Monitoring]  |  [✨ AI Analyst] [📄 Executive Report] [🔔 3] [👤 Pradyumna Biswal]
```

- **Logo (`🛡️ AccessGuard`):** Clicking returns to the Dashboard.
- **Organization Badge (`Anurag Technologies`):** Displays the currently isolated tenant domain (`anurag.tech`).
- **Navigation Links:** Instant client-side routing to `Dashboard`, `Applications`, `Findings`, `Suppliers`, `Connectors`, and `Monitoring`.
- **Global Search Bar (`Ctrl+K`):** Quickly search apps, scopes, or vendors by name.
- **`✨ AI Analyst` Button:** Opens the slide-over Google Gemini advisory drawer.
- **`📄 Executive Report` Button:** Opens a clean printable report card modal.
- **`🔔 Notification Center Bell` (with red unread badge):** Displays recent real-time security alerts.
- **`👤 User Profile & Role Switcher`:** Displays the logged-in user's name and role (e.g. `Pradyumna Biswal · SECURITY_ADMIN`). Clicking opens the profile & user administration dropdown.

---

### 4.2. Login Page & Quick Role Switcher (`LoginPage.tsx`)

#### What is on this page:
- **Brand Header:** AccessGuard Shield logo and product subtitle.
- **Email & Password Input Fields:** Default credentials pre-populated (`admin@anurag.tech` / `DemoPass123!`).
- **Interactive Password Visibility Toggle (`Eye` / `EyeOff`):** Clicking the eye icon reveals or conceals password characters.
- **Account Lockout Alert:** Automatically warns users if 5 failed login attempts triggered the 15-minute brute-force lockout defense.
- **Hackathon Quick Demo Role Switcher:** 5 colored shortcut buttons designed specifically for jury evaluation:
  1. 🔵 **Pradyumna Biswal (`admin@anurag.tech`):** Security Admin — full SecOps, simulation, and connector rights.
  2. ⚪ **Subankar Swain (`viewer@anurag.tech`):** Viewer — read-only dashboard exploration.
  3. 🟢 **Simran Swain (`auditor@anurag.tech`):** Auditor — read-only findings & SHA-256 evidence verification.
  4. 🟣 **Anurag Swain (`devops@anurag.tech`):** App Owner — restricted strictly to assigned engineering apps (GitHub).
  5. 🔴 **Jahanabi Dalai (`superadmin@anurag.tech`):** Super Admin — full user administration & demo reset capabilities.

#### What to tell the judges:
> *"Our login page enforces enterprise authentication with HttpOnly JWT session cookies and brute-force lockout protection. For evaluation, we built this 1-click role switcher so you can immediately see how the platform enforces least-privilege RBAC across all 5 roles."*

---

### 4.3. Main Dashboard (`DashboardPage.tsx`)

#### What is on this page:

```
┌──────────────────────────────┬──────────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│     TOTAL APPLICATIONS       │     ACTIVE APPLICATIONS      │      SHADOW SAAS APPS        │      CRITICAL FINDINGS       │
│              9               │              8               │              3               │              1               │
│   Connected SaaS Tokens      │    Active Runtime Tokens     │    Unapproved Integrations   │    Immediate Action Needed   │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

1. **Security Posture Score Meter (`62.4 / 100`):**  
   - Calculated deterministically from the organization's aggregated technical risk, exposure, and vendor trust scores.
   - Shows a colored progress bar indicating that the organization is currently in the **Medium-Risk** zone due to 1 critical over-privileged app.
2. **The 4 Metric KPI Cards:**
   - **Total Applications (9):** Complete count of software integrations holding access tokens.
   - **Active Applications (8):** Applications that have exchanged tokens or communicated in the last 30 days.
   - **Shadow SaaS (3):** Unapproved tools connected by employees via SSO without IT approval (*Canva*, *Zapier*, *Unknown AI Tool*).
   - **Critical / High Findings (3):** Total open actionable security vulnerabilities (1 Critical, 2 High).
3. **Risk Distribution Bar:** Visual breakdown showing `1 Critical`, `2 High`, `3 Medium`, `3 Low`.
4. **Top Risky Applications Table:** Immediate view of the 3 highest risk integrations:
   - **GitHub Production Sync** 🔴 `Score: 94.5 (Critical)` · Owner: `cto@anurag.tech`
   - **Zapier Support Automation** 🟠 `Score: 78.2 (High)` · Owner: `support@anurag.tech`
   - **Unknown AI Productivity Tool** 🟠 `Score: 78.0 (High)` · Owner: `unknown@anurag.tech`
5. **Quick Jump Action Buttons:** Direct buttons to *"Investigate Attack Paths"* or *"Simulate Fixes"*.

#### What to tell the judges:
> *"The Dashboard gives SecOps an immediate health check. Notice our posture score is 62.4. In one second, an executive sees that while we have 9 apps, 3 are unapproved Shadow SaaS and 1 has a Critical finding with a risk score of 94.5. Let's investigate that app."*

---

### 4.4. Applications & Inventory Page (`ApplicationsPage.tsx`)

#### What is on this page:
- **Search Bar:** Type any app name (e.g. *"Slack"*, *"GitHub"*, *"Zapier"*) to filter instantly.
- **Provider Filter Badges:** Filter by `All`, `GitHub`, `Google`, `Slack`, `Zapier`, `Canva`, or `Shadow Only`.
- **Applications Table Columns:**
  - **Application Name & Icon:** Displays canonical application name and icon.
  - **Category:** e.g., *Developer Tools*, *Collaboration*, *Workflow Automation*, *Design*.
  - **Authorized By:** Employee email who granted the token (e.g., `cto@anurag.tech`, `cfo@anurag.tech`).
  - **Status Badge:** `Approved (Green)` vs `Shadow SaaS (Amber)` vs `Dormant (Gray)`.
  - **Risk Severity Badge:** `Critical`, `High`, `Medium`, `Low`.
  - **Risk Score:** Precise 0–100 score computed by RiskEngine v1.5.0.
  - **Actions Button:** *"Inspect"* button to open the side drawer.

#### What happens when you click an app (The Application Drawer):
Clicking **"GitHub Production Sync"** slides out `ApplicationDrawer.tsx` on the right side:
- **Metadata Card:** App ID, OAuth Client ID, First Connected Date, Vendor Name (*GitHub Inc.*).
- **Granted Permissions List:** Shows normalized scopes (`admin:org`, `repo:write`, `user:email`).
- **Reachable Data Assets:** Shows that this app has access to **Primary Source Code Repository (Crown Jewel)**.
- **💥 Empirical Blast Radius Assessment:**
  - **Blast Radius Score:** `75.0 [High]`.
  - **Affected Business Processes:** *Software Delivery Process (Criticality 5/5)*.
  - **Affected Users:** *28 users across Engineering, DevOps, and Finance*.

#### What to tell the judges:
> *"Here is our full application inventory. Notice that when I click GitHub Production Sync, our side drawer opens without losing our search filters. AccessGuard doesn't just show permissions—it calculates the exact Blast Radius: 75.0 High, reaching 1 Crown Jewel and affecting 28 enterprise users across 3 departments."*

---

### 4.5. Security Findings & Live Remediation Simulator (`FindingsPage.tsx`)

#### What is on this page:
- **Findings Feed:** Lists all actionable security findings categorized by severity.
- **The Top Finding:**  
  🔴 **CRITICAL:** *Excessive Organization Admin Privilege Granted to GitHub Sync*
  - **Contribution:** `45.0 risk points`.
  - **Affected Asset:** *Primary Source Code Repository*.
  - **Reason:** Business purpose only requires code deployment, but application holds full organization administration.

#### How to run the Live Remediation Simulator (The "WOW" Moment):
1. Click on the Critical GitHub finding card.
2. The `FindingDrawer.tsx` slides out on the right.
3. Scroll down to the **Remediation Simulator** section:
   - **Current Baseline Score:** `100.0` (Maximum Critical Danger).
   - **Active Scopes:** Shows checked boxes for `admin:org` and `repo:status`.
4. **Uncheck the `admin:org` checkbox.**
5. Click the blue **"Simulate Remediation"** button.
6. **Watch the Result in Real Time:**
   - The score instantly drops from **`100.0` down to `68.4` (a 31.6-point drop!)**.
   - Severity changes from 🔴 **Critical** to 🟡 **Medium**.
   - The Remediation Optimizer confirms: *"Remaining scope 'repo:status' satisfies all active CI/CD deployment requirements—zero developer workflow disruption."*
   - An immutable audit log (`SIMULATION_EXECUTED`) is written automatically.

#### Inspecting the SHA-256 Cryptographic Evidence:
- Below the simulator, inspect the **Raw Evidence Provenance Box**:
  - Displays the raw API payload timestamp.
  - Shows the immutable **SHA-256 Hash**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  - Proves to auditors that evidence is cryptographically tamper-proof.

#### What to tell the judges:
> *"This is AccessGuard's most innovative feature: Zero-Disruption Remediation Simulation. In the real world, administrators are afraid to revoke permissions because they might crash CI/CD pipelines. With AccessGuard, the admin unchecks 'admin:org' and clicks Simulate. In under 50 milliseconds, our engine proves the risk drops by 31.6 points while confirming that deployment continues running smoothly."*

---

### 4.6. Suppliers / Vendors & C-SCRM Due Diligence (`VendorsPage.tsx`)

#### What is on this page:
- **Directory of 6 Evaluated Vendors:** GitHub Inc., Google LLC, Slack Technologies, Zapier Inc., Canva Pty Ltd, AI Productivity Inc.
- **NIST SP 1326 5-Component Due Diligence Matrix:**
  1. **FOCI (Foreign Ownership & Control):** Evaluates vendor country of origin and adversary jurisdiction risks.
  2. **Provenance & Subprocessors:** Cloud hosting location (e.g. *AWS US-East*) and 4th-party subprocessor dependencies.
  3. **Resilience:** Documented BCP/DR, verified backup recovery testing, and SLA uptime (99.9%).
  4. **Foundational Cyber Practices:** Enforced MFA, vulnerability management, and encryption in transit/rest.
  5. **Supply Chain Tiers:** Categorized from direct SaaS (Tier 1) down to cloud infrastructure (Tier 3).
- **Automated Priority Review Queue:**  
  - Automatically flags suppliers into **P0 (Urgent)**, **P1 (High)**, or **P2 (Standard)** queues:
    - **P0 (Urgent): GitHub Inc.** — Critical supplier with active Crown Jewel reachability.
    - **P0 (Urgent): Zapier Inc.** — High-criticality supplier with overdue security review.
    - **P1 (High): AI Productivity Inc.** — Unapproved shadow tool with unknown FOCI posture.
- **Hosting Concentration Risk Box:** Analyzes whether too many critical vendors rely on the same cloud availability zone (e.g., AWS US-East-1).

#### What to tell the judges:
> *"In Phase 8, we expanded AccessGuard into full Cyber Supply Chain Risk Management (C-SCRM) aligned with NIST SP 1326 standards. Notice our automated Priority Review Queue: vendors are flagged as P0 not because of human opinion, but because the graph detected that the vendor has an active path to a Crown Jewel database."*

---

### 4.7. Cloud Connectors Gateway (`ConnectorsPage.tsx`)

#### What is on this page:
- **Active Provider Cards:**
  - **GitHub App Connector:** Status `CONNECTED (Green)`, Sync Frequency `900s`, Last Sync `2 mins ago`.
  - **Google Workspace Connector:** Status `CONNECTED (Green)`, Auditing 1 Google Drive & Email integration.
  - **Slack Connector:** Status `CONNECTED (Green)`, Auditing 2 bot integrations.
- **"Sync Now" Action Button:** Triggers an immediate manual background synchronization with provider REST APIs.
- **"Add Connector" Modal:** Guided workflow for IT admins to input OAuth client credentials and configure webhook listeners.

#### What to tell the judges:
> *"Our Connectors page manages live API connections. We can click 'Sync Now' on the GitHub connector to pull fresh OAuth grants in real time and re-evaluate the graph immediately."*

---

### 4.8. Continuous Monitoring & Shadow SaaS Page (`MonitoringPage.tsx`)

#### What is on this page:
- **Real-Time Security Timeline:** Chronological event feed capturing every permission grant, role change, and token issuance in the last 15 minutes.
- **Shadow SaaS Detection Panel:**
  - Lists 3 unapproved integrations discovered via connector telemetry:
    1. **Canva Marketing Team** (`marketing@anurag.tech`) — Dormant design integration.
    2. **Zapier Support Automation** (`support@anurag.tech`) — High-risk tool exporting customer PII.
    3. **Unknown AI Productivity Tool** (`unknown@anurag.tech`) — Unvetted AI productivity integration.
  - **1-Click Administrative Action Buttons:** Admins can click **"Approve"** (marks tool as approved with assigned purpose) or **"Restrict"** (blocks token and updates risk score).
- **Correlated Incidents Panel:** Groups related high-risk findings into structured incident tickets.
- **Snapshot Comparison Button:** Opens the `SnapshotComparisonDrawer.tsx` to compare graph deltas between two time periods.

#### What to tell the judges:
> *"Employees frequently connect AI tools using company logins without telling IT. Our Continuous Monitoring engine detected 3 Shadow SaaS integrations—including an unapproved AI tool exporting data. Administrators can approve or restrict them with a single click."*

---

## 🪟 5. Drawers, Modals & Global Floating Tools

---

### 5.1. Application Investigation Drawer (`ApplicationDrawer.tsx`)
- **Trigger:** Click any row in the Applications table.
- **Capabilities:** Displays application description, authorizing user email, assigned business purpose, complete list of normalized scopes, connected Crown Jewel data assets, and the empirical blast radius breakdown.

---

### 5.2. Finding Detail & Proof Drawer (`FindingDrawer.tsx`)
- **Trigger:** Click any finding card on the Findings page.
- **Capabilities:** Decomposes the 9-factor risk score, displays the SHA-256 evidence provenance record, and hosts the **interactive remediation simulation sandbox**.

---

### 5.3. AI Security Analyst (`AIAnalystDrawer.tsx`)
- **Trigger:** Click the **`✨ AI Analyst`** button in the top navigation bar.
- **Capabilities:**
  - Slide-over chat interface powered by **Google Gemini**.
  - One-click prompt suggestions: *"Explain GitHub risk to executive leadership"*, *"Summarize top 3 attack paths"*, *"Generate remediation plan"*.
  - **Strict Sandboxing Rule:** The AI is advisory only. It **never** calculates risk scores, never overrides authorization, and never executes write actions.

---

### 5.4. In-App Notification Center (`NotificationCenter.tsx`)
- **Trigger:** Click the Bell icon (`🔔`) in the top navbar.
- **Capabilities:**
  - Displays real-time security alerts (e.g. *New Shadow SaaS Detected*, *Critical Finding Triggered*).
  - Unread badge counter synchronizes with backend `GET /api/v1/monitoring/notifications/count`.
  - **"Mark All Read" Button:** Calls `POST /api/v1/monitoring/notifications/read-all` to clear unread counts across all user sessions.

---

### 5.5. Executive Report Generator Modal (`ExecutiveReportModal.tsx`)
- **Trigger:** Click the **`📄 Executive Report`** button in the top navbar.
- **Capabilities:**
  - Generates a clean, formatted executive posture summary card.
  - Displays organizational security score, top 3 risks, blast radius summaries, and compliance mappings (NIST SP 800-161, NIST SP 1326).
  - Ready for immediate printing or PDF export for leadership.

---

### 5.6. User & RBAC Administration Modal (`UserManagementModal.tsx`)
- **Trigger:** Click user profile in top-right → select *"Manage Users"*.
- **Capabilities:** Allows Super Admins (`Jahanabi Dalai`) to view all 5 user accounts, update roles (`SECURITY_ADMIN`, `AUDITOR`, `APP_OWNER`, `VIEWER`), and invite new team members.

---

### 5.7. Snapshot Graph Comparison Drawer (`SnapshotComparisonDrawer.tsx`)
- **Trigger:** Click *"Compare Snapshots"* on the Monitoring page.
- **Capabilities:**
  - Select two snapshots (e.g., *Snapshot A: Baseline* vs *Snapshot B: Post-Remediation*).
  - Graph delta engine highlights **Added Nodes (Green)**, **Removed Nodes (Red)**, and **Modified Risk Edges (Amber)**.

---

## 🔒 6. Frontend State Management & Security Architecture

### 1. Authentication & Session Management (`AuthContext.tsx`)
- On initial page load, the frontend makes an authenticated call to `GET /api/v1/auth/me`.
- If a valid HttpOnly session cookie exists, the user profile (`id`, `email`, `display_name`, `role`, `organization_name`) is restored immediately with zero login prompts.
- `AuthContext` provides global access to `user`, `login()`, `logout()`, and `setDemoUser()`.

### 2. Centralized Typed API Client (`services/api.ts`)
- Implements 23 typed asynchronous API functions covering all CRUD, simulation, graph, vendor, and monitoring endpoints.
- **Anti-CSRF Header Injection:** Every request automatically includes:
  ```typescript
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest', // Anti-CSRF Custom Header
  }
  ```
- **SameSite HttpOnly Cookies:** All requests include `credentials: 'include'` to ensure browser session cookies are securely sent across all API calls.

### 3. Role-Based Access Control (RBAC) Client Enforcement
- The UI dynamically adapts based on the active role:
  - `VIEWER` and `AUDITOR`: Remediation simulation and approve/restrict buttons are disabled with tooltip explanations.
  - `APP_OWNER`: Inventory is filtered strictly to apps owned by that user (`devops@anurag.tech`).
  - `SECURITY_ADMIN` and `SUPER_ADMIN`: Full access to all simulation, connector, and administration controls.

---

## 📂 7. Directory Tree & File Reference

```
frontend/
├── index.html                       # HTML5 entry with Inter & JetBrains Mono fonts
├── package.json                     # Dependencies & build scripts
├── tsconfig.json                    # Strict TypeScript compiler options
├── vite.config.ts                   # Vite bundler with API proxy to localhost:8000
└── src/
    ├── main.tsx                     # React root mount
    ├── index.css                    # Global Tailwind & design token styles
    ├── designTokens.ts              # Color constants, status palettes, and badge styles
    ├── app/
    │   └── App.tsx                  # Main layout, tab switcher, and drawer state manager
    ├── context/
    │   └── AuthContext.tsx          # Session provider & demo role switching
    ├── services/
    │   └── api.ts                   # 23 typed API client functions with anti-CSRF headers
    ├── types/
    │   └── index.ts                 # TypeScript interfaces (Dashboard, Finding, Graph, Vendor)
    ├── pages/
    │   ├── LoginPage.tsx            # Login screen with password eye toggle & demo buttons
    │   ├── DashboardPage.tsx        # Posture score, KPI tiles, and risky apps table
    │   ├── ApplicationsPage.tsx     # Filterable application registry
    │   ├── FindingsPage.tsx         # Security findings & live remediation simulator
    │   ├── VendorsPage.tsx          # NIST SP 1326 C-SCRM due diligence & priority queue
    │   ├── ConnectorsPage.tsx       # Live cloud connectors (GitHub, Google, Slack)
    │   └── MonitoringPage.tsx       # Security changes timeline & Shadow SaaS control
    └── components/
        ├── Navbar.tsx               # Top header bar with search and profile dropdown
        ├── ApplicationDrawer.tsx    # Slide-out application metadata & blast radius panel
        ├── FindingDrawer.tsx        # Slide-out finding investigation & simulator panel
        ├── AIAnalystDrawer.tsx      # Slide-out Google Gemini advisory assistant
        ├── NotificationCenter.tsx   # Slide-out notification feed with 'Mark All Read'
        ├── SnapshotComparisonDrawer.tsx # Side-by-side snapshot graph comparison
        ├── ExecutiveReportModal.tsx # Printable executive summary report card modal
        └── UserManagementModal.tsx   # 5-tier RBAC user administration modal
```

---

## 👥 Team GCE Kalahandi (SIH 2026)

- **Pradyumna Biswal** (`admin@anurag.tech`) — Security Admin
- **Anurag Swain** (`devops@anurag.tech`) — App Owner / Graph Architect
- **Simran Swain** (`auditor@anurag.tech`) — Auditor / Compliance Lead
- **Subankar Swain** (`viewer@anurag.tech`) — Viewer / Frontend Engineer
- **Jahanabi Dalai** (`superadmin@anurag.tech`) — Super Admin / Cloud Security
