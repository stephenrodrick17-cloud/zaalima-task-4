# Contributing
## Ground rules
- Keep changes small and focused.
- Prefer clear names and readable code over clever code.
- Add/update docs when behavior changes.

## Recommended workflow

1. **Create a branch**
   - `feature/<short-name>`
   - `fix/<short-name>`
   - `docs/<short-name>`

2. **Make your changes**
   - Keep formatting consistent with the existing code.
   - Avoid committing secrets (`.env`, API keys).

3. **Test locally**
   - Start backend + frontend (project-specific).
   - Verify core flows:
     - auth
     - chat
     - document upload / retrieval

4. **Open a Pull Request**
   - Describe what changed and why.
   - Include screenshots for UI changes.
   - Call out any breaking changes.

## Commit message style

Use short, descriptive messages. Examples:

- `feat: add document chunking`
- `fix: handle missing OPENROUTER_API_KEY`
- `docs: update setup instructions`

## Code style

- Prefer **ESLint/Prettier** if configured in the repo.
- Keep API responses consistent (shape + error codes).

## Adding new environment variables

- Update `API_KEYS_NEEDED.md` (or add a new section).
- If you have an example env file, update it too (e.g., `.env.example`).

