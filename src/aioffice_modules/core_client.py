from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, cast
from urllib.request import Request, urlopen

from aioffice_modules.models import ModuleResult


@dataclass(frozen=True)
class CoreClientConfig:
    base_url: str
    timeout_seconds: float = 10.0


class CoreClient:
    """Minimal Core API client.

    This client carries no secrets and does not access the database directly.
    Authentication headers can be added later through approved platform secret stores.
    """

    def __init__(self, config: CoreClientConfig) -> None:
        self._config = config

    def health(self) -> dict[str, Any]:
        url = f"{self._config.base_url}/health"
        with urlopen(url, timeout=self._config.timeout_seconds) as response:
            return cast(dict[str, Any], json.loads(response.read().decode("utf-8")))

    def operations_summary(self) -> dict[str, Any]:
        url = f"{self._config.base_url}/operations/summary"
        with urlopen(url, timeout=self._config.timeout_seconds) as response:
            return cast(dict[str, Any], json.loads(response.read().decode("utf-8")))

    def submit_result(self, result: ModuleResult) -> dict[str, Any]:
        body = json.dumps(result.to_contract()).encode("utf-8")
        request = Request(
            f"{self._config.base_url}/module-results",
            data=body,
            method="POST",
            headers={"content-type": "application/json"},
        )
        with urlopen(request, timeout=self._config.timeout_seconds) as response:
            return cast(dict[str, Any], json.loads(response.read().decode("utf-8")))
