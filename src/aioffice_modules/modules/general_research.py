from __future__ import annotations

from typing import Literal

from aioffice_modules.interfaces import ModuleContext, ModuleInput
from aioffice_modules.models import ModuleResult


class GeneralResearchModule:
    name: Literal["general_research"] = "general_research"

    def run(self, context: ModuleContext, module_input: ModuleInput) -> ModuleResult:
        return ModuleResult(
            task_id=context.task_id,
            module=self.name,
            markdown=(
                "# General Research\n\n"
                "Gate 1 placeholder result. Facts, citations, and uncertainty separation "
                "will be implemented after source connectors are approved."
            ),
            json={
                "promptSummary": module_input.prompt[:160],
                "references": list(module_input.references),
                "verificationPolicy": "primary_sources_first",
            },
        )
