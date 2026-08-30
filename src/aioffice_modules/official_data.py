from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Protocol
from urllib.parse import urlparse

CONTRACT_VERSION = "aioffice.official-data.v1"
Provider = Literal["fred", "ecos", "opendart"]
Capability = Literal[
    "series_observations",
    "release_metadata",
    "statistics_observations",
    "disclosure_list",
    "filing_facts",
]
CAPABILITIES: dict[str, set[str]] = {
    "fred": {"series_observations", "release_metadata"},
    "ecos": {"statistics_observations"},
    "opendart": {"disclosure_list", "filing_facts"},
}
OUTCOMES = {
    "success",
    "rate_limited",
    "timeout",
    "unavailable",
    "invalid_configuration",
    "malformed_response",
    "empty_result",
    "failed",
}
WARNINGS = {
    "stale_source",
    "revised_observation",
    "license_review_required",
    "attribution_review_required",
    "provider_rate_limited",
    "provider_timeout",
    "provider_unavailable",
    "empty_result",
    "partial_result",
}


class OfficialDataContractError(ValueError):
    pass


@dataclass(frozen=True)
class OfficialDataRequest:
    request_id: str
    task_id: str
    provider: Provider
    capability: Capability
    requested_at: str = "2026-08-30T00:00:00Z"
    scenario: str = "success"

    def to_contract(self) -> dict[str, Any]:
        return {
            "schemaVersion": CONTRACT_VERSION,
            "requestId": self.request_id,
            "taskId": self.task_id,
            "provider": self.provider,
            "capability": self.capability,
            "executionMode": "mock",
            "requestedAt": self.requested_at,
        }


class OfficialDataProvider(Protocol):
    def collect(self, request: OfficialDataRequest) -> dict[str, Any]: ...


def _strict(value: object, required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != required | (optional or set()):
        raise OfficialDataContractError("Official data object shape is invalid.")
    return value


def _non_empty(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def _date_time(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value
    ):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _date(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def validate_official_data_request(value: object) -> dict[str, Any]:
    record = _strict(
        value,
        {
            "schemaVersion",
            "requestId",
            "taskId",
            "provider",
            "capability",
            "executionMode",
            "requestedAt",
        },
    )
    provider = record["provider"]
    if (
        record["schemaVersion"] != CONTRACT_VERSION
        or not _non_empty(record["requestId"])
        or not _non_empty(record["taskId"])
        or provider not in CAPABILITIES
        or record["capability"] not in CAPABILITIES[str(provider)]
        or record["executionMode"] != "mock"
        or not _date_time(record["requestedAt"])
    ):
        raise OfficialDataContractError("Official data request is invalid.")
    return record


def validate_official_data_result(value: object) -> dict[str, Any]:
    record = _strict(
        value,
        {
            "schemaVersion",
            "resultId",
            "requestId",
            "taskId",
            "provider",
            "capability",
            "executionMode",
            "status",
            "createdAt",
            "sources",
            "observations",
            "providerOutcomes",
            "warnings",
            "usage",
        },
    )
    provider = record["provider"]
    if (
        record["schemaVersion"] != CONTRACT_VERSION
        or not all(_non_empty(record[key]) for key in ("resultId", "requestId", "taskId"))
        or provider not in CAPABILITIES
        or record["capability"] not in CAPABILITIES[str(provider)]
        or record["executionMode"] != "mock"
        or record["status"] not in {"completed", "partial", "retryable", "failed"}
        or not _date_time(record["createdAt"])
        or not all(
            isinstance(record[key], list)
            for key in ("sources", "observations", "providerOutcomes", "warnings")
        )
    ):
        raise OfficialDataContractError("Official data result is invalid.")
    source_ids: set[str] = set()
    for raw in record["sources"]:
        source = _strict(
            raw,
            {"sourceId", "provider", "locator", "collectedAt", "freshness", "attribution"},
            {"publishedDate"} if isinstance(raw, dict) and "publishedDate" in raw else set(),
        )
        attribution = _strict(source["attribution"], {"notice", "reviewStatus"})
        locator = urlparse(source["locator"] if isinstance(source["locator"], str) else "")
        if (
            not _non_empty(source["sourceId"])
            or source["sourceId"] in source_ids
            or source["provider"] != provider
            or locator.scheme != "https"
            or not locator.hostname
            or not locator.hostname.endswith(".test")
            or not _date_time(source["collectedAt"])
            or source["freshness"] not in {"fresh", "stale", "unknown"}
            or ("publishedDate" in source and not _date(source["publishedDate"]))
            or not _non_empty(attribution["notice"])
            or attribution["reviewStatus"] not in {"not_required", "required", "unknown"}
        ):
            raise OfficialDataContractError("Official source is invalid or duplicated.")
        source_ids.add(source["sourceId"])
    observation_ids: set[str] = set()
    for raw in record["observations"]:
        observation = _strict(
            raw,
            {
                "observationId",
                "sourceId",
                "observedDate",
                "value",
                "unit",
                "revision",
                "attributes",
            },
        )
        if (
            not _non_empty(observation["observationId"])
            or observation["observationId"] in observation_ids
            or observation["sourceId"] not in source_ids
            or not _date(observation["observedDate"])
            or type(observation["value"]) not in {str, int, float, bool, type(None)}
            or not _non_empty(observation["unit"])
            or observation["revision"] not in {"initial", "revised", "unknown"}
            or not isinstance(observation["attributes"], dict)
        ):
            raise OfficialDataContractError("Official observation is invalid or duplicated.")
        observation_ids.add(observation["observationId"])
    for raw in record["providerOutcomes"]:
        outcome = _strict(
            raw,
            {"provider", "status", "retryable"},
            {"retryAfterSeconds"}
            if isinstance(raw, dict) and "retryAfterSeconds" in raw
            else set(),
        )
        if (
            outcome["provider"] != provider
            or outcome["status"] not in OUTCOMES
            or not isinstance(outcome["retryable"], bool)
            or (
                "retryAfterSeconds" in outcome
                and (
                    type(outcome["retryAfterSeconds"]) is not int
                    or outcome["retryAfterSeconds"] < 0
                )
            )
        ):
            raise OfficialDataContractError("Official provider outcome is invalid.")
    if any(item not in WARNINGS for item in record["warnings"]) or len(
        set(record["warnings"])
    ) != len(record["warnings"]):
        raise OfficialDataContractError("Official warnings are invalid.")
    usage = _strict(
        record["usage"],
        {"actualCostKrw", "simulated", "estimatedRequests", "estimatedCredits", "estimatedTokens"},
    )
    if (
        usage["actualCostKrw"] != 0
        or usage["simulated"] is not True
        or any(
            type(usage[key]) is not int or usage[key] < 0
            for key in ("estimatedRequests", "estimatedCredits", "estimatedTokens")
        )
    ):
        raise OfficialDataContractError("Mock usage must be simulated and zero-cost.")
    return record


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


class _MockAdapter:
    provider: Provider
    notice: str
    default_capability: Capability

    def collect(self, request: OfficialDataRequest) -> dict[str, Any]:
        validate_official_data_request(request.to_contract())
        if request.provider != self.provider:
            raise OfficialDataContractError("Adapter provider does not match request.")
        outcome_status = {
            "rate_limited": "rate_limited",
            "timeout": "timeout",
            "unavailable": "unavailable",
            "invalid_configuration": "invalid_configuration",
            "malformed_response": "malformed_response",
            "empty_result": "empty_result",
        }.get(request.scenario, "success")
        retryable = outcome_status in {"rate_limited", "timeout", "unavailable"}
        outcome: dict[str, Any] = {
            "provider": self.provider,
            "status": outcome_status,
            "retryable": retryable,
        }
        if outcome_status == "rate_limited":
            outcome["retryAfterSeconds"] = 30
        has_data = outcome_status == "success"
        stale = request.scenario == "stale"
        revised = request.scenario in {"revised", "filing_fact_normalization"}
        review = (
            request.scenario in {"license_review_required", "attribution_review_required"}
            or self.provider != "opendart"
        )
        source = {
            "sourceId": f"source-{self.provider}",
            "provider": self.provider,
            "locator": f"https://{self.provider}.test/official/synthetic",
            "publishedDate": "2026-08-29",
            "collectedAt": "2026-08-30T00:00:00Z",
            "freshness": "stale" if stale else "fresh",
            "attribution": {
                "notice": self.notice,
                "reviewStatus": "required" if review else "not_required",
            },
        }
        attributes: dict[str, str]
        if self.provider == "fred":
            attributes = {"seriesIdentifier": "SYNTHETIC_SERIES"}
        elif self.provider == "ecos":
            attributes = {
                "statisticsTable": "SYNTHETIC_TABLE",
                "itemCode": "SYNTHETIC_ITEM",
                "cycle": "M",
                "timePeriod": "202608",
            }
        else:
            attributes = {
                "receiptNumber": "SYNTHETIC_RECEIPT",
                "corporationCode": "SYNTHETIC_CORP",
                "reportName": "Synthetic filing",
                "filer": "Synthetic issuer",
                "receiptDate": "2026-08-29",
                "factName": "Synthetic fact",
            }
        warnings: list[str] = []
        if stale:
            warnings.append("stale_source")
        if revised:
            warnings.append("revised_observation")
        if request.scenario == "license_review_required":
            warnings.append("license_review_required")
        if request.scenario == "attribution_review_required":
            warnings.append("attribution_review_required")
        warning_by_outcome = {
            "rate_limited": "provider_rate_limited",
            "timeout": "provider_timeout",
            "unavailable": "provider_unavailable",
            "empty_result": "empty_result",
        }
        if outcome_status in warning_by_outcome:
            warnings.append(warning_by_outcome[outcome_status])
        result = {
            "schemaVersion": CONTRACT_VERSION,
            "resultId": f"official-result-{request.request_id}",
            "requestId": request.request_id,
            "taskId": request.task_id,
            "provider": self.provider,
            "capability": request.capability,
            "executionMode": "mock",
            "status": "completed" if has_data else ("retryable" if retryable else "failed"),
            "createdAt": "2026-08-30T00:00:00Z",
            "sources": [source] if has_data else [],
            "observations": [
                {
                    "observationId": f"observation-{self.provider}",
                    "sourceId": source["sourceId"],
                    "observedDate": "2026-08-29",
                    "value": "42.0",
                    "unit": "synthetic_units",
                    "revision": "revised" if revised else "initial",
                    "attributes": attributes,
                }
            ]
            if has_data
            else [],
            "providerOutcomes": [outcome],
            "warnings": warnings,
            "usage": {
                "actualCostKrw": 0,
                "simulated": True,
                "estimatedRequests": 1,
                "estimatedCredits": 1,
                "estimatedTokens": 0,
            },
        }
        return validate_official_data_result(result)


class FredMockAdapter(_MockAdapter):
    provider = "fred"
    default_capability = "series_observations"
    notice = "Synthetic FRED fixture; no endorsement implied; series copyright review required."


class EcosMockAdapter(_MockAdapter):
    provider = "ecos"
    default_capability = "statistics_observations"
    notice = "Synthetic ECOS fixture; attribution, redistribution, and retention require review."


class OpenDartMockAdapter(_MockAdapter):
    provider = "opendart"
    default_capability = "disclosure_list"
    notice = "Synthetic OpenDART fixture; current terms and changing limits require review."


def render_official_data_markdown(result: dict[str, Any]) -> str:
    validate_official_data_result(result)
    evidence = [
        f"- [{item['observationId']}] {item['value']} {item['unit']} ({item['sourceId']})"
        for item in result["observations"]
    ]
    return "\n".join(
        [
            "# Official Data",
            "",
            f"Status: {result['status']}",
            "",
            "## Evidence",
            *(evidence or ["- No official observation available."]),
            "",
            "## Attribution",
            *[f"- {item['attribution']['notice']}" for item in result["sources"]],
        ]
    )


def to_research_result(result: dict[str, Any]) -> dict[str, Any]:
    validate_official_data_result(result)
    sources = [
        {
            "sourceId": item["sourceId"],
            "locator": item["locator"],
            "publishedAt": f"{item.get('publishedDate', '2026-08-30')}T00:00:00Z",
            "collectedAt": item["collectedAt"],
            "freshness": item["freshness"],
        }
        for item in result["sources"]
    ]
    evidence = [
        {
            "evidenceId": item["observationId"],
            "sourceId": item["sourceId"],
            "observation": f"{item['value']} {item['unit']}",
            "relation": "supports",
        }
        for item in result["observations"]
    ]
    claims = [
        {
            "claimId": f"claim-{item['observationId']}",
            "text": f"Synthetic official observation: {item['value']} {item['unit']}.",
            "evidenceIds": [item["observationId"]],
            "confidence": "high",
        }
        for item in result["observations"]
    ]
    return {
        "schemaVersion": "aioffice.research.v1",
        "resultId": f"research-{result['resultId']}",
        "requestId": result["requestId"],
        "taskId": result["taskId"],
        "status": result["status"],
        "createdAt": result["createdAt"],
        "sources": sources,
        "evidence": evidence,
        "claims": claims,
        "providerOutcomes": [
            {
                "providerId": result["provider"],
                "status": "success" if result["status"] == "completed" else "failed",
                "retryable": result["status"] == "retryable",
            }
        ],
        "warnings": [],
        "usage": result["usage"],
    }


def to_core_module_result(result: dict[str, Any]) -> dict[str, Any]:
    validate_official_data_result(result)
    return {
        "taskId": result["taskId"],
        "module": "general_research",
        "markdown": render_official_data_markdown(result),
        "json": result,
        "createdAt": result["createdAt"],
    }
