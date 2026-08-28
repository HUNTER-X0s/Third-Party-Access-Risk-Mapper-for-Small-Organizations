"""
app/ai/tool_guard.py
Read-only AI tool capability registry.
Enforces architectural capability checks for any tool or query helper exposed to the AI layer.
WRITE, EXECUTE, and arbitrary NETWORK capabilities are strictly forbidden in Phase 6.
"""
import logging
from enum import Enum
from typing import Callable, Dict, Any, List

logger = logging.getLogger(__name__)


class ToolCapability(str, Enum):
    READ_ONLY = "READ_ONLY"
    WRITE = "WRITE"            # Forbidden in Phase 6
    EXECUTE = "EXECUTE"        # Forbidden in Phase 6
    NETWORK = "NETWORK"        # Forbidden in Phase 6


class SecurityViolationError(PermissionError):
    """Raised when an AI tool execution violates the read-only safety policy."""
    pass


class AIToolRegistry:
    """
    Registry of safe, read-only query tools that the AI Security Analyst may invoke.
    Every registered tool MUST declare capability = READ_ONLY.
    """

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, capability: ToolCapability, description: str, fn: Callable):
        """Register a query tool with explicit capability checks."""
        if capability != ToolCapability.READ_ONLY:
            raise SecurityViolationError(
                f"Cannot register tool '{name}' with capability '{capability.value}'. "
                "Phase 6 AI layer strictly permits READ_ONLY tools."
            )
        self._tools[name] = {
            "capability": capability,
            "description": description,
            "function": fn,
        }

    def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool with runtime capability verification."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered in AI Tool Registry.")

        tool_info = self._tools[name]
        if tool_info["capability"] != ToolCapability.READ_ONLY:
            raise SecurityViolationError(f"Tool '{name}' capability violation: forbidden action.")

        logger.info("Executing safe AI query tool: %s", name)
        return tool_info["function"](**kwargs)

    def list_tools(self) -> List[Dict[str, str]]:
        """List all available read-only query tools."""
        return [
            {"name": name, "description": info["description"], "capability": info["capability"].value}
            for name, info in self._tools.items()
        ]
