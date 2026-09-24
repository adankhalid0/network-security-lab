FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends nftables iproute2 iputils-ping && \
    rm -rf /var/lib/apt/lists/*

COPY nftables.conf /etc/nftables.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
