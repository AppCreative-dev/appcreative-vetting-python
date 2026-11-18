from fastapi.testclient import TestClient

import recommendations_app as rec

FAKE_MODEL_REPLY = {
    "model": "practice-model-1",
    "results": [
        {"product_id": "P-104", "score": 0.91, "reason": "Handy for early-morning trail runs."},
        {"product_id": "P-105", "score": 0.35, "reason": "Useful when the weather turns."},
        {"product_id": "P-106", "score": 0.77, "reason": "Takes strain off the knees on descents."},
        {"product_id": "P-107", "score": 0.12, "reason": "A warm layer for cold starts."},
        {"product_id": "P-110", "score": 0.64, "reason": "Carries water and snacks on longer runs."},
    ],
    "usage": {"input_tokens": 80, "output_tokens": 70},
}

REQUEST = {
    "customer": {"id": "C-001", "name": "Jordan Lee", "email": "jordan.lee@example.com"},
    "purchased": ["Trail Running Shoes", "Wool Hiking Socks"],
    "limit": 3,
}


def test_returns_top_three_products_with_names_and_reasons(monkeypatch):
    async def fake_call_model(prompt):
        return FAKE_MODEL_REPLY

    monkeypatch.setattr(rec, "call_model", fake_call_model)
    client = TestClient(rec.app)

    resp = client.post("/recommend", json=REQUEST)

    assert resp.status_code == 200
    recs = resp.json()["recommendations"]
    assert [r["product_id"] for r in recs] == ["P-104", "P-106", "P-110"]
    assert [r["name"] for r in recs] == ["Headlamp", "Trekking Poles", "Daypack 20L"]
    assert all(r["reason"] for r in recs)
