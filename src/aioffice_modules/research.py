from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Protocol, TypedDict
from urllib.parse import urlparse

CONTRACT_VERSION = "aioffice.research.v1"
Scenario = Literal[
    "success",
    "rate_limited",
    "timeout",
    "stale_source",
    "source_conflict",
    "partial",
]


class SourceReference(TypedDict, total=False):
    sourceId: str
    locator: str
    publishedAt: str
    collectedAt: str
    freshness: Literal["fresh", "stale", "unknown"]


class Evidence(TypedDict):
    evidenceId: str
    sourceId: str
    observation: str
    relation: Literal["supports", "contradicts"]


class Claim(TypedDict):
    claimId: str
    text: str
    evidenceIds: list[str]
    confidence: Literal["low", "medium", "high"]


class ResearchResult(TypedDict):
    schemaVersion: str
    resultId: str
    requestId: str
    taskId: str
    status: Literal["completed", "partial", "retryable", "failed"]
    createdAt: str
    sources: list[SourceReference]
    evidence: list[Evidence]
    claims: list[Claim]
    providerOutcomes: list[dict[str, Any]]
    warnings: list[str]
    usage: dict[str, Any]


class ResearchContractError(ValueError):
    pass


@dataclass(frozen=True)
class ResearchRequest:
    schema_version: str
    request_id: str
    task_id: str
    kind: Literal["investment_research", "general_research"]
    question: str
    created_at: str
    scenario: Scenario = "success"

    def to_contract(self) -> dict[str, Any]:
        return {
            "schemaVersion": self.schema_version,
            "requestId": self.request_id,
            "taskId": self.task_id,
            "kind": self.kind,
            "question": self.question,
            "createdAt": self.created_at,
            "scenario": self.scenario,
        }


class ResearchProvider(Protocol):
    def collect(self, request: ResearchRequest) -> list[dict[str, Any]]:
        """Return deterministic normalized provider outcomes without network access."""


def _date_time(value: object) -> bool:
    if not isinstance(value, str) or "T" not in value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return value.endswith("Z") or "+" in value[10:] or "-" in value[10:]


def _strict(record: object, required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
    optional = optional or set()
    if not isinstance(record, dict) or set(record) != required | (set(record) & optional):
        raise ResearchContractError("Research contract fields are invalid.")
    return record


def validate_research_request(value: object) -> dict[str, Any]:
    record = _strict(
        value,
        {"schemaVersion", "requestId", "taskId", "kind", "question", "createdAt", "scenario"},
    )
    if record["schemaVersion"] != CONTRACT_VERSION:
        raise ResearchContractError("Unsupported research schema version.")
    if record["kind"] not in {"investment_research", "general_research"}:
        raise ResearchContractError("Research kind is invalid.")
    if record["scenario"] not in {
        "success",
        "rate_limited",
        "timeout",
        "stale_source",
        "source_conflict",
        "partial",
    }:
        raise ResearchContractError("Research scenario is invalid.")
    if not all(
        isinstance(record[key], str) and record[key] for key in ("requestId", "taskId", "question")
    ):
        raise ResearchContractError("Research identifiers and question must be non-empty.")
    if not _date_time(record["createdAt"]):
        raise ResearchContractError("Research createdAt must be RFC 3339 date-time.")
    return record


def validate_research_result(value: object) -> dict[str, Any]:
    record = _strict(
        value,
        {
            "schemaVersion",
            "resultId",
            "requestId",
            "taskId",
            "status",
            "createdAt",
            "sources",
            "evidence",
            "claims",
            "providerOutcomes",
            "warnings",
            "usage",
        },
    )
    if record["schemaVersion"] != CONTRACT_VERSION:
        raise ResearchContractError("Unsupported research schema version.")
    if record["status"] not in {"completed", "partial", "retryable", "failed"}:
        raise ResearchContractError("Research result status is invalid.")
    if not all(
        isinstance(record[key], str) and record[key] for key in ("resultId", "requestId", "taskId")
    ):
        raise ResearchContractError("Research result identifiers must be non-empty.")
    if not _date_time(record["createdAt"]):
        raise ResearchContractError("Research result createdAt must be RFC 3339 date-time.")
    if not all(
        isinstance(record[key], list)
        for key in ("sources", "evidence", "claims", "providerOutcomes", "warnings")
    ):
        raise ResearchContractError("Research result collections are invalid.")

    source_ids: set[str] = set()
    for source in record["sources"]:
        source = _strict(
            source, {"sourceId", "locator", "collectedAt", "freshness"}, {"publishedAt"}
        )
        if (
            source["sourceId"] in source_ids
            or not isinstance(source["sourceId"], str)
            or not source["sourceId"]
        ):
            raise ResearchContractError("Source identifiers must be unique and non-empty.")
        parsed = urlparse(source["locator"] if isinstance(source["locator"], str) else "")
        if parsed.scheme not in {"https", "fixture"} or not parsed.netloc:
            raise ResearchContractError("Source locator is invalid.")
        if source["freshness"] not in {"fresh", "stale", "unknown"} or not _date_time(
            source["collectedAt"]
        ):
            raise ResearchContractError("Source freshness or collection time is invalid.")
        if "publishedAt" in source and not _date_time(source["publishedAt"]):
            raise ResearchContractError("Source publishedAt is invalid.")
        source_ids.add(source["sourceId"])

    evidence_ids: set[str] = set()
    for evidence in record["evidence"]:
        evidence = _strict(evidence, {"evidenceId", "sourceId", "observation", "relation"})
        if evidence["evidenceId"] in evidence_ids or evidence["sourceId"] not in source_ids:
            raise ResearchContractError(
                "Evidence references an unknown source or duplicates an ID."
            )
        if evidence["relation"] not in {"supports", "contradicts"}:
            raise ResearchContractError("Evidence relation is invalid.")
        if not isinstance(evidence["observation"], str) or not evidence["observation"]:
            raise ResearchContractError("Evidence observation must be non-empty.")
        evidence_ids.add(evidence["evidenceId"])

    claim_ids: set[str] = set()
    for claim in record["claims"]:
        claim = _strict(claim, {"claimId", "text", "evidenceIds", "confidence"})
        if (
            claim["claimId"] in claim_ids
            or not isinstance(claim["claimId"], str)
            or not claim["claimId"]
        ):
            raise ResearchContractError("Claim identifiers must be unique and non-empty.")
        if claim["confidence"] not in {"low", "medium", "high"}:
            raise ResearchContractError("Claim confidence is invalid.")
        if not isinstance(claim["evidenceIds"], list) or not claim["evidenceIds"]:
            raise ResearchContractError("Claims require evidence references.")
        if (
            len(set(claim["evidenceIds"])) != len(claim["evidenceIds"])
            or not set(claim["evidenceIds"]) <= evidence_ids
        ):
            raise ResearchContractError("Claim references unknown or duplicate evidence.")
        claim_ids.add(claim["claimId"])

    for outcome in record["providerOutcomes"]:
        outcome = _strict(outcome, {"providerId", "status", "retryable"}, {"retryAfterSeconds"})
        if outcome["status"] not in {"success", "rate_limited", "timeout", "failed"}:
            raise ResearchContractError("Provider outcome status is invalid.")
        if not isinstance(outcome["retryable"], bool):
            raise ResearchContractError("Provider retryable must be boolean.")
        if "retryAfterSeconds" in outcome and (
            not isinstance(outcome["retryAfterSeconds"], int) or outcome["retryAfterSeconds"] < 0
        ):
            raise ResearchContractError("retryAfterSeconds is invalid.")

    allowed_warnings = {
        "stale_source",
        "source_conflict",
        "provider_rate_limited",
        "provider_timeout",
        "partial_result",
    }
    if any(warning not in allowed_warnings for warning in record["warnings"]):
        raise ResearchContractError("Research warning is invalid.")
    usage = _strict(
        record["usage"],
        {"actualCostKrw", "simulated", "estimatedRequests", "estimatedCredits", "estimatedTokens"},
    )
    if usage["actualCostKrw"] != 0 or usage["simulated"] is not True:
        raise ResearchContractError("Mock usage must have zero actual cost and be simulated.")
    if any(
        not isinstance(usage[key], int) or usage[key] < 0
        for key in ("estimatedRequests", "estimatedCredits", "estimatedTokens")
    ):
        raise ResearchContractError("Simulated usage values must be non-negative integers.")
    return record


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


class DeterministicMockProvider:
    def collect(self, request: ResearchRequest) -> list[dict[str, Any]]:
        validate_research_request(request.to_contract())
        scenario = request.scenario
        if scenario == "rate_limited":
            return [
                {
                    "providerId": "mock-search",
                    "status": "rate_limited",
                    "retryable": True,
                    "retryAfterSeconds": 30,
                }
            ]
        if scenario == "timeout":
            return [{"providerId": "mock-search", "status": "timeout", "retryable": True}]
        if scenario == "partial":
            return [
                {"providerId": "mock-search", "status": "success", "retryable": False},
                {"providerId": "mock-archive", "status": "timeout", "retryable": True},
            ]
        return [{"providerId": "mock-search", "status": "success", "retryable": False}]


def run_mock_research(
    request: ResearchRequest, provider: ResearchProvider | None = None
) -> tuple[dict[str, Any], str]:
    validate_research_request(request.to_contract())
    outcomes = (provider or DeterministicMockProvider()).collect(request)
    scenario = request.scenario
    sources: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    warnings: list[str] = []
    status = "completed"
    if scenario not in {"rate_limited", "timeout"}:
        stale = scenario == "stale_source"
        sources.append(
            {
                "sourceId": "source-1",
                "locator": "https://publisher.test/research/alpha",
                "publishedAt": "2026-01-01T00:00:00Z" if stale else "2026-08-29T00:00:00Z",
                "collectedAt": "2026-08-30T00:00:00Z",
                "freshness": "stale" if stale else "fresh",
            }
        )
        evidence.append(
            {
                "evidenceId": "evidence-1",
                "sourceId": "source-1",
                "observation": "Synthetic indicator equals 42 units.",
                "relation": "supports",
            }
        )
        claims.append(
            {
                "claimId": "claim-1",
                "text": "The synthetic indicator is 42 units.",
                "evidenceIds": ["evidence-1"],
                "confidence": "high",
            }
        )
        if stale:
            warnings.append("stale_source")
        if scenario == "source_conflict":
            sources.append(
                {
                    "sourceId": "source-2",
                    "locator": "https://archive.test/research/beta",
                    "publishedAt": "2026-08-29T01:00:00Z",
                    "collectedAt": "2026-08-30T00:00:00Z",
                    "freshness": "fresh",
                }
            )
            evidence.append(
                {
                    "evidenceId": "evidence-2",
                    "sourceId": "source-2",
                    "observation": "Synthetic indicator equals 39 units.",
                    "relation": "contradicts",
                }
            )
            claims[0]["evidenceIds"].append("evidence-2")
            claims[0]["confidence"] = "low"
            warnings.append("source_conflict")
    if scenario == "rate_limited":
        status, warnings = "retryable", ["provider_rate_limited"]
    elif scenario == "timeout":
        status, warnings = "retryable", ["provider_timeout"]
    elif scenario == "partial":
        status, warnings = "partial", ["provider_timeout", "partial_result"]
    result = {
        "schemaVersion": CONTRACT_VERSION,
        "resultId": f"result-{request.request_id}",
        "requestId": request.request_id,
        "taskId": request.task_id,
        "status": status,
        "createdAt": "2026-08-30T00:00:00Z",
        "sources": sources,
        "evidence": evidence,
        "claims": claims,
        "providerOutcomes": outcomes,
        "warnings": warnings,
        "usage": {
            "actualCostKrw": 0,
            "simulated": True,
            "estimatedRequests": len(outcomes),
            "estimatedCredits": len(outcomes),
            "estimatedTokens": 120 if claims else 0,
        },
    }
    validate_research_result(result)
    markdown = _render_markdown(result)
    return result, markdown


def _render_markdown(result: dict[str, Any]) -> str:
    claims = result["claims"]
    claim_lines = [f"- {claim['text']} [{', '.join(claim['evidenceIds'])}]" for claim in claims]
    evidence_lines = [
        f"- [{item['evidenceId']}] {item['observation']} ({item['sourceId']}, {item['relation']})"
        for item in result["evidence"]
    ]
    return "\n".join(
        [
            "# Research Summary",
            "",
            f"Status: {result['status']}",
            "",
            "## Key Claims",
            *(claim_lines or ["- No evidence-backed claim available."]),
            "",
            "## Evidence and Sources",
            *(evidence_lines or ["- No evidence available."]),
            "",
            "## Conflicts or Unverified Information",
            *(
                [f"- {item}" for item in result["warnings"] if item == "source_conflict"]
                or ["- None."]
            ),
            "",
            "## Stale Warnings",
            *(["- stale_source"] if "stale_source" in result["warnings"] else ["- None."]),
            "",
            "## Provider Errors",
            *(
                [
                    f"- {item['providerId']}: {item['status']}"
                    for item in result["providerOutcomes"]
                    if item["status"] != "success"
                ]
                or ["- None."]
            ),
            "",
            "## Simulated Usage",
            f"- Requests: {result['usage']['estimatedRequests']}; actual cost KRW: 0 (simulated).",
        ]
    )


def to_core_module_result(
    request: ResearchRequest, result: dict[str, Any], markdown: str
) -> dict[str, Any]:
    validate_research_result(result)
    if result["requestId"] != request.request_id or result["taskId"] != request.task_id:
        raise ResearchContractError("Research request/result correlation is invalid.")
    return {
        "taskId": request.task_id,
        "module": "investment_analysis"
        if request.kind == "investment_research"
        else "general_research",
        "markdown": markdown,
        "json": result,
        "createdAt": result["createdAt"],
    }
