from __future__ import annotations

import json
from pathlib import Path
from typing import cast

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


def load_fixture(name: str) -> dict[str, object]:
    return cast(
        dict[str, object],
        json.loads(Path(f"contracts/fixtures/{name}.json").read_text(encoding="utf-8")),
    )


@pytest.mark.parametrize(
    ("name", "scenario"),
    [
        ("research-success", "success"),
        ("research-rate-limited", "rate_limited"),
        ("research-timeout", "timeout"),
        ("research-stale-source", "stale_source"),
        ("research-source-conflict", "source_conflict"),
        ("research-partial", "partial"),
    ],
)
def test_valid_scenario_fixture_matches_deterministic_pipeline(name: str, scenario: str) -> None:
    fixture = load_fixture(name)
    generated, _ = run_mock_research(request(scenario))
    assert canonical_json(fixture) == canonical_json(generated)
    validate_research_result(fixture)


@pytest.mark.parametrize(
    ("name", "reason"),
    [
        ("research-invalid-reference", "unknown or duplicate evidence"),
        ("research-duplicate-id", "Source identifiers must be unique"),
        ("research-version-mismatch", "Unsupported research schema version"),
    ],
)
def test_invalid_fixture_is_rejected_for_expected_reason(name: str, reason: str) -> None:
    with pytest.raises(ResearchContractError, match=reason):
        validate_research_result(load_fixture(name))


def test_simulated_usage_fixture_is_valid_and_has_zero_actual_cost() -> None:
    fixture = load_fixture("research-simulated-usage")
    validate_research_result(fixture)
    usage = fixture["usage"]
    assert isinstance(usage, dict)
    assert usage == {
        "actualCostKrw": 0,
        "estimatedCredits": 5,
        "estimatedRequests": 4,
        "estimatedTokens": 600,
        "simulated": True,
    }


def test_fixtures_are_synthetic_and_pipeline_has_no_network_client() -> None:
    for path in Path("contracts/fixtures").glob("research-*.json"):
        text = path.read_text(encoding="utf-8")
        assert 'actualCostKrw":0' in text
        for locator in [value for value in json.loads(text).get("sources", [])]:
            assert locator["locator"].startswith("https://")
            assert ".test/" in locator["locator"]
    source = Path("src/aioffice_modules/research.py").read_text(encoding="utf-8")
    assert "urlopen(" not in source
    assert "requests." not in source
    assert "httpx." not in source
