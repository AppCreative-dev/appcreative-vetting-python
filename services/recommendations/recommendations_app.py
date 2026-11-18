"""Recommendations service.

Asks an AI model which products a customer is likely to want next.
Runs on port 8002 and calls the AI model on port 8003.
"""
import logging

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from settings import LLM_API_KEY, LLM_MODEL, LLM_URL

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s recommendations %(levelname)s %(message)s"
)
log = logging.getLogger("recommendations")

app = FastAPI(title="Recommendations")

CATALOG = [
    {"product_id": "P-101", "name": "Wool Hiking Socks", "best_seller_rank": 1},
    {"product_id": "P-102", "name": "Trail Running Shoes", "best_seller_rank": None},
    {"product_id": "P-103", "name": "Insulated Water Bottle", "best_seller_rank": 2},
    {"product_id": "P-104", "name": "Headlamp", "best_seller_rank": 3},
    {"product_id": "P-105", "name": "Rain Shell Jacket", "best_seller_rank": 4},
    {"product_id": "P-106", "name": "Trekking Poles", "best_seller_rank": None},
    {"product_id": "P-107", "name": "Merino Base Layer", "best_seller_rank": None},
    {"product_id": "P-108", "name": "Snowboard Wax Kit", "best_seller_rank": None},
    {"product_id": "P-109", "name": "Ski Goggles", "best_seller_rank": None},
    {"product_id": "P-110", "name": "Daypack 20L", "best_seller_rank": None},
]


class Customer(BaseModel):
    id: str
    name: str
    email: str


class RecommendRequest(BaseModel):
    customer: Customer
    purchased: list[str]
    limit: int = 3


def build_prompt(customer: Customer, purchased: list[str], candidates: list[dict]) -> str:
    lines = [
        "You are a helpful shopping assistant.",
        f"Customer: {customer.name} <{customer.email}> (id {customer.id})",
        f"They just bought: {', '.join(purchased)}",
        "Score each product below from 0 to 1 for how likely they are to want it next,",
        "and give a one-sentence reason.",
        "Products:",
    ]
    lines += [f"- {p['product_id']} | {p['name']}" for p in candidates]
    return "\n".join(lines)


async def call_model(prompt: str) -> dict:
    """Send the prompt to the AI model and return its JSON reply."""
    # The model is slow sometimes, so we never time out on it.
    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.post(
            LLM_URL,
            json={"model": LLM_MODEL, "prompt": prompt},
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
        )
    resp.raise_for_status()
    return resp.json()


def rank(results: list[dict]) -> list[dict]:
    """Order the model's results from best to worst."""
    return sorted(results, key=lambda r: r["score"])


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/recommend")
async def recommend(req: RecommendRequest):
    candidates = [p for p in CATALOG if p["name"] not in req.purchased]
    log.info("Recommending for customer %s from %d products", req.customer.id, len(candidates))

    prompt = build_prompt(req.customer, req.purchased, candidates)
    model_reply = await call_model(prompt)
    ranked = rank(model_reply["results"])

    # TODO: finish this feature.
    # Return the top `req.limit` products. Each one needs its product_id,
    # its name (from CATALOG) and the model's reason.
    return {"recommendations": ranked}
