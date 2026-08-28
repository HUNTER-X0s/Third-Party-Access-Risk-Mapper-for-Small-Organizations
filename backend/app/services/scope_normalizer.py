"""
Scope Normalizer Service
Provider-neutral mapping of raw provider OAuth scopes into canonical permissions.
"""

SCOPE_MAPPING_RULES = {
    # Canonical: ADMIN
    "admin:org": ("ADMIN", "Organization Admin", "Full administrative access over organization resources", "Critical"),
    "organization_admin": ("ADMIN", "Organization Admin", "Full administrative access over organization resources", "Critical"),
    "https://www.googleapis.com/auth/admin.directory.user": ("ADMIN", "User Directory Admin", "Full access to manage user directory", "Critical"),
    "Directory.AccessAsApp.All": ("ADMIN", "App Directory Admin", "Full tenant app administration access", "Critical"),
    
    # Canonical: EXPORT / DELETE
    "repo_export": ("EXPORT", "Repository Export", "Export complete source code repositories", "High"),
    "Mail.Export": ("EXPORT", "Mail Export", "Export full mailbox archives", "High"),
    "Customer.Export": ("EXPORT", "Customer Data Export", "Export full customer PII database", "Critical"),
    "https://www.googleapis.com/auth/drive.readonly": ("EXPORT", "Drive Export/Read", "Read/Export all organization files", "High"),
    
    # Canonical: WRITE
    "repo_write": ("WRITE", "Repository Write", "Push code and modify repository settings", "High"),
    "Mail.Send": ("WRITE", "Send Mail", "Send emails on behalf of users", "High"),
    "Files.ReadWrite.All": ("WRITE", "Read & Write Files", "Read and write to all organization files", "High"),
    "Customer.Write": ("WRITE", "Customer Data Write", "Modify customer records", "High"),
    
    # Canonical: READ
    "repo_read": ("READ", "Repository Read", "Read code repositories and issues", "Low"),
    "repo": ("READ", "Repository Access", "Access repository content", "Medium"),
    "Mail.Read": ("READ", "Read Mail", "Read user emails", "Medium"),
    "https://www.googleapis.com/auth/gmail.readonly": ("READ", "Read Gmail", "Read user Gmail messages", "High"),
    "Customer.Read": ("READ", "Read Customer Data", "Read customer contact records", "Medium"),
    "read_user_directory": ("READ", "Read User Directory", "Read basic employee profiles", "Low"),
    "read_calendar": ("READ", "Read Calendar", "Read user calendar events", "Low"),
    "read_contacts": ("READ", "Read Contacts", "Read customer contacts", "Low"),
}

def normalize_scope(raw_scope: str, provider_type: str = "oauth2") -> tuple[str, str, str, str]:
    """
    Normalizes a raw provider scope into (canonical_name, display_name, description, severity).
    Defaults to (READ, display_name, description, Medium) if scope is unknown.
    """
    if raw_scope in SCOPE_MAPPING_RULES:
        return SCOPE_MAPPING_RULES[raw_scope]
    
    # Heuristic fallback matching
    raw_lower = raw_scope.lower()
    if "admin" in raw_lower or "manage" in raw_lower:
        return ("ADMIN", f"Admin Access ({raw_scope})", f"Administrative scope: {raw_scope}", "Critical")
    elif "write" in raw_lower or "send" in raw_lower or "modify" in raw_lower:
        return ("WRITE", f"Write Access ({raw_scope})", f"Modify scope: {raw_scope}", "High")
    elif "export" in raw_lower or "download" in raw_lower:
        return ("EXPORT", f"Export Access ({raw_scope})", f"Export scope: {raw_scope}", "High")
    elif "delete" in raw_lower or "remove" in raw_lower:
        return ("DELETE", f"Delete Access ({raw_scope})", f"Deletion scope: {raw_scope}", "Critical")
    else:
        return ("READ", f"Read Access ({raw_scope})", f"Read scope: {raw_scope}", "Low")
