# AccessGuard Hackathon Demo Presentation Runbook

**Document Type:** Operator & Presenter Guide  
**Version:** 3.0.0  
**Target Viewport:** 1920x1080 / 1440x900 (Laptop / Projector Mode)  
**Demo Duration:** 3 – 5 Minutes  
**Mode:** DEMO / SIMULATED ENVIRONMENT (100% Offline Compatible)  

---

## 1. Quick Startup & Clean State Setup

Execute the following commands in PowerShell before starting the presentation:

```powershell
# 1. Clean stale DB files
Remove-Item -Path "." -Filter "*.db" -Force -ErrorAction SilentlyContinue

# 2. Start Backend Server (Port 8000)
$env:PYTHONPATH="backend"
.\backend\venv\Scripts\uvicorn app.main:app --port 8000 --reload

# 3. Start Frontend (Port 5173) in separate terminal
cd frontend
npm run dev

# 4. Open browser to http://localhost:5173
```

---

## 2. Canonical Presentation Sequence (Anurag Technologies Scenario)

### Step 1: Opening & Context (20 – 30 Seconds)
- **Visual:** `Dashboard` Page (`http://localhost:5173`)
- **Presenter Wording:**
  > *"AccessGuard is an evidence-backed third-party access intelligence platform built specifically for small organizations. Small companies rely heavily on OAuth integrations like GitHub, Zapier, and Google Workspace, but often lack visibility into what sensitive data those integrations can actually reach."*
- **Highlight on Screen:** Point out the **Organization Access Posture Score: 62.4 / 100 (HIGH RISK)** banner and the deterministic badge.

---

### Step 2: Discovery & Priority Queue (30 – 45 Seconds)
- **Visual:** Dashboard `Top Remediation Priorities Queue` (P0, P1, P2)
- **Presenter Wording:**
  > *"Rather than drowning administrators in dozens of generic alerts, AccessGuard prioritizes actionable risk. Notice our P0 Critical Priority: GitHub Production Sync has a critical risk score of 94.5 and exposes our Source Code Crown Jewel asset."*
- **Action:** Click on the **GitHub P0 Priority Card** or select **GitHub Production Sync** under High Risk Integrations to open the `ApplicationDrawer`.

---

### Step 3: Application Investigation & Evidence (60 Seconds)
- **Visual:** `ApplicationDrawer` (Split-Pane View)
- **Presenter Wording:**
  > *"Let's investigate GitHub. Under declared business purpose, this integration only requires read-only access for CI/CD builds. However, looking at granted scopes: it holds `organization_admin`—full administrative control over our entire organization. AccessGuard flags `organization_admin` as an excessive privilege."*
- **Action:** Point out the **Reachable Crown Jewel Data Asset** (*Source Code & Prop Algorithms*) and show the SHA-256 evidence integrity status (`VERIFIED_INTACT`).

---

### Step 4: Attack Path & Blast Radius (30 – 45 Seconds)
- **Visual:** Click **Risk Map** tab (`AccessGraphView`) or view Blast Radius card.
- **Presenter Wording:**
  > *"AccessGuard maps third-party access into an attack graph. If an attacker compromises GitHub's OAuth token, they gain an unhindered potential access path directly to our Source Code Crown Jewel, directly impacting our Software Delivery Process. Our Blast Radius engine calculates an organizational damage score of 75.0 / 100."*
- **Highlight on Screen:** Show the 4 blast factors (+30 Crown Jewel, +10 Sensitive Asset, +20 Critical Processes, +15 User Exposure = 75.0).

---

### Step 5: Minimum Effective Remediation Simulation (45 Seconds)
- **Visual:** Click **Findings** -> Open **Excessive Organization Admin Privilege** Finding Drawer.
- **Presenter Wording:**
  > *"Instead of asking the admin to delete the entire integration, AccessGuard's Minimum Effective Remediation engine calculates the smallest scope revocation set required to bring risk below policy threshold. Clicking 'Simulate Candidate Remediation'..."*
- **Action:** Click **Simulate Candidate Remediation**.
- **Highlight Result:**
  - Current Risk: **94.5 (Critical)** → Simulated Residual Risk: **53.6 (Medium)**
  - Risk Reduction: **-40.9 pts (43.3% reduction)**
  - Blast Radius: **75.0 → 50.0 (Reduction: 25.0 pts)**
  - Target Achieved: **YES (53.6 ≤ 55.0)**
  - Highly visible safety badge: `⚡ SIMULATION ONLY — NO PROVIDER CHANGES EXECUTED`

---

### Step 6: Posture History & Executive Reporting (30 Seconds)
- **Visual:** Click **Analyze Posture Delta** or click **Executive Report** in Navbar.
- **Presenter Wording:**
  > *"Finally, AccessGuard tracks posture change over time with Security Snapshots and generates deterministic, audit-ready Executive Security Summaries formatted for CISOs and board members."*
- **Action:** Click **Executive Report** to render the modal preview.

---

## 3. Authoritative Expected Values Matrix

Verify these exact numbers during your demo prep:

| Metric / Screen | Expected Value |
|---|---|
| Organization Posture Score | **62.4 / 100** |
| GitHub Application Risk | **94.5 (Critical)** |
| GitHub Current Blast Radius | **75.0 / 100 (High)** |
| GitHub Post-Remediation Blast Radius | **50.0 / 100 (Medium)** |
| Blast Radius Reduction | **25.0 pts** |
| Simulated Residual Risk | **53.6 (Medium)** |
| Target Policy Threshold | **55.0** (`is_target_achieved: True`) |
| Evidence Hash Verification | **`VERIFIED_INTACT`** |

---

## 4. Deterministic Demo Reset & Recovery Procedure

If during the presentation you need to reset the data back to the clean baseline:

1. Click **Reset Demo** in the top right of the navigation bar.
2. Confirm the browser prompt (*"Reset AccessGuard demo database to canonical dataset?"*).
3. The database will drop/reseed instantly and display the toast notification:  
   `✓ Demo database reset to canonical Anurag Technologies dataset.`

---

## 5. Offline & Fallback Safeguards

- **100% Local Execution:** AccessGuard requires zero internet connection, zero external API keys, and zero active cloud tokens.
- **AI Independence:** The AI Security Analyst layer is strictly advisory/optional and sandboxed. The core risk, graph, blast radius, evidence, and remediation engines run 100% deterministically on Python SQLite.
- **No Third-Party Rate Limits:** Demo seeds are embedded directly in `backend/app/db/seed.py`.

---

*AccessGuard Hackathon Demo Runbook v3.0.0 — Ready for Presentation.*
