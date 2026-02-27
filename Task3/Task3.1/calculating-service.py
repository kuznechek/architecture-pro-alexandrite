import os
import logging
from fastapi import FastAPI, Response, Request
import asyncio
import random
from opentelemetry import trace, context, propagate
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import Status, StatusCode, NonRecordingSpan
from opentelemetry.propagate import extract, inject
from opentelemetry.context import attach, detach

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", 8080))
URL_COLLECTOR = os.getenv("URL_COLLECTOR")
SERVICE_NAME = "calculating-service"

resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: SERVICE_NAME
})

trace_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(trace_provider)

otlp_exporter = OTLPSpanExporter(endpoint=URL_COLLECTOR)
span_processor = BatchSpanProcessor(otlp_exporter)
trace_provider.add_span_processor(span_processor)

tracer = trace.get_tracer(SERVICE_NAME)

app = FastAPI()

async def calculating():
    with tracer.start_as_current_span(f"{SERVICE_NAME}: ") as span:
        
        sum = random.randint(1, 100_000)
        await asyncio.sleep(0.1)
        return f"calculated sum : {sum}"

@app.get("/")
async def root(request: Request):
    # Извлекаем контекст из заголовков входящего запроса
    extracted_ctx = extract(request.headers)

    # Используем извлечённый контекст
    with tracer.start_as_current_span(
        f"{SERVICE_NAME}:handler",
        context=extracted_ctx
    ) as span:
        try:
            calculating_content = await calculating()

            span.set_attribute("order.id", "Номер заказа")
            span.add_event("status_change", {"status": "CALCULATED"})

            return Response(content=calculating_content, media_type="text/plain")
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error(f"Error: {e}")
            return Response(status_code=500, content="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
