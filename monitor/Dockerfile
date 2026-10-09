FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping nmap tcpdump iproute2 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY port_scanner.py traffic_logger.py ./
RUN mkdir -p /var/log/monitor

# Route to the other zones through the firewall (address in $GATEWAY).
CMD ["sh", "-c", "ip route add 172.20.0.0/16 via $GATEWAY; exec tail -f /dev/null"]
