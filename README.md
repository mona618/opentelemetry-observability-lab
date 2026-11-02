# Assignment 9 — OpenTelemetry observability lab

Owner: 何采妮（B11309014） · GitHub: [mona618](https://github.com/mona618)

This lab demonstrates console traces (A), a Dockerized OTLP Collector (E), and
two Collector pipelines with correlated traces and logs (O). The Collector
receives OTLP/gRPC on port 4317, batches the data, and exports it to its debug
console and local JSON files.

## Data path

```text
Python app → OTLP/gRPC :4317 → Collector OTLP receiver
                                 ├─ traces → memory_limiter → batch → debug + traces.json
                                 └─ logs   → memory_limiter → batch → debug + logs.json
```

## Run locally

Python 3.10+ and Docker with Compose are required for the full pipeline.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python basic_console.py
docker compose up -d
docker compose ps
python otel_app.py
python verify_evidence.py
docker compose logs --tail=80 otel-collector
docker compose down
```

On Windows, activate the virtual environment or use `.venv\\Scripts\\python.exe`
for the Python commands. The `evidence/` directory is mounted at `/data` in
the Collector container; generated telemetry is excluded from Git.

## Automated evidence

The [Actions workflow](.github/workflows/otel-lab.yml) performs the same steps
on an Ubuntu runner with Docker Compose. It saves console output, Collector
logs, file exports, and a verification summary as the `otel-evidence` artifact.
The verifier checks that the three spans exist and that exported spans and logs
share a trace ID. A failed assertion fails the workflow.

This is a learning setup. The debug exporter and local JSON files make the
signals visible, but a production system would route them to a secured and
retained telemetry backend with explicit access, sampling, and data handling
policies.

