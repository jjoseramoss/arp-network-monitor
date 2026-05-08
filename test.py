from scapy.all import conf, get_working_ifaces

for iface in get_working_ifaces():
    print(iface.name, iface.description, iface.ip)

print("conf.iface =", conf.iface)