from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest

from aioffice_modules.official_data import (
    Capability,
    EcosMockAdapter,
    FredMockAdapter,
    OfficialDataContractError,
    OfficialDataProvider,
    OfficialDataRequest,
    OpenDartMockAdapter,
    Provider,
    canonical_json,
    render_official_data_markdown,
    to_core_module_result,
    to_research_result,
    validate_official_data_request,
    validate_official_data_result,
)


def make_request(provider: str, scenario: str = "success") -> OfficialDataRequest:
    capability = {
        "fred": "series_observations",
        "ecos": "statistics_observations",
        "opendart": "filing_facts",
    }[provider]
    return OfficialDataRequest(
        "request-synthetic",
        "task-synthetic",
        cast(Provider, provider),
        cast(Capability, capability),
        scenario=scenario,
    )


def load_fixture(name: str) -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(Path(f"contracts/fixtures/{name}.json").read_text()),
    )


@pytest.mark.parametrize(
    ("provider", "scenario", "status"),
    [
        ("fred", "success", "completed"),
        ("fred", "rate_limited", "retryable"),
        ("fred", "stale", "completed"),
        ("fred", "revised", "completed"),
        ("fred", "license_review_required", "completed"),
        ("ecos", "success", "completed"),
        ("ecos", "timeout", "retryable"),
        ("ecos", "unavailable", "retryable"),
        ("ecos", "malformed_response", "failed"),
        ("ecos", "attribution_review_required", "completed"),
        ("opendart", "success", "completed"),
        ("opendart", "rate_limited", "retryable"),
        ("opendart", "empty_result", "failed"),
        ("opendart", "invalid_configuration", "failed"),
        ("opendart", "filing_fact_normalization", "completed"),
    ],
)
def test_deterministic_provider_scenarios(provider: str, scenario: str, status: str) -> None:
    adapter: OfficialDataProvider = {
        "fred": FredMockAdapter(),
        "ecos": EcosMockAdapter(),
        "opendart": OpenDartMockAdapter(),
    }[provider]
    first = adapter.collect(make_request(provider, scenario))
    second = adapter.collect(make_request(provider, scenario))
    assert first["status"] == status
    assert canonical_json(first) == canonical_json(second)
    assert first["usage"]["actualCostKrw"] == 0
    assert first["usage"]["simulated"] is True


def test_shared_fred_fixture_validates_and_converts_without_http() -> None:
    fixture = json.loads(Path("contracts/fixtures/official-data-fred-success.json").read_text())
    validate_official_data_result(fixture)
    markdown = render_official_data_markdown(fixture)
    research = to_research_result(fixture)
    envelope = to_core_module_result(fixture)
    assert "[observation-fred]" in markdown
    assert research["evidence"][0]["sourceId"] == research["sources"][0]["sourceId"]
    assert envelope["json"] == fixture
    assert envelope["module"] == "general_research"


def test_invalid_capability_reference_version_unknown_fields_and_duplicates() -> None:
    with pytest.raises(OfficialDataContractError):
        validate_official_data_request(load_fixture("official-data-invalid-capability"))
    with pytest.raises(OfficialDataContractError):
        validate_official_data_result(load_fixture("official-data-invalid-reference"))
    valid = load_fixture("official-data-fred-success")
    changes: list[dict[str, Any]] = [
        {**valid, "schemaVersion": "aioffice.official-data.v0"},
        {**valid, "unknown": True},
        {**valid, "sources": [valid["sources"][0], valid["sources"][0]]},
        {**valid, "observations": [valid["observations"][0], valid["observations"][0]]},
    ]
    for changed in changes:
        with pytest.raises(OfficialDataContractError):
            validate_official_data_result(changed)


def test_partial_multi_provider_is_composed_without_weakening_provider_contracts() -> None:
    fred = FredMockAdapter().collect(make_request("fred"))
    ecos = EcosMockAdapter().collect(make_request("ecos", "timeout"))
    combined: dict[str, Any] = {"status": "partial", "results": [fred, ecos]}
    assert combined["status"] == "partial"
    assert [item["provider"] for item in combined["results"]] == ["fred", "ecos"]
    assert ecos["providerOutcomes"][0]["retryable"] is True


def test_attribution_boundaries_are_explicit_and_no_quota_is_hardcoded() -> None:
    fred = FredMockAdapter().collect(make_request("fred", "license_review_required"))
    ecos = EcosMockAdapter().collect(make_request("ecos", "attribution_review_required"))
    dart = OpenDartMockAdapter().collect(make_request("opendart"))
    assert "no endorsement" in fred["sources"][0]["attribution"]["notice"]
    assert "redistribution" in ecos["sources"][0]["attribution"]["notice"]
    assert "changing limits" in dart["sources"][0]["attribution"]["notice"]
    source = Path("src/aioffice_modules/official_data.py").read_text()
    assert "20000" not in source and "20,000" not in source and "020" not in source


def test_shared_contract_artifacts_have_canonical_json_and_sha256() -> None:
    for name in (
        "official-data-request.schema.json",
        "official-data-result.schema.json",
    ):
        data = Path(f"contracts/schemas/{name}").read_bytes()
        assert len(hashlib.sha256(data).hexdigest()) == 64
        assert canonical_json(json.loads(data))
    data = Path("contracts/fixtures/official-data-fred-success.json").read_bytes()
    assert len(hashlib.sha256(data).hexdigest()) == 64


def test_mock_implementation_has_no_network_or_database_client() -> None:
    source = Path("src/aioffice_modules/official_data.py").read_text()
    for forbidden in ("requests.", "httpx.", "urlopen(", "supabase", "api_key", "access_token"):
        assert forbidden not in source.lower()
