# net-cfg V1.18
1. Fix centos network script bugs for /etc/sysconfig/network-scripts/
   a. Correct GATEWAY script
   a. Correct DNS script
# net-cfg V1.17
Configure network configuration for Unix system

How to use:
python net-cfg.pypy -a
network.json required
e.g.,
{
    "network": [
        {
            "address": "192.168.10.88",
            "gateway": "192.168.10.1",
            "dns1": "8.8.8.8",
            "dns2": "8.8.4.4",
            "mac": "00:0c:29:ff:f6:45",
            "metric": "101",
            "mode": "static",
            "type": "ens"
        }
    ]
}


Centos version:
to set up a VLAN configuration, i.e., 
ens192 mac: 00:0c:29:07:f3:fa
/etc/sysconfig/network-scripts/ifcfg-ens192.1234
DEVICE=ens192.1234
BOOTPROTO=none
IPADDR=192.168.5.5
NETMASK=255.255.255.0
GATEWAY 192.168.5.1
USERCTL=no
ONBOOT=yes
VLAN=yes

The network.json required
{
  "network": [
    {
      "address": "192.168.5.5",
      "netmask": "255.255.255.0",
      "gateway": "192.168.5.1",
      "mac": "00:0c:29:07:f3:fa",
      "mode": "static",
      "type": "vlan",
      "vlan_id": "1234"
    }
  ]
}
