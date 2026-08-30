# Gate 3B Official Data Mock Adapters

Modules exposes an `OfficialDataProvider` protocol with deterministic `FredMockAdapter`,
`EcosMockAdapter`, and `OpenDartMockAdapter` implementations. They normalize only synthetic
fixtures, preserve source-to-observation references, distinguish retryable provider outcomes,
render evidence-linked Markdown, and build existing Core `/module-results` envelopes without
performing HTTP calls.

FRED output carries the non-endorsement and series copyright review boundary. ECOS keeps
attribution, redistribution, and retention unresolved for later approval. OpenDART records
that current terms and limits must be rechecked and does not hard-code error `020` or a
20,000-request quota. This checkpoint adds no dependency, secret, database access, workflow,
external request, deployment, schedule, or live notification.
