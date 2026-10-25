"""Extensible tool registry with risk classification and idempotency metadata."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    required_permissions: list[str] = field(default_factory=list)
    risk: RiskLevel = RiskLevel.LOW
    timeout_seconds: int = 30
    idempotent: bool = False
    implementation: Optional[Callable[..., Any]] = None
    result_schema: Optional[dict[str, Any]] = None
    verification_strategy: str = "none"
    audit_required: bool = False


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def list(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def has_permission(self, name: str, user_permissions: list[str]) -> bool:
        spec = self._tools.get(name)
        if spec is None:
            return False
        return all(p in user_permissions for p in spec.required_permissions)


tool_registry = ToolRegistry()
