# net-cfg
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

