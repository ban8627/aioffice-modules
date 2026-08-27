from aioffice_modules.interfaces import Module, ModuleContext, ModuleInput
from aioffice_modules.modules import (
    ContentDesignModule,
    DevelopmentGitHubModule,
    GeneralResearchModule,
    InvestmentAnalysisModule,
)


def test_all_modules_return_markdown_and_json_contracts() -> None:
    context = ModuleContext(task_id="task_1")
    module_input = ModuleInput(prompt="Summarize the approved Gate 1 shape.")

    modules: list[Module] = [
        InvestmentAnalysisModule(),
        GeneralResearchModule(),
        ContentDesignModule(),
        DevelopmentGitHubModule(),
    ]

    for module in modules:
        result = module.run(context, module_input)
        contract = result.to_contract()

        assert contract["taskId"] == "task_1"
        assert contract["markdown"].startswith("# ")
        assert isinstance(contract["json"], dict)
        assert contract["module"] == module.name
