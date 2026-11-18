"""Practice AI model.

Stands in for a real AI provider so the exercise is free and gives the same
answers every time. Candidates should treat it as an outside service they
don't control. Runs on port 8003.
"""
import asyncio
import hashlib
import re

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

EXPECTED_API_KEY = "sk-practice-7f3a9c2e-DO-NOT-LEAK"

app = FastAPI(title="Practice AI model")


class GenerateRequest(BaseModel):
    model: str
    prompt: str


def _score(product_id: str, customer_line: str) -> float:
    digest = hashlib.sha256(f"{product_id}|{customer_line}".encode()).hexdigest()
    return round(int(digest[:8], 16) / 0xFFFFFFFF, 2)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/v1/generate")
async def generate(body: GenerateRequest, authorization: str | None = Header(default=None)):
    if authorization != f"Bearer {EXPECTED_API_KEY}":
        raise HTTPException(status_code=401, detail="invalid API key")

    prompt = body.prompt

    # Like real AI providers, this model has bad days for some requests.
    if "snowboard" in prompt.lower().split("products:")[0]:
        await asyncio.sleep(8)

    customer_match = re.search(r"^Customer: .*$", prompt, re.MULTILINE)
    customer_line = customer_match.group(0) if customer_match else ""
    bought_match = re.search(r"^They just bought: (.*)$", prompt, re.MULTILINE)
    first_bought = bought_match.group(1).split(",")[0].strip() if bought_match else "your order"

    products = re.findall(r"^- (P-\d+) \| (.+)$", prompt, re.MULTILINE)
    results = [
        {
            "product_id": pid,
            "score": _score(pid, customer_line),
            "reason": f"People who buy {first_bought} often pick up {name} too.",
        }
        for pid, name in products
    ]

    return {
        "model": body.model,
        "results": results,
        "usage": {
            "input_tokens": int(len(prompt.split()) * 1.3),
            "output_tokens": 14 * len(results),
        },
    }
