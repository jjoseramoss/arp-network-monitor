function fmtTs(sec) {
  const d = new Date(sec * 1000);
  return d.toLocaleTimeString();
}

async function loadConfig() {
  const res = await fetch("/api/config");
  const cfg = await res.json();

  document.getElementById("cidrInput").value = cfg.cidr || "";
  document.getElementById("ifaceInput").value = cfg.iface || "";
  document.getElementById("intervalInput").value = cfg.interval ?? 10;
}

async function applyConfig(e) {
  e.preventDefault();
  const status = document.getElementById("configStatus");
  status.textContent = "Saving...";

  const body = {
    cidr: document.getElementById("cidrInput").value.trim(),
    iface: document.getElementById("ifaceInput").value.trim(),
    interval: Number(document.getElementById("intervalInput").value),
  };

  const res = await fetch("/api/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    status.textContent = data.error || "Failed to save config";
    return;
  }

  status.textContent = "Saved";
  await refresh();
}


async function refresh() {
  const res = await fetch("/api/state");
  const data = await res.json();

  const tbody = document.querySelector("#devices tbody");
  tbody.innerHTML = "";
  for (const d of data.devices) {
    const tr = document.createElement("tr");
    tr.className = d.status;

    tr.innerHTML = `
      <td>${d.status}</td>
      <td>${d.ip}</td>
      <td>${d.mac}</td>
      <td>${fmtTs(d.first_seen)}</td>
      <td>${fmtTs(d.last_seen)}</td>
      <td>${d.misses}</td>
      <td>${d.vendor}</td>
    `;
    tbody.appendChild(tr);
  }

  const events = document.querySelector("#events");
  events.innerHTML = "";
  for (const e of data.events.slice(0, 15)) {
    const li = document.createElement("li");
    li.textContent = `${fmtTs(e.ts)} - ${e.type.toUpperCase()} - ${e.mac} (${e.ip})`;
    events.appendChild(li);
  }
}

refresh();
setInterval(refresh, 2000);

document.getElementById("configForm").addEventListener("submit", applyConfig);
loadConfig();

