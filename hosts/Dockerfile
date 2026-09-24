FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd iputils-ping curl && \
    rm -rf /var/lib/apt/lists/*

# A minimal "host" that listens on a couple of ports so the monitor
# container has something real to discover and scan, similar to how
# a workstation or small server behaves on a real network.
CMD sh -c "nc -lk -p 22 & nc -lk -p 80 & tail -f /dev/null"
