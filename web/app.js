const briefInput = document.querySelector("#brief");
const competitorsInput = document.querySelector("#competitors");
const form = document.querySelector("#agent-form");
const statusText = document.querySelector("#status");
const reportPreview = document.querySelector("#report-preview");
const loadSampleButton = document.querySelector("#load-sample");
const copyButton = document.querySelector("#copy-report");
const downloadButton = document.querySelector("#download-report");

let latestReport = "";

function setStatus(message) {
  statusText.textContent = message;
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderInline(value) {
  return escapeHtml(value)
    .replaceAll(/`([^`]+)`/g, "<code>$1</code>")
    .replaceAll(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function renderTable(lines, startIndex) {
  const tableLines = [];
  let index = startIndex;
  while (index < lines.length && lines[index].trim().startsWith("|")) {
    tableLines.push(lines[index].trim());
    index += 1;
  }

  if (tableLines.length < 2) {
    return { html: `<p>${renderInline(lines[startIndex])}</p>`, nextIndex: startIndex + 1 };
  }

  const rows = tableLines
    .filter((line, rowIndex) => rowIndex !== 1)
    .map((line) => line.slice(1, -1).split("|").map((cell) => cell.trim()));

  const header = rows.shift() || [];
  const head = `<thead><tr>${header.map((cell) => `<th>${renderInline(cell)}</th>`).join("")}</tr></thead>`;
  const body = `<tbody>${rows
    .map((row) => `<tr>${row.map((cell) => `<td>${renderInline(cell)}</td>`).join("")}</tr>`)
    .join("")}</tbody>`;
  return { html: `<table>${head}${body}</table>`, nextIndex: index };
}

function renderMarkdown(markdown) {
  const lines = markdown.split(/\r?\n/);
  const html = [];
  let listOpen = false;

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const trimmed = line.trim();

    if (!trimmed) {
      if (listOpen) {
        html.push("</ul>");
        listOpen = false;
      }
      continue;
    }

    if (trimmed.startsWith("|")) {
      if (listOpen) {
        html.push("</ul>");
        listOpen = false;
      }
      const table = renderTable(lines, index);
      html.push(table.html);
      index = table.nextIndex - 1;
      continue;
    }

    if (trimmed.startsWith("### ")) {
      if (listOpen) {
        html.push("</ul>");
        listOpen = false;
      }
      html.push(`<h3>${renderInline(trimmed.slice(4))}</h3>`);
      continue;
    }

    if (trimmed.startsWith("## ")) {
      if (listOpen) {
        html.push("</ul>");
        listOpen = false;
      }
      html.push(`<h2>${renderInline(trimmed.slice(3))}</h2>`);
      continue;
    }

    if (trimmed.startsWith("# ")) {
      if (listOpen) {
        html.push("</ul>");
        listOpen = false;
      }
      html.push(`<h1>${renderInline(trimmed.slice(2))}</h1>`);
      continue;
    }

    if (trimmed.startsWith("- ")) {
      if (!listOpen) {
        html.push("<ul>");
        listOpen = true;
      }
      html.push(`<li>${renderInline(trimmed.slice(2))}</li>`);
      continue;
    }

    if (listOpen) {
      html.push("</ul>");
      listOpen = false;
    }
    html.push(`<p>${renderInline(trimmed)}</p>`);
  }

  if (listOpen) {
    html.push("</ul>");
  }

  return html.join("");
}


let busy = false;
let inputVersion = 0;
let resultVersion = -1;
let previousInput = null;
const submitButton = form.querySelector('[type="submit"]');
const undoButton = document.querySelector('#undo-sample');

function syncControls() {
  submitButton.disabled = busy;
  loadSampleButton.disabled = busy;
  copyButton.disabled = busy || !latestReport || resultVersion !== inputVersion;
  downloadButton.disabled = copyButton.disabled;
  form.setAttribute('aria-busy', String(busy));
  submitButton.textContent = busy ? 'Generating report…' : 'Generate report';
}

async function request(url, options = {}) {
  const response = await fetch(url, { ...options, signal: AbortSignal.timeout(30000) });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || 'Unable to complete the request.');
  return payload;
}

async function loadSample() {
  if (busy) return;
  const startedAt = inputVersion;
  busy = true; syncControls(); setStatus('Loading fictional sample…');
  try {
    const sample = await request('/api/sample');
    if (inputVersion !== startedAt) { setStatus('Your edits were kept. Load the sample again when ready.'); return; }
    previousInput = { brief: briefInput.value, competitors: competitorsInput.value };
    briefInput.value = sample.brief || '';
    competitorsInput.value = sample.competitors || '';
    inputVersion += 1; undoButton.hidden = false;
    setStatus('Fictional sample loaded. You can undo this replacement.');
  } catch { setStatus('Sample could not be loaded. Your input is unchanged; try again.'); }
  finally { busy = false; syncControls(); }
}

async function generateReport(event) {
  event.preventDefault();
  if (busy) return;
  const version = inputVersion;
  const snapshot = { brief: briefInput.value, competitors: competitorsInput.value };
  if (!snapshot.brief.trim() || !snapshot.competitors.trim()) { setStatus('Add a product brief and competitor CSV before generating.'); return; }
  busy = true; syncControls(); setStatus('Generating from your submitted inputs…');
  try {
    const payload = await request('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(snapshot) });
    if (typeof payload.report !== 'string' || !payload.report.trim()) throw new Error('The report was empty. Please try again.');
    latestReport = payload.report;
    resultVersion = version;
    reportPreview.innerHTML = renderMarkdown(latestReport);
    setStatus(version === inputVersion ? 'Report ready. Review the evidence before exporting.' : 'Inputs changed during generation. Generate again to export the updated report.');
  } catch (error) {
    setStatus(error.name === 'TypeError' || error.name === 'TimeoutError' ? 'Connection interrupted. Your inputs and previous report are preserved. Try again.' : error.message);
  } finally { busy = false; syncControls(); }
}

async function copyReport() {
  if (copyButton.disabled) return;
  try { await navigator.clipboard.writeText(latestReport); setStatus('Report copied.'); }
  catch { setStatus('Clipboard access was denied. Use Download to keep your report.'); }
}

function downloadReport() {
  if (downloadButton.disabled) return;
  const link = document.createElement('a');
  link.href = URL.createObjectURL(new Blob([latestReport], { type: 'text/markdown;charset=utf-8' }));
  link.download = 'market-research-demo.md'; link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  setStatus('Report downloaded.');
}

for (const input of [briefInput, competitorsInput]) input.addEventListener('input', () => {
  inputVersion += 1; syncControls();
  if (latestReport) setStatus('Inputs changed. Generate again to update the report.');
});
undoButton.addEventListener('click', () => {
  if (!previousInput || busy) return;
  briefInput.value = previousInput.brief; competitorsInput.value = previousInput.competitors;
  inputVersion += 1; previousInput = null; undoButton.hidden = true;
  setStatus('Previous inputs restored.'); syncControls();
});
form.addEventListener('keydown', event => {
  if (event.key === 'Enter' && (event.ctrlKey || event.metaKey) && !event.isComposing) { event.preventDefault(); form.requestSubmit(); }
});
loadSampleButton.addEventListener('click', loadSample);
form.addEventListener('submit', generateReport);
copyButton.addEventListener('click', copyReport);
downloadButton.addEventListener('click', downloadReport);
syncControls();
