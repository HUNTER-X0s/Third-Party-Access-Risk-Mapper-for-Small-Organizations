# AccessGuard — Light Enterprise Design System

**Specification Version:** 1.0.0  
**Status:** Canonical Design Token & Component Reference  
**Visual Philosophy:** Mature Light Enterprise · Product-Led · High Operational Density · Zero AI Gimmicks  

---

## 1. Design Principles

AccessGuard's interface is built on the principles of mature cybersecurity engineering products:

1. **Clarity Over Novelty:** Every visual element serves a direct SecOps operational decision-making purpose.
2. **Light Canvas by Default:** Base canvas `#F8F9FB` / `#F7F8FA`, surface `#FFFFFF`, border `#E5E7EB` (`border-slate-200`).
3. **Calm, Authoritative Color Hierarchy:** High-contrast neutral slates with precise semantic status accents. Primary brand is a deep navy/royal blue (`#3157D5` / `blue-600`).
4. **Selective Typography:** Clean, modern Inter font for all product interfaces; monospace (`JetBrains Mono`) strictly reserved for technical identifiers, cryptographic hashes (SHA-256), raw OAuth scopes, and IDs.
5. **No AI Aesthetic Gimmicks:** No neon glowing borders, no purple gradient blobs, no floating particles, no giant empty cards (`rounded-3xl`), and no chatbot-first takeovers.

---

## 2. Color Palette & Semantic Tokens

### Canvas & Surfaces
| Token | Hex Value | Tailwind Class | Usage |
| :--- | :--- | :--- | :--- |
| `canvas.base` | `#F8F9FB` | `bg-[#F8F9FB]` | Main application viewport background |
| `surface.card` | `#FFFFFF` | `bg-white` | Cards, side drawers, modals, tables |
| `surface.subtle`| `#F1F5F9` | `bg-slate-50` / `bg-slate-100` | Table headers, secondary stat chips, disabled inputs |
| `border.default`| `#E2E8F0` | `border-slate-200` | Default 1px crisp container and table dividers |
| `border.strong` | `#CBD5E1` | `border-slate-300` | Input borders, active element boundaries |

### Typography Colors
| Token | Hex Value | Tailwind Class | Usage |
| :--- | :--- | :--- | :--- |
| `text.primary` | `#0F172A` | `text-slate-900` | Headers, metric values, primary titles |
| `text.secondary`| `#475569` | `text-slate-600` | Body copy, descriptions, table labels |
| `text.muted` | `#94A3B8` | `text-slate-400` | Timestamps, secondary subtitles, metadata |

### Semantic Severity Badges
| Severity | Background | Text | Border | Dot Indicator |
| :--- | :--- | :--- | :--- | :--- |
| **Critical** | `bg-red-50` | `text-red-700` | `border-red-200` | `bg-red-500` |
| **High** | `bg-amber-50` | `text-amber-700` | `border-amber-200` | `bg-amber-500` |
| **Medium** | `bg-yellow-50` | `text-yellow-700` | `border-yellow-200` | `bg-yellow-500` |
| **Low** | `bg-emerald-50` | `text-emerald-700` | `border-emerald-200` | `bg-emerald-500` |
| **Info / Neutral** | `bg-blue-50` | `text-blue-700` | `border-blue-200` | `bg-blue-500` |

---

## 3. Component Specifications

### 3.1 Data Tables (`.ag-table`)
- **Container:** `bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden`
- **Header:** `bg-slate-50/70 border-b border-slate-200 text-slate-500 font-semibold text-[11px] uppercase tracking-wider`
- **Row:** `border-b border-slate-100 hover:bg-slate-50/80 transition-colors cursor-pointer`
- **Typography:** Inter 12px for names/actions; JetBrains Mono 11px for scopes/hashes/IDs.

### 3.2 Slide-Over Context Drawers
- **Width:** 540px to 560px on desktop viewports.
- **Surface:** `bg-white border-l border-slate-200 shadow-2xl`
- **Backdrop:** Light scrim `bg-slate-900/30`
- **Hierarchy:**
  1. Sticky top header with severity badge and title
  2. Scrollable body with structured information blocks
  3. Action buttons (e.g. "Run Simulation", "View in Graph") with distinct visual priority
  4. Immutable SHA-256 evidence provenance footer

### 3.3 Interactive Access Graph
- **Canvas:** Crisp light background (`#FFFFFF` or `#F8F9FB`) with subtle `#CBD5E1` dot grid.
- **Nodes:** White architecture cards with 1px border (`border-slate-200`), rounded corners, clear type badge (App, Scope, Crown Jewel Asset).
- **Edges:** Semantic muted lines (Emerald for added, Amber for changed, Red for critical reachability).

---

## 4. Architectural Guarantee

Frontend styling changes operate exclusively at the presentation and interaction layers. Backend deterministic engines (`RiskEngine v1.5.0`, `GraphEngine`, `BlastRadiusCalculator`, `SnapshotEngine`, `SecurityDiffEngine`, `RemediationOptimizer`, `EvidenceEngine`) and database row-level tenant isolation models remain authoritative and untouched.
