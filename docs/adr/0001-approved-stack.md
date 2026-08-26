# ADR 0001: Approved Gate 1 Stack

Date: 2026-08-26 KST

## Status

Approved for Gate 1 implementation.

## Context

AIOffice modules need a Python-first runtime for investment analysis, general research, content workflows, development assistance, and Windows PC agent work. Modules must remain separated from private data storage and must not connect directly to the database.

## Decision

- Investment, research, content modules, and the Windows PC agent use Python with FastAPI.
- Cloud schedules and task delivery are owned by AIOffice Core using TypeScript, Cloudflare Workers, Cron Triggers, and Queues.
- Cloudflare and Supabase both start on Free plans.
- Queue messages are delivery-only. Task originals and state are stored by Core.
- Modules must not access the database directly. They call Core APIs through least-privilege contracts.
- Initial module outputs use Markdown and JSON.
- The dashboard will be implemented in `aioffice-core` with Next.js after Core contracts are stable.
- Repository contracts use OpenAPI and JSON Schema.
- Logs combine redacted Core audit events with provider operational logs.
- Secrets must use approved platform secret stores only.

## Consequences

- No Cloudflare or Supabase paid plan is activated in Gate 1.
- No real deployment, API key entry, database migration, investment order feature, Instagram posting connection, or production deployment is included.
- Domain modules expose deterministic interfaces that are testable without live APIs.

## References

- Root requirements document: `AI_Office_requirements_review_v0.22.md`
- Gate handoff: `AIOffice_Gate1_Codex_handoff.md`
