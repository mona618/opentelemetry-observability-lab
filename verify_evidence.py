"""Verify that Collector file exports contain correlated traces and logs."""

from __future__ import annotations

import base64
import json
from pathlib import Path


def records(path: Path, group_key: str, scope_key: str, item_key: str) -> list[dict]:
    result: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        for group in data.get(group_key, []):
            for scope in group.get(scope_key, []):
                result.extend(scope.get(item_key, []))
    return result


def normalized_trace_id(value: str) -> str:
    """OTLP JSON uses base64 for bytes; some exporters emit hex instead."""
    if len(value) == 32 and all(char in "0123456789abcdefABCDEF" for char in value):
        return value.lower()
    return base64.b64decode(value).hex()


def main() -> None:
    root = Path(__file__).parent / "evidence"
    spans = records(root / "traces.json", "resourceSpans", "scopeSpans", "spans")
    logs = records(root / "logs.json", "resourceLogs", "scopeLogs", "logRecords")
    span_names = {span.get("name") for span in spans}
    expected_names = {"checkout.request", "inventory.reserve", "payment.authorize"}
    assert expected_names <= span_names, f"missing spans: {expected_names - span_names}"
    assert len(logs) >= 3, f"expected at least 3 logs, got {len(logs)}"

    span_ids = {normalized_trace_id(span["traceId"]) for span in spans if span.get("traceId")}
    log_ids = {normalized_trace_id(log["traceId"]) for log in logs if log.get("traceId")}
    shared = span_ids & log_ids
    assert shared, "No common trace ID in span and log exports"
    assert all(len(value) == 32 for value in shared)

    print("VERIFICATION PASSED")
    print(f"Spans: {len(spans)}; logs: {len(logs)}")
    print("Span names: " + ", ".join(sorted(expected_names)))
    print("Shared trace ID: " + sorted(shared)[0])
    print("Trace and log pipelines both exported OTLP data to local files.")


if __name__ == "__main__":
    main()

