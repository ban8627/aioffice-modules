# Security Policy

## Public Repository Rule

This repository is public. Do not commit personal information, account data, portfolio data, API keys, tokens, passwords, cookies, private keys, production logs, real environment configuration, or private source materials.

## Domain Safety

- Investment modules are limited to analysis and reporting.
- Do not automate real orders or financial transactions.
- Brokerage API designs must request read-only scopes.
- Content modules must not store private master assets unless the storage location is explicitly approved.

## Secret Handling

- Store secrets only in approved secret stores after the technology stack is approved.
- Keep decryption keys separate from encrypted data.
- Use least-privilege credentials.
- Never place secret values in prompts, logs, screenshots, generated documents, or Git history.

## Reporting

If a secret or personal dataset is found in the repository, stop work, avoid printing the value, and report the path and remediation steps without revealing the secret.
