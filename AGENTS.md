# AGENTS.md

## Scope

This repository covers AIOffice domain modules: investment research, general research, content and design generation, development assistance, and shared module interfaces.

## Current Gate

Gate 1 is active. Until the user approves a technology stack, agents may edit only:

- `README.md`
- `AGENTS.md`
- `docs/gate1-plan.md`
- `docs/architecture-options.md`
- `.gitignore`
- `SECURITY.md`

Do not write application code before explicit user approval.

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
