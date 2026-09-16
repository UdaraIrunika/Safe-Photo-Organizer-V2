const state = {
  plan: null,
  executionRows: [],
  scan: null,
  history: {},
  operation: null,
};

function updateOperationControls() {
  const controls = document.getElementById('operationControls');
  const operation = state.operation;
  if (!controls) return;
  controls.hidden = !operation || operation.dryRun;
  if (operation && !operation.dryRun) {
    document.getElementById('pauseOperationButton').disabled = !operation.controller || operation.paused;
    document.getElementById('resumeOperationButton').disabled = Boolean(operation.controller) || !operation.paused;
  }
}

function pauseOperation() {
  if (!state.operation || state.operation.dryRun || !state.operation.controller) return;
  state.operation.paused = true;
  state.operation.controller.abort();
  document.getElementById('progressText').textContent = 'Execution paused. Resume when ready.';
  updateOperationControls();
}

function resumeOperation() {
  if (!state.operation || state.operation.dryRun || !state.operation.paused) return;
  state.operation.paused = false;
  runExecute(false, true);
}

function cancelOperation() {
  if (!state.operation || state.operation.dryRun) return;
  state.operation.cancelled = true;
  if (state.operation.controller) {
    state.operation.controller.abort();
  } else {
    state.operation = null;
    updateOperationControls();
  }
  document.getElementById('progressText').textContent = 'Execution cancelled.';
}

const historyLabels = {
  plan: 'Plan History',
  directories: 'Directory History',
  execute_approved: 'Execute Approved Plan History',
  dry_run: 'Dry Run Execute History',
  file_names: 'File Name History',
};

async function loadHistory() {
  const response = await fetch('/api/history');
  if (!response.ok) return;
  state.history = await response.json();
}

async function clearHistory() {
  if (!window.confirm('Clear all saved history? This cannot be undone.')) return;
  const response = await fetch('/api/history', { method: 'DELETE' });
  if (!response.ok) {
    alert('Unable to clear history.');
    return;
  }
  state.history = { plan: [], directories: [], execute_approved: [], dry_run: [], file_names: [] };
  closeHistory();
  alert('History cleared successfully.');
}

function historyDetail(record, key) {
  const details = record.details || {};
  if (key === 'file_names') return `${(details.files || []).length} file names`;
  if (key === 'directories') return `${details.count || 0} directories`;
  if (key === 'plan') return `${details.media_count || 0} media planned`;
  const report = details.report || {};
  return `${report.copied || 0} copied, ${report.verified || 0} verified`;
}

function showHistory(key) {
  const records = state.history[key] || [];
  document.getElementById('historyModalTitle').textContent = historyLabels[key] || 'History';
  const list = document.getElementById('historyList');
  list.innerHTML = '';
  records.forEach((record) => {
    const item = document.createElement('div');
    item.className = 'history-record';
    const title = document.createElement('strong');
    title.textContent = historyDetail(record, key);
    const source = document.createElement('small');
    source.textContent = `${record.source} - ${new Date(record.created_at).toLocaleString()}`;
    item.append(title, source);
    if (key === 'file_names') {
      const files = document.createElement('div');
      files.className = 'muted';
      files.textContent = (record.details.files || []).slice(0, 30).join(', ') || 'No files';
      item.appendChild(files);
    }
    list.appendChild(item);
  });
  if (!records.length) list.innerHTML = '<div class="muted">No history recorded yet.</div>';
  document.getElementById('historyModal').hidden = false;
}

function closeHistory() {
  document.getElementById('historyModal').hidden = true;
}

function closeAbout() {
  document.getElementById('aboutModal').hidden = true;
}

function browseFolder(targetId) {
  const input = document.getElementById(targetId);
  const picker = document.getElementById('folderPicker');

  if (picker) {
    picker.onchange = (event) => {
      const files = event.target.files;
      if (!files || !files.length) {
        return;
      }

      const firstFile = files[0];
      const relativePath = firstFile.webkitRelativePath || '';
      const selectedFolder = relativePath ? relativePath.split('/').slice(0, -1).join('/') || '.' : '';

      if (selectedFolder && selectedFolder !== '.') {
        input.value = selectedFolder;
      } else {
        const fallback = window.prompt('Enter the source folder path', input.value || '');
        if (fallback) {
          input.value = fallback;
        }
      }

      picker.value = '';
    };

    if (typeof picker.showPicker === 'function') {
      picker.showPicker();
      return;
    }

    picker.click();
    return;
  }

  const chosen = window.prompt('Enter the source folder path', input.value || '');
  if (chosen) {
    input.value = chosen;
  }
}

async function apiCall(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(errorData.detail || 'Request failed');
  }

  return response.json();
}

function updateSummary(planSummary, scan = state.scan) {
  if (!planSummary) return;
  document.getElementById('totalMedia').textContent = planSummary.total || 0;
  const listedFolders = Array.isArray(scan?.folder_paths)
    ? scan.folder_paths.filter((folder) => folder && folder !== '.').length
    : 0;
  const folderCount = scan?.subfolders ?? (listedFolders || Math.max((scan?.folders || 0) - 1, 0));
  document.getElementById('totalMediaDetails').textContent = `${planSummary.total || 0} media / ${folderCount} folders`;
  document.getElementById('subfolderCount').textContent = folderCount;
  document.getElementById('plannedCount').textContent = planSummary.planned || 0;
  document.getElementById('reviewCount').textContent = planSummary.review_required || 0;
  document.getElementById('conflictCount').textContent = planSummary.conflicts || 0;
  document.getElementById('copiedCount').textContent = '0';
  document.getElementById('verifiedCount').textContent = '0';
}

function summaryLabel(summaryKey) {
  return {
    total: 'Total Media',
    planned: 'Planned',
    review_required: 'Review Required',
    conflicts: 'Conflicts',
    copied: 'Copied',
    verified: 'Verified',
    subfolders: 'Subfolders',
  }[summaryKey] || 'Summary';
}

function rowMatchesSummary(row, summaryKey) {
  const executionStatus = row.live_status || row.execution_status;
  if (summaryKey === 'total') return true;
  if (summaryKey === 'planned') return row.status === 'PLANNED' || executionStatus === 'PLANNED';
  if (summaryKey === 'review_required') return row.status === 'REVIEW_REQUIRED';
  if (summaryKey === 'conflicts') return row.status === 'DATE_CONFLICT';
  if (summaryKey === 'copied' || summaryKey === 'verified') return executionStatus === 'VERIFIED';
  if (summaryKey === 'subfolders') return false;
  return false;
}

function showSummaryDetails(summaryKey) {
  const matchingRows = state.executionRows.filter((row) => rowMatchesSummary(row, summaryKey));
  const folders = new Map();
  matchingRows.forEach((row) => {
    const parts = (row.relative_path || '').split(/[\\/]/).filter(Boolean);
    parts.pop();
    const folder = parts.length ? parts.join('/') : '(root)';
    folders.set(folder, (folders.get(folder) || 0) + 1);
  });

  if (summaryKey === 'subfolders') {
    (state.scan?.folder_paths || []).filter((folder) => folder !== '.').forEach((folder) => {
      const mediaCount = state.executionRows.filter((row) => {
        const relativePath = row.relative_path || '';
        return relativePath.startsWith(`${folder}/`) || relativePath.startsWith(`${folder}\\`);
      }).length;
      folders.set(folder, mediaCount);
    });
  }

  document.getElementById('summaryModalTitle').textContent = summaryKey === 'subfolders'
    ? 'Subfolders'
    : `${summaryLabel(summaryKey)} by subfolder`;
  document.getElementById('summaryModalTotal').textContent = `Total: ${summaryKey === 'subfolders' ? folders.size : matchingRows.length}`;
  const breakdown = document.getElementById('folderBreakdown');
  breakdown.innerHTML = '';
  [...folders.entries()].sort((left, right) => left[0].localeCompare(right[0])).forEach(([folder, count]) => {
    const row = document.createElement('div');
    row.className = 'folder-row';
    const name = document.createElement('span');
    name.textContent = folder;
    const value = document.createElement('strong');
    value.textContent = count;
    row.append(name, value);
    breakdown.appendChild(row);
  });
  if (!folders.size) {
    breakdown.innerHTML = '<div class="muted">No files in this category yet.</div>';
  }
  document.getElementById('summaryModal').hidden = false;
}

function closeSummaryDetails() {
  document.getElementById('summaryModal').hidden = true;
}

function previewMarkup(row) {
  const mediaType = (row.media_type || '').toUpperCase();
  if (!row.source || !mediaType) {
    return '<span class="preview-placeholder">No preview</span>';
  }

  const previewUrl = `/api/preview?path=${encodeURIComponent(row.source)}`;
  if (mediaType === 'IMAGE') {
    return `<img class="file-preview" src="${previewUrl}" alt="Photo preview" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('span'), { className: 'preview-placeholder', textContent: 'Unavailable' }))">`;
  }
  if (mediaType === 'VIDEO') {
    return `<video class="file-preview" src="${previewUrl}" muted preload="metadata" controls aria-label="Video preview"></video>`;
  }
  return '<span class="preview-placeholder">No preview</span>';
}

function renderRows(rows) {
  const tbody = document.getElementById('resultTableBody');
  tbody.innerHTML = '';

  rows.forEach((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="preview-cell">${previewMarkup(row)}</td>
      <td>${row.source ? row.source.split(/[\\/]/).pop() : ''}</td>
      <td>${row.relative_path || ''}</td>
      <td>${row.detected_date || 'N/A'}</td>
      <td>${row.date_source || 'UNKNOWN'}</td>
      <td>${row.planned_destination || ''}</td>
      <td><span class="status-pill status-${row.live_status || row.execution_status || row.status || 'PLANNED'}">${row.live_status || row.execution_status || row.status || 'PLANNED'}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderPlan(planData) {
  state.plan = planData;
  state.scan = planData.scan || null;
  state.executionRows = (planData.plan || []).map((item) => ({ ...item }));
  const summary = planData.summary || {};
  updateSummary(summary, state.scan);

  const rows = state.executionRows.slice(0, 200);
  renderRows(rows);

  const progress = rows.length ? 100 : 0;
  document.getElementById('progressBar').style.width = `${progress}%`;
  document.getElementById('progressText').textContent = `Loaded ${rows.length} media items from the selected source.`;
}

async function createPlan() {
  const source = document.getElementById('sourceFolder').value.trim();
  if (!source) {
    alert('Please choose a source folder first.');
    return;
  }

  const planButton = document.getElementById('planButton');
  try {
    planButton.disabled = true;
    planButton.classList.add('is-loading');
    document.getElementById('progressText').textContent = 'Creating plan...';
    const result = await apiCall('/api/plan', { source });
    renderPlan(result);
    document.getElementById('progressText').textContent = `Plan created successfully. Loaded ${state.executionRows.length} media items.`;
  } catch (error) {
    alert(error.message);
    document.getElementById('progressText').textContent = `Plan creation failed: ${error.message}`;
  } finally {
    planButton.disabled = false;
    planButton.classList.remove('is-loading');
  }
}

async function runExecute(dryRun, resume = false) {
  const source = resume && state.operation
    ? state.operation.source
    : document.getElementById('sourceFolder').value.trim();
  if (!source) {
    alert('Please choose a source folder first.');
    return;
  }

  const buttons = [
    document.getElementById('planButton'),
    document.getElementById('dryRunButton'),
    document.getElementById('startButton'),
  ];
  const activeButton = dryRun ? buttons[1] : buttons[2];
  if (!resume) {
    state.operation = { source, dryRun, paused: false, cancelled: false, controller: null };
  }
  const controller = new AbortController();
  state.operation.controller = controller;
  updateOperationControls();

  try {
    buttons.forEach((button) => {
      button.disabled = true;
      if (button === activeButton) {
        button.classList.add('is-loading');
      }
    });
    document.getElementById('progressText').textContent = dryRun ? 'Starting dry run...' : 'Starting execution...';

    const response = await fetch('/api/execute/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source, dry_run: dryRun }),
      signal: controller.signal,
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(errorData.detail || 'Request failed');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      lines.filter((line) => line.trim()).forEach((line) => {
        const event = JSON.parse(line);
        if (event.type === 'started') {
          document.getElementById('totalMedia').textContent = event.total || 0;
        } else if (event.type === 'progress') {
          const percent = event.total ? Math.round((event.completed / event.total) * 100) : 100;
          document.getElementById('progressBar').style.width = `${percent}%`;
          document.getElementById('progressText').textContent = `${dryRun ? 'Dry run' : 'Executing'} ${event.completed} of ${event.total}...`;
          const summary = event.summary || {};
          document.getElementById('copiedCount').textContent = summary.copied || 0;
          document.getElementById('verifiedCount').textContent = summary.verified || 0;
          const item = event.item || {};
          const matchingRow = state.executionRows.find((row) => row.source === item.source);
          if (matchingRow) {
            matchingRow.live_status = item.execution_status || matchingRow.status;
            renderRows(state.executionRows.slice(0, 200));
          }
        } else if (event.type === 'complete') {
          const report = event.report || {};
          const review = event.review || {};
          document.getElementById('plannedCount').textContent = report.planned || 0;
          document.getElementById('reviewCount').textContent = report.review_required || 0;
          document.getElementById('conflictCount').textContent = report.conflicts || 0;
          document.getElementById('copiedCount').textContent = report.copied || 0;
          document.getElementById('verifiedCount').textContent = report.verified || 0;
          document.getElementById('progressBar').style.width = '100%';
          document.getElementById('progressText').textContent = dryRun
            ? `Dry run completed. Review queue items: ${review.review ? review.review.length : 0}`
            : `Execution completed. Copied: ${report.copied || 0}, Verified: ${report.verified || 0}`;
          window.alert(dryRun
            ? 'Dry run completed successfully.'
            : `Execution completed. Copied: ${report.copied || 0}, Verified: ${report.verified || 0}.`);
          state.operation = null;
          updateOperationControls();
        }
      });

      if (done) break;
    }
  } catch (error) {
    if (error.name === 'AbortError' && state.operation?.cancelled) {
      state.operation = null;
    } else if (error.name !== 'AbortError') {
      alert(error.message);
      document.getElementById('progressText').textContent = `Execution failed: ${error.message}`;
      state.operation = null;
    }
  } finally {
    if (state.operation) state.operation.controller = null;
    buttons.forEach((button) => {
      button.disabled = false;
      button.classList.remove('is-loading');
    });
    updateOperationControls();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const planButton = document.getElementById('planButton');
  const dryRunButton = document.getElementById('dryRunButton');
  const startButton = document.getElementById('startButton');
  const browseButton = document.getElementById('browseButton');
  const summaryModal = document.getElementById('summaryModal');
  const historyModal = document.getElementById('historyModal');
  const aboutModal = document.getElementById('aboutModal');

  if (browseButton) {
    browseButton.addEventListener('click', () => browseFolder('sourceFolder'));
  }

  if (planButton) {
    planButton.addEventListener('click', createPlan);
  }
  if (dryRunButton) {
    dryRunButton.addEventListener('click', () => runExecute(true));
  }
  if (startButton) {
    startButton.addEventListener('click', () => runExecute(false));
  }
  document.getElementById('pauseOperationButton').addEventListener('click', pauseOperation);
  document.getElementById('resumeOperationButton').addEventListener('click', resumeOperation);
  document.getElementById('cancelOperationButton').addEventListener('click', cancelOperation);
  document.querySelectorAll('[data-summary-key]').forEach((metric) => {
    metric.addEventListener('click', () => showSummaryDetails(metric.dataset.summaryKey));
  });
  document.getElementById('summaryModalClose').addEventListener('click', closeSummaryDetails);
  summaryModal.addEventListener('click', (event) => {
    if (event.target === summaryModal) closeSummaryDetails();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeSummaryDetails();
  });
  document.querySelectorAll('[data-history-key]').forEach((item) => {
    item.addEventListener('click', async () => {
      await loadHistory();
      showHistory(item.dataset.historyKey);
    });
  });
  document.getElementById('historyModalClose').addEventListener('click', closeHistory);
  document.getElementById('clearHistoryButton').addEventListener('click', clearHistory);
  historyModal.addEventListener('click', (event) => {
    if (event.target === historyModal) closeHistory();
  });
  document.getElementById('aboutButton').addEventListener('click', () => {
    aboutModal.hidden = false;
  });
  document.getElementById('aboutModalClose').addEventListener('click', closeAbout);
  aboutModal.addEventListener('click', (event) => {
    if (event.target === aboutModal) closeAbout();
  });
  loadHistory();
});
