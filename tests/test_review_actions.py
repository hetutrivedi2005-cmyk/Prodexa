import pytest
import os
from fastapi.testclient import TestClient

os.environ["VERCEL"] = "1"

from server import app

client = TestClient(app)

def test_accept_review_item():
    # Test accept with a product attribute key
    res = client.post(
        "/api/review/PROD-0002:mpn/accept",
        json={"reviewer_id": "Product Specialist", "reason": "Verified against master specs"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["action"] == "accepted"
    assert data["product_id"] == "PROD-0002"
    assert data["field"] == "mpn"
    assert "updated_at" in data

def test_edit_review_item():
    # Test edit with corrected value
    res = client.post(
        "/api/review/PROD-0002:mpn/edit",
        json={"reviewer_id": "Product Specialist", "edited_value": "AVM6EV-CORRECTED", "reason": "Corrected MPN"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["action"] == "edited"
    assert data["product_id"] == "PROD-0002"
    assert data["value"] == "AVM6EV-CORRECTED"

def test_reject_review_item():
    # Test reject
    res = client.post(
        "/api/review/PROD-0002:mpn/reject",
        json={"reviewer_id": "Product Specialist", "reason": "Invalid attribute extracted"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["action"] == "rejected"
    assert data["product_id"] == "PROD-0002"

def test_escalate_review_item():
    # Test escalate
    res = client.post(
        "/api/review/PROD-0002:mpn/escalate",
        json={"reviewer_id": "Product Specialist", "reason": "Needs higher engineering review"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["action"] == "escalated"

def test_edit_empty_value_validation():
    # Test edit with empty value gives controlled 400
    res = client.post(
        "/api/review/PROD-0002:mpn/edit",
        json={"reviewer_id": "Product Specialist", "edited_value": "   "}
    )
    assert res.status_code == 400
