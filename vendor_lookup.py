
def load_oui_map(path: str) -> dict[str, str]:
    oui_map: dict[str, str] = {}

    with open(path, 'r', encoding="utf-8", errors="ignore") as file:
        for line in file:
            if "(hex)" not in line: continue

            left, right = line.split("(hex)", 1)
            prefix = left.strip().replace("-", "").upper()
            vendor = right.strip()

            if len(prefix) == 6:
                if vendor and vendor != "":
                    oui_map[prefix] = vendor
                else:
                    oui_map[prefix] = ""

    return oui_map

def vendor_for_mac(oui_map: dict[str, str], mac: str) -> str:
    prefix = mac.upper().replace(":", "").replace("-", "")[:6]
    
    return oui_map.get(prefix, "unknown")