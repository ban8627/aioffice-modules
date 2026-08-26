from __future__ import annotations

from typing import Literal

from aioffice_modules.interfaces import ModuleContext, ModuleInput
from aioffice_modules.models import ModuleResult


class ContentDesignModule:
    name: Literal["content_design"] = "content_design"

    def run(self, context: ModuleContext, module_input: ModuleInput) -> ModuleResult:
        return ModuleResult(
            task_id=context.task_id,
            module=self.name,
            markdown=(
                "# Content Design\n\n"
                "Gate 1 placeholder package. Instagram automatic posting and external "
                "asset generation are disabled until platform permissions are approved."
            ),
            json={
                "promptSummary": module_input.prompt[:160],
                "deliverables": ["markdown_brief", "json_metadata"],
                "autoPosting": "disabled",
            },
        )
