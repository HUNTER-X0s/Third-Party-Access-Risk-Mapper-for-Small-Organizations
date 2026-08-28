# 08 — Judge Strategy & Evaluation Guide (Hardened)
# AccessGuard: Hackathon Evaluation, SIH Alignment & Demo Script

**Document Type:** Judge Strategy & Demo Guide  
**Version:** 1.5  
**Date:** 2026-08-13  
**Status:** Approved Competition Strategy  

---

## 1. Hackathon Positioning: "Enterprise SecOps for SMBs"

AccessGuard wins hackathons by avoiding pitch-deck fluff and demonstrating **genuine cybersecurity engineering depth**. 

Judges evaluate AccessGuard as a serious security operations platform built on:
- Deterministic, 5-dimensional risk calculation
- Mathematical formula calibration and versioning
- Immutable evidence provenance chains
- Server-side graph reasoning algorithms
- Clean, operational, non-AI-template design (AG-DS)

---

## 2. High-Impact 5-Minute Demo Script

```
00:00 - 00:45: THE PROBLEM & OPERATIONAL DASHBOARD
  - Open AccessGuard SecOps Dashboard (Compact, Slate Theme).
  - Point out Posture Score (64/100) and 23 Discovered Third-Party Apps.
  - Filter by "Shadow Apps": Highlight an unapproved Slack integration created by a former contractor 14 months ago.

00:45 - 02:00: RISK INTELLIGENCE & EXPLAINABILITY
  - Click on High-Risk Application "Zapier Integration" (Score: 84 / Critical).
  - Open Inspection Drawer: Show 5 Risk Dimensions (Technical, Data Exposure, Vendor, Impact, Attack Path).
  - Show Evidence Provenance: Point to SHA-256 raw payload hash and Google Workspace API collection timestamp.
  - Point out Excess Access: Show that Zapier has `read_email` and `write_files`, whereas its assigned Business Purpose "CRM Sync" only justifies `read_contacts`.

02:00 - 03:15: GRAPH REASONING, ATTACK PATHS & BLAST RADIUS
  - Switch to Risk Map Graph view (React Flow rendering server-side NetworkX topology).
  - Highlight Attack Path: Zapier -> Gmail -> Customer PII Database.
  - Show Blast Radius Calculation: "If Zapier is breached, 4 critical data assets across Finance and Executive departments are exposed."

03:15 - 04:15: WHAT-IF SIMULATION & REMEDIATION
  - Click "Simulate Revocation" on 2 excess permissions (`read_email`, `write_files`).
  - Show Amber Simulation Banner: "⚡ SIMULATION ONLY — Score drops from 84 to 38 (Critical -> Low)."
  - Show Attack Path Disruption: The graph dynamically animates the severed access link to the Customer Database.

04:15 - 05:00: AUDIT EVIDENCE & JUDGE Q&A
  - Click "Export Evidence Package" -> Display professional PDF report with cryptographic hashes.
  - Conclude: "AccessGuard brings enterprise third-party access intelligence to small organizations with zero black box AI and 100% deterministic evidence."
```

---

*Judge Strategy Guide v1.5 — Approved Competition Blueprint.*
