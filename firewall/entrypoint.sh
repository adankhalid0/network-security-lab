#!/bin/sh
set -e

# Enable IP forwarding so this container can route between the three
# attached Docker networks, the same role a router/L3 switch plays
# between VLANs on real hardware.
sysctl -w net.ipv4.ip_forward=1

# Load the segmentation ruleset
nft -f /etc/nftables.conf

echo "Firewall ready. Current ruleset:"
nft list ruleset

# Keep the container running and tail the kernel log so DENY rules
# logged by nftables are visible with `docker logs firewall`.
tail -f /dev/null
