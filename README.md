# Network Security Lab

A small Docker-based network project that simulates a segmented enterprise network. It demonstrates, in practice, how to split a network into zones, control traffic between them with a firewall, and monitor what's happening — exactly the kind of work a network engineer or IT support professional deals with day to day.

A voluntary side project I built on my own, independent of my studies.

What the project does

Three zones are set up using Docker, functioning the same way VLANs do on a real switch:

vlan10_corp (172.20.10.0/24) — regular workstations and servers
vlan20_guest (172.20.20.0/24) — an isolated guest network
vlan99_mgmt (172.20.99.0/24) — network for administration and monitoring

A firewall container controls traffic between the zones using nftables. The rules are simple: the management zone can reach the other two zones, workstations can send logs to the monitoring server, but the guest network is completely isolated and cannot reach any of the other zones. Everything that gets blocked is also logged. See the actual rules in firewall/nftables.conf and a simple network map in docs/network-diagram.md.

The management zone hosts a monitoring server with two small Python tools I wrote myself:

port_scanner.py — checks which ports are actually open on a host or an entire network. Used to confirm that the isolation works, i.e. that the guest network genuinely cannot reach the workstations.
traffic_logger.py — listens to network traffic and logs what's happening (source, destination, and port), similar to a simple monitoring sensor.

The project also includes an example WireGuard setup (wireguard/), demonstrating how to configure secure remote access into the management zone.

How to run it

You need Docker and Docker Compose installed.

bash
docker compose up --build -d

Then test that the isolation actually works:

bash
docker compose exec monitor python3 port_scanner.py 172.20.10.0/24
docker compose exec guest-host nc -zv 172.20.10.10 22   # should fail, guest is isolated
docker compose exec corp-host nc -zv 172.20.10.20 80    # should succeed, same zone

Watch traffic and blocked attempts live:

bash
docker compose logs -f firewall
docker compose exec monitor python3 traffic_logger.py --count 50
Why I built this

I built this project because I wanted to showcase this side of me — my practical, curious interest in networking and security. It's been valuable to demonstrate this skill set in a way that's both an engaging hobby project and executed at a professional level, with real segmentation, firewall rules I can explain in detail, and monitoring tools I wrote myself.

Tools used

Docker and Docker Compose, nftables, Python 3 (scapy, socket), WireGuard.
