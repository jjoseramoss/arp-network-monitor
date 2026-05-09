function fmtTs(sec) {
  const d = new Date(sec * 1000);
  return d.toLocaleTimeString();
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
