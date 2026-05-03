/* ============================================================
   ExtForge — Chrome Extension Generator
   app.js
   ============================================================ */

'use strict';

// ─── SYSTEM PROMPT ──────────────────────────────────────────
const SYSTEM_PROMPT = `You are an expert Chrome Extension Architect and Senior Software Engineer.
Your task is to generate COMPLETE, WORKING, and PRODUCTION-READY browser extensions.
You MUST always return output ONLY in STRICT VALID JSON format.
The JSON structure must follow this exact schema:

{
  "project_name": "string",
  "description": "string",
  "files": [
    {
      "filename": "string",
      "content": "string"
    }
  ]
}

CRITICAL RULES:
1. Output ONLY valid JSON.
2. Do NOT include markdown.
3. Do NOT wrap output inside triple backticks.
4. Do NOT include explanations outside JSON.
5. Every file must contain complete code.
6. All code must be properly escaped for JSON.
7. Ensure all quotation marks inside code are escaped correctly.
8. Include ALL necessary files for the extension to run.
9. Use Manifest V3 for Chrome extensions.
10. Ensure the extension is fully functional without missing dependencies.
11. If icons are needed, create placeholder references.
12. Use clean, modular, readable code.
13. The JSON must always be parseable with JSON.parse().
14. Never output trailing commas.
15. Never include comments outside code strings.
16. Include installation instructions inside a README.md file.
17. If CSS or JS files are needed, create separate files.
18. Always generate realistic folder structures.
19. Ensure filenames are unique.
20. Never omit required files like manifest.json.
For browser extensions:
Always include: manifest.json, popup.html, popup.js, popup.css, README.md
Include background.js if needed.
Include content.js if needed.
Include icons references if needed.
Code Quality Requirements:
Use semantic HTML. Use modern JavaScript (ES6+). Avoid inline CSS. Avoid inline JS.
Use async/await where appropriate. Add error handling. Keep code beginner-friendly but production-ready.
VALIDATION REQUIREMENTS: Before outputting:
Verify the JSON is syntactically valid. Verify every opening brace has a closing brace.
Verify all quotes are escaped. Verify all filenames are non-empty. Verify all content fields are strings.
Verify manifest.json contains valid Manifest V3 structure.
OUTPUT POLICY: Return ONLY the JSON object. No extra text. No markdown. No explanations.`;

// ─── EXAMPLE CHIPS ──────────────────────────────────────────
const EXAMPLES = [
  'Dark mode toggle for any website',
  'YouTube video speed controller',
  'Tab group organizer by domain',
  'Reading time estimator for articles',
  'Focus mode — block distracting sites',
  'Copy page URL with one click',
  'Word count on selected text',
  'JSON formatter for API responses',
];

// ─── FILE ICON MAP ──────────────────────────────────────────
const FILE_ICONS = {
  js:   { stroke: '#d97706' },
  ts:   { stroke: '#2563eb' },
  html: { stroke: '#e2580c' },
  css:  { stroke: '#059669' },
  json: { stroke: '#7c3aed' },
  md:   { stroke: '#64748b' },
  txt:  { stroke: '#64748b' },
  png:  { stroke: '#0891b2' },
  jpg:  { stroke: '#0891b2' },
  svg:  { stroke: '#0891b2' },
};

// ─── STATE ──────────────────────────────────────────────────
let generatedFiles = [];
let selectedFileIndex = -1;
let projectName = 'chrome-extension';

// ─── DOM REFS ───────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

const promptInput    = $('prompt-input');
const generateBtn    = $('generate-btn');
const statusDot      = $('status-dot');
const statusText     = $('status-text');
const fileList       = $('file-list');
const treeEmpty      = $('tree-empty');
const fileTreeFooter = $('file-tree-footer');
const extInfoBar     = $('ext-info-bar');
const extNameBadge   = $('ext-name-badge');
const extDescBadge   = $('ext-desc-badge');
const codeHeader     = $('code-header');
const codeTitle      = $('code-title');
const codeContent    = $('code-content');
const emptyViewer    = $('empty-viewer');
const downloadFileBtn = $('download-file-btn');
const downloadAllBtn  = $('download-all-btn');
const notif           = $('notif');
const notifText       = $('notif-text');
const chipsContainer  = $('chips');

// ─── HELPERS ────────────────────────────────────────────────

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function getFileExtension(filename) {
  return filename.split('.').pop().toLowerCase();
}

function buildFileIcon(filename) {
  const ext = getFileExtension(filename);
  const color = FILE_ICONS[ext]?.stroke || '#9ca3af';
  return `<svg class="file-icon" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2">
    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
    <polyline points="13 2 13 9 20 9"/>
  </svg>`;
}

function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
}

// ─── STATUS & NOTIFICATIONS ─────────────────────────────────

function setStatus(type, message) {
  statusDot.className = `status-dot ${type}`;
  statusText.textContent = message;
}

let notifTimer = null;
function showNotif(type, message) {
  if (notifTimer) clearTimeout(notifTimer);
  notif.className = `notif ${type}`;
  notifText.textContent = message;
  notif.classList.add('show');
  notifTimer = setTimeout(() => notif.classList.remove('show'), 3000);
}

// ─── FILE RENDERING ─────────────────────────────────────────

function renderFileTree(files, name, description) {
  projectName = name;

  // Show info bar
  extInfoBar.style.display = 'flex';
  extNameBadge.textContent = name;
  extDescBadge.textContent =
    description.length > 65 ? description.slice(0, 65) + '…' : description;

  // Clear old items
  fileList.innerHTML = '';

  files.forEach((file, index) => {
    const item = document.createElement('div');
    item.className = 'file-item' + (index === 0 ? ' active' : '');
    item.innerHTML = buildFileIcon(file.filename) +
      `<span class="file-name">${escapeHtml(file.filename)}</span>`;
    item.addEventListener('click', () => selectFile(index));
    fileList.appendChild(item);
  });

  fileTreeFooter.style.display = 'flex';

  // Auto-open first file
  if (files.length > 0) selectFile(0);
}

function selectFile(index) {
  const items = fileList.querySelectorAll('.file-item');
  items.forEach((el, i) => el.classList.toggle('active', i === index));

  selectedFileIndex = index;
  const file = generatedFiles[index];

  codeHeader.style.display = 'flex';
  codeTitle.textContent = file.filename;

  if (emptyViewer) emptyViewer.style.display = 'none';

  // Build line-numbered code display
  const lines = file.content.split('\n');
  const pre = document.createElement('pre');
  pre.className = 'code-pre';

  lines.forEach((line, i) => {
    const div = document.createElement('div');
    div.className = 'code-line';
    div.innerHTML =
      `<span class="line-num">${i + 1}</span>` +
      `<span class="line-content">${escapeHtml(line) || ' '}</span>`;
    pre.appendChild(div);
  });

  codeContent.innerHTML = '';
  codeContent.appendChild(pre);
}

// ─── DOWNLOAD ───────────────────────────────────────────────

function downloadSingleFile(filename, content) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showNotif('success', `Downloaded ${filename}`);
}

async function downloadAllAsZip(files, name) {
  if (typeof JSZip === 'undefined') {
    showNotif('error', 'JSZip library not available');
    return;
  }

  try {
    const zip    = new JSZip();
    const folder = zip.folder(slugify(name));

    files.forEach((f) => folder.file(f.filename, f.content));

    const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `${slugify(name)}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showNotif('success', `Downloaded ${files.length} files as .zip`);
  } catch (err) {
    showNotif('error', 'Zip failed: ' + err.message);
    console.error('[ExtForge] Zip error:', err);
  }
}

// ─── JSON PARSING ───────────────────────────────────────────

function parseGeneratedJSON(raw) {
  let cleaned = raw.trim();

  // Strip any accidental markdown fences
  cleaned = cleaned
    .replace(/^```json\s*/i, '')
    .replace(/^```\s*/i, '')
    .replace(/\s*```$/i, '');

  // First attempt: direct parse
  try {
    return JSON.parse(cleaned);
  } catch (_) {
    // Fallback: extract first {...} block
    const match = cleaned.match(/\{[\s\S]*\}/);
    if (match) {
      return JSON.parse(match[0]);
    }
    throw new Error('Model returned unparseable JSON. Try regenerating.');
  }
}

// ─── API CALL ───────────────────────────────────────────────

async function callClaudeAPI(userPrompt) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model:      'claude-sonnet-4-20250514',
      max_tokens: 8000,
      system:     SYSTEM_PROMPT,
      messages:   [{ role: 'user', content: userPrompt }],
    }),
  });

  if (!response.ok) {
    let errMsg = `HTTP ${response.status}`;
    try {
      const errData = await response.json();
      errMsg = errData?.error?.message || errMsg;
    } catch (_) { /* ignore */ }
    throw new Error(errMsg);
  }

  const data = await response.json();
  const textBlock = data.content?.find((c) => c.type === 'text');

  if (!textBlock?.text) {
    throw new Error('Empty response from API');
  }

  return textBlock.text;
}

// ─── GENERATE FLOW ──────────────────────────────────────────

async function generate() {
  const prompt = promptInput.value.trim();

  if (!prompt) {
    showNotif('error', 'Please describe your extension first');
    promptInput.focus();
    return;
  }

  // Set loading state
  generateBtn.disabled = true;
  generateBtn.innerHTML = '<div class="loader-spinner"></div> Generating…';
  setStatus('loading', 'Calling Claude API — generating extension files…');

  try {
    const rawText = await callClaudeAPI(prompt);

    setStatus('loading', 'Parsing generated files…');
    const parsed = parseGeneratedJSON(rawText);

    if (!Array.isArray(parsed.files) || parsed.files.length === 0) {
      throw new Error('No files found in the generated response');
    }

    generatedFiles = parsed.files;
    renderFileTree(
      parsed.files,
      parsed.project_name || 'my-extension',
      parsed.description  || ''
    );

    setStatus('success', `Generated ${parsed.files.length} files — ${parsed.project_name}`);
    showNotif('success', `${parsed.files.length} files ready to download!`);

  } catch (err) {
    setStatus('error', 'Error: ' + err.message);
    showNotif('error', err.message.slice(0, 90));
    console.error('[ExtForge] Generation error:', err);
  } finally {
    generateBtn.disabled = false;
    generateBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polygon points="5 3 19 12 5 21 5 3"/>
      </svg>
      Generate`;
  }
}

// ─── EVENT LISTENERS ────────────────────────────────────────

generateBtn.addEventListener('click', generate);

// Ctrl/Cmd + Enter to generate
promptInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) generate();
});

// Download current file
downloadFileBtn.addEventListener('click', () => {
  if (selectedFileIndex >= 0 && generatedFiles[selectedFileIndex]) {
    const f = generatedFiles[selectedFileIndex];
    downloadSingleFile(f.filename, f.content);
  }
});

// Download all as ZIP
downloadAllBtn.addEventListener('click', () => {
  if (generatedFiles.length > 0) {
    downloadAllAsZip(generatedFiles, projectName);
  }
});

// ─── QUICK-FILL CHIPS ───────────────────────────────────────

EXAMPLES.forEach((example) => {
  const chip = document.createElement('button');
  chip.className = 'chip';
  chip.textContent = example;
  chip.addEventListener('click', () => {
    promptInput.value = example;
    promptInput.focus();
  });
  chipsContainer.appendChild(chip);
});
