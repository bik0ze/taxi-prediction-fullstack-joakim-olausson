const API_BASE = "http://127.0.0.1:8000";

async function predict() {
  const distance = parseFloat(document.getElementById('distance').value);
  const duration = parseFloat(document.getElementById('duration').value);
  const passengers = parseInt(document.getElementById('passengers').value, 10);
  const out = document.getElementById('out');
  out.textContent = 'Beräknar...';

  try {
    const resp = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ distance_km: distance, duration_min: duration, passenger_count: passengers })
    });
    const data = await resp.json();
    if (resp.ok) {
      out.textContent = `Uppskattat pris: $${data.predicted_fare} ${data.used_model ? '(ML-modell)' : '(baseline)'}`;
    } else {
      out.textContent = 'Något gick fel: ' + JSON.stringify(data);
    }
  } catch (e) {
    out.textContent = 'Kunde inte kontakta API: ' + e;
  }
}

async function loadStats() {
  const box = document.getElementById('statsOut');
  box.textContent = 'Hämtar...';
  try {
    const resp = await fetch(`${API_BASE}/stats`);
    const data = await resp.json();
    box.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    box.textContent = 'Kunde inte hämta stats: ' + e;
  }
}

async function loadSample() {
  const box = document.getElementById('sampleOut');
  box.textContent = 'Hämtar...';
  try {
    const resp = await fetch(`${API_BASE}/data/sample?n=5`);
    const data = await resp.json();
    box.innerHTML = renderTable(data.rows || []);
  } catch (e) {
    box.textContent = 'Kunde inte hämta exempelrader: ' + e;
  }
}

function renderTable(rows) {
  if (!rows || rows.length === 0) return '—';
  const cols = Object.keys(rows[0]);
  const head = `<tr>${cols.map(c => `<th>${c}</th>`).join('')}</tr>`;
  const body = rows.map(r => `<tr>${cols.map(c => `<td>${r[c]}</td>`).join('')}</tr>`).join('');
  return `<table><thead>${head}</thead><tbody>${body}</tbody></table>`;
}
