"""Print actual exported records compactly for human inspection in Actions."""

from pathlib import Path

from verify_evidence import context_pair, normalized_id, records


root = Path(__file__).parent / "evidence"
spans = records(root / "traces.json", "resourceSpans", "scopeSpans", "spans")
logs = records(root / "logs.json", "resourceLogs", "scopeLogs", "logRecords")
print("RAW FILE EXPORTS (from the mounted Collector output directory)")
for name in ("traces.json", "logs.json"):
    print(f"{name}: {(root / name).stat().st_size} bytes")
print("\nEXPORTED SPAN HIERARCHY")
for span in sorted(spans, key=lambda s: s["name"]):
    trace_id, span_id = context_pair(span)
    parent = span.get("parentSpanId")
    parent_id = normalized_id(parent, 8) if parent else "ROOT"
    print(f"{span['name']}\n  trace_id={trace_id}\n  span_id={span_id} parent_id={parent_id}")
print("\nEXPORTED LOG CONTEXT")
for log in logs:
    trace_id, span_id = context_pair(log)
    print(f"{log['body']['stringValue']}\n  trace_id={trace_id}\n  span_id={span_id}")
