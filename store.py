from __future__ import annotations
from dataclasses import dataclass, asdict
import time
from typing import Dict, List
from scanner import Device
from vendor_lookup import vendor_for_mac

@dataclass
class TrackedDevice:
    mac: str
    ip: str
    first_seen: float
    last_seen: float
    misses: int
    status: str # "online" | "offline"
    vendor: str = ""

@dataclass
class Event:
    ts: float
    type: str # "joined" | "left" | "ip_changed"
    mac: str
    ip: str

class DeviceStore:
    def __init__(self, offline_after_misses: int = 3, max_events: int = 50) -> None:
        self.offline_after_misses = offline_after_misses
        self.max_events = max_events
        self.devices_by_mac: Dict[str, TrackedDevice] = {}
        self.events : List[Event] = []

    def _push_event(self, event: Event) -> None:
        self.events.append(event)
        
        # remove last event
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events :]
    
    def update(self, seen_devices: list[Device], vendors: dict[str, str]) -> None:
        now = time.time()
        seen_macs: set[str] = set()

        # TODO: iterate seen_devices (which will be your Device dataclass from scanner.py)
        # For each seen device:
        # - add to seen_macs
        # - if new mac: create TrackedDevice + push "joined"
        # - else: update ip if changed (optional event), last_seen, misses=0, status="online"
        for device in seen_devices:
            # New mac appears
            if device.mac not in self.devices_by_mac:
                #Find and add Vendor
                vendor = vendor_for_mac(vendors, device.mac)
                new_device = TrackedDevice(device.mac, device.ip, now, now, 0, "online", vendor)
                self.devices_by_mac[new_device.mac] = new_device
                self._push_event(Event(now, "joined", new_device.mac, new_device.ip))

            else:
                self.devices_by_mac[device.mac].ip = device.ip
                self.devices_by_mac[device.mac].last_seen = now
                self.devices_by_mac[device.mac].misses = 0
                self.devices_by_mac[device.mac].status = "online"

            seen_macs.add(device.mac)



        # TODO: for each tracked device not in seen_macs:
        # - if status is already offline, you can keep it offline (or keep counting misses, either is fine)
        # - else increment misses
        # - if misses reaches offline_after_misses: status="offline" + push "left"
        for device in self.devices_by_mac.values():
            # Device not in seen_macs so these werent "online"
            if device.mac not in seen_macs:
                device.misses += 1
                
                if device.misses >= self.offline_after_misses:
                    if device.status == "online":
                        self._push_event(Event(now, "left", device.mac, device.ip))
                        device.status = "offline"

                




    def snapshot(self) -> dict:
        devices = list(self.devices_by_mac.values())
        devices.sort(key=lambda d: (d.status != "online", -d.last_seen))
        
        return {
            "devices": [asdict(d) for d in devices],
            "events": [asdict(e) for e in reversed(self.events)]
        }