# AccessGuard: Hackathon Demo Recovery Runbook

**Purpose:** Instant recovery procedures during live presentations or judging sessions.

---

## 1. Quick Recovery Commands

### A. Reset Database to Clean Demo State
```bash
# In backend directory:
cd backend
.\venv\Scripts\python.exe -c "from app.db.session import engine; from app.db.base_class import Base; from app.db.seed import seed_database, SessionLocal; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine); db=SessionLocal(); seed_database(db); db.close(); print('DEMO RESET COMPLETE')"
```

### B. Start Backend Server
```bash
cd backend
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

### C. Start Frontend Dev Server
```bash
cd frontend
npm run dev
```

---

## 2. Canonical 3-Minute Demo Flow

1. **Login:** Log in as `admin@anurag.tech` / `DemoPass123!`.
2. **Posture & Inventory:** Point out the Security Posture Score (68.4) and breakdown of active third-party apps.
3. **Critical Finding & Graph:** Click on **GitHub Sync Service** (Risk 94.5 / Critical). Open the Access Map to show direct attack path to Crown Jewel source code.
4. **Remediation Simulation:** In the Application Drawer, click **Optimize Remediation** to show minimum effective scope reduction (target: 55.0).
5. **Continuous Monitoring:** Switch to **Monitoring** tab, show snapshot delta and security incidents.
6. **Suppliers & C-SCRM:** Switch to **Suppliers** tab, inspect NIST SP 1326 Due Diligence, Subprocessors, and Single-Supplier Failure Simulator.
7. **AI Security Analyst:** Open the AI Analyst Drawer, ask: *"Explain why GitHub Sync has critical risk"* to demonstrate grounded advisory analysis.
8. **Export:** Click **Export Executive Report** for PDF/printable summary.

---

## 3. Contingency Fallbacks

- **If Gemini API Key is missing or 429 quota is exceeded:** The AI drawer automatically switches to `OFFLINE_DETERMINISTIC_FALLBACK` and returns pre-computed grounded facts.
- **If GitHub App is unconfigured:** All features operate seamlessly on the synthetic demo dataset.
