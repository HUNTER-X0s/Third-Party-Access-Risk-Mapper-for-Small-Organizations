# Phase 8 Supply Chain Graph Specification

**Status:** Authoritative  
**Endpoint:** `GET /api/v1/graph/supply-chain`  
**Alignment:** NIST SP 800-161 Rev. 1, NIST SP 1326

---

## 1. Graph Topology and Hierarchy

The Supply Chain Graph extends the AccessGuard Graph Engine to represent multi-tiered supply chain dependencies:

```
                  [Organization] (Level 0 - Internal)
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
 [Tier 1 Vendor: GitHub]        [Tier 1 Vendor: Google]
        │                                 │
   ┌────┴────────────┐                    │
   ▼                 ▼                    ▼
[Tier 2 Sub: Azure] [Tier 3 Sub: Fastly] [Tier 2 Sub: GCP]
```

---

## 2. Node Schema

Each node in the supply chain graph carries structured provenance metadata:

```json
{
  "id": "vendor-uuid",
  "type": "vendor",
  "data": {
    "label": "GitHub",
    "tier": 1,
    "criticality": "CRITICAL",
    "supplier_risk": 20.0,
    "trust_boundary": "TIER_1_SUPPLIER"
  },
  "position": { "x": 280, "y": 180 }
}
```

```json
{
  "id": "sub-uuid",
  "type": "subprocessor",
  "data": {
    "label": "Microsoft Azure",
    "service": "Cloud Hosting & CDN",
    "tier": 2,
    "verification": "VERIFIED",
    "trust_boundary": "TIER_2_SUBPROCESSOR"
  },
  "position": { "x": 250, "y": 380 }
}
```

---

## 3. Edge Styling & Verification

- **Tier 1 Direct Supplier Edges**: Solid slate stroke (`#64748b`, width: 2px)
- **Subprocessor Edges**: Dashed slate stroke (`#94a3b8`, strokeDasharray: "4 4") labeled with verification status (`VERIFIED`, `DECLARED`, `INFERRED`).
