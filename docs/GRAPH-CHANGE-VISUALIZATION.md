# Graph Change Visualization Specification

## Overview

The Access Topology Graph supports three distinct inspection modes:
- **`DELTA`**: Highlights added, modified, and removed relationship paths between snapshot states.
- **`CURRENT`**: Displays the active, authoritative access graph topology.
- **`BASELINE`**: Displays the historical trusted baseline snapshot graph.

---

## Edge Visual Language

| Change State | Visual Treatment | Meaning |
|---|---|---|
| **UNCHANGED** | Solid Slate (`#64748b`), 1.5px | Access relationship existed previously and remains unchanged |
| **NEW** | Solid Emerald (`#10b981`), 2.5px | Relationship newly created (e.g. shadow SaaS or new data reachability) |
| **CHANGED** | Solid Amber (`#f59e0b`), 2.5px | Existing relationship with elevated access (e.g. `READ` → `ADMIN`) |
| **REMOVED** | Dashed Red (`#ef4444`), 1.5px | Relationship present in baseline but revoked/removed |

---

## Changed Edge Inspection

Clicking any highlighted edge in Delta mode opens the **Relationship Change Inspection Drawer**, presenting:
1. Change Type & Severity
2. Access Transition (Before → After)
3. Risk Impact Summary
4. Evidence References (SHA-256 raw evidence anchors)
