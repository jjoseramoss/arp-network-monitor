function fmtTs(sec) {
  const d = new Date(sec * 1000);
  return d.toLocaleTimeString();
}

function setConfigSummary(cfg) {
  const el = document.getElementById("configSummary");
  if (!el) return;
  el.textContent = `IP: ${cfg.cidr}     - - | - -     Interface: ${cfg.iface}  - - | - -        Interval: ${cfg.interval}s`;
}

function projectSphere(latDeg, lonDeg, rotDeg) {
  const lat = (latDeg * Math.PI) / 180;
  const lon = ((lonDeg + rotDeg) * Math.PI) / 180;
  const x = Math.cos(lat) * Math.sin(lon);
  const y = Math.sin(lat);
  const z = Math.cos(lat) * Math.cos(lon);
  return { x, y, z };
}

function drawGlobe() {
  const canvas = document.getElementById("globeCanvas");
  if (!canvas) return;

  const dpr = window.devicePixelRatio || 1;
  const cssW = canvas.clientWidth;
  const cssH = canvas.clientHeight;
  const w = Math.max(1, Math.floor(cssW * dpr));
  const h = Math.max(1, Math.floor(cssH * dpr));
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w;
    canvas.height = h;
  }

  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(dpr, dpr);

  const cx = cssW / 2;
  const cy = cssH / 2;
  const r = Math.min(cssW, cssH) * 0.38;

  const now = performance.now();
  const rot = (now * 0.012) % 360;

  ctx.clearRect(0, 0, cssW, cssH);

  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  const grad = ctx.createRadialGradient(cx - r * 0.35, cy - r * 0.25, r * 0.12, cx, cy, r * 1.05);
  grad.addColorStop(0, "rgba(52, 153, 169, 0.1)");
  grad.addColorStop(0.45, "rgba(15,23,42,0.55)");
  grad.addColorStop(1, "rgba(2,6,23,0.72)");
  ctx.fillStyle = grad;
  ctx.fill();
  ctx.lineWidth = 1;
  ctx.strokeStyle = "rgba(33, 246, 33, 0.22)";
  ctx.stroke();

  function drawGreatCircle(points, color) {
    ctx.beginPath();
    let started = false;
    for (const p of points) {
      if (p.z <= 0) {
        started = false;
        continue;
      }
      const x = cx + p.x * r;
      const y = cy - p.y * r;
      if (!started) {
        ctx.moveTo(x, y);
        started = true;
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  for (let lat = -60; lat <= 60; lat += 20) {
    const pts = [];
    for (let lon = -180; lon <= 180; lon += 3) {
      pts.push(projectSphere(lat, lon, rot));
    }
    drawGreatCircle(pts, "rgba(34, 255, 0, 0.18)");
  }

  for (let lon = -150; lon <= 150; lon += 30) {
    const pts = [];
    for (let lat = -90; lat <= 90; lat += 3) {
      pts.push(projectSphere(lat, lon, rot));
    }
    drawGreatCircle(pts, "rgba(255, 247, 247, 0.16)");
  }

  const links = [
    { a: [29.76, -95.37], b: [51.51, -0.12] },
    { a: [40.71, -74.0], b: [35.68, 139.69] },
    { a: [37.77, -122.42], b: [-33.86, 151.21] },
    { a: [19.43, -99.13], b: [48.85, 2.35] },
    { a: [1.35, 103.82], b: [52.52, 13.4] },
  ];

  function drawArc(lat1, lon1, lat2, lon2) {
    const steps = 110;
    let started = false;
    ctx.beginPath();
    for (let i = 0; i <= steps; i++) {
      const u = i / steps;
      const lat = lat1 + (lat2 - lat1) * u;
      const lon = lon1 + (lon2 - lon1) * u;
      const p = projectSphere(lat, lon, rot);
      if (p.z <= 0) {
        started = false;
        continue;
      }
      const x = cx + p.x * r;
      const y = cy - p.y * r;
      if (!started) {
        ctx.moveTo(x, y);
        started = true;
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
  }

  ctx.lineWidth = 2;
  ctx.strokeStyle = "rgba(56, 146, 255, 0.72)";
  for (const l of links) {
    drawArc(l.a[0], l.a[1], l.b[0], l.b[1]);
  }

  requestAnimationFrame(drawGlobe);
}

async function loadConfig() {
  const res = await fetch("/api/config");
  const cfg = await res.json();

  document.getElementById("cidrInput").value = cfg.cidr || "";
  document.getElementById("ifaceInput").value = cfg.iface || "";
  document.getElementById("intervalInput").value = cfg.interval ?? 10;
  setConfigSummary(cfg);
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
  if (data.config) setConfigSummary(data.config);
  await refresh();
}

async function refresh() {
  const res = await fetch("/api/state");
  const data = await res.json();

  const deviceCount = document.getElementById("deviceCount");
  if (deviceCount) deviceCount.textContent = `${data.devices.length} total`;

  const tbody = document.querySelector("#devices tbody");
  tbody.innerHTML = "";
  for (const d of data.devices) {
    const tr = document.createElement("tr");
    tr.className = d.status;

    tr.innerHTML = `
      <td>${d.status}</td>
      <td>${d.ip}</td>
      <td>${d.mac}</td>
      <td>${d.vendor}</td>
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

document.getElementById("configForm").addEventListener("submit", applyConfig);
loadConfig();
drawGlobe();
