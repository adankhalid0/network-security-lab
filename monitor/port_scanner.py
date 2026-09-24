#!/usr/bin/env python3
"""
port_scanner.py — simple TCP connect-scan for the network-security-lab.

Scans one or more hosts/subnets for a set of common ports and logs the
results with timestamps, similar in spirit to what a network engineer
would use to verify which services are actually reachable across a
segmented network (e.g. confirming the guest VLAN cannot reach a host
in the corp VLAN).

Usage:
    python3 port_scanner.py 172.20.10.0/24
    python3 port_scanner.py 172.20.10.10 172.20.20.10
    python3 port_scanner.py 172.20.10.0/24 --ports 22,80,443 --timeout 0.5
"""

import argparse
import datetime
import ipaddress
import logging
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_PORTS = [22, 23, 25, 53, 80, 110, 143, 443, 445, 3389, 8080]
LOG_PATH = "/var/log/monitor/scan.log"


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_PATH) if _log_dir_writable() else logging.NullHandler(),
        ],
    )


def _log_dir_writable() -> bool:
    try:
        with open(LOG_PATH, "a"):
            return True
    except OSError:
        return False


def expand_targets(targets: list[str]) -> list[str]:
    hosts: list[str] = []
    for target in targets:
        try:
            network = ipaddress.ip_network(target, strict=False)
            hosts.extend(str(ip) for ip in network.hosts())
        except ValueError:
            hosts.append(target)
    return hosts


def scan_port(host: str, port: int, timeout: float) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def scan_host(host: str, ports: list[int], timeout: float) -> list[int]:
    open_ports = []
    with ThreadPoolExecutor(max_workers=len(ports) or 1) as pool:
        futures = {pool.submit(scan_port, host, port, timeout): port for port in ports}
        for future in as_completed(futures):
            port = futures[future]
            try:
                if future.result():
                    open_ports.append(port)
            except OSError:
                pass
    return sorted(open_ports)


def main() -> None:
    parser = argparse.ArgumentParser(description="TCP connect-scan for the network-security-lab")
    parser.add_argument("targets", nargs="+", help="IP addresses and/or CIDR subnets to scan")
    parser.add_argument("--ports", default=",".join(map(str, DEFAULT_PORTS)),
                         help="Comma-separated list of ports (default: common services)")
    parser.add_argument("--timeout", type=float, default=0.75, help="Per-port timeout in seconds")
    args = parser.parse_args()

    setup_logging()
    ports = [int(p) for p in args.ports.split(",")]
    hosts = expand_targets(args.targets)

    logging.info("Starting scan of %d host(s) on %d port(s): %s", len(hosts), len(ports), ports)

    for host in hosts:
        open_ports = scan_host(host, ports, args.timeout)
        if open_ports:
            logging.info("%s -> OPEN ports: %s", host, open_ports)
        else:
            logging.info("%s -> no open ports found (host may be down or filtered)", host)

    logging.info("Scan complete at %s", datetime.datetime.now().isoformat())


if __name__ == "__main__":
    main()
