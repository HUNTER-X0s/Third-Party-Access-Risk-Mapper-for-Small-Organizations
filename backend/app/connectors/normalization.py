"""
connectors/normalization.py
GitHub → AccessGuard canonical permission mapping.
Based on official GitHub App permission semantics, API version 2022-11-28.
Reference: https://docs.github.com/en/rest/overview/permissions-required-for-github-apps

NORMALIZATION_VERSION = "1.0.0"
Any change to this mapping MUST increment the version and document in PHASE-5-NORMALIZATION-MAP.md.
"""
import re
import hashlib
import json
from typing import Any, Dict, List, Tuple
from app.connectors.models import (
    NormalizedPermission, CanonicalPermission, NormalizationStatus
)

NORMALIZATION_VERSION = "1.0.0"

# Secret field names to redact from evidence payloads before persistence.
# Prevents private keys, tokens, or credentials appearing in the database.
_SECRET_FIELD_PATTERNS = re.compile(
    r"(authorization|token|access_token|refresh_token|private_key|client_secret|"
    r"pem|bearer|password|credential|secret)",
    re.IGNORECASE
)

# -------------------------------------------------------------------------
# GitHub permission mapping table
# Source: https://docs.github.com/en/rest/overview/permissions-required-for-github-apps
# Format: (resource, access_level) -> (CanonicalPermission, severity, notes)
# -------------------------------------------------------------------------
GITHUB_PERMISSION_MAP: Dict[Tuple[str, str], Tuple[CanonicalPermission, str, str]] = {
    # Contents
    ("contents", "read"):          (CanonicalPermission.READ,      "LOW",      "Read repository contents"),
    ("contents", "write"):         (CanonicalPermission.WRITE,     "HIGH",     "Write to repository contents"),

    # Metadata (always required by GitHub Apps)
    ("metadata", "read"):          (CanonicalPermission.READ,      "INFO",     "Required metadata read — always granted"),

    # Administration
    ("administration", "read"):    (CanonicalPermission.READ,      "MEDIUM",   "Read org/repo settings"),
    ("administration", "write"):   (CanonicalPermission.ADMIN,     "CRITICAL", "Full admin control of repository/organization"),

    # Members
    ("members", "read"):           (CanonicalPermission.READ,      "MEDIUM",   "Read organization members"),
    ("members", "write"):          (CanonicalPermission.WRITE,     "HIGH",     "Manage organization members"),

    # Issues
    ("issues", "read"):            (CanonicalPermission.READ,      "LOW",      "Read issues"),
    ("issues", "write"):           (CanonicalPermission.WRITE,     "MEDIUM",   "Create and manage issues"),

    # Pull requests
    ("pull_requests", "read"):     (CanonicalPermission.READ,      "LOW",      "Read pull requests"),
    ("pull_requests", "write"):    (CanonicalPermission.WRITE,     "MEDIUM",   "Manage pull requests"),

    # Actions / Workflows
    ("actions", "read"):           (CanonicalPermission.READ,      "MEDIUM",   "Read CI/CD actions and logs"),
    ("actions", "write"):          (CanonicalPermission.EXECUTE,   "HIGH",     "Trigger and manage CI/CD workflows"),

    # Secrets
    ("secrets", "read"):           (CanonicalPermission.READ,      "CRITICAL", "Read repository/org secrets"),
    ("secrets", "write"):          (CanonicalPermission.WRITE,     "CRITICAL", "Create/update secrets — potential credential exposure"),

    # Code scanning / security
    ("security_events", "read"):   (CanonicalPermission.READ,      "MEDIUM",   "Read security alerts"),
    ("security_events", "write"):  (CanonicalPermission.WRITE,     "HIGH",     "Manage security alerts"),

    # Environments
    ("environments", "read"):      (CanonicalPermission.READ,      "LOW",      "Read deployment environments"),
    ("environments", "write"):     (CanonicalPermission.CONFIGURE, "HIGH",     "Manage deployment environments"),

    # Deployments
    ("deployments", "read"):       (CanonicalPermission.READ,      "LOW",      "Read deployments"),
    ("deployments", "write"):      (CanonicalPermission.EXECUTE,   "HIGH",     "Trigger deployments"),

    # Pages
    ("pages", "read"):             (CanonicalPermission.READ,      "LOW",      "Read GitHub Pages"),
    ("pages", "write"):            (CanonicalPermission.WRITE,     "MEDIUM",   "Manage GitHub Pages"),

    # Packages
    ("packages", "read"):          (CanonicalPermission.READ,      "MEDIUM",   "Read package registry"),
    ("packages", "write"):         (CanonicalPermission.WRITE,     "HIGH",     "Publish/delete packages"),

    # Checks
    ("checks", "read"):            (CanonicalPermission.READ,      "LOW",      "Read CI check results"),
    ("checks", "write"):           (CanonicalPermission.WRITE,     "MEDIUM",   "Create and update CI checks"),

    # Commit statuses
    ("statuses", "read"):          (CanonicalPermission.READ,      "LOW",      "Read commit statuses"),
    ("statuses", "write"):         (CanonicalPermission.WRITE,     "LOW",      "Update commit statuses"),

    # Webhooks
    ("repository_hooks", "read"):  (CanonicalPermission.READ,      "MEDIUM",   "Read repository webhooks"),
    ("repository_hooks", "write"): (CanonicalPermission.CONFIGURE, "HIGH",     "Manage repository webhooks — potential data exfiltration"),
    ("organization_hooks", "read"): (CanonicalPermission.READ,     "HIGH",     "Read org-level webhooks"),
    ("organization_hooks", "write"): (CanonicalPermission.ADMIN,   "CRITICAL", "Manage org webhooks — organization-wide data routing"),

    # Team discussions
    ("team_discussions", "read"):  (CanonicalPermission.READ,      "LOW",      "Read team discussions"),
    ("team_discussions", "write"): (CanonicalPermission.WRITE,     "MEDIUM",   "Manage team discussions"),

    # Organization projects
    ("organization_projects", "read"):  (CanonicalPermission.READ,  "LOW",     "Read org projects"),
    ("organization_projects", "write"): (CanonicalPermission.WRITE, "MEDIUM",  "Manage org projects"),
    ("organization_projects", "admin"): (CanonicalPermission.ADMIN, "HIGH",    "Admin org projects"),

    # Organization plan
    ("organization_plan", "read"): (CanonicalPermission.READ,      "MEDIUM",   "Read org billing/plan details"),

    # Single file
    ("single_file", "read"):       (CanonicalPermission.READ,      "MEDIUM",   "Read a specific configured file"),
    ("single_file", "write"):      (CanonicalPermission.WRITE,     "HIGH",     "Write a specific configured file"),

    # Email addresses
    ("emails", "read"):            (CanonicalPermission.READ,      "MEDIUM",   "Read user email addresses — PII"),
    ("emails", "write"):           (CanonicalPermission.WRITE,     "HIGH",     "Manage user email addresses — PII"),

    # Followers
    ("followers", "read"):         (CanonicalPermission.READ,      "LOW",      "Read followers"),
    ("followers", "write"):        (CanonicalPermission.WRITE,     "LOW",      "Manage followers"),

    # Git SSH keys
    ("keys", "read"):              (CanonicalPermission.READ,      "HIGH",     "Read SSH keys"),
    ("keys", "write"):             (CanonicalPermission.WRITE,     "CRITICAL", "Manage SSH keys — authentication credential access"),

    # GPG keys
    ("gpg_keys", "read"):          (CanonicalPermission.READ,      "MEDIUM",   "Read GPG keys"),
    ("gpg_keys", "write"):         (CanonicalPermission.WRITE,     "HIGH",     "Manage GPG keys"),
}


def normalize_github_permissions(raw_permissions: Dict[str, str]) -> List[NormalizedPermission]:
    """
    Normalize a dict of GitHub permission key→level into NormalizedPermission objects.
    Unknown permissions are NOT silently dropped or mapped to READ — they surface as UNKNOWN.
    """
    result = []
    for resource, level in raw_permissions.items():
        key = (resource.lower(), level.lower())
        if key in GITHUB_PERMISSION_MAP:
            canonical, severity, notes = GITHUB_PERMISSION_MAP[key]
            result.append(NormalizedPermission(
                raw_provider_key=resource,
                raw_provider_value=level,
                canonical_permission=canonical,
                normalization_status=NormalizationStatus.NORMALIZED,
                normalization_version=NORMALIZATION_VERSION,
                severity=severity,
                notes=notes,
            ))
        else:
            # UNKNOWN — conservative handling. Surfaces for review. Critical finding potential.
            result.append(NormalizedPermission(
                raw_provider_key=resource,
                raw_provider_value=level,
                canonical_permission=CanonicalPermission.UNKNOWN,
                normalization_status=NormalizationStatus.UNKNOWN,
                normalization_version=NORMALIZATION_VERSION,
                severity="HIGH",   # Conservative — assume impactful until mapped
                notes=f"Unknown GitHub permission '{resource}:{level}' — requires manual mapping review.",
            ))
    return result


def redact_secrets(payload: Any) -> Any:
    """
    Recursively redact secret field values from a payload before evidence persistence.
    Matches field names against known secret patterns.
    """
    if isinstance(payload, dict):
        return {
            k: "[REDACTED]" if _SECRET_FIELD_PATTERNS.search(str(k)) else redact_secrets(v)
            for k, v in payload.items()
        }
    elif isinstance(payload, list):
        return [redact_secrets(item) for item in payload]
    return payload


def compute_evidence_hash(payload: Any) -> str:
    """SHA-256 hash of the canonicalized, redacted payload for tamper-evident evidence."""
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()
