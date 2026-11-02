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


def normalized_id(value: str, byte_length: int) -> str:
    """Normalize an OTLP hex/base64 ID and reject missing or zero context."""
    if not isinstance(value, str) or not value:
        raise ValueError("Missing telemetry context ID")
    text = value.removeprefix("0x")
    if len(text) == byte_length * 2 and all(
        char in "0123456789abcdefABCDEF" for char in text
    ):
        raw = bytes.fromhex(text)
    else:
        raw = base64.b64decode(value, validate=True)
    if len(raw) != byte_length or not any(raw):
        raise ValueError(f"Expected a nonzero {byte_length}-byte context ID")
    return raw.hex()


def context_pair(record: dict) -> tuple[str, str]:
    return (
        normalized_id(record.get("traceId"), 16),
        normalized_id(record.get("spanId"), 8),
    )


def validate_correlation(spans: list[dict], logs: list[dict]) -> tuple[str, int]:
    """Require every log's trace/span pair to resolve to an exported span."""
    if not spans or not logs:
        raise AssertionError("Both exported spans and logs are required")
    span_pairs = {context_pair(span) for span in spans}
    log_pairs = [context_pair(log) for log in logs]
    unmatched = set(log_pairs) - span_pairs
    if unmatched:
        raise AssertionError(f"Unmatched log trace/span context: {sorted(unmatched)}")
    return sorted({pair[0] for pair in log_pairs})[0], len(log_pairs)


def main() -> None:
    root = Path(__file__).parent / "evidence"
    spans = records(root / "traces.json", "resourceSpans", "scopeSpans", "spans")
    logs = records(root / "logs.json", "resourceLogs", "scopeLogs", "logRecords")
    span_names = {span.get("name") for span in spans}
    expected_names = {"checkout.request", "inventory.reserve", "payment.authorize"}
    assert expected_names <= span_names, f"missing spans: {expected_names - span_names}"
    assert len(logs) >= 3, f"expected at least 3 logs, got {len(logs)}"

    shared, matched = validate_correlation(spans, logs)

    print("VERIFICATION PASSED")
    print(f"Spans: {len(spans)}; logs: {len(logs)}")
    print("Span names: " + ", ".join(sorted(expected_names)))
    print("Shared trace ID: " + shared)
    print(f"Trace/Span pairs matched: {matched}/{len(logs)} logs")
    print("Every log context resolves to an exported span in the same trace.")
    print("Trace and log pipelines both exported OTLP data to local files.")


if __name__ == "__main__":
    main()

