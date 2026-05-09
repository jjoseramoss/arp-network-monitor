from __future__ import annotations

import threading
import time

from flask import Flask, jsonify, render_template, Response, request

from scanner import arp_scan
from store import DeviceStore

from vendor_lookup import load_oui_map

import csv
import io
import json


app = Flask(__name__)

store = DeviceStore(offline_after_misses=3)
state_lock = threading.Lock()
config_lock = threading.Lock()

CIDR = "192.168.1.0/24"
IFACE = "Ethernet"
SCAN_INTERVAL_SECONDS = 10

config = {"cidr": CIDR, "iface": IFACE, "interval" : SCAN_INTERVAL_SECONDS}

OUI_MAP = load_oui_map("assets/oui.txt")


def scan_loop() -> None:
    while True:
        with config_lock:
            cidr = config["cidr"]
            iface = config["iface"]
            interval = config["interval"]
        devices = arp_scan(cidr, iface=iface)
        with state_lock:
            store.update(devices, OUI_MAP)
        time.sleep(interval)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def api_state():
    with state_lock:
        return jsonify(store.snapshot())

@app.get("/api/export.json")
def export_json():
    with state_lock:
        snap = store.snapshot()
    return Response(
        json.dumps(snap, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=arp_devices.json"},
    )
    
@app.get("/api/export.csv")
def export_csv():
    with state_lock:
        snap = store.snapshot()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["status", "ip", "mac", "vendor", "first_seen", "last_seen", "misses"])

    for d in snap["devices"]:
        writer.writerow([
            d.get("status", ""),
            d.get("ip", ""),
            d.get("mac", ""),
            d.get("vendor", ""),
            d.get("first_seen", ""),
            d.get("last_seen", ""),
            d.get("misses", ""),
        ])

    csv_text = output.getvalue()
    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=arp_devices.csv"},
    )

@app.get("/api/config")
def get_config():
    with config_lock:
        return jsonify(config)

@app.post("/api/config")
def update_config():
    data = request.get_json(silent=True) or {}

    cidr = str(data.get("cidr", "")).strip()
    iface = str(data.get("iface", "")).strip()
    interval = data.get("interval")

    if "/" not in cidr:
        return jsonify({"error": "cidr must look like 192.168.1.0/24"}), 400
    if not iface:
        return jsonify({"error": "iface is required (example: Ethernet)"}), 400
    try:
        interval_int = int(interval)
        if interval_int < 1:
            raise ValueError()
    except Exception:
        return jsonify({"error": "interval must be an integer >= 1"}), 400

    with config_lock:
        config["cidr"] = cidr
        config["iface"] = iface
        config["interval"] = interval_int

    return jsonify({"ok": True, "config": config})

if __name__ == "__main__":
    t = threading.Thread(target=scan_loop, daemon=True)
    t.start()
    app.run(host="127.0.0.1", port=5000, debug=True)
