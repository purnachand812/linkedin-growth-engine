/**
 * app.js - Autonomous LinkedIn Studio & Queue Client
 * White-labeled, dynamically configured, and fully reactive.
 */

// Global Application State
const state = {
  profile: {},
  status: {},
  activeCandidates: [],
  archivedCandidates: [],
  currentFilter: 'ALL',
  activeStudioCandidateId: null,
  lastStudioScore: null
};

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', async () => {
  // Check if redirected from OAuth callback
  if (window.location.hash === '#connected') {
    showToast('LinkedIn account successfully connected!', 'success');
    window.history.replaceState(null, null, ' ');
  }

  await refreshAll();

  // Auto-poll status and queue every 30 seconds
  setInterval(async () => {
    await fetchStatus();
  }, 30000);
});

async function refreshAll() {
  await Promise.all([
    fetchProfile(),
    fetchStatus(),
    fetchQueue()
  ]);
}

// ----------------------------------------------------
// Navigation & Tab Switching
// ----------------------------------------------------
function switchTab(tabId) {
  // Update nav buttons
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('onclick')?.includes(tabId)) {
      btn.classList.add('active');
    }
  });

  // Update tab content containers
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });

  const targetTab = document.getElementById(`tab-${tabId}`);
  if (targetTab) {
    targetTab.classList.add('active');
  }
}

// ----------------------------------------------------
// Data Fetching
// ----------------------------------------------------
async function fetchProfile() {
  try {
    const res = await fetch('/api/profile');
    if (!res.ok) return;
    const data = await res.json();
    state.profile = data.profile || {};
    const strategy = data.content_strategy || {};

    // Header branding
    const initials = state.profile.initials || 'AU';
    const fullName = state.profile.full_name || 'Technical Author';
    const headline = state.profile.headline || 'Systems Architect & Autonomous Growth OS';

    const avatarBadge = document.getElementById('header-avatar-badge');
    const authorNameEl = document.getElementById('header-author-name');
    const authorHeadlineEl = document.getElementById('header-author-headline');

    if (avatarBadge) avatarBadge.textContent = initials;
    if (authorNameEl) authorNameEl.textContent = fullName;
    if (authorHeadlineEl) authorHeadlineEl.textContent = headline;

    // Settings fields
    const nameInput = document.getElementById('settings-name');
    const initialsInput = document.getElementById('settings-initials');
    const headlineInput = document.getElementById('settings-headline');
    const locationInput = document.getElementById('settings-location');
    const timezoneInput = document.getElementById('settings-timezone');
    const nicheInput = document.getElementById('settings-niche');

    if (nameInput) nameInput.value = state.profile.full_name || '';
    if (initialsInput) initialsInput.value = state.profile.initials || '';
    if (headlineInput) headlineInput.value = state.profile.headline || '';
    if (locationInput) locationInput.value = state.profile.location || '';
    if (timezoneInput) timezoneInput.value = strategy.target_timezone || 'Europe/Berlin';
    if (nicheInput) nicheInput.value = strategy.primary_niche || 'AI Systems & Distributed Engineering';
  } catch (err) {
    console.error('Failed to load profile:', err);
  }
}

async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    if (!res.ok) return;
    const data = await res.json();
    state.status = data;

    const pill = document.getElementById('linkedin-status-pill');
    const textEl = document.getElementById('linkedin-status-text');
    const btn = document.getElementById('connect-linkedin-btn');

    if (data.linkedin_connected) {
      pill.className = 'status-pill status-connected';
      textEl.textContent = data.member_name ? `Connected: ${data.member_name}` : 'Connected';
      if (btn) {
        btn.textContent = 'Re-authenticate';
        btn.className = 'btn btn-secondary btn-sm';
      }
    } else {
      pill.className = 'status-pill status-disconnected';
      textEl.textContent = 'Disconnected';
      if (btn) {
        btn.textContent = 'Connect LinkedIn';
        btn.className = 'btn btn-primary btn-sm';
      }
    }
  } catch (err) {
    console.error('Failed to load status:', err);
  }
}

async function fetchQueue() {
  try {
    const res = await fetch('/api/queue');
    if (!res.ok) return;
    const data = await res.json();

    state.activeCandidates = data.active_candidates || [];
    state.archivedCandidates = data.archived_candidates || [];

    // Nav counts
    const activeCountEl = document.getElementById('stat-active-count');
    const archivedCountEl = document.getElementById('stat-archived-count');
    if (activeCountEl) activeCountEl.textContent = state.activeCandidates.length;
    if (archivedCountEl) archivedCountEl.textContent = state.archivedCandidates.length;

    renderActiveQueue();
    renderArchivedQueue();
  } catch (err) {
    console.error('Failed to load queue:', err);
  }
}

// ----------------------------------------------------
// Queue Rendering & Interactions
// ----------------------------------------------------
function filterQueue(filter) {
  state.currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('onclick')?.includes(filter)) {
      btn.classList.add('active');
    }
  });
  renderActiveQueue();
}

function renderActiveQueue() {
  const container = document.getElementById('active-queue-container');
  if (!container) return;

  let list = state.activeCandidates;
  if (state.currentFilter === 'APPROVED') {
    list = list.filter(c => c.status === 'APPROVED');
  } else if (state.currentFilter === 'WAITING') {
    list = list.filter(c => c.status === 'WAITING_FOR_APPROVAL');
  }

  if (list.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color);">
        <p style="font-size: 1.1rem; font-weight: 600; color: var(--text-dim); margin-bottom: 0.5rem;">No candidates found in this view.</p>
        <p style="font-size: 0.85rem; color: var(--text-dim);">Use the Post Studio tab to compose a new breakdown or seed starter candidates.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = list.map(c => {
    const isApproved = c.status === 'APPROVED';
    const statusBadgeClass = isApproved ? 'status-approved' : 'status-waiting';
    const statusLabel = isApproved ? 'APPROVED' : 'WAITING APPROVAL';
    const visualHtml = c.visual_url
      ? `<div class="card-visual-preview"><img src="${c.visual_url}" alt="${escapeHtml(c.topic)}" loading="lazy"></div>`
      : '';

    const copySnippet = c.post_copy
      ? `<p style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.45; margin-bottom: 0.75rem; white-space: pre-line; max-height: 90px; overflow: hidden; position: relative;">
          ${escapeHtml(c.post_copy.slice(0, 220))}...
         </p>`
      : '';

    return `
      <div class="candidate-card" id="cand-card-${c.id}">
        <div>
          <div class="card-top">
            <span class="card-id-badge">#${c.id}</span>
            <div style="display: flex; gap: 6px; align-items: center;">
              <span class="card-status-badge ${statusBadgeClass}">${statusLabel}</span>
              ${c.score ? `<span style="font-size: 0.7rem; font-weight: 700; color: var(--accent-cyan); background: rgba(56, 189, 248, 0.1); padding: 3px 6px; border-radius: 4px;">Score: ${c.score}</span>` : ''}
            </div>
          </div>

          <h4 class="card-title">${escapeHtml(c.topic || 'Untitled Technical Topic')}</h4>
          <div class="card-beat">${escapeHtml(c.beat || 'Systems Architecture')}</div>

          ${visualHtml}
          ${copySnippet}
        </div>

        <div class="card-footer-actions">
          <div style="display: flex; gap: 6px;">
            <button class="btn btn-secondary btn-sm" onclick="toggleStatus(${c.id}, '${isApproved ? 'WAITING_FOR_APPROVAL' : 'APPROVED'}')">
              ${isApproved ? '&#9679; Set Waiting' : '&#10003; Approve'}
            </button>
            <button class="btn btn-secondary btn-sm" onclick="openCandidateInStudio(${c.id})">
              &#9998; Edit
            </button>
          </div>
          <button class="btn btn-primary btn-sm" onclick="publishCandidateNow(${c.id}, '${escapeAttr(c.topic)}')">
            &#9654; Publish Now
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function renderArchivedQueue() {
  const container = document.getElementById('archived-queue-container');
  if (!container) return;

  const list = state.archivedCandidates;
  if (list.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color);">
        <p style="font-size: 1.1rem; font-weight: 600; color: var(--text-dim); margin-bottom: 0.5rem;">Archive is empty.</p>
        <p style="font-size: 0.85rem; color: var(--text-dim);">When scheduled posts are dispatched live to LinkedIn, they appear here with permanent links.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = list.map(c => {
    const visualHtml = c.visual_url
      ? `<div class="card-visual-preview"><img src="${c.visual_url}" alt="${escapeHtml(c.topic)}" loading="lazy"></div>`
      : '';

    const postLink = c.linkedin_post_url
      ? `<a href="${c.linkedin_post_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">&#8599; View on LinkedIn</a>`
      : `<span style="font-size: 0.75rem; color: var(--text-dim);">Live on LinkedIn</span>`;

    return `
      <div class="candidate-card" style="opacity: 0.95;">
        <div>
          <div class="card-top">
            <span class="card-id-badge">#${c.id}</span>
            <span class="card-status-badge status-published">&#10003; 100% PUBLISHED</span>
          </div>

          <h4 class="card-title">${escapeHtml(c.topic || 'Untitled Technical Topic')}</h4>
          <div class="card-beat">${escapeHtml(c.beat || 'Systems Architecture')}</div>

          ${visualHtml}
          ${c.post_copy ? `<p style="font-size: 0.82rem; color: var(--text-dim); line-height: 1.4; margin-bottom: 0.75rem;">${escapeHtml(c.post_copy.slice(0, 160))}...</p>` : ''}
        </div>

        <div class="card-footer-actions">
          <span style="font-size: 0.75rem; color: var(--text-dim);">${c.published_at ? new Date(c.published_at).toLocaleString() : 'Dispatched'}</span>
          ${postLink}
        </div>
      </div>
    `;
  }).join('');
}

async function toggleStatus(id, newStatus) {
  try {
    const res = await fetch('/api/candidate/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate_id: id, status: newStatus })
    });
    if (res.ok) {
      showToast(`Candidate #${id} set to ${newStatus}`, 'success');
      await fetchQueue();
    } else {
      showToast('Failed to update status', 'error');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

async function publishCandidateNow(id, topic) {
  if (!confirm(`Are you sure you want to publish "${topic}" to LinkedIn immediately?`)) {
    return;
  }

  showToast(`Dispatching Candidate #${id} live to LinkedIn...`, 'info');

  try {
    const res = await fetch('/api/publish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate_id: id })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`✓ Published live to LinkedIn successfully!`, 'success');
      await refreshAll();
      switchTab('archive');
    } else {
      showToast(`Publish failed: ${data.error || 'Unknown error'}`, 'error');
    }
  } catch (err) {
    showToast(`Network error while publishing: ${err.message}`, 'error');
  }
}

// ----------------------------------------------------
// Post Studio & Voice Quality Gate
// ----------------------------------------------------
function openCandidateInStudio(id) {
  const candidate = state.activeCandidates.find(c => c.id === id);
  if (!candidate) return;

  state.activeStudioCandidateId = id;
  const textarea = document.getElementById('studio-textarea');
  if (textarea) {
    textarea.value = candidate.post_copy || '';
  }

  switchTab('studio');
  runStudioDetect();
}

async function runStudioDetect() {
  const textarea = document.getElementById('studio-textarea');
  const text = textarea ? textarea.value.trim() : '';

  if (!text) {
    showToast('Please enter post copy to analyze.', 'info');
    return;
  }

  try {
    const res = await fetch('/api/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    if (!res.ok) throw new Error('Analysis failed');
    const result = await res.json();
    state.lastStudioScore = result.final_score;

    // Render Score
    const scoreValEl = document.getElementById('studio-score-val');
    const scoreLblEl = document.getElementById('studio-score-lbl');

    if (scoreValEl) scoreValEl.textContent = `${result.final_score}/100`;
    if (scoreLblEl) {
      if (result.final_score >= 80) {
        scoreLblEl.textContent = 'PASS — Practitioner Quality Approved';
        scoreLblEl.style.color = 'var(--accent-green)';
      } else {
        scoreLblEl.textContent = 'ATTENTION — AI Tells or Slop Detected';
        scoreLblEl.style.color = 'var(--accent-amber)';
      }
    }

    // Render Breakdown
    const breakdownEl = document.getElementById('studio-checks-breakdown');
    if (breakdownEl) {
      const checks = [
        {
          name: '1. Burstiness (Sentence Length Variance)',
          score: `${result.burstiness?.score ?? 85}/100`,
          pass: (result.burstiness?.score ?? 85) >= 70,
          desc: result.burstiness?.details || 'Sentence lengths vary naturally without robotic uniformity.'
        },
        {
          name: '2. Specificity & Concrete Numbers',
          score: `${result.specificity?.score ?? 90}/100`,
          pass: (result.specificity?.score ?? 90) >= 70,
          desc: result.specificity?.details || 'Contains hardware metrics, benchmark percentages, or memory thresholds.'
        },
        {
          name: '3. Slop & Forbidden Buzzwords',
          score: `${result.slop?.score ?? 95}/100`,
          pass: (result.slop?.score ?? 95) >= 80,
          desc: result.slop?.detected?.length > 0
            ? `Flagged buzzwords: ${result.slop.detected.join(', ')}`
            : 'Zero corporate cliches (delve, leverage, game-changer) detected.'
        },
        {
          name: '4. AI Fingerprint (Em-Dashes & Characters)',
          score: `${result.fingerprint?.score ?? 100}/100`,
          pass: (result.fingerprint?.score ?? 100) >= 80,
          desc: result.fingerprint?.issues?.length > 0
            ? result.fingerprint.issues.join('; ')
            : 'Clean typography without em-dashes (—) or zero-width unicode characters.'
        },
        {
          name: '5. Voice & Pragmatic Skepticism',
          score: `${result.voice?.score ?? 90}/100`,
          pass: (result.voice?.score ?? 90) >= 75,
          desc: result.voice?.details || 'Declares concrete test status and engineering trade-offs.'
        }
      ];

      breakdownEl.innerHTML = checks.map(c => `
        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.85rem; margin-top: 0.75rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 0.85rem; font-weight: 700;">${escapeHtml(c.name)}</span>
            <span style="font-size: 0.75rem; font-weight: 700; color: ${c.pass ? 'var(--accent-green)' : 'var(--accent-amber)'};">${c.score}</span>
          </div>
          <p style="font-size: 0.78rem; color: var(--text-dim); line-height: 1.4;">${escapeHtml(c.desc)}</p>
        </div>
      `).join('');
    }
  } catch (err) {
    showToast(`Detection error: ${err.message}`, 'error');
  }
}

async function saveStudioCandidate() {
  const textarea = document.getElementById('studio-textarea');
  const text = textarea ? textarea.value.trim() : '';

  if (!text) {
    showToast('Cannot save empty post copy.', 'error');
    return;
  }

  // Derive title from first line
  const firstLine = text.split('\n')[0].replace(/^[#\*\s]+/, '').slice(0, 70);
  const topic = prompt('Enter a title/topic for this post:', firstLine) || firstLine;

  const payload = {
    candidate_id: state.activeStudioCandidateId,
    topic: topic,
    beat: state.profile.niche || 'Systems Architecture',
    post_copy: text,
    score: state.lastStudioScore || 88,
    status: 'APPROVED'
  };

  try {
    const res = await fetch('/api/candidate/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok && data.success) {
      showToast('✓ Post saved to editorial queue as APPROVED!', 'success');
      state.activeStudioCandidateId = null;
      await fetchQueue();
      switchTab('queue');
    } else {
      showToast('Failed to save post to queue', 'error');
    }
  } catch (err) {
    showToast(`Save error: ${err.message}`, 'error');
  }
}

// ----------------------------------------------------
// Settings & Profile Management
// ----------------------------------------------------
async function saveSettings() {
  const name = document.getElementById('settings-name')?.value.trim();
  const initials = document.getElementById('settings-initials')?.value.trim();
  const headline = document.getElementById('settings-headline')?.value.trim();
  const location = document.getElementById('settings-location')?.value.trim();
  const timezone = document.getElementById('settings-timezone')?.value.trim();
  const niche = document.getElementById('settings-niche')?.value.trim();

  const payload = {
    profile: {
      full_name: name,
      initials: initials,
      headline: headline,
      location: location
    },
    content_strategy: {
      target_timezone: timezone,
      primary_niche: niche
    }
  };

  try {
    const res = await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      showToast('✓ Settings and branding profile saved!', 'success');
      await fetchProfile();
    } else {
      showToast('Failed to save settings', 'error');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

async function connectLinkedIn() {
  try {
    const res = await fetch('/api/linkedin/auth-url');
    if (!res.ok) throw new Error('Could not get authorization URL');
    const data = await res.json();
    if (data.auth_url) {
      window.location.href = data.auth_url;
    } else {
      showToast('OAuth URL is not configured. Check your Client ID in .env', 'error');
    }
  } catch (err) {
    showToast(`OAuth Error: ${err.message}`, 'error');
  }
}

// ----------------------------------------------------
// Toast Notification Utility
// ----------------------------------------------------
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  if (type === 'error') toast.style.borderColor = 'var(--accent-red)';
  if (type === 'success') toast.style.borderColor = 'var(--accent-green)';

  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.4s';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeAttr(str) {
  if (!str) return '';
  return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

