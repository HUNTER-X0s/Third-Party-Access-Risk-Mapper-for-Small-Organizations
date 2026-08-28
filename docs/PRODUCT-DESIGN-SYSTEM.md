# ACCESSGUARD DESIGN SYSTEM (AG-DS)
# Operational Cybersecurity Product Design Specification

**Document Type:** Design System Specification  
**Version:** 1.1  
**Date:** 2026-08-13  
**Status:** Approved Product Specification  

---

## 1. ACCESSGUARD PRODUCT AUTHENTICITY MANDATE

> **The UI must not look like an AI-generated application.**
>
> Do not imitate common AI-generated SaaS interfaces.
>
> **Strictly prohibit defaulting to:**
> - generic dark dashboards
> - excessive cards
> - excessive rounded containers
> - random gradients
> - glassmorphism
> - neon cyberpunk decoration
> - giant KPI tiles
> - generic chatbot interfaces
> - purple/blue AI gradients
> - decorative animation
> - generic component-library styling
>
> Use component libraries only as low-level primitives.
>
> The final interface must have a distinctive AccessGuard information architecture, visual language, typography system, spacing system, status system, interaction model, and security-operations workflow.
>
> Every visual element must serve an information or operational purpose.
>
> The application should feel like a mature cybersecurity product designed by an experienced product and engineering organization.
>
> **Prioritize:**
> - **clarity**
> - **evidence**
> - **density**
> - **hierarchy**
> - **operational usefulness**
> - **consistency**
> - **restraint**
> - **accessibility**
> - **trust**
>
> Do not use "AI-powered" as a substitute for product design.
> **AI is a subsystem of AccessGuard, not the identity of the product.**

---

## 2. Design Philosophy: "Operational Precision"

AccessGuard is an enterprise security operations platform. The interface must evoke calm control, high information density, extreme legibility, and operational trustworthiness.

### Core Operational Principles:
1. **Zero Visual Gimmicks**: Prohibit glowing borders, purple AI gradients, floating background blobs, and decorative rounded cards.
2. **High Information Density**: Prioritize structured tabular data, compact key-value inspection lists, and split-pane investigation drawers over empty padding.
3. **Monospaced Technical Context**: All OAuth scopes, API tokens, IP addresses, database keys, and risk formulas are rendered in monospaced typography (`JetBrains Mono`).
4. **Restrained Color Palette**: High-contrast neutral slate/zinc backgrounds (`slate-950`/`slate-900`) with precise, functional semantic status accents (Red/Amber/Yellow/Emerald).
5. **Immediate Operational Answers**: Every view must immediately answer: *What is risky? Why? What data is exposed? What is the evidence? What is the fix?*

---

## 3. Palette & Tokens

### 3.1 Neutral Base (Dark Slate Operational Canvas)
- **Canvas / Background**: `slate-950` (`#020617`)
- **Surface Layer 1 (Cards/Panels)**: `slate-900` (`#0f172a`)
- **Surface Layer 2 (Hover/Active)**: `slate-800/80` (`#1e293b`)
- **Subtle Borders**: `slate-800` (`#1e293b`) — crisp 1px borders only. No drop shadows.
- **Primary Text**: `slate-100` (`#f8fafc`)
- **Muted Text**: `slate-400` (`#94a3b8`)
- **Faint Text**: `slate-500` (`#64748b`)

### 3.2 Semantic Severity Colors (High-Contrast, Accessible)
- **Critical (Score 85–100)**: Text `red-400` (`#f87171`), BG `red-950/40`, Border `red-800/60`
- **High (Score 65–84)**: Text `orange-400` (`#fb923c`), BG `orange-950/40`, Border `orange-800/60`
- **Medium (Score 40–64)**: Text `yellow-400` (`#facc15`), BG `yellow-950/40`, Border `yellow-800/60`
- **Low (Score 15–39)**: Text `emerald-400` (`#34d399`), BG `emerald-950/40`, Border `emerald-800/60`
- **Info / Clear (Score 0–14)**: Text `slate-400` (`#94a3b8`), BG `slate-900`, Border `slate-800`

---

## 4. Typography System

- **Primary UI Font**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif`
- **Code / Scopes / Technical Font**: `JetBrains Mono`, `Fira Code`, `monospace`

| Style | Font | Size | Weight | Line Height | Case | Usage |
|---|---|---|---|---|---|---|
| Page Title | Inter | 18px | 600 (SemiBold) | 24px | Sentence | View Header |
| Section Header | Inter | 14px | 600 (SemiBold) | 20px | Sentence | Panel Headers |
| Body Text | Inter | 13px | 400 (Regular) | 18px | Sentence | Standard Copy |
| Muted Label | Inter | 11px | 500 (Medium) | 16px | UPPERCASE | Table Headers, Form Labels |
| Monospace Data | Monospace | 12px | 400 (Regular) | 16px | Exact | OAuth Scopes, API Hashes, IDs |
| Severity Badge | Inter | 11px | 600 (SemiBold) | 14px | UPPERCASE | Status Indicators |

---

## 5. Layout Architecture & Information Architecture

### 5.1 Master View Structure
AccessGuard avoids full-page navigation context switches. The primary interface uses a **Split-Pane & Inspection Drawer** layout.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ TOP BAR: Org Switcher | System Health Status | Search | Audit Log | User  │
├──────────────┬──────────────────────────────────────────┬───────────────┤
│ SIDEBAR      │ MAIN CONTENT AREA                        │ INSPECTION    │
│              │                                          │ DRAWER        │
│ 📊 Dashboard │  Compact Header & Global Filters         │ (Contextual)  │
│ 📦 Apps (23) │ ┌──────────────────────────────────────┐ │               │
│ 🏢 Vendors   │ │ Tabular Data View / Graph Canvas     │ │ Finding #104  │
│ 🛡 Risk Map  │ │                                      │ │ ------------- │
│ 🔍 Findings  │ │  - Monospace scopes                  │ │ Score: 84     │
│ ⚡ Remediate │ │  - Compact severity tags             │ │ Evidence Logs │
│ 📄 Reports   │ │  - Direct action triggers            │ │ What-If Simulation│
│ ⚙️ Settings  │ └──────────────────────────────────────┘ │ [Simulate]    │
└──────────────┴──────────────────────────────────────────┴───────────────┘
```

---

## 6. Component Specifications

### 6.1 Tables (Precision Data Views)
- **Header**: `bg-slate-900/90`, text `slate-400`, 11px uppercase tracking-wider.
- **Rows**: 36px height, 1px border bottom (`slate-800`), hover background `bg-slate-800/40`.
- **Numeric/Score Alignment**: Right-aligned, fixed-width tabular numbers.
- **Monospace Columns**: Scope strings, app IDs, timestamps rendered in `font-mono text-xs`.

### 6.2 Contextual Inspection Drawers (Replace Modals)
- Slide-over panel from right (width: 480px or 640px).
- Displays raw evidence, normalization step tree, business purpose comparison, and simulation trigger.
- Dismissable via `Esc` or header close icon.

### 6.3 Filter & Search Bar
- Compact horizontal bar (`h-9`).
- Instant search input with keyboard shortcut (`/` or `Cmd+K`).
- Faceted multi-select dropdowns: *Severity*, *Category*, *Data Sensitivity*, *Authorization Status (Shadow/Approved)*.

---

## 7. Prohibited vs Required UI Reference

```
❌ BAD (AI-Generated Hackathon Look)        ✅ GOOD (AccessGuard SecOps Design)
----------------------------------------    -----------------------------------------
- Generic dark dashboard w/ giant KPI tiles - High-density compact tabular data view
- Huge rounded cards (rounded-3xl)          - Compact, crisp 4px rounded cards (rounded)
- Purple/Pink neon glowing borders          - Neutral 1px slate borders (border-slate-800)
- "✨ AI-Powered Magic Insight!"             - "EVIDENCE: 3 excessive scopes detected"
- Giant centered landing hero graphics      - High-density filterable inventory table
- Full-screen floating modal overlays       - Inline split-pane drawer inspection
- Chatbot bar replacing structured views    - Structured data table w/ advisory drawer
- Glassmorphism & backdrop blur spam        - Opaque slate surface hierarchy (slate-900)
```

---

*AccessGuard Design System v1.1 — Permanent Product Authenticity Standard.*
