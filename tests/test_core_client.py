from __future__ import annotations

import json
from typing import Any
from urllib.request import Request

from aioffice_modules.core_client import CoreClient, CoreClientConfig
from aioffice_modules.models import ModuleResult


class FakeResponse:
    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps({"accepted": True, "receivedAt": "2026-08-26T00:00:00.000Z"}).encode(
            "utf-8"
        )


def test_submit_result_posts_to_module_results_with_core_contract(
    monkeypatch: Any,
) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["headers"] = dict(request.header_items())
        captured["timeout"] = timeout
        data = request.data
        assert isinstance(data, bytes)
        captured["body"] = json.loads(data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr("aioffice_modules.core_client.urlopen", fake_urlopen)

    result = ModuleResult(
        task_id="task_1",
        module="general_research",
        markdown="# Result\n\nNo private data.",
        json={"status": "complete"},
        created_at="2026-08-26T00:00:00.000Z",
    )

    response = CoreClient(CoreClientConfig(base_url="https://core.test")).submit_result(result)

    assert response["accepted"] is True
    assert captured["url"] == "https://core.test/module-results"
    assert captured["method"] == "POST"
    assert captured["headers"]["Content-type"] == "application/json"
    assert captured["timeout"] == 10.0
    assert captured["body"] == result.to_contract()


def test_operations_summary_uses_core_dashboard_contract(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(url: str, timeout: float) -> FakeResponse:
        captured["url"] = url
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("aioffice_modules.core_client.urlopen", fake_urlopen)

    response = CoreClient(CoreClientConfig(base_url="https://core.test")).operations_summary()

    assert response["accepted"] is True
    assert captured["url"] == "https://core.test/operations/summary"
    assert captured["timeout"] == 10.0
