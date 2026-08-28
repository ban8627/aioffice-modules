# Gate 2 Plan: Investment And General Research Modules

Status: planning only. Implementation requires user approval.

Last reviewed: 2026-08-28 KST.

## Purpose

Gate 2 plans the module-side contracts and provider choices for investment and economic research plus general research. This document does not add application code, dependencies, external API calls, secrets, deployment, account access, or database access.

## Module Responsibilities

- Accept scoped research work from Core only.
- Produce Markdown and JSON reports that separate facts, interpretation, uncertainty, and recommendations.
- Submit results back to Core through approved Core APIs.
- Measure provider cost, latency, source freshness, and accuracy indicators.
- Avoid direct database access.
- Avoid actual investment orders or order-capable credentials.

## Investment And Economic Research Module

Planned coverage:

- Korean and US stocks and ETFs
- interest rates, inflation, exchange rates, and macroeconomic indicators
- disclosures, policy changes, volume, volatility, and material risk events
- read-only brokerage account and asset data only after explicit user approval
- stale-data warnings when provider or account data cannot be refreshed

Excluded:

- investment order placement
- order correction or cancellation
- order-capable credential storage
- real portfolio data in repository fixtures

## General Research Module

Planned coverage:

- AI, technology, software, product, service, policy, legal, social, learning, and job-knowledge research
- link, document, image, scheduled tracking, and information-gap inputs
- source-backed comparison, recommendation, and follow-up task plans
- explicit uncertainty and conflict reporting

## Candidate Data Contracts

The following names are planning candidates only. Final schema files require user approval.

### ResearchRequest

- `requestId`: caller-provided idempotency key
- `taskId`: Core task id
- `kind`: `investment_research` or `general_research`
- `question`: user-facing question or objective
- `subjects`: normalized tickers, topics, issuers, products, or entities
- `freshnessTarget`: required recency window
- `requiredCapabilities`: provider capability list
- `language`: report language
- `riskLevel`: normal, approval-required, or blocked
- `sourcePolicy`: minimum source count and primary-source preference
- `budgetPolicy`: cost ceiling and free-tier preference

### ResearchResult

- `requestId`
- `taskId`
- `status`
- `markdown`
- `json`
- `sources`
- `claims`
- `evidence`
- `conflicts`
- `uncertainties`
- `costEvents`
- `latencyMs`
- `accuracyEvaluation`

### SourceReference

- provider
- source type
- official URL or document id
- publisher
- publication time when available
- retrieval time
- freshness status
- license or redistribution note

### Claim And Evidence

- Claims must be traceable to one or more sources.
- Evidence must point to a source, field path, document section, or URL fragment when available.
- At least two independent sources are required for material investment or policy claims unless the report marks confirmation as unavailable.
- Conflicting sources must be grouped and shown with uncertainty instead of hidden.

## Source Quality And Freshness

- Prefer official filings, official economic data, regulator notices, issuer releases, and provider documentation.
- Use market/news aggregators as discovery aids, then verify material claims against primary or high-quality secondary sources.
- Record source publication time and retrieval time separately.
- Flag stale account, market, or macro data in both Markdown and JSON.

## Cross-Verification

- Material claims should cite at least two independent sources.
- If only one official source exists, mark the source as authoritative but not independently cross-verified.
- If sources conflict, report the conflict, affected conclusion, and what data is needed to resolve it.
- Do not fabricate missing prices, limits, policies, or provider terms.

## Reporting Format

- Markdown is the human-readable report.
- JSON is the machine-readable result for Core and dashboards.
- Markdown must include source labels, freshness notes, uncertainty notes, and approval-needed items.
- JSON must preserve source ids, claim ids, evidence ids, cost events, latency, and accuracy evaluation fields.

## Metrics

- cost by provider and capability
- latency by provider and capability
- number of sources
- independent-source count
- stale-source count
- conflict count
- extraction/parsing failure count
- missing-data count
- user-review-required flag

## Fixture And Mock Validation Scope

Before any live provider connection, tests should use fixtures and mocks for:

- successful investment research result
- successful general research result
- stale source
- conflicting source
- provider `429`
- provider timeout
- malformed provider response
- missing source publication time
- source confidence and freshness scoring
- Markdown and JSON report shape
- Core API result submission

## Approval Required Before Implementation

- Final research contract fields and schema locations
- Provider list and capability mapping
- Environment variable names for approved secret stores
- Monthly provider budget and paid-plan rules
- Data retention and raw payload policy
- Whether OpenAI API, ChatGPT Work, or other AI providers are used for extraction and summarization
- Read-only brokerage scope and account-data handling

## Explicit Exclusions

- Application code changes in this planning PR
- Dependency changes
- Live API calls
- API key or token creation
- `.env` changes
- Direct database access
- Real account, portfolio, or market data fixtures
- Investment order features
- Deployment
- License file creation
