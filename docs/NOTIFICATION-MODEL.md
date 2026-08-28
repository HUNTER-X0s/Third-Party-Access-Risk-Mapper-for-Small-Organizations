# Notification Model & Deduplication Specification

## Overview

The `SecurityNotification` model (`backend/app/models/monitoring.py`) and `NotificationEngine` (`backend/app/services/notification_engine.py`) govern alert generation, fingerprint deduplication, and read state tracking for third-party access security events.

---

## Data Model

```python
class SecurityNotification(Base):
    id: str                    # UUID Primary Key
    organization_id: str       # Tenant isolation key
    title: str                 # Human-readable title
    body: str                  # Event summary & context
    severity: str              # Critical, High, Medium, Low, Info
    notification_type: str     # Classification taxonomy
    source_type: str           # CHANGE, INCIDENT, CONNECTOR
    source_id: str             # UUID of generating entity
    fingerprint: str           # SHA-256 hex string
    is_read: bool              # Read status
    read_at: datetime          # Read timestamp
    created_at: datetime       # Creation timestamp
```

---

## Notification Classifications

- `CRITICAL_PERMISSION_ESCALATION`
- `NEW_CROWN_JEWEL_REACHABILITY`
- `HIGH_SHADOW_SAAS`
- `CRITICAL_RISK_SPIKE`
- `NEW_ATTACK_PATH`
- `HIGH_BLAST_RADIUS_INCREASE`
- `CONNECTOR_AUTH_FAILURE`
- `CONNECTOR_STALE`

---

## Deduplication Fingerprint Algorithm

```python
raw = f"{org_id}:{notification_type}:{source_id}:{snapshot_pair}"
fingerprint = hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

If an existing notification with the same `organization_id` and `fingerprint` exists in the database, creation is skipped, preventing alert fatigue across continuous polling cycles.
