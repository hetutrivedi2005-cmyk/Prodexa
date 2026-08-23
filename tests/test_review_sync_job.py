import pytest
from fastapi.testclient import TestClient
from server import app
from src.pipeline.job_manager import pipeline_job_manager
from src.review.review_service import review_service

client = TestClient(app)

def test_realtime_review_queue_job_sync():
    # 1. Create a CSV with 15 products: 8 clean, 7 needing review
    csv_lines = ["mpn,brand,manufacturer,product_name"]
    for i in range(1, 16):
        if i <= 8:
            csv_lines.append(f"MPN-TEST-{i:04d},DeWalt,Stanley Black & Decker,Industrial Angle Grinder #{i}")
        else:
            # Missing brand/manufacturer triggers low confidence & NEEDS_REVIEW
            csv_lines.append(f"MPN-TEST-{i:04d},,,Generic Industrial Tool #{i}")
    
    sample_csv = "\n".join(csv_lines).encode("utf-8")
    
    response = client.post(
        "/api/jobs",
        files={"file": ("sync_test.csv", sample_csv, "text/csv")}
    )
    assert response.status_code == 200
    job_data = response.json()
    job_id = job_data["job_id"]
    assert job_data["total_rows"] == 15

    # Force job completion
    job = pipeline_job_manager.get_job(job_id)
    pipeline_job_manager._run_job_pipeline(job_id)

    # Fetch final status of job
    status_resp = client.get(f"/api/jobs/{job_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    
    needs_review_cnt = status_data["needs_review_rows"]
    successful_cnt = status_data["successful_rows"]
    total_cnt = status_data["total_rows"]

    assert total_cnt == 15
    assert needs_review_cnt == 7
    assert successful_cnt == 8

    # 2. Fetch Review Queue for this exact job ID
    rev_resp = client.get(f"/api/review/queue?job_id={job_id}&status_filter=PENDING")
    assert rev_resp.status_code == 200
    pending_items = rev_resp.json()
    
    # 3. Assert Results Page needs_review_rows matches Review Queue pending count
    assert len(pending_items) == 7

    # 4. Accept 1 review item
    target_item = pending_items[0]
    accept_resp = client.post(
        f"/api/review/{target_item['review_id']}/accept",
        json={"reviewer_id": "Test Specialist", "reason": "Approved in test"}
    )
    assert accept_resp.status_code == 200

    # 5. Verify updated counts
    updated_status_resp = client.get(f"/api/jobs/{job_id}")
    updated_status = updated_status_resp.json()
    assert updated_status["needs_review_rows"] == 6
    assert updated_status["successful_rows"] == 9

    # Verify updated Review Queue
    updated_rev_resp = client.get(f"/api/review/queue?job_id={job_id}&status_filter=PENDING")
    assert len(updated_rev_resp.json()) == 6
