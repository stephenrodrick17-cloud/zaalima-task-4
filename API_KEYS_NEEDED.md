# API Keys 
### 1) OpenRouter API Key

Used for LLM access (chat/completions and/or embeddings depending on your implementation).

1. Create a key: https://openrouter.ai/keys
2. Add to `backend/.env`:

```env
OPENROUTER_API_KEY=your_actual_openrouter_key_here
```

Optional (recommended) metadata headers:

```env
OPENROUTER_SITE_URL=http://localhost:3000
OPENROUTER_APP_NAME=zaalima-task-4
```

### 2) Clerk Secret Key (Auth)

1. Get it from: https://dashboard.clerk.com/
2. Add to `backend/.env`:

```env
CLERK_SECRET_KEY=sk_test_your_actual_key_here
```

## Security notes

- **Never** commit `.env` files.
- Rotate keys immediately if you accidentally exposed them.

