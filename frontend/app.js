const API_URL = "http://127.0.0.1:8000";
document.getElementById("apiUrl").textContent = API_URL;

const $ = (id) => document.getElementById(id);
const btn = $("btn");
const form = $("form");

async function getModelInfo() {
  try {
    const r = await fetch(`${API_URL}/model/info`);
    if (!r.ok) return;
    const j = await r.json();
    const b = $("modelBadge");
    b.textContent = j.model_loaded ? `Modell: ${j.model_name}` : "Ingen ML-modell laddad";
    b.classList.toggle("ok", !!j.model_loaded);
  } catch (_) {}
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const distance_km = Number($("distance").value);
  const duration_min = Number($("duration").value);
  const passenger_count = Number($("passengers").value);

  if (distance_km < 0 || duration_min < 0 || passenger_count < 1) {
    $("result").textContent = "Ogiltiga värden.";
    return;
  }

  btn.disabled = true; const old = btn.textContent; btn.textContent = "Beräknar…";
  $("result").textContent = "–";

  try {
    const r = await fetch(`${API_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ distance_km, duration_min, passenger_count }),
    });
    if (!r.ok) throw new Error("Kunde inte beräkna");

    const j = await r.json();
    const used = j.used_model ? "ML-modell" : "Baslinje";
    const name = j.model_name ? ` (${j.model_name})` : "";
    $("result").innerHTML = `Uppskattat pris: <strong>$${Number(j.predicted_fare).toFixed(2)}</strong> <span class="badge ok">${used}${name}</span>`;
  } catch (err) {
    $("result").textContent = "Något gick fel. Kontrollera att API:et körs.";
  } finally {
    btn.disabled = false; btn.textContent = old;
    getModelInfo(); // uppdatera badgen om modellen laddades/ändrades
  }
});

// Stats
$("btnStats").addEventListener("click", async () => {
  try {
    const r = await fetch(`${API_URL}/stats`);
    const j = await r.json();
    const el = $("stats");
    el.textContent = JSON.stringify(j, null, 2);
    el.classList.remove("hidden");
  } catch (_) {}
});

// Sample
$("btnSample").addEventListener("click", async () => {
  try {
    const n = Math.max(1, Math.min(50, Number($("nRows").value || 5)));
    const r = await fetch(`${API_URL}/data/sample?n=${n}`);
    const j = await r.json();
    const rows = j.rows || [];
    const wrap = $("sampleWrap");
    const thead = $("sampleTable").querySelector("thead");
    const tbody = $("sampleTable").querySelector("tbody");
    if (!rows.length) { wrap.classList.add("hidden"); return; }
    const cols = Object.keys(rows[0]);
    thead.innerHTML = `<tr>${cols.map(c=>`<th>${c}</th>`).join("")}</tr>`;
    tbody.innerHTML = rows.map(r=>`<tr>${cols.map(c=>`<td>${r[c]}</td>`).join("")}</tr>`).join("");
    wrap.classList.remove("hidden");
  } catch (_) {}
});

getModelInfo();
