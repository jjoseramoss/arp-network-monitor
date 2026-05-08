# ARP Device Dashboard

A small networks project that discovers devices on a local LAN using ARP scans and shows them in a live web dashboard.

## What it does (MVP)
- Repeatedly ARP-scans a target subnet (e.g. `192.168.1.0/24`)
- Tracks devices by MAC address (first seen / last seen)
- Marks a device offline after it misses 3 scans
- Displays a dashboard (table + recent join/leave events)

## Tech stack
- Python
- Scapy (ARP scanning)
- Flask (web server + API)
- Npcap (required on Windows for Scapy layer-2)

## Requirements
- Windows machine on the same network you want to scan
- Python 3.10+
- Npcap installed (Wireshark installer can add it)
- Run in an Administrator terminal (recommended)

## Running (later)
Steps will be added once the Flask dashboard is wired up.

## Networking notes
ARP (Address Resolution Protocol) maps IPv4 addresses to MAC addresses on a local network. This project uses ARP broadcast requests ("who-has") and listens for replies ("is-at") to discover active hosts.
