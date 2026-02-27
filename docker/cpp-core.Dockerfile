FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake libcurl4-openssl-dev ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY cpp-core /app
RUN cmake -S . -B build && cmake --build build -j

ENV INGEST_API_URL=http://python-api:8000/internal/events
CMD ["/app/build/event_processor"]
