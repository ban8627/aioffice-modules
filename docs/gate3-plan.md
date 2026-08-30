# Gate 3 Plan: Official Economic And Disclosure Providers

Status: planning checkpoint approved. Live provider access is not approved.

Last reviewed: 2026-08-30 KST.

## Purpose

Gate 3 prepares provider-neutral module adapters for:

1. FRED United States economic series and release metadata.
2. Bank of Korea ECOS Korean economic statistics.
3. OpenDART Korean issuer disclosures and structured filing data.

This checkpoint is document-only. It creates no provider account, API key, SDK, live network request, dependency, database connection, deployment, schedule, notification, or real-data fixture.

## Official Documentation

### FRED

- API: https://fred.stlouisfed.org/docs/api/fred/
- Terms: https://fred.stlouisfed.org/docs/api/terms_of_use.html
- Requires an API key.
- Requires the FRED non-endorsement notice.
- Series may have third-party copyright restrictions.
- Fixed quota assumptions are prohibited because FRED may change transaction and bandwidth limits.

### Bank of Korea ECOS

- Official portal: https://ecos.bok.or.kr/api/
- The portal describes API-key application, API discovery, application creation, and application registration.
- Exact public quota, redistribution, and retention terms were not confirmed from the publicly accessible page reviewed. Live work remains blocked until those conditions are verified from the official application or account view.

### OpenDART

- Introduction: https://opendart.fss.or.kr/intro/main.do
- Terms: https://opendart.fss.or.kr/intro/terms.do
- Development guide: https://opendart.fss.or.kr/guide/main.do
- Requires membership approval and an authentication key.
- The service is free in principle under the current terms, but usage limits may change.
- Error `020` means request-limit exhaustion. Endpoint documentation says it generally occurs above 20,000 requests but may use a different threshold.

## Module Boundary

Modules must:

- Receive scoped provider work from Core.
- Receive no secret value in task payloads.
- Return normalized source, observation, freshness, attribution, warning, and provider-outcome metadata.
- Avoid direct database access.
- Avoid storing raw provider responses.
- Avoid logging query values that reveal personal portfolio or account interests.
- Keep actual cost separate from simulated or estimated usage.
- Preserve provider identifiers and official source locators without implying provider endorsement.

## Proposed Provider Protocol

A later Gate 3 mock checkpoint may define a provider-neutral protocol with:

- provider identifier
- capability
- normalized request
- deterministic collection result
- provider status and retry metadata
- normalized source references
- normalized observations
- attribution and license notes
- freshness evaluation
- simulated usage with actual cost zero

The existing `aioffice.research.v1` request and result contract remains unchanged during planning. Any additive extension must preserve Core and Modules parity. Breaking changes require a new contract version and separate approval.

## Proposed Normalization

### FRED

Normalize only approved series or release fields:

- series identifier
- observation date
- value as received
- units and frequency metadata
- release or source metadata
- retrieved time
- copyright or attribution note

Do not treat observation date as publication time unless the official endpoint supplies an actual publication timestamp.

### ECOS

Normalize only approved statistics fields:

- statistics table
- item codes
- cycle
- time period
- unit
- value as received
- retrieved time

Publication time, revision status, and attribution rules must be confirmed before live use.

### OpenDART

Normalize only approved disclosure fields:

- receipt number
- corporation code
- report name
- filer
- receipt date
- disclosure locator
- structured financial or report fields when separately approved
- retrieved time

Do not store full report bodies or raw XML/ZIP payloads by default.

## Mock Scenarios For Gate 3B

Each provider mock should cover:

- success
- invalid configuration
- rate limit
- timeout
- provider maintenance or unavailable response
- malformed response
- empty result
- stale or revised observation
- attribution or license-review required
- partial multi-provider result
- deterministic normalization
- simulated usage with zero actual cost

Fixtures must use synthetic identifiers, fictional values, and `.test` locators. They must not copy real provider payloads or real economic and disclosure values.

## Recommended Delivery Order

1. Provider-neutral protocol and synthetic fixtures.
2. FRED mock normalization.
3. ECOS mock normalization.
4. OpenDART mock normalization.
5. Cross-repository contract parity and Gate 3 full validation.
6. Separate live-pilot approval, recommended to start with a small FRED series allowlist.

## Approval Required Before Live Work

- Provider account creation or use
- API-key issuance and approved secret store
- Environment-variable names
- Endpoint, series, table, item, and disclosure allowlists
- Request, retry, and cost budgets
- Raw and normalized data retention
- Attribution and redistribution rules
- Live-data use in reports
- Any dependency or network client
- Deployment, scheduling, or notification activation

## Explicit Exclusions

- Live provider implementation
- Real API calls
- Credentials or `.env` files
- Real provider response fixtures
- Real market, portfolio, or account data
- Brokerage integration
- Investment orders
- Direct database access
- Dependency changes
- Deployment
