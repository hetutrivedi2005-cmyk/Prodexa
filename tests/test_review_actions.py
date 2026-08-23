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

def test_queue_state_transitions_and_decrement():
    # 1. Fetch initial queue
    q_res = client.get("/api/review/queue")
    assert q_res.status_code == 200
    initial_items = q_res.json()
    initial_pending = [i for i in initial_items if i.get("review_status") == "PENDING"]
    initial_pending_cnt = len(initial_pending)

    if initial_pending_cnt > 0:
        first_pending = initial_pending[0]
        item_id = first_pending["review_id"]
        pid = first_pending["product_id"]
        attr = first_pending["attribute_name"]

        # Accept first pending item
        accept_res = client.post(
            f"/api/review/{item_id}/accept",
            json={"reviewer_id": "Product Specialist", "reason": "Verified specs"}
        )
        assert accept_res.status_code == 200

        # Refetch queue
        q_res2 = client.get("/api/review/queue")
        assert q_res2.status_code == 200
        after_items = q_res2.json()
        after_pending = [i for i in after_items if i.get("review_status") == "PENDING"]
        
        # Must have decremented by 1
        assert len(after_pending) == initial_pending_cnt - 1
        
        # The specific item must now have review_status == APPROVED
        matching = [i for i in after_items if i["review_id"] == item_id or (i["product_id"] == pid and i["attribute_name"] == attr)]
        assert len(matching) > 0
        assert matching[0]["review_status"] == "APPROVED"

