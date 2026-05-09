from vendor_lookup import load_oui_map, vendor_for_mac

OUI_PATH = r"assets\oui.txt"

def main() -> None:
    oui_map = load_oui_map(OUI_PATH)
    print("loaded prefixes:", len(oui_map))

    macs = [
        "f0:81:75:ca:3c:62",
        "18:c0:4d:75:4d:93",
        "86:f7:4b:0e:8a:13",
    ]

    for mac in macs:
        print(mac, "->", vendor_for_mac(oui_map, mac))

if __name__ == "__main__":
    main()
