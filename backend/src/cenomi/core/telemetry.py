"""OpenTelemetry setup (ARCH-R099)."""

from __future__ import annotations

import logging

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from cenomi.core.settings import Settings

logger = logging.getLogger(__name__)


def configure_telemetry(settings: Settings) -> None:
    if settings.otel_exporter == "none":
        return

    resource = Resource.create(
        {"service.name": "api", "deployment.environment": settings.cenomi_env}
    )
    provider = TracerProvider(resource=resource)

    if settings.otel_exporter == "console":
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    elif settings.otel_exporter == "otlp":
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        except ImportError as exc:
            logger.warning("OTLP exporter unavailable: %s", exc)
            return
        endpoint = settings.otel_exporter_otlp_endpoint or "http://localhost:4317"
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))

    trace.set_tracer_provider(provider)
