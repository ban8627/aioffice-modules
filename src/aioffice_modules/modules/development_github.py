from __future__ import annotations

from typing import Literal

from aioffice_modules.interfaces import ModuleContext, ModuleInput
from aioffice_modules.models import ModuleResult


class DevelopmentGitHubModule:
    name: Literal["development_github"] = "development_github"

    def run(self, context: ModuleContext, module_input: ModuleInput) -> ModuleResult:
        return ModuleResult(
            task_id=context.task_id,
            module=self.name,
            markdown=(
                "# Development and GitHub\n\n"
                "Gate 1 placeholder result. CI, tests, security scanning, PR review, "
                "and no automatic merge remain the default policy."
            ),
            json={
                "promptSummary": module_input.prompt[:160],
                "automationRetries": 3,
                "autoMerge": "disabled",
            },
        )
