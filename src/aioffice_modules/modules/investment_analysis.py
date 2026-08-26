from __future__ import annotations

from typing import Literal

from aioffice_modules.interfaces import ModuleContext, ModuleInput
from aioffice_modules.models import ModuleResult


class InvestmentAnalysisModule:
    name: Literal["investment_analysis"] = "investment_analysis"

    def run(self, context: ModuleContext, module_input: ModuleInput) -> ModuleResult:
        return ModuleResult(
            task_id=context.task_id,
            module=self.name,
            markdown=(
                "# Investment Analysis\n\n"
                "Gate 1 placeholder analysis only. Real brokerage API access remains read-only "
                "and requires approved Core-mediated credentials."
            ),
            json={
                "promptSummary": module_input.prompt[:160],
                "sources": list(module_input.references),
                "orderExecution": "not_supported",
                "dataAccess": "core_api_only",
            },
        )
