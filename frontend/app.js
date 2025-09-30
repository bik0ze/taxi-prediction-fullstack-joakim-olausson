async function predict() {
  const distance = parseFloat(document.getElementById('distance').value);
  const duration = parseFloat(document.getElementById('duration').value);
  const passengers = parseInt(document.getElementById('passengers').value, 10);
  const out = document.getElementById('out');
  out.textContent = 'Beräknar...';

  try {
    const resp = await fetch('http://127.0.0.1:8000/predict', {
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
