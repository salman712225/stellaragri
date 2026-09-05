/**
 * Stellar Agri AI - Admin Dashboard Controller
 * MCP Connection, Voice Agents, Call Logs, Farmer Enquiries & Error Diagnostics
 */

document.addEventListener('DOMContentLoaded', async () => {
  // ── Auth Guard: Ensure Authenticated Session ──
  async function checkAuthSession() {
    try {
      const token = localStorage.getItem('stellar_admin_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const res = await fetch('/api/auth/me', { headers });
      if (!res.ok) {
        window.location.href = '/login';
        return false;
      }
      const data = await res.json();
      if (!data.authenticated) {
        window.location.href = '/login';
        return false;
      }
      return true;
    } catch (err) {
      window.location.href = '/login';
      return false;
    }
  }

  const isAuthed = await checkAuthSession();
  if (!isAuthed) return;

  // State
  let dashboardData = null;
  let callsData = [];
  let enquiriesData = [];
  let claimsData = [];
  let currentFilterStatus = 'all';
  let searchQuery = '';
  let enquiryFilterStatus = 'all';
  let enquirySearchQuery = '';
  let claimFilterStatus = 'all';
  let claimSearchQuery = '';
  let autoRefreshTimer = null;

  // DOM Elements
  const mcpBadge = document.getElementById('mcp-status-pill');
  const pingLatencyEl = document.getElementById('ping-latency');
  const walletInrEl = document.getElementById('wallet-inr');
  const walletCentsEl = document.getElementById('wallet-cents');
  const activeNumberEl = document.getElementById('active-phone-number');
  const totalCallsEl = document.getElementById('total-calls-count');
  const avgLatencyEl = document.getElementById('avg-llm-latency');
  const agentsContainer = document.getElementById('agents-grid');
  const callsTableBody = document.getElementById('calls-table-body');
  const enquiriesTableBody = document.getElementById('enquiries-table-body');
  const claimsTableBody = document.getElementById('claims-table-body');
  const dbStatusBadge = document.getElementById('db-status-badge');
  const terminalBody = document.getElementById('terminal-body');
  const toastContainer = document.getElementById('toast-container');
  const logoutBtn = document.getElementById('admin-logout-btn');
  
  // Drawer Elements
  const drawerOverlay = document.getElementById('transcript-drawer');
  const drawerCloseBtn = document.getElementById('drawer-close-btn');
  const drawerCallId = document.getElementById('drawer-call-id');
  const drawerSummary = document.getElementById('drawer-summary');
  const drawerEvaluation = document.getElementById('drawer-evaluation');
  const drawerAudioPlayer = document.getElementById('drawer-audio');
  const drawerAudioContainer = document.getElementById('drawer-audio-container');
  const drawerTranscriptThread = document.getElementById('drawer-transcript-thread');

  // Sign Out Handler
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        await fetch('/api/auth/logout', { method: 'POST' });
      } catch (e) {}
      localStorage.removeItem('stellar_admin_token');
      window.location.href = '/login';
    });
  }

  // Tab switching
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add('active');
    });
  });

  // Outbound Call Form
  const outboundForm = document.getElementById('outbound-call-form');
  if (outboundForm) {
    outboundForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const agentId = parseInt(document.getElementById('outbound-agent-select').value);
      const toNumber = document.getElementById('outbound-phone').value.trim();
      const farmerName = document.getElementById('outbound-farmer-name').value.trim() || 'Farmer';
      const crop = document.getElementById('outbound-crop').value.trim() || 'Rice';
      const language = document.getElementById('outbound-language')?.value || 'hi-IN';
      const alertMsg = document.getElementById('outbound-alert-msg').value.trim();

      if (!toNumber) {
        showToast('Please enter a valid destination phone number in E.164 format (+91...)', 'error');
        return;
      }

      showToast(`Initiating call to ${toNumber} in ${language}...`, 'info');
      try {
        const res = await fetch('/api/admin/calls/outbound', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agentId,
            toNumber,
            farmerName,
            crop,
            language,
            alertMessage: alertMsg || undefined
          })
        });
        const result = await res.json();
        if (result.success || result.id || (result.data && result.data.id)) {
          const callId = result.id || (result.data && result.data.id);
          showToast(`✅ Call #${callId} initiated successfully!`, 'success');
          setTimeout(fetchCalls, 2000);
        } else {
          showToast(`❌ Call failed: ${result.error || result.details || 'Unknown error'}`, 'error');
        }
      } catch (err) {
        showToast(`❌ Network Error: ${err.message}`, 'error');
      }
    });
  }

  // Provision Agent Button
  const provisionBtn = document.getElementById('provision-agent-btn');
  if (provisionBtn) {
    provisionBtn.addEventListener('click', async () => {
      provisionBtn.disabled = true;
      provisionBtn.innerText = 'Creating Agent...';
      try {
        const res = await fetch('/api/admin/provision-stellar-agent', { method: 'POST' });
        const data = await res.json();
        if (data.success || data.id || (data.data && data.data.id)) {
          showToast('✅ Stellar Agri Voice Advisor created & phone assigned!', 'success');
          await fetchDashboardStatus();
        } else {
          showToast(`❌ Failed: ${data.error || 'Check API key/permissions'}`, 'error');
        }
      } catch (err) {
        showToast(`❌ Error: ${err.message}`, 'error');
      } finally {
        provisionBtn.disabled = false;
        provisionBtn.innerText = '✨ Provision Stellar Agri Voice Advisor';
      }
    });
  }

  // Filter & Search (Calls)
  const statusFilter = document.getElementById('status-filter');
  if (statusFilter) {
    statusFilter.addEventListener('change', (e) => {
      currentFilterStatus = e.target.value;
      renderCallsTable();
    });
  }

  const searchInput = document.getElementById('call-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      renderCallsTable();
    });
  }

  // Filter & Search (Farmer Enquiries)
  const enquiryStatusFilterEl = document.getElementById('enquiry-status-filter');
  if (enquiryStatusFilterEl) {
    enquiryStatusFilterEl.addEventListener('change', (e) => {
      enquiryFilterStatus = e.target.value;
      fetchEnquiries();
    });
  }

  const enquirySearchInputEl = document.getElementById('enquiry-search-input');
  if (enquirySearchInputEl) {
    enquirySearchInputEl.addEventListener('input', (e) => {
      enquirySearchQuery = e.target.value.toLowerCase().trim();
      fetchEnquiries();
    });
  }

  // Drawer Controls
  if (drawerCloseBtn) {
    drawerCloseBtn.addEventListener('click', () => {
      drawerOverlay.classList.remove('open');
      if (drawerAudioPlayer) drawerAudioPlayer.pause();
    });
  }

  if (drawerOverlay) {
    drawerOverlay.addEventListener('click', (e) => {
      if (e.target === drawerOverlay) {
        drawerOverlay.classList.remove('open');
        if (drawerAudioPlayer) drawerAudioPlayer.pause();
      }
    });
  }

  // Refresh Button
  const refreshBtn = document.getElementById('refresh-all-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      fetchDashboardStatus();
      fetchCalls();
      fetchEnquiries();
      fetchDbStatus();
      fetchErrorsAndLogs();
      showToast('Dashboard data refreshed', 'info');
    });
  }

  // ── Fetch Operations ──

  async function fetchDashboardStatus() {
    try {
      const res = await fetch('/api/admin/status');
      const data = await res.json();
      dashboardData = data;
      renderStatusAndKPIs(data);
      renderAgents(data.agents?.list || []);
      populateAgentDropdown(data.agents?.list || []);
    } catch (err) {
      console.error('Status fetch failed:', err);
    }
  }

  async function fetchDbStatus() {
    try {
      const res = await fetch('/api/admin/database-status');
      const data = await res.json();
      if (dbStatusBadge) {
        if (data.type === 'mongodb_atlas' && data.connected) {
          dbStatusBadge.innerHTML = '🍃 MongoDB Atlas: Connected';
          dbStatusBadge.style.color = '#34d399';
          dbStatusBadge.style.borderColor = 'rgba(52, 211, 153, 0.4)';
          dbStatusBadge.style.background = 'rgba(16, 185, 129, 0.15)';
        } else {
          dbStatusBadge.innerHTML = '📁 Storage: Local JSON Mode';
          dbStatusBadge.style.color = '#fbbf24';
          dbStatusBadge.style.borderColor = 'rgba(251, 191, 36, 0.4)';
          dbStatusBadge.style.background = 'rgba(245, 158, 11, 0.12)';
        }
      }
    } catch (err) {
      console.error('DB status check failed:', err);
    }
  }

  async function fetchEnquiries() {
    try {
      let url = `/api/admin/enquiries?limit=100`;
      if (enquiryFilterStatus && enquiryFilterStatus !== 'all') {
        url += `&status=${encodeURIComponent(enquiryFilterStatus)}`;
      }
      if (enquirySearchQuery) {
        url += `&search=${encodeURIComponent(enquirySearchQuery)}`;
      }
      const res = await fetch(url);
      enquiriesData = await res.json();
      renderEnquiriesTable();
    } catch (err) {
      console.error('Enquiries fetch failed:', err);
    }
  }

  async function fetchClaims() {
    try {
      let url = `/api/admin/claims?limit=100`;
      if (claimFilterStatus && claimFilterStatus !== 'all') {
        url += `&status=${encodeURIComponent(claimFilterStatus)}`;
      }
      if (claimSearchQuery) {
        url += `&search=${encodeURIComponent(claimSearchQuery)}`;
      }
      const res = await fetch(url);
      claimsData = await res.json();
      renderClaimsTable();
    } catch (err) {
      console.error('Claims fetch failed:', err);
    }
  }

  let hazardsData = [];
  const hazardsContainer = document.getElementById('hazards-container');
  const scanHazardsBtn = document.getElementById('scan-hazards-btn');

  if (scanHazardsBtn) {
    scanHazardsBtn.addEventListener('click', () => {
      showToast('Scanning Open-Meteo & ISRO Bhuvan satellite radar...', 'info');
      fetchHazards();
    });
  }

  async function fetchHazards() {
    try {
      if (!hazardsContainer) return;
      const res = await fetch('/api/admin/hazards');
      const data = await res.json();
      hazardsData = data;
      renderHazards(data);
    } catch (err) {
      console.error('Hazards fetch failed:', err);
    }
  }

  function renderHazards(hazards) {
    if (!hazardsContainer) return;
    hazardsContainer.innerHTML = '';

    if (!Array.isArray(hazards) || hazards.length === 0) {
      hazardsContainer.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 20px;">
          No critical weather/disaster alerts active across monitored districts right now.
        </div>`;
      return;
    }

    hazards.forEach(hazard => {
      const isSevere = hazard.severity === 'Severe' || hazard.severity === 'Critical';
      const card = document.createElement('div');
      card.style.cssText = `
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid ${isSevere ? 'rgba(239, 68, 68, 0.35)' : 'rgba(245, 158, 11, 0.35)'};
        border-radius: 10px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      `;

      card.innerHTML = `
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <h4 style="font-size: 0.95rem; font-weight: 600; color: #fff; margin: 0;">
              📍 ${escapeHtml(hazard.district)}, ${escapeHtml(hazard.state)}
            </h4>
            <span class="status-badge" style="background: ${isSevere ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)'}; color: ${isSevere ? '#fca5a5' : '#fde68a'}; border-color: ${isSevere ? 'rgba(239,68,68,0.4)' : 'rgba(245,158,11,0.4)'};">
              ${escapeHtml(hazard.severity)} Alert
            </span>
          </div>

          <div style="font-size: 0.84rem; color: #93c5fd; font-weight: 500; margin-bottom: 6px;">
            ⚠️ ${escapeHtml(hazard.hazard_type)}
          </div>

          <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.4; margin-bottom: 10px;">
            ${escapeHtml(hazard.description)}
          </p>

          <div style="font-size: 0.76rem; color: var(--text-dim); background: rgba(0,0,0,0.25); padding: 8px 10px; border-radius: 6px; margin-bottom: 12px;">
            <div><strong>🛰️ Sensor/Telemetry:</strong> ${escapeHtml(hazard.satellite_sensor || 'Open-Meteo & Radar')}</div>
            <div><strong>👥 At-Risk Contacts:</strong> ${hazard.farmer_count || 0} Registered Farmers</div>
            <div><strong>📜 PMFBY Clause:</strong> ${escapeHtml(hazard.applicable_pmfby_clause || 'Localized Calamity')}</div>
          </div>
        </div>

        <button class="btn btn-primary trigger-campaign-btn" style="width: 100%; font-size: 0.82rem; padding: 8px; justify-content: center; background: ${isSevere ? '#dc2626' : 'var(--primary)'};">
          📞 Launch Mode B Proactive Outreach
        </button>
      `;

      card.querySelector('.trigger-campaign-btn').addEventListener('click', async () => {
        if (!confirm(`Launch proactive outbound voice advisory calls to farmers in ${hazard.district}?`)) return;
        showToast(`Dispatching proactive AI calls to farmers in ${hazard.district}...`, 'info');
        try {
          const res = await fetch('/api/admin/hazards/trigger-campaign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              district: hazard.district,
              custom_hazard_msg: hazard.outreach_script
            })
          });
          const resData = await res.json();
          if (res.ok && resData.success) {
            showToast(`✅ Proactive Campaign Launched! ${resData.total_initiated} calls placed.`, 'success');
            setTimeout(fetchCalls, 2000);
          } else {
            showToast(`❌ Campaign error: ${resData.detail || 'Failed'}`, 'error');
          }
        } catch (e) {
          showToast(`❌ Error: ${e.message}`, 'error');
        }
      });

      hazardsContainer.appendChild(card);
    });
  }

  async function fetchCalls() {
    try {
      const res = await fetch('/api/admin/calls');
      callsData = await res.json();
      renderCallsTable();
    } catch (err) {
      console.error('Calls fetch failed:', err);
    }
  }

  async function fetchErrorsAndLogs() {
    try {
      const res = await fetch('/api/admin/errors-and-logs');
      const data = await res.json();
      renderErrorsAndTerminal(data);
    } catch (err) {
      console.error('Errors fetch failed:', err);
    }
  }

  // ── Render Functions ──

  function renderStatusAndKPIs(data) {
    const mcp = data.mcp || {};
    const wallet = data.wallet || {};
    const telephony = data.telephony || {};
    const agents = data.agents || {};

    // MCP Pill
    if (mcpBadge) {
      const dot = mcpBadge.querySelector('.pulse-dot');
      const text = mcpBadge.querySelector('.status-lbl');
      if (mcp.connected) {
        dot.className = 'pulse-dot';
        text.innerText = `MCP Connected (${mcp.toolCount || 76} tools)`;
      } else {
        dot.className = 'pulse-dot offline';
        text.innerText = 'MCP Disconnected';
      }
    }

    if (pingLatencyEl) {
      pingLatencyEl.innerText = `${mcp.pingLatencyMs || 0} ms`;
    }

    // Wallet
    if (walletInrEl) {
      walletInrEl.innerText = `₹${(wallet.balanceInr || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
    }
    if (walletCentsEl) {
      walletCentsEl.innerText = `${(wallet.balanceCents || 0).toLocaleString('en-IN')} paise (approx ${(wallet.balanceInr / 5).toFixed(0)} mins)`;
    }

    // Phone Number
    if (activeNumberEl) {
      const primaryNumber = telephony.numbers?.[0];
      if (primaryNumber) {
        activeNumberEl.innerText = primaryNumber.number;
      } else {
        activeNumberEl.innerText = 'No number linked';
      }
    }

    // Total agents
    const activeAgentsCount = document.getElementById('active-agents-count');
    if (activeAgentsCount) {
      activeAgentsCount.innerText = `${agents.activeCount || 0} Active / ${agents.total || 0} Total`;
    }
  }

  function renderAgents(agentsList) {
    if (!agentsContainer) return;
    agentsContainer.innerHTML = '';

    if (!agentsList || agentsList.length === 0) {
      agentsContainer.innerHTML = `
        <div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-dim);">
          <p>No voice agents configured yet.</p>
        </div>`;
      return;
    }

    agentsList.forEach(agent => {
      const isActive = agent.status === 'active';
      const card = document.createElement('div');
      card.className = 'agent-card';

      // Format specs cleanly
      const formatModel = (val) => {
        if (!val) return 'Default';
        if (val.length > 22 && val.includes('-')) {
          return val.split('-')[0] + '...';
        }
        return val;
      };

      const asrText = `${agent.asrProvider || 'Sarvam'}${agent.asrModel ? ' (' + formatModel(agent.asrModel) + ')' : ''}`;
      const llmText = `${agent.llmProvider || 'Sarvam'}${agent.llmModel ? ' (' + formatModel(agent.llmModel) + ')' : ''}`;
      const ttsText = `${agent.ttsProvider || 'Sarvam'}${agent.ttsVoice ? ' (' + formatModel(agent.ttsVoice) + ')' : ''}`;
      const telText = `${agent.telephonyProvider || 'Vobiz'}`;

      card.innerHTML = `
        <div class="agent-card-header">
          <div class="agent-title">
            <h3 title="${escapeHtml(agent.name || '')}">${escapeHtml(agent.name || 'Unnamed Agent')}</h3>
            <span class="agent-id">ID: #${agent.id} • ${agent.language || 'en-IN'}</span>
          </div>
          <span class="status-tag ${agent.status}">${agent.status}</span>
        </div>

        <div class="agent-specs">
          <div class="spec-item" title="STT: ${escapeHtml(agent.asrProvider || '')} / ${escapeHtml(agent.asrModel || '')}">
            <div class="spec-label">STT / ASR</div>
            <span class="spec-val">${escapeHtml(asrText)}</span>
          </div>
          <div class="spec-item" title="LLM: ${escapeHtml(agent.llmProvider || '')} / ${escapeHtml(agent.llmModel || '')}">
            <div class="spec-label">LLM Brain</div>
            <span class="spec-val">${escapeHtml(llmText)}</span>
          </div>
          <div class="spec-item" title="TTS: ${escapeHtml(agent.ttsProvider || '')} / ${escapeHtml(agent.ttsVoice || '')}">
            <div class="spec-label">TTS Voice</div>
            <span class="spec-val">${escapeHtml(ttsText)}</span>
          </div>
          <div class="spec-item" title="Telephony: ${escapeHtml(telText)}">
            <div class="spec-label">Telephony</div>
            <span class="spec-val">${escapeHtml(telText)}</span>
          </div>
        </div>

        <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 14px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${escapeHtml(agent.greetingMessage || '')}">
          <strong>Greeting:</strong> "${escapeHtml(agent.greetingMessage || 'Hello, how can I help you today?')}"
        </div>

        <div class="agent-actions">
          <button class="btn ${isActive ? 'btn-outline' : 'btn-primary'} toggle-agent-btn" data-id="${agent.id}" style="width: 100%; font-size: 0.8rem;">
            ${isActive ? '⏸️ Deactivate (Set Draft)' : '▶️ Activate Agent'}
          </button>
        </div>
      `;

      card.querySelector('.toggle-agent-btn').addEventListener('click', async () => {
        try {
          showToast(`Toggling Agent #${agent.id}...`, 'info');
          const res = await fetch(`/api/admin/agents/${agent.id}/toggle`, { method: 'PATCH' });
          const resData = await res.json();
          showToast(`Agent status updated!`, 'success');
          await fetchDashboardStatus();
        } catch (e) {
          showToast(`Toggle failed: ${e.message}`, 'error');
        }
      });

      agentsContainer.appendChild(card);
    });
  }

  function populateAgentDropdown(agentsList) {
    const select = document.getElementById('outbound-agent-select');
    if (!select) return;
    select.innerHTML = '';
    agentsList.forEach(a => {
      const opt = document.createElement('option');
      opt.value = a.id;
      opt.textContent = `#${a.id} - ${a.name} (${a.status.toUpperCase()})`;
      select.appendChild(opt);
    });
  }

  function renderCallsTable() {
    if (!callsTableBody) return;
    callsTableBody.innerHTML = '';

    let filtered = callsData.filter(c => {
      if (currentFilterStatus !== 'all' && c.status !== currentFilterStatus) return false;
      if (searchQuery) {
        const str = `${c.toNumber} ${c.agentName} ${c.transcript || ''} ${c.callSummary || ''}`.toLowerCase();
        if (!str.includes(searchQuery)) return false;
      }
      return true;
    });

    if (totalCallsEl) {
      totalCallsEl.innerText = `${callsData.length} Calls`;
    }

    if (filtered.length === 0) {
      callsTableBody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; padding: 36px; color: var(--text-dim);">
            No calls matching current filters.
          </td>
        </tr>`;
      return;
    }

    filtered.forEach(call => {
      const row = document.createElement('tr');
      const dateStr = call.createdAt ? new Date(call.createdAt).toLocaleString('en-IN', {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      }) : 'N/A';

      const durationStr = call.durationSeconds ? `${call.durationSeconds}s` : '0s';
      const costInr = call.costCents ? `₹${(call.costCents / 100).toFixed(2)}` : '₹0.00';
      const hasAudio = Boolean(call.recordingUrl || call.audioUrl || call.recording_url || call.audio_url || call.recording);

      row.innerHTML = `
        <td style="font-weight: 600;">#${call.id}</td>
        <td>
          <div style="font-weight: 500;">${call.toNumber || 'Anonymous'}</div>
          <div style="font-size: 0.72rem; color: var(--text-dim);">${call.agentName || 'Agent'} (ID: ${call.agentId})</div>
        </td>
        <td><span class="status-tag ${call.status}">${call.status}</span></td>
        <td>${durationStr}</td>
        <td style="color: var(--accent-light); font-weight: 600;">${costInr}</td>
        <td style="font-size: 0.75rem; color: var(--text-muted);">${dateStr}</td>
        <td>
          <div style="display: flex; gap: 6px;">
            ${hasAudio ? `
            <button class="btn btn-primary play-audio-btn" style="padding: 4px 8px; font-size: 0.75rem;">
              ▶ Play
            </button>` : ''}
            <button class="btn btn-outline view-transcript-btn" style="padding: 4px 10px; font-size: 0.75rem;">
              🔍 Details
            </button>
          </div>
        </td>
      `;

      row.addEventListener('click', () => openCallDrawer(call));
      callsTableBody.appendChild(row);
    });
  }

  async function openCallDrawer(call) {
    if (!drawerOverlay) return;

    if (drawerCallId) drawerCallId.innerText = `Call #${call.id} (${call.toNumber || ''})`;
    if (drawerSummary) {
      drawerSummary.innerText = call.callSummary || 'Loading call details...';
    }
    if (drawerEvaluation) {
      drawerEvaluation.innerText = call.successEvaluation || 'Evaluation recorded.';
    }

    // Audio recording resolution
    let audioSrc = call.recordingUrl || call.audioUrl || call.recording_url || call.audio_url || call.stereoRecordingUrl || call.monoRecordingUrl || call.mediaUrl || (typeof call.recording === 'string' ? call.recording : call.recording?.url);
    if (!audioSrc && call.id) {
      audioSrc = `/api/admin/calls/${call.id}/audio`;
    }

    if (drawerAudioContainer && drawerAudioPlayer) {
      drawerAudioContainer.style.display = 'block';
      drawerAudioPlayer.src = audioSrc || '';
      drawerAudioPlayer.load();
    }

    // Render Transcript Thread
    renderTranscriptBubbles(call);

    drawerOverlay.classList.add('open');

    // Deep fetch specific call details to populate fresh signed audio recording if missing
    try {
      const res = await fetch(`/api/admin/calls/${call.id}`);
      if (res.ok) {
        const fullCall = await res.json();
        if (fullCall) {
          if (drawerSummary && fullCall.callSummary) drawerSummary.innerText = fullCall.callSummary;
          if (drawerEvaluation && fullCall.successEvaluation) drawerEvaluation.innerText = fullCall.successEvaluation;

          const freshAudio = fullCall.recordingUrl || fullCall.audioUrl || fullCall.recording_url || fullCall.audio_url || fullCall.stereoRecordingUrl || fullCall.monoRecordingUrl || fullCall.mediaUrl || (typeof fullCall.recording === 'string' ? fullCall.recording : fullCall.recording?.url);
          if (freshAudio && drawerAudioPlayer) {
            drawerAudioPlayer.src = freshAudio;
            drawerAudioPlayer.load();
          }

          if (fullCall.transcript) {
            renderTranscriptBubbles(fullCall);
          }
        }
      }
    } catch (e) {
      console.warn('Deep call fetch notice:', e);
    }
  }

  function renderTranscriptBubbles(call) {
    if (!drawerTranscriptThread) return;
    drawerTranscriptThread.innerHTML = '';
    if (call.transcript && call.transcript.trim()) {
      const lines = call.transcript.split('\n');
      lines.forEach(line => {
        if (!line.trim()) return;
        const bubble = document.createElement('div');
        const isAgent = line.toLowerCase().startsWith('agent:') || line.toLowerCase().startsWith('assistant:');
        bubble.className = `chat-bubble ${isAgent ? 'agent' : 'caller'}`;

        let author = isAgent ? (call.agentName || 'Voice Agent') : 'Farmer / Caller';
        let text = line.replace(/^(Agent:|Assistant:|Caller:|User:)/i, '').trim();

        bubble.innerHTML = `
          <div class="bubble-author">${author}</div>
          <div class="bubble-content">${escapeHtml(text)}</div>
        `;
        drawerTranscriptThread.appendChild(bubble);
      });
    } else {
      drawerTranscriptThread.innerHTML = `
        <div style="text-align: center; color: var(--text-dim); padding: 24px;">
          No conversation transcript recorded for this session.
        </div>`;
    }
  }

  function renderErrorsAndTerminal(data) {
    if (!terminalBody) return;
    terminalBody.innerHTML = '';

    const metrics = data.metrics || {};
    if (avgLatencyEl) {
      avgLatencyEl.innerText = `${metrics.avgLlmLatencyMs || 0} ms`;
    }

    const errors = data.recentErrors || [];
    if (errors.length === 0) {
      terminalBody.innerHTML = `
        <div class="log-entry ok">
          <div class="log-meta">[${new Date().toLocaleTimeString()}] SYSTEM DIAGNOSTICS: OK</div>
          <div>All SnapServe MCP channels, REST endpoints, and Webhooks are functioning normally with 0 reported runtime errors.</div>
        </div>
      `;
    } else {
      errors.forEach(err => {
        const item = document.createElement('div');
        item.className = 'log-entry err';
        item.innerHTML = `
          <div class="log-meta">[${new Date(err.timestamp).toLocaleTimeString()}] ${escapeHtml(err.category)} (Status: ${err.status_code || 500})</div>
          <div>${escapeHtml(err.message)}</div>
        `;
        terminalBody.appendChild(item);
      });
    }

    // Append latency telemetry
    const latencyItem = document.createElement('div');
    latencyItem.className = 'log-entry ok';
    latencyItem.innerHTML = `
      <div class="log-meta">[TELEMETRY] VOICE PIPELINE LATENCY BENCHMARKS</div>
      <div>⚡ STT Latency: <strong>${metrics.avgSttLatencyMs || 0}ms</strong> | ⚡ LLM 1st-Token: <strong>${metrics.avgLlmLatencyMs || 0}ms</strong> | ⚡ TTS Audio Chunk: <strong>${metrics.avgTtsFirstChunkMs || 0}ms</strong></div>
    `;
    terminalBody.appendChild(latencyItem);
  }

  function showToast(message, type = 'info') {
    if (!toastContainer) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';

    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // ── Farmer Enquiries Operations & Rendering ──

  function renderEnquiriesTable() {
    if (!enquiriesTableBody) return;
    enquiriesTableBody.innerHTML = '';

    if (!Array.isArray(enquiriesData) || enquiriesData.length === 0) {
      enquiriesTableBody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; color: var(--text-dim); padding: 32px;">
            No farmer enquiries found matching the criteria.
          </td>
        </tr>
      `;
      return;
    }

    enquiriesData.forEach(item => {
      const row = document.createElement('tr');
      const status = (item.status || 'pending').toLowerCase();
      let badgeClass = 'badge-pending';
      if (status === 'completed' || status === 'resolved') badgeClass = 'badge-success';
      if (status === 'failed') badgeClass = 'badge-failed';
      if (status === 'call_initiated') badgeClass = 'badge-ringing';

      const dateStr = item.created_at ? new Date(item.created_at).toLocaleString('en-IN') : '--';

      row.innerHTML = `
        <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--text-muted);">#${item.id}</td>
        <td>
          <div style="font-weight: 600; color: #fff;">${escapeHtml(item.farmer_name || 'Farmer')}</div>
          <div style="font-size: 0.78rem; color: var(--accent-light);">${escapeHtml(item.phone_number || '')}</div>
        </td>
        <td><span class="status-badge" style="background: rgba(16,185,129,0.15); color: #6ee7b7; border-color: rgba(16,185,129,0.3);">${escapeHtml(item.crop || 'General')}</span></td>
        <td style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(item.language || 'hi-IN')}</td>
        <td style="max-width: 260px; font-size: 0.82rem; color: var(--text-main); white-space: normal;">
          ${escapeHtml(item.issue || '')}
        </td>
        <td><span class="status-badge ${badgeClass}">${escapeHtml(item.status || 'Unknown')}</span></td>
        <td style="font-size: 0.78rem; color: var(--text-muted); white-space: nowrap;">${dateStr}</td>
        <td>
          <div style="display: flex; gap: 6px;">
            <button class="btn btn-sm btn-outline redial-enquiry-btn" title="Redial Call to Farmer">📞 Redial</button>
            <button class="btn btn-sm btn-outline resolve-enquiry-btn" title="Mark Resolved">✅</button>
            <button class="btn btn-sm btn-outline delete-enquiry-btn" style="color: #f87171; border-color: rgba(239, 68, 68, 0.3);" title="Delete Enquiry">🗑️</button>
          </div>
        </td>
      `;

      // Redial
      row.querySelector('.redial-enquiry-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        triggerRedial(item);
      });

      // Resolve
      row.querySelector('.resolve-enquiry-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        updateEnquiryStatus(item.id, 'resolved');
      });

      // Delete
      row.querySelector('.delete-enquiry-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        deleteEnquiry(item.id);
      });

      enquiriesTableBody.appendChild(row);
    });
  }

  async function updateEnquiryStatus(enquiryId, newStatus) {
    try {
      const res = await fetch(`/api/admin/enquiries/${enquiryId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(`✅ Enquiry marked as ${newStatus}`, 'success');
        fetchEnquiries();
      } else {
        showToast(`❌ Update failed: ${data.detail || 'Error'}`, 'error');
      }
    } catch (err) {
      showToast(`❌ Error: ${err.message}`, 'error');
    }
  }

  async function deleteEnquiry(enquiryId) {
    if (!confirm(`Are you sure you want to delete Enquiry #${enquiryId}?`)) return;
    try {
      const res = await fetch(`/api/admin/enquiries/${enquiryId}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (res.ok) {
        showToast(`✅ Enquiry #${enquiryId} deleted`, 'success');
        fetchEnquiries();
      } else {
        showToast(`❌ Delete failed: ${data.detail || 'Error'}`, 'error');
      }
    } catch (err) {
      showToast(`❌ Error: ${err.message}`, 'error');
    }
  }

  async function triggerRedial(item) {
    const agents = dashboardData?.agents?.list || [];
    const activeAgent = agents.find(a => a.status === 'active') || agents[0];
    const agentId = activeAgent?.id || 1028;

    showToast(`Initiating redial to ${item.farmer_name || 'Farmer'} (${item.phone_number})...`, 'info');
    try {
      const res = await fetch('/api/admin/calls/outbound', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId,
          toNumber: item.phone_number,
          farmerName: item.farmer_name || 'Farmer',
          crop: item.crop || 'Paddy',
          language: item.language || 'hi-IN',
          alertMessage: `Follow-up advisory regarding: ${item.issue || 'general agricultural query'}`
        })
      });
      const data = await res.json();
      if (data.success || data.id || (data.data && data.data.id)) {
        showToast(`✅ Redial placed successfully! Call ID: #${data.id || data.data?.id}`, 'success');
        setTimeout(() => {
          fetchCalls();
          fetchEnquiries();
        }, 2000);
      } else {
        showToast(`❌ Redial failed: ${data.error || data.details || 'Error'}`, 'error');
      }
    } catch (err) {
      showToast(`❌ Network error: ${err.message}`, 'error');
    }
  }

  // ── PMFBY Crop Insurance Claims Docket Operations & Rendering ──

  function renderClaimsTable() {
    if (!claimsTableBody) return;
    claimsTableBody.innerHTML = '';

    if (!Array.isArray(claimsData) || claimsData.length === 0) {
      claimsTableBody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; color: var(--text-dim); padding: 32px;">
            No insurance claims found in the docket.
          </td>
        </tr>
      `;
      return;
    }

    claimsData.forEach(claim => {
      const row = document.createElement('tr');
      const score = Math.round((claim.plausibility_score || 0.85) * 100);
      let plausibilityBadge = `<span class="status-badge badge-success" title="${escapeHtml(claim.notes || '')}">✅ ${score}% Plausible</span>`;
      if (claim.status === 'flagged_mismatch' || score < 50) {
        plausibilityBadge = `<span class="status-badge badge-failed" title="${escapeHtml(claim.notes || '')}">⚠️ ${score}% Anomaly Mismatch</span>`;
      } else if (score < 80) {
        plausibilityBadge = `<span class="status-badge badge-pending" title="${escapeHtml(claim.notes || '')}">🔍 ${score}% Verify Station</span>`;
      }

      const status = (claim.status || 'pending_surveyor_review').toLowerCase();
      let statusBadge = `<span class="status-badge badge-pending">Pending Survey</span>`;
      if (status === 'verified') statusBadge = `<span class="status-badge badge-success">Verified</span>`;
      if (status === 'flagged_mismatch') statusBadge = `<span class="status-badge badge-failed">Mismatch Flagged</span>`;
      if (status === 'escalated') statusBadge = `<span class="status-badge badge-ringing">Escalated to Human</span>`;

      const dateStr = claim.event_date || (claim.created_at ? new Date(claim.created_at).toLocaleDateString('en-IN') : '--');

      row.innerHTML = `
        <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">#${claim.id}</td>
        <td>
          <div style="font-weight: 600; color: #fff;">${escapeHtml(claim.farmer_name || 'Farmer')}</div>
          <div style="font-size: 0.78rem; color: var(--accent-light);">${escapeHtml(claim.phone_number || '')}</div>
        </td>
        <td>
          <div style="font-weight: 600; color: #34d399;">${escapeHtml(claim.crop || 'Crop')}</div>
          <div style="font-size: 0.75rem; color: var(--text-dim);">${escapeHtml(String(claim.affected_acres || '2.0'))} Acres</div>
        </td>
        <td style="font-size: 0.82rem; color: #fca5a5; font-weight: 500;">
          ${escapeHtml(claim.damage_type || 'Loss Event')}
        </td>
        <td>
          <div style="font-size: 0.8rem; color: var(--text-main);">${escapeHtml(claim.location || 'India')}</div>
          <div style="font-size: 0.75rem; color: var(--text-dim);">Event: ${dateStr}</div>
        </td>
        <td>${plausibilityBadge}</td>
        <td>${statusBadge}</td>
        <td>
          <div style="display: flex; gap: 6px;">
            <button class="btn btn-sm btn-outline verify-claim-btn" title="Verify & Pass to Surveyor">✅ Verify</button>
            <button class="btn btn-sm btn-outline escalate-claim-btn" style="color: #fbbf24; border-color: rgba(251, 191, 36, 0.4);" title="Escalate to Human Field Officer">🚨 Escalate</button>
          </div>
        </td>
      `;

      // Verify button
      row.querySelector('.verify-claim-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        updateClaimStatus(claim.id, 'verified', 'Verified with local Mandal agricultural telemetry.');
      });

      // Escalate button
      row.querySelector('.escalate-claim-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        updateClaimStatus(claim.id, 'escalated', 'Escalated for senior district officer manual review.');
      });

      claimsTableBody.appendChild(row);
    });
  }

  async function updateClaimStatus(claimId, newStatus, notes) {
    try {
      const res = await fetch(`/api/admin/claims/${claimId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus, notes: notes })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(`✅ Claim #${claimId} marked as ${newStatus}`, 'success');
        fetchClaims();
      } else {
        showToast(`❌ Update failed: ${data.detail || 'Error'}`, 'error');
      }
    } catch (err) {
      showToast(`❌ Error: ${err.message}`, 'error');
    }
  }

  // Hook Claims Search & Filter
  const claimsSearchInput = document.getElementById('claims-search-input');
  if (claimsSearchInput) {
    claimsSearchInput.addEventListener('input', (e) => {
      claimSearchQuery = e.target.value.trim().toLowerCase();
      fetchClaims();
    });
  }

  const claimsStatusFilter = document.getElementById('claims-status-filter');
  if (claimsStatusFilter) {
    claimsStatusFilter.addEventListener('change', (e) => {
      claimFilterStatus = e.target.value;
      fetchClaims();
    });
  }

  // Manual Claim Intake Button
  const addClaimBtn = document.getElementById('add-claim-manual-btn');
  if (addClaimBtn) {
    addClaimBtn.addEventListener('click', async () => {
      const farmerName = prompt('Enter Farmer Name:', 'Kishore Raman');
      if (!farmerName) return;
      const phone = prompt('Enter Farmer Phone:', '+919876543210');
      const crop = prompt('Enter Crop Name:', 'Paddy');
      const damage = prompt('Enter Nature of Damage (e.g., Cyclone / Flood / Drought / Hailstorm):', 'Cyclone Michaung Inundation');
      const acres = parseFloat(prompt('Enter Affected Acres:', '3.5')) || 3.5;
      const location = prompt('Enter Location (Village / District):', 'Cuddalore, Tamil Nadu');

      showToast('Logging claim and cross-validating meteorological plausibility...', 'info');
      try {
        const res = await fetch('/api/admin/claims', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            farmer_name: farmerName,
            phone_number: phone,
            crop: crop,
            damage_type: damage,
            affected_acres: acres,
            location: location,
            event_date: new Date().toISOString().split('T')[0]
          })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          showToast(`✅ Claim #${data.claim.id} logged! Plausibility: ${Math.round(data.claim.plausibility_score * 100)}%`, 'success');
          fetchClaims();
        } else {
          showToast(`❌ Claim submission error: ${data.detail || 'Failed'}`, 'error');
        }
      } catch (err) {
        showToast(`❌ Network error: ${err.message}`, 'error');
      }
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[m]);
  }

  // Initial Load
  fetchDashboardStatus();
  fetchCalls();
  fetchClaims();
  fetchHazards();
  fetchEnquiries();
  fetchDbStatus();
  fetchErrorsAndLogs();

  // Auto-refresh every 12 seconds
  autoRefreshTimer = setInterval(() => {
    fetchDashboardStatus();
    fetchCalls();
    fetchClaims();
    fetchHazards();
    fetchEnquiries();
    fetchDbStatus();
    fetchErrorsAndLogs();
  }, 12000);
});
