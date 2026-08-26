# Architecture Options

Status: proposal for user approval. Nothing in this document finalizes the technology stack.

Last reviewed: 2026-08-26 KST.

## Decision Criteria

- Fit within the additional monthly operations budget of 71,000 KRW.
- Support Korean language and KST schedules.
- Connect safely to the AIOffice core platform and a Windows PC agent.
- Use least-privilege access and secret isolation.
- Support recovery, tests, and public repository safety.

## 1. Module Language and Runtime

### Option A: Python

Strengths:

- Strong fit for investment analysis, document parsing, image processing, and research workflows.
- FastAPI can expose module APIs later if approved.
- RQ and Celery are available options for background module work.

Tradeoffs:

- A separate dashboard stack is still likely.
- Type contracts must be generated or validated separately if the dashboard uses TypeScript.

Official references:

- https://fastapi.tiangolo.com/async/
- https://python-rq.org/docs/
- https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html

### Option B: TypeScript

Strengths:

- Strong type sharing with a future Next.js dashboard.
- NestJS has queue and scheduling patterns for modular services.

Tradeoffs:

- Finance/data-science libraries may be less convenient than Python.
- Some Windows PC automation may require helper processes.

Official references:

- https://docs.nestjs.com/techniques/task-scheduling
- https://docs.nestjs.com/techniques/queues

### Option C: Mixed Python Modules with TypeScript UI Contracts

Strengths:

- Lets data-heavy modules use Python while UI contracts remain language-neutral.
- Avoids forcing all domains into one runtime.

Tradeoffs:

- Requires stricter interface contracts and CI validation.
- More moving pieces once implementation starts.

Recommendation for approval: Python-first modules with OpenAPI/JSON Schema contracts to the core platform. This is a recommendation only, not a final decision.

## 2. Queue and Scheduler Integration

### Option A: Core-owned Cloudflare Queues and Cron Triggers

Strengths:

- Keeps scheduling and queue state centralized in `aioffice-core`.
- Good fit for lightweight trigger and dispatch logic.

Tradeoffs:

- UTC cron behavior must be converted for KST schedules.
- Long-running module work may need a separate worker.

Official references:

- https://developers.cloudflare.com/queues/get-started/
- https://developers.cloudflare.com/workers/configuration/cron-triggers/

### Option B: Python RQ Module Workers

Strengths:

- Simple Python background processing.
- RQ documents Windows-compatible `SpawnWorker`.

Tradeoffs:

- Requires Redis or Valkey.
- The core platform still needs a single source of truth for state.

Official references:

- https://python-rq.org/docs/scheduling/
- https://python-rq.org/docs/workers/

### Option C: Celery Module Workers

Strengths:

- Mature distributed task model.
- Periodic tasks can use an explicit timezone setting.

Tradeoffs:

- More complex than needed for early Gate 1.

Official reference: https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html

Recommendation for approval: core-owned scheduling with module workers receiving jobs through a documented contract.

## 3. Data and Secret Boundaries

### Option A: Core-owned Supabase Postgres and Vault

Strengths:

- Keeps personal data and secrets out of the module repository.
- Supabase documents RLS, server-side secret handling, Vault, and backups.

Tradeoffs:

- Modules need explicit access policies and service boundaries.
- PITR should not be enabled without cost approval.

Official references:

- https://supabase.com/docs/guides/database/secure-data
- https://supabase.com/docs/guides/database/vault
- https://supabase.com/docs/guides/platform/backups

### Option B: Core-owned Neon Postgres

Strengths:

- Branching is useful for development and migration testing.
- Free and usage-based plans may fit early testing.

Tradeoffs:

- Secret storage must be paired with another approved secret manager.

Official references:

- https://neon.com/pricing
- https://neon.com/docs/get-started-with-neon/workflow-primer

### Option C: No Direct Module DB Access

Strengths:

- Strongest least-privilege boundary.
- Modules receive only task inputs and return outputs through core APIs.

Tradeoffs:

- More API work in the core repository.
- Some analytics tasks may need carefully scoped data views.

Recommendation for approval: no direct module DB access by default; use core-mediated data access and explicit read-only scopes.

## 4. Dashboard and Review Surface

### Option A: Core-hosted Next.js Dashboard

Strengths:

- Keeps approval, review, and status screens in one place.
- Next.js supports a dashboard-oriented App Router model.

Tradeoffs:

- Modules must expose clean data contracts.

Official references:

- https://nextjs.org/docs/app
- https://nextjs.org/docs/app/getting-started/deploying

### Option B: Module-Generated Markdown Reports

Strengths:

- Cheap and simple for early research output.
- Easy to inspect in GitHub and ChatGPT Work.

Tradeoffs:

- Not a full operational dashboard.

### Option C: Core API plus Later Dashboard

Strengths:

- Lets Gate 1 focus on queue, policy, and audit contracts first.

Tradeoffs:

- Less usable until UI work begins.

Recommendation for approval: module-generated structured outputs first, dashboard rendering owned by `aioffice-core`.

## 5. Cloud Execution and PC Agent

### Option A: Cloudflare Workers for Dispatch, PC Agent for Local Work

Strengths:

- Avoids exposing the PC directly to the internet.
- Keeps always-on work lightweight.

Tradeoffs:

- PC-offline work waits in the cloud queue.

Official references:

- https://developers.cloudflare.com/workers/platform/pricing/
- https://developers.cloudflare.com/workers/platform/limits/

### Option B: Supabase Edge Functions for Module API Gateways

Strengths:

- Close to database and secrets if Supabase is approved.

Tradeoffs:

- Long-running local or AI-heavy tasks still need a worker.

Official reference: https://supabase.com/docs

### Option C: GitHub Actions for Development Module Checks

Strengths:

- Good for repository audit and CI workflows.

Tradeoffs:

- Not suitable as the primary production module runner.

Official reference: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

Recommendation for approval: cloud dispatch plus pull-based PC agent for local tasks, with no inbound PC port exposure.

## 6. Logging, Cost Measurement, and Secrets

### Option A: Core Audit Events

Strengths:

- Central source of truth for task input, source, model/tool use, cost, result, error, approval, and recovery metadata.

Tradeoffs:

- Requires careful redaction before logs are stored.

### Option B: Provider-Native Logs Only

Strengths:

- Low build effort.

Tradeoffs:

- Logs become scattered and may miss approval context.

### Option C: Hybrid Logs

Strengths:

- Core stores redacted audit metadata; providers keep operational logs.

Tradeoffs:

- Requires retention and redaction rules.

Recommendation for approval: hybrid logs, with redacted core audit events and no raw secrets or personal data in logs.

## 7. Cross-Repository Contract and Versioning

### Option A: OpenAPI plus JSON Schema

Strengths:

- Language-neutral and public-review friendly.
- Works with Python and TypeScript.

Tradeoffs:

- Needs CI validation later.

### Option B: Protocol Buffers

Strengths:

- Strong generated clients and versioning.

Tradeoffs:

- More complex than necessary for Gate 1.

### Option C: Shared Package

Strengths:

- Convenient if a single language is approved.

Tradeoffs:

- Prematurely couples both repositories to that language.

Recommendation for approval: OpenAPI plus JSON Schema, with semantic versioning after the first approved implementation.

## Approval Needed

Please approve or revise:

- module implementation language
- queue integration model
- data access boundary
- module output format
- PC agent connection model
- logging and redaction policy
- cross-repository contract format
