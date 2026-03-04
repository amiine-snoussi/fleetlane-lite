console.log("fleetlane-lite app.js loaded");

const logEl = document.getElementById("log");
const apiStatusEl = document.getElementById("apiStatus");
const vehiclesListEl = document.getElementById("vehiclesList");
const reservationsListEl = document.getElementById("reservationsList");

function log(msg) {
  const ts = new Date().toISOString();
  logEl.textContent = `[${ts}] ${msg}\n` + logEl.textContent;
}

async function api(path, opts = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    let detail = data?.detail ?? `${res.status} ${res.statusText}`;
    // FastAPI 422 returns detail as an array of objects
    if (Array.isArray(detail)) {
      detail = detail
        .map(d => `${(d.loc || []).join(".")}: ${d.msg}`)
        .join("\n");
    }
    throw new Error(detail);
  }
  return data;
}

function toISO(dtLocalValue) {
  if (!dtLocalValue) return null;
  return dtLocalValue.length === 16 ? dtLocalValue + ":00" : dtLocalValue;
}

async function refreshVehicles() {
  const list = await api("/vehicles");
  vehiclesListEl.innerHTML = "";
  for (const v of list) {
    const div = document.createElement("div");
    div.className = "item";
    div.innerHTML = `
      <div class="top">
        <div><strong>#${v.id}</strong> ${v.plate}</div>
        <div class="badge">${v.status}</div>
      </div>
      <div class="small">mileage=${v.mileage} | location=${v.location ?? "-"}</div>
    `;
    vehiclesListEl.appendChild(div);
  }
  log(`Loaded ${list.length} vehicles`);
}

async function refreshReservations() {
  const list = await api("/reservations");
  reservationsListEl.innerHTML = "";
  for (const r of list) {
    const div = document.createElement("div");
    div.className = "item";
    div.innerHTML = `
      <div class="top">
        <div><strong>#${r.id}</strong> cust=${r.customer_id} vehicle=${r.vehicle_id}</div>
        <div class="badge">${r.status}</div>
      </div>
      <div class="small">start=${r.start_at} | end=${r.end_at}</div>
      <div class="small">mileage_out=${r.mileage_out ?? "-"} | mileage_in=${r.mileage_in ?? "-"} | notes=${r.checkin_notes ?? "-"}</div>
      <div class="actions">
        <button data-action="sign">Sign</button>
        <button data-action="checkout">Checkout</button>
        <button data-action="checkin">Checkin</button>
      </div>
    `;

    div.querySelectorAll("button").forEach(btn => {
      btn.addEventListener("click", async () => {
        const action = btn.dataset.action;
        try {
          if (action === "sign") {
            const name = prompt("Signed by (name):");
            if (!name) return;
            await api(`/reservations/${r.id}/sign`, { method: "POST", body: JSON.stringify({ signed_by: name }) });
            log(`Signed agreement for reservation #${r.id}`);
          }
          if (action === "checkout") {
            const m = prompt("Mileage out:");
            if (!m) return;
            await api(`/reservations/${r.id}/checkout`, { method: "POST", body: JSON.stringify({ mileage_out: Number(m) }) });
            log(`Checked out reservation #${r.id}`);
          }
          if (action === "checkin") {
            const m = prompt("Mileage in:");
            if (!m) return;
            const notes = prompt("Notes (optional):") || null;
            await api(`/reservations/${r.id}/checkin`, { method: "POST", body: JSON.stringify({ mileage_in: Number(m), notes }) });
            log(`Checked in reservation #${r.id}`);
          }
          await refreshReservations();
          await refreshVehicles();
        } catch (e) {
          log(`ERROR (${action}): ${e.message}`);
          alert(e.message);
        }
      });
    });

    reservationsListEl.appendChild(div);
  }
  log(`Loaded ${list.length} reservations`);
}

async function init() {
  try {
    const h = await api("/health");
    apiStatusEl.textContent = `API: ${h.status}`;
  } catch (e) {
    apiStatusEl.textContent = "API: error";
    log(`API health failed: ${e.message}`);
  }

  document.getElementById("refreshVehicles").addEventListener("click", () => refreshVehicles().catch(e => alert(e.message)));
  document.getElementById("refreshReservations").addEventListener("click", () => refreshReservations().catch(e => alert(e.message)));

  document.getElementById("vehicleForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    try {
      const payload = {
        plate: fd.get("plate"),
        mileage: Number(fd.get("mileage") || 0),
        location: fd.get("location") || null,
      };
      const v = await api("/vehicles", { method: "POST", body: JSON.stringify(payload) });
      log(`Created vehicle #${v.id}`);
      ev.target.reset();
      await refreshVehicles();
    } catch (e) {
      log(`ERROR (create vehicle): ${e.message}`);
      alert(e.message);
    }
  });

  document.getElementById("customerForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    try {
      const payload = {
        name: fd.get("name"),
        contact: fd.get("contact") || null,
      };
      const c = await api("/customers", { method: "POST", body: JSON.stringify(payload) });
      log(`Created customer #${c.id}`);
      ev.target.reset();
    } catch (e) {
      log(`ERROR (create customer): ${e.message}`);
      alert(e.message);
    }
  });

  document.getElementById("reservationForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    try {
      const payload = {
        customer_id: Number(fd.get("customer_id")),
        vehicle_id: Number(fd.get("vehicle_id")),
        start_at: toISO(fd.get("start_at")),
        end_at: toISO(fd.get("end_at")),
      };
      const r = await api("/reservations", { method: "POST", body: JSON.stringify(payload) });
      log(`Created reservation #${r.id}`);
      await refreshReservations();
      await refreshVehicles();
    } catch (e) {
      log(`ERROR (create reservation): ${e.message}`);
      alert(e.message);
    }
  });

  await refreshVehicles();
  await refreshReservations();
}
const start = document.querySelector('input[name="start_at"]');
const end = document.querySelector('input[name="end_at"]');
if (start && end && !start.value && !end.value) {
  const now = new Date();
  now.setMinutes(now.getMinutes() + 5);
  const endDt = new Date(now);
  endDt.setHours(endDt.getHours() + 1);

  const fmt = (d) => d.toISOString().slice(0,16); // "YYYY-MM-DDTHH:MM"
  start.value = fmt(now);
  end.value = fmt(endDt);
}

init().catch(e => log(`INIT ERROR: ${e.message}`));
