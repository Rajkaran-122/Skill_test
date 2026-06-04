# PROMPT: Generate a pytest suite for a FastAPI /events/ingest endpoint that accepts batches of events. Ensure it tests idempotency (same event_id should not be duplicated), invalid payloads (should return 422), and partial success. Use pytest fixtures and TestClient.
# CHANGES MADE: Adapted the schema to match the `VisitorEvent` model perfectly. Added a specific test for the 500-event batch limit logic introduced to strictly match the challenge constraints.

import pytest
from fastapi.testclient import TestClient
from src.main import app
import uuid
import datetime

client = TestClient(app)

def test_ingest_valid_batch():
    event_id = str(uuid.uuid4())
    payload = [{
        "event_id": event_id,
        "store_id": "ST100",
        "camera_id": "cam1",
        "visitor_id": "VIS123",
        "event_type": "ENTRY",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "is_staff": False
    }]
    response = client.post("/events/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["processed"] == 1
    assert response.json()["status"] == "success"

def test_ingest_batch_limit_exceeded():
    payload = []
    for _ in range(501):
        payload.append({
            "event_id": str(uuid.uuid4()),
            "store_id": "ST100",
            "camera_id": "cam1",
            "visitor_id": "VIS123",
            "event_type": "ENTRY",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        })
    response = client.post("/events/ingest", json=payload)
    assert response.status_code == 400
    assert "limit of 500" in response.json()["detail"]

def test_ingest_invalid_payload():
    payload = [{
        "event_id": "123",
        "store_id": "ST100"
        # Missing required fields like visitor_id, event_type, timestamp
    }]
    response = client.post("/events/ingest", json=payload)
    assert response.status_code == 422 # FastAPI validation error
