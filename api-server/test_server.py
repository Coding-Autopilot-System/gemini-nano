from fastapi import HTTPException
from fastapi.testclient import TestClient

from server import app, resolve


def test_resolve_accepts_documented_aliases() -> None:
    assert resolve("nano") == "gemma3:1b"
    assert resolve("best") == "gemma3:12b"
    assert resolve("qwen") == "qwen3:8b"


def test_resolve_rejects_unknown_models() -> None:
    try:
        resolve("missing-model")
    except HTTPException as exc:
        assert exc.status_code == 404
        assert "Unknown model" in str(exc.detail)
    else:
        raise AssertionError("resolve() should reject unknown models")


def test_list_models_endpoint_exposes_catalog() -> None:
    client = TestClient(app)

    response = client.get("/v1/models")

    assert response.status_code == 200
    payload = response.json()
    ids = {model["id"] for model in payload["data"]}
    assert payload["object"] == "list"
    assert {"gemma3:12b", "qwen3:8b", "gemma3:1b", "phi3:mini"} <= ids
