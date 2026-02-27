# Event Monitoring & Alerting System

Production-grade backend/distributed systems portfolio project with a multithreaded C++ ingestion core and FastAPI analytics/control plane.

## Architecture

```text
+-------------------------------+
| 7+ Simulated Event Producers  |
+---------------+---------------+
                |
                v
+-------------------------------+
| C++ Core                      |
| - Bounded queue (backpressure)|
| - Thread pool workers         |
| - Validation, retry, DLQ      |
+---------------+---------------+
                | HTTP (internal)
                v
+-------------------------------+
| FastAPI Service               |
| - Event ingestion endpoint    |
| - Alert rule CRUD             |
| - Analytics APIs              |
| - Alert engine (window rules) |
+---------------+---------------+
                |
                v
+-------------------------------+
| PostgreSQL                    |
| events / alert_rules / alerts |
+-------------------------------+
```

## Repository Layout

```text
event-monitoring-system/
├── cpp-core/
├── python-api/
├── docker/
├── docker-compose.yml
├── .env.example
├── .github/workflows/ci.yml
└── README.md
```

## Concurrency Model (C++)

- **Producer-consumer pattern** with 7 concurrent simulated source threads.
- **Bounded `EventQueue`** uses condition variables for backpressure.
- **Custom `ThreadPool`** executes processing workers.
- **Graceful shutdown** via signal handling + queue close + worker joins.
- **Fault tolerance** with event validation, retries with backoff, and dead-letter queue.

## Alert Engine Logic

- Alert rules are persisted in `alert_rules`.
- During event ingest, matching enabled rules are evaluated.
- Time-window count query checks whether `threshold_count` is met for `window_seconds`.
- Triggered incidents are persisted in `alert_incidents`.

## API Surface

### Event APIs
- `GET /events` (pagination/filtering)
- `GET /events/{id}`
- `GET /events/source/{source_id}`

### Alert Configuration APIs
- `POST /alerts`
- `GET /alerts`
- `PUT /alerts/{id}`
- `DELETE /alerts/{id}`

### Analytics APIs
- `GET /analytics/summary`
- `GET /analytics/severity-distribution`
- `GET /analytics/time-series`

Swagger docs available at `/docs`.

## Setup

### Docker Compose (recommended)

```bash
docker compose up --build
```

Services:
- PostgreSQL on `localhost:5432`
- FastAPI on `localhost:8000`
- C++ core continuously producing + dispatching events

### Local Development

Python API:
```bash
cd python-api
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

C++ core:
```bash
cd cpp-core
cmake -S . -B build
cmake --build build -j
./build/event_processor
```

## Testing

Python:
```bash
cd python-api
pytest --cov=app
```

C++:
```bash
cd cpp-core
cmake -S . -B build
cmake --build build -j
ctest --test-dir build --output-on-failure
```

## Engineering Notes

- RAII and explicit ownership in C++ components.
- No hard-coded service URLs in code paths used for deployment (environment-driven).
- Layered Python architecture: API -> services -> models/db.
- CI workflow compiles C++, runs tests, and performs Python compile check.
