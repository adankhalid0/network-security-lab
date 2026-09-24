FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping nmap tcpdump && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY port_scanner.py traffic_logger.py ./
RUN mkdir -p /var/log/monitor

CMD ["tail", "-f", "/dev/null"]
