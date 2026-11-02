"""E/O-level: send correlated spans and log records over OTLP gRPC."""

from __future__ import annotations

import logging
import os

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def main() -> None:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
    resource = Resource.create(
        {
            "service.name": "a9-order-service",
            "service.version": "1.0.0",
            "deployment.environment": "assignment-lab",
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    )
    trace.set_tracer_provider(tracer_provider)
    tracer = trace.get_tracer(__name__)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint, insecure=True))
    )
    set_logger_provider(logger_provider)
    logger = logging.getLogger("a9.order")
    logger.setLevel(logging.INFO)
    logger.addHandler(LoggingHandler(level=logging.INFO, logger_provider=logger_provider))

    with tracer.start_as_current_span("checkout.request") as checkout:
        checkout.set_attribute("order.id", "A9-1001")
        trace_id = f"{checkout.get_span_context().trace_id:032x}"
        logger.info("checkout started for order A9-1001")
        with tracer.start_as_current_span("inventory.reserve") as reserve:
            reserve.set_attribute("item.count", 2)
            logger.info("reserved 2 items for order A9-1001")
        with tracer.start_as_current_span("payment.authorize") as payment:
            payment.set_attribute("payment.method", "demo-card")
            logger.info("payment authorized for order A9-1001")
        print(f"TRACE_SUMMARY trace_id={trace_id} service=a9-order-service", flush=True)

    assert tracer_provider.force_flush(timeout_millis=10000), "span export timed out"
    assert logger_provider.force_flush(timeout_millis=10000), "log export timed out"
    tracer_provider.shutdown()
    logger_provider.shutdown()


if __name__ == "__main__":
    main()

