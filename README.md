# AIOffice Modules

AIOffice Modules is the planned public repository for AIOffice domain modules.

This repository is intended to hold module designs for:

- investment and economic research
- general research and decision support
- content and design generation
- development and GitHub project work
- shared module interfaces

## Gate Status

- Gate 0 requirements review: PASS, based on `AI_Office_requirements_review_v0.23.md`.
- Gate 1 repository bootstrap: PASS.
- Technology stack: approved, see `docs/adr/0001-approved-stack.md`.
- Gate 1 implementation: COMPLETE, merged to main on 2026-08-28.
- Gate 2 research implementation: COMPLETE, merged to main on 2026-08-30.
- Gate 3 official economic and disclosure data planning: in progress, see `docs/gate3-plan.md`.

## Public Repository Safety

This public repository must not contain:

- personal information
- account or portfolio data
- API keys, tokens, passwords, cookies, or private keys
- production logs
- real environment configuration
- brokerage credentials
- investment order logic connected to real accounts

Example configuration, when later approved, must use fictional values and schema-only examples.

## Source Requirements

### Gate 1 Historical Basis

- `AI_Office_requirements_review_v0.22.md`
- `AIOffice_Gate1_Codex_handoff.md`

### Gate 2 Historical Basis

- `AI_Office_requirements_review_v0.23.md`
- `AIOffice_Gate2_Codex_handoff.md`
- `docs/gate2-plan.md`
- `docs/gate2-mock-implementation.md`

### Current Gate 3 Basis

- `docs/gate3-plan.md`
- Official FRED, ECOS, and OpenDART documentation linked from that plan

No open source license is granted in this repository unless the owner later approves one explicitly.
