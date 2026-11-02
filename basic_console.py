"""A-level: export a parent span and two child spans to the console."""

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


def main() -> None:
    resource = Resource.create({"service.name": "a9-console-demo", "service.version": "1.0.0"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("checkout.request") as parent:
        parent.set_attribute("order.id", "A9-1001")
        trace_id = f"{parent.get_span_context().trace_id:032x}"
        parent_id = f"{parent.get_span_context().span_id:016x}"
        with tracer.start_as_current_span("inventory.reserve") as inventory:
            inventory.set_attribute("item.count", 2)
            inventory_id = f"{inventory.get_span_context().span_id:016x}"
        with tracer.start_as_current_span("payment.authorize") as payment:
            payment.set_attribute("payment.method", "demo-card")
            payment_id = f"{payment.get_span_context().span_id:016x}"
        print(
            "TRACE_SUMMARY "
            f"trace_id={trace_id} parent_span_id={parent_id} "
            f"child_span_ids={inventory_id},{payment_id}",
            flush=True,
        )

    provider.force_flush()
    provider.shutdown()


if __name__ == "__main__":
    main()

