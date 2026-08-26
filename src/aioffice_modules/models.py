from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

ModuleName = Literal[
    "investment_analysis",
    "general_research",
    "content_design",
    "development_github",
]


@dataclass(frozen=True)
class ModuleResult:
    task_id: str
    module: ModuleName
    markdown: str
    json: dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_contract(self) -> dict[str, Any]:
        return {
            "taskId": self.task_id,
            "module": self.module,
            "markdown": self.markdown,
            "json": self.json,
            "createdAt": self.created_at,
        }
