# ExtForge — Chrome Extension Generator

A clean, production-ready **vanilla web app** that turns plain‑English ideas into complete, downloadable **Chrome Extensions (Manifest V3)**.

Type what you want to build, click **Generate**, then preview every generated file and download either a single file or the entire extension as a `.zip`.

---

## What this project is

ExtForge is a single-page app (HTML/CSS/JS) that:
- sends your prompt to **Anthropic Claude**
- enforces **strict JSON output** from the model (so it’s machine-parseable)
- renders the returned file list like an IDE (file tree + code viewer)
- lets you download:
  - one file at a time, or
  - all files as a ZIP (via **JSZip**)

---

## Features

- **Prompt → extension generator** (Manifest V3)
- **Example chips** to quickly try common extension ideas
- **Strict JSON parsing** with fallback extraction for safety
- **File tree + code viewer** with line numbers
- **Download single file** (as plain text)
- **Download all as ZIP** (one click)
- **Status + notifications** for better UX
- **Keyboard shortcut:** `Ctrl + Enter` / `Cmd + Enter` to generate

---

## Tech Stack

- **HTML / CSS / JavaScript** (no build tools)
- **Claude Sonnet 4** (Anthropic Messages API)
- **JSZip** (CDN) for ZIP downloads
- Google Fonts: **JetBrains Mono** + **Syne**

---

## Project Structure

The runnable app lives in:

```text
Downloads/zallima 4 task/
├── index.html   # App shell & UI markup
├── styles.css   # Styling (light + dark via prefers-color-scheme)
├── app.js       # State, rendering, API calls, downloads
└── README.md    # App-specific notes
```

> Note: The root `README.md` also includes a week-by-week summary. This README focuses on the actual implemented app in the repository.

---

## Getting Started

### Option A — Open directly (quick test)

Open this file in a browser:

- `Downloads/zallima 4 task/index.html`

### Option B — Run via a local server (recommended)

Running from a server avoids common browser restrictions and makes fetch/CORS behavior more predictable.

```bash
# Python 3
python -m http.server 8080

# Node
npx serve .
```

Then open:
- `http://localhost:8080/Downloads/zallima%204%20task/`

---

## Usage

1. Open the app
2. Describe the Chrome extension you want to build
3. Click **Generate** (or press `Ctrl/Cmd + Enter`)
4. Preview the generated files in the left panel
5. Click a file to view its contents
6. Download:
   - **Download** (single file), or
   - **Download all (.zip)**

---

## Installing a generated extension in Chrome

1. Download the `.zip` and extract it
2. Open: `chrome://extensions`
3. Enable **Developer mode**
4. Click **Load unpacked**
5. Select the extracted folder

---

## API / Configuration Notes (Important)

This repo includes additional documentation:
- `API_KEYS_NEEDED.md` — required keys and where to place them
- `SECURITY.md` — security guidance (don’t commit secrets)
- `ARCHITECTURE.md` — high-level architecture notes

### Anthropic API call

In `Downloads/zallima 4 task/app.js`, the app calls:

- `https://api.anthropic.com/v1/messages`

If you run this app outside of the environment that injects API credentials (e.g., Claude artifacts / proxy setup), you will need to add proper headers (e.g., `x-api-key`) and handle CORS securely.

**Do not expose secret keys in frontend code for real deployments.**

---

## How generation works (high level)

1. Your prompt is sent with a strict `SYSTEM_PROMPT` requiring JSON output.
2. Claude returns JSON with:
   - `project_name`
   - `description`
   - `files[]` → `{ filename, content }`
3. The app parses the JSON and renders the file tree.
4. Downloads are created from Blob URLs or zipped via JSZip.

---

## Roadmap / Improvements (optional)

- Add server-side proxy to securely call Anthropic/OpenRouter without exposing keys
- Add schema validation (e.g., Zod) for stronger JSON guarantees
- Add syntax highlighting in the code viewer
- Add template presets for different extension categories

---

## Contributing

See `CONTRIBUTING.md` for recommended workflow and commit conventions.

---

## License

If this project needs an explicit license, add a `LICENSE` file (MIT/Apache-2.0 recommended).
