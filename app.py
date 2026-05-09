from __future__ import annotations

import threading
import time

from flask import Flask, jsonify, render_template

from scanner import arp_scan
from store import DeviceStore

app = Flask(__name__)

store = DeviceStore(offline_after_misses=3)
state_lock = threading.Lock()

CIDR = "192.168.1.0/24"
IFACE = "Ethernet"
SCAN_INTERVAL_SECONDS = 10


def scan_loop() -> None:
    while True:
        devices = arp_scan(CIDR, iface=IFACE)
        with state_lock:
            store.update(devices)
        time.sleep(SCAN_INTERVAL_SECONDS)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def api_state():
    with state_lock:
        return jsonify(store.snapshot())


if __name__ == "__main__":
    t = threading.Thread(target=scan_loop, daemon=True)
    t.start()
    app.run(host="127.0.0.1", port=5000, debug=True)
