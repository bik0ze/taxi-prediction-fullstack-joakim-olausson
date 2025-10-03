// ====== Konfiguration ======
const API_URL = "http://127.0.0.1:8000"; // ändra vid behov
const CURRENCY = "kr";                    // visa belopp i kr (byt om du vill)

// ====== Hjälpare ======
const $ = (sel, p=document) => p.querySelector(sel);
const $$ = (sel, p=document) => [...p.querySelectorAll(sel)];
const fmtMoney = v => isFinite(v) ? `${Number(v).toFixed(2)} ${CURRENCY}` : "–";
const setText = (el, t) => { el.textContent = t; };
const toast = msg => {
  const t = $("#toast");
  t.textContent = msg; t.classList.add("toast--show");
  setTimeout(()=>t.classList.remove("toast--show"), 1800);
};

// Visa aktiv API-URL i UI
$("#apiUrlText").textContent = API_URL;

// Tema (mörk/ljus) – valfritt
$("#themeBtn").addEventListener("click", () => {
  document.documentElement.toggleAttribute("data-light"); // enkel toggle
});

// ====== API-anrop ======
async function apiGet(path){
  const res = await fetch(`${API_URL}${path}`);
  if(!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}
async function apiPost(path, body){
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(body)
  });
  if(!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

// ====== Init: hämta status & modell-info ======
async function init(){
  try{
    const health = await apiGet("/health");
    $("#apiStatus").classList.toggle("status--on", health?.status === "ok");
  }catch{ /* lämna röd */ }

  try{
    const info = await apiGet("/model/info");
    const name = info?.model_name || "Okänd modell";
    $("#modelBadge").textContent = `ML-modell: ${name}`;
  }catch{
    $("#modelBadge").textContent = "ML-modell: okänd";
  }

  // Återställ senaste värden
  const saved = JSON.parse(localStorage.getItem("predictForm") || "{}");
  if(saved.distance) $("#distance").value = saved.distance;
  if(saved.duration) $("#duration").value = saved.duration;
  if(saved.passengers) $("#passengers").value = saved.passengers;
}
init();

// ====== Predict-form ======
$("#demoBtn").addEventListener("click", () => {
  $("#distance").value = 5;
  $("#duration").value = 15;
  $("#passengers").value = 1;
});

$("#predictForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const distance = parseFloat($("#distance").value);
  const duration = parseFloat($("#duration").value);
  const passengers = parseInt($("#passengers").value, 10);

  if([distance, duration, passengers].some(v => !isFinite(v) || v < 0) || passengers < 1){
    toast("Kontrollera att alla fält är ifyllda korrekt.");
    return;
  }

  // spara inputs
  localStorage.setItem("predictForm", JSON.stringify({distance, duration, passengers}));

  const btn = $("#predictBtn");
  btn.disabled = true; btn.textContent = "Beräknar…";
  try{
    const data = await apiPost("/predict", {
      distance_km: distance,
      duration_min: duration,
      passenger_count: passengers
    });

    // Resultat
    const usedModel = data?.used_model === true;
    const modelName = data?.model_name || (usedModel ? "ML-modell" : "Baslinje");
    setText($("#price"), fmtMoney(data?.predicted_fare));
    setText($("#usedModel"), usedModel ? `ML-modell (${modelName})` : "Baslinje");
    toast("Pris uppdaterat!");
  }catch(err){
    console.error(err);
    toast("Kunde inte beräkna pris. Är API:t igång?");
  }finally{
    btn.disabled = false; btn.textContent = "Beräkna pris";
  }
});

// ====== Stats ======
$("#btnStats").addEventListener("click", async () => {
  const box = $("#statsBox");
  box.textContent = "Hämtar…";
  try{
    const s = await apiGet("/stats");
    box.textContent = JSON.stringify(s, null, 2);
    toast("Stats hämtade");
  }catch(err){
    box.textContent = "Kunde inte hämta stats.";
  }
});

// ====== Sample ======
$("#btnSample").addEventListener("click", async () => {
  const n = parseInt($("#sampleN").value || "5", 10);
  const tbody = $("#sampleTable tbody");
  tbody.innerHTML = `<tr><td colspan="4" class="muted">Hämtar…</td></tr>`;
  try{
    const s = await apiGet(`/data/sample?n=${Math.max(1, Math.min(50, n))}`);
    const rows = s?.rows || [];
    tbody.innerHTML = rows.map(r => `
      <tr>
        <td>${Number(r.distance_km).toFixed(2)}</td>
        <td>${Number(r.duration_min).toFixed(2)}</td>
        <td>${r.passenger_count}</td>
        <td>${Number(r.fare).toFixed(4)}</td>
      </tr>
    `).join("") || `<tr><td colspan="4" class="muted">Inga rader.</td></tr>`;
    toast("Exempelrader uppdaterade");
  }catch{
    tbody.innerHTML = `<tr><td colspan="4">Kunde inte hämta data.</td></tr>`;
  }
});
