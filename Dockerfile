FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        software-properties-common curl ca-certificates && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.13 python3.13-venv libpython3.13 git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# 1. Clean up dummymodules permanently
RUN rm -rf dist/dummymodules

# 2. Install mod dependencies (pure-Python or aarch64 wheels)
RUN python3.13 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir \
      aiohttp discord.py flask requests cryptography pywebpush pyyaml \
      waitress ecdsa

ENV PATH="/opt/venv/bin:${PATH}"

# 3. Fix permissions
RUN chmod +x bombsquad_server && \
    chmod +x dist/bombsquad_headless dist/bombsquad_headless_aarch64

EXPOSE 43210/udp

# 4. Launch using the server manager (shebang uses python3.13).
CMD ["python3.13", "./bombsquad_server"]
