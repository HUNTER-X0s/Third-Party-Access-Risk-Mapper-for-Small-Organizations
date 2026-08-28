"""
test_ai_tool_guard.py
Tests AIToolRegistry capability enforcement (READ_ONLY permitted, WRITE/EXECUTE rejected).
"""
import pytest
from app.ai.tool_guard import AIToolRegistry, ToolCapability, SecurityViolationError


def test_ai_tool_registry_allows_read_only_tools():
    """AIToolRegistry allows registering and executing READ_ONLY query tools."""
    registry = AIToolRegistry()
    registry.register_tool(
        name="get_app_score",
        capability=ToolCapability.READ_ONLY,
        description="Query app risk score",
        fn=lambda app_id: {"app_id": app_id, "score": 94.5}
    )

    res = registry.execute_tool("get_app_score", app_id="app-1")
    assert res["score"] == 94.5


def test_ai_tool_registry_rejects_write_capability():
    """AIToolRegistry raises SecurityViolationError if registering WRITE or EXECUTE tools."""
    registry = AIToolRegistry()

    with pytest.raises(SecurityViolationError, match="strictly permits READ_ONLY"):
        registry.register_tool(
            name="revoke_permission_tool",
            capability=ToolCapability.WRITE,
            description="Revoke scope",
            fn=lambda: None
        )

    with pytest.raises(SecurityViolationError, match="strictly permits READ_ONLY"):
        registry.register_tool(
            name="execute_remediation_tool",
            capability=ToolCapability.EXECUTE,
            description="Execute mutation",
            fn=lambda: None
        )
