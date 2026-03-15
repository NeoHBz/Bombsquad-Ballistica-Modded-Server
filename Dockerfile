FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        software-properties-common curl ca-certificates && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.13 python3.13-venv libpython3.13 git

WORKDIR /app

COPY dist block_banned_ips.py bombsquad_server config.json nbstreamreader.py .

EXPOSE 43210/udp

CMD ["./bombsquad_server"]
