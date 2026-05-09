from scanner import Device
from store import DeviceStore

store = DeviceStore(offline_after_misses=3)

A = Device(ip="192.168.1.10", mac="aa:aa:aa:aa:aa:aa")
B = Device(ip="192.168.1.11", mac="bb:bb:bb:bb:bb:bb")

scans = [
    [A, B],  # scan 1: both join
    [A, B],  # scan 2: both still online
    [A],     # scan 3: B missed 1
    [A],     # scan 4: B missed 2
    [A],     # scan 5: B missed 3 -> should become offline + "left"
]

for i, seen in enumerate(scans, start=1):
    store.update(seen)
    snap = store.snapshot()
    print("\nSCAN", i)
    for d in snap["devices"]:
        print(d["mac"], d["ip"], d["status"], "misses=", d["misses"])
    print("events:", [(e["type"], e["mac"]) for e in snap["events"]])
