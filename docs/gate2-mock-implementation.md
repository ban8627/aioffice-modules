# Gate 2 Mock Research Implementation

This checkpoint implements `aioffice.research.v1` without any live provider, credential, database, or deployment.

- Schemas: `contracts/schemas/research-request.schema.json` and `research-result.schema.json`
- Fixtures in `contracts/fixtures/`: `research-success`, `research-rate-limited`,
  `research-timeout`, `research-stale-source`, `research-source-conflict`,
  `research-partial`, `research-invalid-reference`, `research-duplicate-id`,
  `research-version-mismatch`, and `research-simulated-usage`.
- Runtime: `src/aioffice_modules/research.py`
- Tests: `tests/test_research.py`

The deterministic provider covers success, rate limit with retry-after, timeout, stale source, source conflict, and partial outcomes. Usage values are simulated; actual cost is always zero. The pipeline produces validated JSON, evidence-linked Markdown, and the existing `/module-results` payload without making an HTTP request.

Cross-repository parity is checked by canonical JSON and SHA-256 for the copied schemas and representative fixtures. Live provider selection, credentials, retention, budget, account data, and network clients still require separate approval.

The success, rate-limit, timeout, stale, conflict, partial, and simulated-usage fixtures are valid. Invalid-reference, duplicate-ID, and version-mismatch fixtures are intentionally rejected with a scenario-specific validation reason. All locators use `.test`, actual cost is zero, and usage counters are explicitly estimated or simulated.

Targeted verification uses `python -m pytest tests/test_research.py`, plus mypy and Ruff against only the new research files. Full regression, full security scanning, build checks, and final cross-repository parity remain for Gate 2 completion.
