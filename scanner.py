from __future__ import annotations
from dataclasses import dataclass
import time
from scapy.all import Ether, srp, ARP

@dataclass(frozen=True)
class Device:
    ip: str
    mac: str

def arp_scan(cidr: str, iface: str) -> list[Device]:
    # Create packet and start ARP scanning
    dst = "ff:ff:ff:ff:ff:ff"
    packet = Ether(dst=dst)/ARP(pdst=cidr)
    ans, unans = srp(packet, timeout=3, retry=1, iface=iface, verbose=False)

    # Convert arp scan to list of devices
    devices: list[Device] = []
    for _sent, recieved in ans:
        devices.append(Device(ip=recieved.psrc, mac=recieved.hwsrc))
    return devices

if __name__ == "__main__":
    cidr = "192.168.1.0/24"
    
    # "Scan a few times" loop
    for i in range(5):
        devices = arp_scan(cidr, iface="Ethernet")
        print(f"\nscan {i + 1}: found {len(devices)}")
        for d in devices:
            print(d.ip, d.mac)
        time.sleep(2)

    print("Printing Devices:")
    for d in devices:
        print(d.ip, d.mac)
    print(f"found: {len(devices)}")