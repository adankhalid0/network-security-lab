FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd iputils-ping curl iproute2 && \
    rm -rf /var/lib/apt/lists/*

# A minimal "host" that listens on a couple of ports so the monitor
# container has something real to discover and scan, similar to how
# a workstation or small server behaves on a real network.
#
# On start it adds a route to the other zones (172.20.0.0/16) through the
# firewall container, the same job a default gateway has on a real VLAN.
# The firewall address comes from the GATEWAY environment variable.
CMD sh -c "ip route add 172.20.0.0/16 via $GATEWAY; nc -lk -p 22 & nc -lk -p 80 & tail -f /dev/null"
