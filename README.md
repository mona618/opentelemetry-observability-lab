# Assignment 8 — OpenTelemetry observability lab

Owner: 何采妮（B11309014） · GitHub: [mona618](https://github.com/mona618)

This lab demonstrates console traces (A), a Dockerized OTLP Collector (E), and
two Collector pipelines with correlated traces and logs (O). The standard official
`otel/opentelemetry-collector:0.164.0` image is pinned for reproducibility. The Collector
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
python show_evidence.py
docker compose logs --tail=80 otel-collector
docker compose down
```

On Windows, activate the virtual environment or use `.venv\\Scripts\\python.exe`
for the Python commands. The `evidence/` directory is mounted at `/data` in
the Collector container; generated telemetry is excluded from Git. On Linux,
set `HOST_UID=$(id -u)` and `HOST_GID=$(id -g)` when starting Compose so the
Collector can write to this bind mount without running as root. The Actions
workflow sets those variables automatically.

## Automated evidence

The [Actions workflow](.github/workflows/otel-lab.yml) performs the same steps
on an Ubuntu runner with Docker Compose. It saves console output, Collector
logs, file exports, and a verification summary as the `otel-evidence` artifact.
The verifier checks that the three spans exist and that every log's
`(traceId, spanId)` pair resolves to an exported span in the same trace. Missing,
zero, unknown, or mismatched context fails the gate. Regression checks also
confirm that an unknown span and a span belonging to another trace are rejected.
The hierarchy gate also requires the two child spans to have the same trace ID
as checkout and a parent ID equal to checkout's span ID. Seven regression checks
exercise valid and deliberately invalid contexts. A failed assertion fails the workflow.

## Execution environment and report

The SDK console demo runs on local Windows Python as well as in CI.
The Dockerized Collector runs on a GitHub-hosted Ubuntu runner: Docker is not
installed on this Windows device. The bind-mounted output is local to that runner,
then preserved as an artifact. The repository supports both the earlier A9
and the revised A8 OpenTelemetry assignment. The A8 instructions themselves specify
the submission filename `A9_YourName_Opentelemetry.pdf`; the PDF retains that prefix.

The standard distribution includes the file exporter in its
[versioned manifest](https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.164.0/distributions/otelcol/manifest.yaml).

## Evidence map

- A: `A-level console spans` prints raw JSON and a trace summary.
- E: `Start Dockerized Collector`, `Send OTLP traces and logs`, and `Show Collector output`.
- O: `Inspect actual exported contexts` and `Verify both pipelines and correlation`.
- Gate reliability: `Test correlation and hierarchy guards`.

Local files contain demonstration order identifiers only, not production telemetry.

This is a learning setup. The debug exporter and local JSON files make the
signals visible, but a production system would route them to a secured and
retained telemetry backend with explicit access, sampling, and data handling
policies.
