# ExtForge — Chrome Extension Generator

A clean, production-ready web app that turns plain-English descriptions
into complete, downloadable Chrome extensions using the Claude API.

## Files

```
extforge/
├── index.html    ← App shell & markup
├── styles.css    ← All styles (light + dark mode)
├── app.js        ← API calls, state, rendering logic
└── README.md     ← You are here
```

## How to run

### Option A — Open directly in browser
Just open `index.html` in Chrome, Firefox, or any modern browser.
No build step, no dependencies to install.

> **Note:** The Anthropic API is called client-side.  
> The app uses the embedded API key relay from Claude.ai Artifacts.  
> If you host this independently, add your own `x-api-key` header.

### Option B — Local dev server (recommended to avoid CORS issues)
```bash
# Python 3
python -m http.server 8080

# Node (npx)
npx serve .
```
Then open `http://localhost:8080`.

## Usage

1. Type what Chrome extension you want in the text area  
   (or click one of the example chips to prefill)
2. Press **Generate** or hit `Ctrl+Enter`
3. Browse the generated files in the left panel
4. Click any file to inspect the code
5. Hit **Download** (single file) or **Download all (.zip)** for everything

## Installing a generated extension in Chrome

1. Click **Download all (.zip)** and extract the archive
2. Open Chrome → `chrome://extensions`
3. Enable **Developer mode** (top-right toggle)
4. Click **Load unpacked** → select the extracted folder
5. The extension is now installed and ready to use

## Tech stack

| Concern       | Solution                          |
|---------------|-----------------------------------|
| AI generation | Claude Sonnet 4 (via Anthropic API) |
| Zipping files | JSZip 3.10 (cdnjs CDN)           |
| Fonts         | JetBrains Mono + Syne (Google Fonts) |
| Framework     | Vanilla HTML / CSS / JS — zero dependencies |

## Customisation

- **Model** — change `claude-sonnet-4-20250514` in `app.js` → `callClaudeAPI()`
- **System prompt** — edit `SYSTEM_PROMPT` in `app.js`
- **Example chips** — edit the `EXAMPLES` array in `app.js`
- **Theme** — all colours live in `:root` in `styles.css`; dark mode is handled automatically via `prefers-color-scheme`
