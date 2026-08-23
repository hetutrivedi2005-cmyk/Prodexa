import time
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_unihack_1000_rows_pipeline():
    print("================================================================================")
    print("PRODEXA — VERIFYING 15-PHASE PRODUCT INTELLIGENCE PIPELINE ON 1,000-ROW UNIHACK CSV")
    print("================================================================================\n")

    input_file = Path("data/raw/input.csv")
    assert input_file.exists(), "data/raw/input.csv not found!"

    print("=== 1. UPLOADING 1,000-ROW UNIHACK CSV ===")
    with open(input_file, "rb") as f:
        csv_bytes = f.read()

    res = requests.post(
        f"{BASE_URL}/api/jobs",
        files={"file": ("unihack_1000_input.csv", csv_bytes, "text/csv")}
    )
    print(f"POST /api/jobs status code: {res.status_code}")
    assert res.status_code == 200, f"Upload failed: {res.text}"

    data = res.json()
    job_id = data["job_id"]
    total_rows = data["total_rows"]
    print(f"Created Job: {job_id} | Total Rows Detected: {total_rows}")
    assert total_rows == 1000, f"Expected 1000 rows, got {total_rows}"

    print("\n=== 2. TRACKING REAL-TIME 15-STAGE PROCESSING ===")
    max_wait = 180
    start_time = time.time()
    last_stage = ""

    while time.time() - start_time < max_wait:
        sres = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
        assert sres.status_code == 200
        jdata = sres.json()
        status = jdata["status"]
        progress = jdata.get("overall_progress", 0)
        curr_stage = jdata.get("current_stage", "")
        stages = jdata.get("stages", [])

        if curr_stage != last_stage or progress % 20 == 0:
            print(f"  Job {job_id} -> Status: {status} | Progress: {progress}% | Current Stage: {curr_stage}")
            last_stage = curr_stage

        if status == "COMPLETED":
            print(f"\nAll {len(stages)} Stages Completed Successfully in {time.time() - start_time:.2f}s!")
            assert len(stages) == 15, f"Expected 15 stages, got {len(stages)}"
            break
        elif status == "FAILED":
            raise RuntimeError(f"Job failed: {jdata.get('error')}")

        time.sleep(1)

    print("\n=== 3. VERIFYING JOB RESULTS API & METRICS ===")
    rres = requests.get(f"{BASE_URL}/api/jobs/{job_id}/results?page=1&page_size=10")
    assert rres.status_code == 200
    res_data = rres.json()
    total_results = res_data["total"]
    print(f"Total Processed Items: {total_results}")
    assert total_results == 1000, f"Expected 1000 results, got {total_results}"

    successful_count = jdata.get("successful_rows", 0)
    needs_review_count = jdata.get("needs_review_rows", 0)
    failed_count = jdata.get("failed_rows", 0)

    print(f"  Successfully Classified: {successful_count} ({successful_count/total_results*100:.1f}%)")
    print(f"  Needs Review:           {needs_review_count} ({needs_review_count/total_results*100:.1f}%)")
    print(f"  Failed:                 {failed_count} ({failed_count/total_results*100:.1f}%)")

    assert successful_count > 600, f"Expected >600 successfully classified, got {successful_count}"
    assert needs_review_count < 400, f"Expected <400 needs review, got {needs_review_count}"

    print("\n=== 4. VERIFYING CANONICAL CORE DATASET (PRODUCTS PAGE) ===")
    pres = requests.get(f"{BASE_URL}/api/products?page=1&limit=10")
    assert pres.status_code == 200
    prod_data = pres.json()
    print(f"Products Page Total Items: {prod_data['total']}")
    assert prod_data["total"] == 1000, f"Expected 1000 products, got {prod_data['total']}"

    first_prod = prod_data["items"][0]
    pid = first_prod["product"]["product_id"]
    print(f"Sample Product [{pid}]:")
    print(f"  Title: {first_prod.get('descriptions', {}).get('title')}")
    print(f"  Brand: {first_prod['product'].get('brand')} | Mfr: {first_prod['product'].get('manufacturer')}")
    print(f"  Category: {first_prod['product'].get('product_type')}")
    print(f"  Confidence: {first_prod['validation'].get('confidence')}")

    print("\n=== 5. VERIFYING DASHBOARD SUMMARY METRICS ===")
    dres = requests.get(f"{BASE_URL}/api/dashboard/summary")
    assert dres.status_code == 200
    dash_data = dres.json()
    print(f"Dashboard Summary:")
    print(f"  Products Processed:       {dash_data['products_processed']}")
    print(f"  Successfully Classified:  {dash_data['successfully_classified']}")
    print(f"  Needs Review:             {dash_data['needs_review']}")
    print(f"  Average Confidence:       {dash_data['average_confidence']}%")
    print(f"  Completed Phases:         {dash_data['pipeline_completed_phases']}/15")

    assert dash_data["products_processed"] == 1000
    assert dash_data["pipeline_completed_phases"] == 15

    print("\n=== 6. VERIFYING REVIEW QUEUE AND HUMAN AUDIT ACTION ===")
    qres = requests.get(f"{BASE_URL}/api/review/queue")
    assert qres.status_code == 200
    qitems = qres.json()
    print(f"Review Queue Total Flagged Items: {len(qitems)}")

    if qitems:
        rev_item = qitems[0]
        rev_id = rev_item["review_id"]
        rev_pid = rev_item["product_id"]
        attr_name = rev_item.get("field_name") or rev_item.get("attribute_name")
        print(f"Selected Review Item: {rev_id} for Product {rev_pid} (Field: {attr_name})")

        # Edit the field
        edit_payload = {
            "edited_value": "Industrial Ultra-High Precision Spec",
            "reason": "Verified against manufacturer catalog master index"
        }
        ares = requests.post(f"{BASE_URL}/api/review/{rev_id}/edit", json=edit_payload)
        assert ares.status_code == 200, f"Edit failed: {ares.text}"
        print(f"Edit action succeeded: {ares.json().get('message')}")

        # Check product detail
        pdres = requests.get(f"{BASE_URL}/api/products/{rev_pid}")
        assert pdres.status_code == 200
        pdetail = pdres.json()
        updated_val = pdetail.get("attributes", {}).get(attr_name) or pdetail.get("fields", {}).get(attr_name, {}).get("value")
        print(f"Verified Updated Product Detail Field [{attr_name}]: {updated_val}")
        assert updated_val == "Industrial Ultra-High Precision Spec", f"Expected 'Industrial Ultra-High Precision Spec', got '{updated_val}'"

    print("\n=== 7. VERIFYING AUTOMATED COMPREHENSIVE REPORT API ===")
    rres = requests.get(f"{BASE_URL}/api/jobs/{job_id}/report")
    assert rres.status_code == 200, f"Report failed: {rres.text}"
    report_json = rres.json()
    print(f"Report ID: {report_json.get('report_id')}")
    print(f"Executive Summary Classified Rate: {report_json['executive_summary']['classification_success_rate']}%")
    print(f"Confidence Distribution Bands: {list(report_json['confidence_distribution']['bands'].keys())}")
    print(f"15 Pipeline Stages Recorded: {len(report_json['pipeline_phases'])}")
    assert len(report_json["pipeline_phases"]) == 15
    assert report_json["executive_summary"]["total_products_processed"] == 1000

    csv_rep_res = requests.get(f"{BASE_URL}/api/jobs/{job_id}/report/csv")
    assert csv_rep_res.status_code == 200
    assert "product_id" in csv_rep_res.text
    print(f"Report CSV Download Length: {len(csv_rep_res.text)} bytes")

    reps_list_res = requests.get(f"{BASE_URL}/api/reports")
    assert reps_list_res.status_code == 200
    all_reps = reps_list_res.json()
    print(f"Total Generated Reports in Directory: {len(all_reps)}")
    assert len(all_reps) >= 1

    print("\n================================================================================")
    print("ALL 15-PHASE UNIHACK PIPELINE & AUTOMATED REPORT CHECKS PASSED WITH ZERO ERRORS!")
    print("================================================================================")

if __name__ == "__main__":
    test_unihack_1000_rows_pipeline()
