# Gate 2 Mock Research Implementation

This checkpoint implements `aioffice.research.v1` without any live provider, credential, database, or deployment.

- Schemas: `contracts/schemas/research-request.schema.json` and `research-result.schema.json`
- Fixtures: `contracts/fixtures/research-success.json` and `research-invalid-reference.json`
- Runtime: `src/aioffice_modules/research.py`
- Tests: `tests/test_research.py`

The deterministic provider covers success, rate limit with retry-after, timeout, stale source, source conflict, and partial outcomes. Usage values are simulated; actual cost is always zero. The pipeline produces validated JSON, evidence-linked Markdown, and the existing `/module-results` payload without making an HTTP request.

Cross-repository parity is checked by canonical JSON and SHA-256 for the copied schemas and representative fixtures. Live provider selection, credentials, retention, budget, account data, and network clients still require separate approval.
