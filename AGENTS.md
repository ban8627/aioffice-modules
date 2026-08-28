# AGENTS.md

## Scope

This repository covers AIOffice domain modules: investment research, general research, content and design generation, development assistance, and shared module interfaces.

## Current Gate

Gate 1 is complete and merged to `main`. Gate 2 is in investment and general research planning and provider approval preparation.

During Gate 2 planning, keep changes document-only unless the user explicitly approves implementation. Do not add application code, dependencies, external API calls, deployment configuration, database migrations, secrets, or real account data.

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
