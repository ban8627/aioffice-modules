from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from aioffice_modules.models import ModuleName, ModuleResult


@dataclass(frozen=True)
class ModuleContext:
    task_id: str
    locale: str = "ko-KR"
    timezone: str = "Asia/Seoul"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModuleInput:
    prompt: str
    references: tuple[str, ...] = ()
    payload: dict[str, Any] = field(default_factory=dict)


class Module(Protocol):
    @property
    def name(self) -> ModuleName:
        """Stable module identifier used in Core contracts."""

    def run(self, context: ModuleContext, module_input: ModuleInput) -> ModuleResult:
        """Run a module without direct database access."""
