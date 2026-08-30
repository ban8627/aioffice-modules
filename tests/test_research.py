from __future__ import annotations

import json
from pathlib import Path

import pytest

from aioffice_modules.research import (
    CONTRACT_VERSION,
    ResearchContractError,
    ResearchRequest,
    canonical_json,
    run_mock_research,
    to_core_module_result,
    validate_research_result,
)


def request(scenario: str = "success") -> ResearchRequest:
    return ResearchRequest(
        schema_version=CONTRACT_VERSION,
        request_id=f"request-{scenario}",
        task_id=f"task-{scenario}",
        kind="general_research",
        question="Evaluate the synthetic indicator.",
        created_at="2026-08-30T00:00:00Z",
        scenario=scenario,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    ("scenario", "status", "warning"),
    [
        ("success", "completed", None),
        ("rate_limited", "retryable", "provider_rate_limited"),
        ("timeout", "retryable", "provider_timeout"),
        ("stale_source", "completed", "stale_source"),
        ("source_conflict", "completed", "source_conflict"),
        ("partial", "partial", "partial_result"),
    ],
)
def test_mock_scenarios(scenario: str, status: str, warning: str | None) -> None:
    result, markdown = run_mock_research(request(scenario))
    assert result["status"] == status
    assert warning is None or warning in result["warnings"]
    assert "## Evidence and Sources" in markdown
    assert result["usage"]["actualCostKrw"] == 0
    assert result["usage"]["simulated"] is True


def test_mock_output_is_deterministic_and_builds_core_payload() -> None:
    first = run_mock_research(request())
    second = run_mock_research(request())
    assert canonical_json(first[0]) == canonical_json(second[0])
    payload = to_core_module_result(request(), first[0], first[1])
    assert payload["taskId"] == first[0]["taskId"]
    assert payload["json"] == first[0]
    assert "[evidence-1]" in first[1]


def test_representative_fixture_matches_pipeline() -> None:
    fixture = json.loads(
        Path("contracts/fixtures/research-success.json").read_text(encoding="utf-8")
    )
    result, _ = run_mock_research(request())
    assert canonical_json(fixture) == canonical_json(result)
    validate_research_result(fixture)


def test_invalid_reference_duplicate_id_version_and_unknown_field_are_rejected() -> None:
    invalid = json.loads(
        Path("contracts/fixtures/research-invalid-reference.json").read_text(encoding="utf-8")
    )
    with pytest.raises(ResearchContractError):
        validate_research_result(invalid)
    valid, _ = run_mock_research(request())
    for changed in (
        {**valid, "schemaVersion": "aioffice.research.v0"},
        {**valid, "unexpected": True},
        {**valid, "sources": [valid["sources"][0], valid["sources"][0]]},
    ):
        with pytest.raises(ResearchContractError):
            validate_research_result(changed)


def test_rate_limit_retry_after_and_timeout_are_distinct() -> None:
    rate_limited, _ = run_mock_research(request("rate_limited"))
    timeout, _ = run_mock_research(request("timeout"))
    assert rate_limited["providerOutcomes"][0]["retryAfterSeconds"] == 30
    assert "retryAfterSeconds" not in timeout["providerOutcomes"][0]


def test_unbacked_claim_is_not_rendered_as_fact() -> None:
    timeout, markdown = run_mock_research(request("timeout"))
    assert timeout["claims"] == []
    assert "No evidence-backed claim available" in markdown
