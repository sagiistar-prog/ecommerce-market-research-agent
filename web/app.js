const briefInput = document.querySelector("#brief");
const competitorsInput = document.querySelector("#competitors");
const form = document.querySelector("#agent-form");
const statusText = document.querySelector("#status");
const reportPreview = document.querySelector("#report-preview");
const loadSampleButton = document.querySelector("#load-sample");
const copyButton = document.querySelector("#copy-report");
const downloadButton = document.querySelector("#download-report");

let latestReport = "";
let latestAnalysis = null;
let currentView = 'summary';
const dataButton = document.querySelector('#download-data');
const importButton = document.querySelector('#import-csv');
const fileInput = document.querySelector('#csv-file');
const resultNav = document.querySelector('#result-nav');
const staleNotice = document.querySelector('#stale-notice');

function setStatus(message) {
  statusText.textContent = message;
}

let busy = false;
let inputVersion = 0;
let resultVersion = -1;
let previousInput = null;
const submitButton = form.querySelector('[type="submit"]');
const undoButton = document.querySelector('#undo-sample');

function element(tag, value, className) {
  const node = document.createElement(tag);
  if (value != null) node.textContent = String(value).replaceAll('·', ' ');
  if (className) node.className = className;
  return node;
}

function refs(ids) {
  const container = element('div', null, 'evidence-refs');
  container.append(element('span', ids.length ? 'Based on' : 'Based on the brief'));
  for (const id of ids) {
    const button = element('button', id);
    button.type = 'button';
    button.setAttribute('aria-label', `View observation ${id}`);
    button.addEventListener('click', () => {
      currentView = 'evidence'; renderReview();
      const detail = document.getElementById(`observation-${id}`);
      if (detail) { detail.open = true; detail.querySelector('summary').focus(); detail.scrollIntoView({ block: 'nearest' }); }
    });
    container.append(button);
  }
  return container;
}

function renderReview() {
  if (!latestAnalysis) return;
  reportPreview.replaceChildren();
  for (const button of resultNav.querySelectorAll('button')) button.setAttribute('aria-pressed', String(button.dataset.view === currentView));
  const a = latestAnalysis;
  if (currentView === 'summary') {
    reportPreview.append(element('h3', a.brief.research_goal || 'Define the decision you want to make'));
    reportPreview.append(element('p', a.brief.category ? `${a.brief.category} / ${a.brief.target_country || 'Market not specified'}` : 'Your original brief is preserved in the exported report. Add labeled fields to focus the review.'));
    const s = a.sample;
    reportPreview.append(element('p', `${s.observation_count} observations, ${s.priced_count} prices, ${s.source_date_count} rows with source and date. ${s.synthetic_count} rows are synthetic.`, 'sample-summary'));
    reportPreview.append(element('p', 'This sample supports research planning. It does not establish demand, market share or a launch price.', 'field-help'));
    for (const item of a.observations) {
      const section = element('section', null, 'observation');
      section.append(element('p', item.text), refs(item.evidence_ids));
      reportPreview.append(section);
    }
    if (s.ungrouped_count) reportPreview.append(element('p', `${s.ungrouped_count} observations have no comparison group. Their prices are excluded from group statistics.`, 'field-help'));
    const next = element('button', 'Review next actions', 'secondary-button');
    next.type = 'button'; next.addEventListener('click', () => { currentView = 'tasks'; renderReview(); reportPreview.focus(); });
    reportPreview.append(next);
  } else if (currentView === 'tasks') {
    reportPreview.append(element('h3', 'Turn gaps into research tasks'));
    for (const item of a.research_tasks) {
      const section = element('section', null, 'research-task');
      section.append(element('h4', `${item.priority[0].toUpperCase()}${item.priority.slice(1)}: ${item.question}`), element('p', item.action));
      const detail = element('details'); detail.append(element('summary', 'What counts as completion'), element('p', item.success_signal));
      section.append(detail, refs(item.evidence_ids)); reportPreview.append(section);
    }
  } else {
    reportPreview.append(element('h3', 'Inspect the submitted evidence'), element('p', 'These are input records. Source links and evidence levels have not been verified.', 'field-help'));
    for (const item of a.evidence) {
      const detail = element('details', null, 'evidence-record'); detail.id = `observation-${item.id}`;
      detail.append(element('summary', `${item.id} / ${item.brand} / ${item.data_kind}`));
      const list = element('dl');
      for (const [label, value] of [['Price USD', item.price_usd == null ? null : item.price_usd.toFixed(2)], ['Channel', item.channel], ['Positioning', item.positioning_claim], ['Feature', item.key_feature], ['Content hook', item.content_hook], ['Group', item.comparison_group], ['Declared evidence', item.declared_evidence_level], ['Observed at', item.observed_at], ['Notes', item.notes]]) {
        list.append(element('dt', label), element('dd', value || 'Not provided'));
      }
      list.append(element('dt', 'Source'));
      const source = element('dd');
      if (item.source_url) {
        const link = element('a', item.source_url); link.href = item.source_url; link.target = '_blank'; link.rel = 'noopener noreferrer'; source.append(link);
      } else source.textContent = 'Not provided';
      list.append(source); detail.append(list); reportPreview.append(detail);
    }
  }
}

for (const button of resultNav.querySelectorAll('button')) button.addEventListener('click', () => { currentView = button.dataset.view; renderReview(); });

importButton.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', async () => {
  const file = fileInput.files[0]; fileInput.value = '';
  if (!file || busy) return;
  if (file.size > 400000) { setStatus('CSV is too large. Keep it under 100000 characters and 250 rows.'); return; }
  const version = inputVersion;
  busy = true; syncControls();
  try {
    const contents = new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer());
    if (contents.length > 100000) throw new Error('CSV is too large. Keep it under 100000 characters.');
    if (version !== inputVersion) { setStatus('Your edits were kept. Import again when ready.'); return; }
    previousInput = { brief: briefInput.value, competitors: competitorsInput.value };
    competitorsInput.value = contents; inputVersion += 1; undoButton.hidden = false;
    setStatus('CSV imported locally. You can undo this replacement.');
  } catch (error) { setStatus(error instanceof TypeError ? 'CSV could not be decoded. Save it as UTF-8 and import again.' : error.message); }
  finally { busy = false; syncControls(); }
});

dataButton.addEventListener('click', () => {
  if (dataButton.disabled) return;
  const link = document.createElement('a');
  link.href = URL.createObjectURL(new Blob([JSON.stringify({schema_version: '2.0', analysis: latestAnalysis}, null, 2)], {type:'application/json;charset=utf-8'}));
  link.download = 'market-research-evidence.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 1000); setStatus('Evidence JSON downloaded.');
});

function syncControls() {
  submitButton.disabled = busy;
  loadSampleButton.disabled = busy;
  copyButton.disabled = busy || !latestReport || resultVersion !== inputVersion;
  downloadButton.disabled = copyButton.disabled;
  dataButton.disabled = copyButton.disabled;
  importButton.disabled = busy;
  undoButton.disabled = busy;
  resultNav.hidden = !latestAnalysis;
  document.querySelector('.export-actions').hidden = !latestAnalysis;
  staleNotice.hidden = !latestAnalysis || resultVersion === inputVersion;
  form.setAttribute('aria-busy', String(busy));
  submitButton.textContent = busy ? 'Analyzing observations…' : 'Analyze observations';
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
  busy = true; syncControls(); setStatus('Checking your submitted observations…');
  try {
    const payload = await request('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(snapshot) });
    if (typeof payload.report !== 'string' || !payload.report.trim()) throw new Error('The report was empty. Please try again.');
    if (!payload.analysis?.evidence?.length) throw new Error('Analysis is missing. Check the local server version.');
    latestReport = payload.report;
    latestAnalysis = payload.analysis;
    currentView = 'summary';
    resultVersion = version;
    renderReview();
    if (window.matchMedia('(max-width: 980px)').matches) document.querySelector('#report-title').scrollIntoView({block: 'start'});
    setStatus(version === inputVersion ? 'Review ready. Sources have not been independently verified.' : 'Inputs changed during generation. Generate again to export the updated report.');
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
  link.download = 'market-research-review.md'; link.click();
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
