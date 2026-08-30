# AGENTS.md

## Scope

This repository covers AIOffice domain modules: investment research, general research, content and design generation, development assistance, and shared module interfaces.

## Current Gate

Gate 2 research contracts and the deterministic mock pipeline are complete and merged to `main`.

Gate 3 planning covers provider-neutral boundaries for FRED, Bank of Korea ECOS, and OpenDART. The current Gate 3 checkpoint is document-only. Do not add live provider clients, credentials, dependencies, external API calls, database access, deployment configuration, or real data until the applicable implementation and credential approvals are recorded.

## Safety Rules

- Do not store secrets, API keys, tokens, account data, portfolio data, personal data, production logs, or real environment files.
- Do not add a license file unless the user explicitly approves it.
- Do not automate investment orders or real financial transactions.
- Financial integrations must be designed as read-only unless the user approves a separate future policy change.
- Require user approval before security, permission, authentication, database migration, data deletion, large dependency, compatibility, or production deployment changes.

## Documentation Rules

- Mark unapproved decisions as proposals.
- Use official documentation for technology claims when current behavior, pricing, or service limits matter.
- Separate facts, assumptions, and recommendations.
