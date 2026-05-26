# Security Policy

This repository contains code that uses external API keys and authentication providers.

## Reporting a vulnerability

If you discover a security issue, **do not open a public issue** with sensitive details.

Instead, report it privately to the repository owner/maintainers.

Include:

- A clear description of the issue
- Steps to reproduce
- Impact assessment
- Any suggested fix

## Secrets and credentials

- Do **not** commit secrets.
- Keep secrets in `backend/.env`.
- Add `.env` to `.gitignore`.
- Rotate any key immediately if it is exposed.

### Known secrets used by this project

- `OPENROUTER_API_KEY`
- `CLERK_SECRET_KEY`

(Keep this list updated as new providers are added.)

## Authentication

- Clerk is used for authentication.
- Backend must verify incoming tokens server-side.
- Avoid “temporary auth bypass” in production.

## Dependency security

Recommended practices:

- Keep dependencies up to date.
- Use `npm audit` / `pnpm audit`.
- Enable Dependabot alerts (if available).

