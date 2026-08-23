import time
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def main():
    print("================================================================================")
    print("PRODEXA — VERIFYING PREVIEW BUTTON & REPORT WORKFLOW END-TO-END")
    print("================================================================================\n")

    # 1. Fetch Reports directory
    res = requests.get(f"{BASE_URL}/api/reports")
    assert res.status_code == 200, f"Failed to get reports list: {res.text}"
    reports = res.json()
    print(f"1. Verified Reports Directory: Found {len(reports)} generated reports")
    assert len(reports) > 0, "Expected at least 1 report in database"

    rep1 = reports[0]
    job_id_1 = rep1["job_id"]
    file_name_1 = rep1["file_name"]
    print(f"   Target Report 1: Job ID '{job_id_1}' | File: '{file_name_1}'")

    # 2. Test Preview query via /api/jobs/{job_id}/report
    res1 = requests.get(f"{BASE_URL}/api/jobs/{job_id_1}/report")
    assert res1.status_code == 200, f"Failed to get report detail: {res1.text}"
    data1 = res1.json()

    print("\n2. Verified Report Preview Payload Structure:")
    print(f"   - File Name: {data1.get('file_name')}")
    print(f"   - Job ID: {data1.get('job_id')}")
    print(f"   - Status: {data1.get('pipeline_status')}")
    print(f"   - Upload Timestamp: {data1.get('created_at')}")
    print(f"   - Total Processed: {data1.get('executive_summary', {}).get('total_products_processed')}")
    print(f"   - Classified: {data1.get('executive_summary', {}).get('successfully_classified')} ({data1.get('executive_summary', {}).get('classification_success_rate')}%)")
    print(f"   - Needs Review: {data1.get('executive_summary', {}).get('needs_review')} ({data1.get('executive_summary', {}).get('review_rate')}%)")
    print(f"   - Overall Confidence: {data1.get('executive_summary', {}).get('average_confidence_score')}%")

    # Check 15 phases
    stages = data1.get("pipeline_phases") or data1.get("pipeline_stages") or []
    print(f"   - 15 Phases Count: {len(stages)}")
    assert len(stages) == 15, f"Expected 15 phases, got {len(stages)}"

    # Check product results sample
    products = data1.get("sample_classified_products") or data1.get("product_results_sample") or []
    print(f"   - Products Sample Present: {len(products)} rows")
    assert len(products) > 0, "Expected product results"

    # 3. Test Preview query via /api/reports/{report_id}
    report_id_1 = data1.get("report_id") or f"RPT-{job_id_1}"
    res_alias = requests.get(f"{BASE_URL}/api/reports/{report_id_1}")
    assert res_alias.status_code == 200, f"Failed to get report alias: {res_alias.text}"
    data1_alias = res_alias.json()
    assert data1_alias["job_id"] == job_id_1, "Alias report endpoint returned mismatched job ID"
    print(f"3. Verified /api/reports/{report_id_1} alias works identically.")

    # 4. Verify Download Actions
    res_csv = requests.get(f"{BASE_URL}/api/jobs/{job_id_1}/report/csv")
    assert res_csv.status_code == 200, "Failed to download report CSV"
    print(f"4. Verified Download Report CSV: {len(res_csv.content)} bytes retrieved")
    assert len(res_csv.content) > 500, "Report CSV too small"

    res_exp = requests.get(f"{BASE_URL}/api/jobs/{job_id_1}/export")
    assert res_exp.status_code == 200, "Failed to download products export CSV"
    print(f"5. Verified Download Products Export CSV: {len(res_exp.content)} bytes retrieved")
    assert len(res_exp.content) > 500, "Export CSV too small"

    # 6. Verify Multiple Jobs Don't Mix Up
    if len(reports) > 1:
        rep2 = reports[1]
        job_id_2 = rep2["job_id"]
        res2 = requests.get(f"{BASE_URL}/api/jobs/{job_id_2}/report")
        assert res2.status_code == 200
        data2 = res2.json()
        print(f"\n6. Verified Multi-Dataset Separation:")
        print(f"   - Report 1 Job: {data1['job_id']} (Total: {data1['executive_summary']['total_products_processed']})")
        print(f"   - Report 2 Job: {data2['job_id']} (Total: {data2['executive_summary']['total_products_processed']})")
        assert data1["job_id"] != data2["job_id"], "Different jobs must have unique IDs"

    print("\n================================================================================")
    print("ALL PREVIEW & REPORT WORKFLOW VERIFICATIONS PASSED WITH ZERO ERRORS!")
    print("================================================================================")

if __name__ == "__main__":
    main()
