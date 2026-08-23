import os
import sys
import json
import time
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from server import app
from src.pipeline.job_manager import pipeline_job_manager

client = TestClient(app)

def test_csv_upload_validation_invalid_extension():
    response = client.post(
        "/api/jobs",
        files={"file": ("test.txt", b"invalid file content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_csv_upload_validation_empty_file():
    response = client.post(
        "/api/jobs",
        files={"file": ("empty.csv", b"", "text/csv")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_csv_upload_supports_any_header_columns():
    sample_csv = "random_col1,random_col2\nval1,val2\n".encode("utf-8")
    response = client.post(
        "/api/jobs",
        files={"file": ("custom_columns.csv", sample_csv, "text/csv")}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_csv_upload_job_creation_and_pipeline():
    sample_csv = (
        "mpn,brand,manufacturer,product_name\n"
        "DCB518,Diablo,Freud Inc,Sanding Belt 1/2 in x 18 in\n"
        "AVM6EV,Malco,Malco Products,Snip Offset Left\n"
        "DW1234,DeWalt,Stanley Black & Decker,Drill Bit\n"
    ).encode("utf-8")

    response = client.post(
        "/api/jobs",
        files={"file": ("sample_products.csv", sample_csv, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "job_id" in data
    assert data["total_rows"] == 3

    job_id = data["job_id"]

    # Verify job status endpoint
    job_res = client.get(f"/api/jobs/{job_id}")
    assert job_res.status_code == 200
    job_data = job_res.json()
    assert job_data["job_id"] == job_id
    assert len(job_data["stages"]) == 11

def test_job_stream_endpoint():
    sample_csv = "mpn,brand\nMPN-STREAM-01,BrandA\n".encode("utf-8")
    create_res = client.post("/api/jobs", files={"file": ("stream_test.csv", sample_csv, "text/csv")})
    job_id = create_res.json()["job_id"]

    gen = pipeline_job_manager.event_stream(job_id)
    first_event = next(gen)
    assert "data:" in first_event
    assert "job" in first_event

def test_job_results_filtering_and_export():
    sample_csv = "mpn,brand\nMPN-01,BrandA\nMPN-02,BrandB\n".encode("utf-8")
    create_res = client.post("/api/jobs", files={"file": ("items.csv", sample_csv, "text/csv")})
    job_id = create_res.json()["job_id"]

    # Wait briefly for background execution
    time.sleep(1.5)

    # Test Results Filtering & Pagination
    res = client.get(f"/api/jobs/{job_id}/results?page=1&page_size=10&status_filter=ALL")
    assert res.status_code == 200
    res_data = res.json()
    assert "items" in res_data
    assert "total" in res_data

    # Test Export Download
    export_res = client.get(f"/api/jobs/{job_id}/export")
    assert export_res.status_code == 200
    assert "text/csv" in export_res.headers["content-type"]

def test_job_retry_endpoint():
    sample_csv = "mpn,brand\nMPN-RETRY-01,BrandA\n".encode("utf-8")
    create_res = client.post("/api/jobs", files={"file": ("retry_test.csv", sample_csv, "text/csv")})
    job_id = create_res.json()["job_id"]

    retry_res = client.post(f"/api/jobs/{job_id}/retry")
    assert retry_res.status_code == 200
    assert retry_res.json()["status"] == "success"
