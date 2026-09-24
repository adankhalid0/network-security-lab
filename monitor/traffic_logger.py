#!/usr/bin/env python3
"""
traffic_logger.py — lightweight traffic logger for the network-security-lab.

Sniffs packets visible to the monitor host (attached to the mgmt VLAN)
and logs a one-line summary per connection attempt: timestamp, protocol,
source, destination and port. This plays the same role as a syslog
receiver or a very small IDS sensor watching for unexpected cross-zone
traffic that the firewall's nftables rules should already be blocking.

Requires NET_RAW/NET_ADMIN (granted to the "monitor" service in
docker-compose.yml). Run as root inside the container.

Usage:
    python3 traffic_logger.py                 # sniff indefinitely
    python3 traffic_logger.py --count 50       # stop after 50 packets
"""

import argparse
import datetime
import logging
import sys

try:
    from scapy.all import IP, TCP, UDP, sniff
except ImportError:  # pragma: no cover - scapy is declared in requirements.txt
    sys.exit("scapy is required: pip install -r requirements.txt")

LOG_PATH = "/var/log/monitor/traffic.log"


def setup_logging():
    handlers = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.append(logging.FileHandler(LOG_PATH))
    except OSError:
        pass
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", handlers=handlers)


def handle_packet(packet):
    if IP not in packet:
        return

    src, dst = packet[IP].src, packet[IP].dst

    if TCP in packet:
        proto, sport, dport = "TCP", packet[TCP].sport, packet[TCP].dport
    elif UDP in packet:
        proto, sport, dport = "UDP", packet[UDP].sport, packet[UDP].dport
    else:
        proto, sport, dport = packet[IP].proto, None, None

    logging.info("%s %s:%s -> %s:%s", proto, src, sport, dst, dport)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sniff and log traffic for the network-security-lab")
    parser.add_argument("--iface", default=None, help="Interface to sniff on (default: scapy auto-detect)")
    parser.add_argument("--count", type=int, default=0, help="Stop after N packets (0 = run forever)")
    args = parser.parse_args()

    setup_logging()
    logging.info("traffic_logger starting at %s", datetime.datetime.now().isoformat())

    sniff(iface=args.iface, prn=handle_packet, store=False, count=args.count)


if __name__ == "__main__":
    main()
