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

async function loadSample() {
  setStatus("Loading sample");
  const response = await fetch("/api/sample");
  const sample = await response.json();
  briefInput.value = sample.brief || "";
  competitorsInput.value = sample.competitors || "";
  setStatus("Sample loaded");
}

async function generateReport(event) {
  event.preventDefault();
  setStatus("Generating");
  reportPreview.innerHTML = '<p class="empty-state">Generating report...</p>';

  const response = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      brief: briefInput.value,
      competitors: competitorsInput.value,
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    latestReport = "";
    reportPreview.innerHTML = `<p class="error">${escapeHtml(payload.error || "Unable to generate report.")}</p>`;
    setStatus("Needs input review");
    return;
  }

  latestReport = payload.report || "";
  reportPreview.innerHTML = renderMarkdown(latestReport);
  setStatus("Report ready");
}

async function copyReport() {
  if (!latestReport) {
    setStatus("No report to copy");
    return;
  }
  await navigator.clipboard.writeText(latestReport);
  setStatus("Copied");
}

function downloadReport() {
  if (!latestReport) {
    setStatus("No report to download");
    return;
  }
  const blob = new Blob([latestReport], { type: "text/markdown;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "generated_market_report.md";
  link.click();
  URL.revokeObjectURL(link.href);
  setStatus("Downloaded");
}

loadSampleButton.addEventListener("click", loadSample);
form.addEventListener("submit", generateReport);
copyButton.addEventListener("click", copyReport);
downloadButton.addEventListener("click", downloadReport);

loadSample().catch(() => setStatus("Sample unavailable"));
