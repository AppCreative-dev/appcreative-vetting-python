"""Orders service.

Returns an order together with product recommendations.
Runs on port 8001 and calls the recommendations service on port 8002.
"""
import logging

import httpx
from fastapi import FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

RECOMMENDATIONS_URL = "http://localhost:8002/recommend"

logging.basicConfig(level=logging.INFO, format="%(asctime)s orders %(levelname)s %(message)s")
log = logging.getLogger("orders")

# --- Telemetry ---------------------------------------------------------------
# Traces from this service are sent to the OpenTelemetry Collector on port 4318,
# which forwards them to Grafana.
provider = TracerProvider(resource=Resource.create({"service.name": "orders"}))
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
)
trace.set_tracer_provider(provider)

app = FastAPI(title="Orders")
FastAPIInstrumentor.instrument_app(app)

# --- Practice data -----------------------------------------------------------
CUSTOMERS = {
    "C-001": {"id": "C-001", "name": "Jordan Lee", "email": "jordan.lee@example.com"},
    "C-002": {"id": "C-002", "name": "Sam Rivera", "email": "sam.rivera@example.com"},
    "C-003": {"id": "C-003", "name": "Alex Chen", "email": "alex.chen@example.com"},
}

ORDERS = {
    "A1001": {"customer_id": "C-001", "items": ["Trail Running Shoes", "Wool Hiking Socks"]},
    "A1002": {"customer_id": "C-002", "items": ["Insulated Water Bottle"]},
    "A1003": {"customer_id": "C-003", "items": ["Snowboard", "Snowboard Bindings"]},
}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")

    customer = CUSTOMERS[order["customer_id"]]
    log.info("Order %s requested", order_id)

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(
            RECOMMENDATIONS_URL,
            json={"customer": customer, "purchased": order["items"], "limit": 3},
        )
    resp.raise_for_status()

    return {
        "order_id": order_id,
        "items": order["items"],
        "recommendations": resp.json()["recommendations"],
    }
