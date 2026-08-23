import io
import time
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_e2e_upload_pipeline():
    print("=== 1. PREPARING CUSTOM TEST CSV ===")
    sample_csv = (
        "item_id,part_number,brand_name,manufacturer_name,item_description,material,color,dimensions\n"
        "PROD-9001,DIAB-500,Diablo,Freud Inc,Heavy-Duty Industrial Saw Blade 10 inch,Carbide,Red,10 in x 5/8 in\n"
        "PROD-9002,MLC-700,Malco,Malco Products,Aviation Snip Left Cut 10 inch,Hardened Steel,Blue,10 in\n"
        "PROD-9003,DWT-990,DeWalt,Stanley Black & Decker,Compact Cordless Drill Driver,Reinforced Polymer,Yellow,8.5 in\n"
        "PROD-9004,MK-1010,Makita,Makita Corp,Brushless Circular Saw 7-1/4 inch,Magnesium,Teal,7-1/4 in\n"
        "PROD-9016,UNK-0016,,,Ambiguous Replacement Bracket,Uncertain Plastic,Gray,\n"
        "PROD-9032,UNK-0032,,,Mystery Fastener Accessory,Unknown Metal,Black,\n"
    )

    print(f"Uploading 6 custom rows with explicit and reviewable data...")

    files = {"file": ("test_catalog_upload.csv", io.BytesIO(sample_csv.encode("utf-8")), "text/csv")}
    res = requests.post(f"{BASE_URL}/api/jobs", files=files)
    print(f"POST /api/jobs status code: {res.status_code}")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"

    data = res.json()
    job_id = data["job_id"]
    print(f"Created Job: {job_id} | Total Rows Detected: {data['total_rows']}")
    assert data["total_rows"] == 6

    print("\n=== 2. POLLING REAL-TIME JOB PROCESSING ===")
    for _ in range(30):
        jres = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
        assert jres.status_code == 200
        job_data = jres.json()
        status = job_data["status"]
        prog = job_data["overall_progress"]
        stage = job_data["current_stage"]
        print(f"  Job {job_id} -> Status: {status} | Progress: {prog}% | Current Stage: {stage}")
        if status in ["COMPLETED", "FAILED"]:
            break
        time.sleep(0.5)

    assert job_data["status"] == "COMPLETED", f"Job failed or did not finish: {job_data}"
    assert len(job_data["stages"]) == 11
    print("All 11 Stages Completed Successfully!")

    print("\n=== 3. VERIFYING JOB RESULTS API ===")
    rres = requests.get(f"{BASE_URL}/api/jobs/{job_id}/results?page=1&page_size=10&status_filter=ALL")
    assert rres.status_code == 200
    results_data = rres.json()
    print(f"Total Processed Items: {results_data['total']}")
    assert results_data["total"] == 6
    for item in results_data["items"]:
        print(f"  * Product ID: {item['product_id']} | MPN: {item['mpn']} | Brand: {item['brand']} | Status: {item['status']} | Confidence: {item['confidence']}")

    print("\n=== 4. VERIFYING SYNCHRONIZATION TO CORE APPLICATION (PRODUCTS PAGE) ===")
    pres = requests.get(f"{BASE_URL}/api/products?page=1&limit=10")
    assert pres.status_code == 200
    prod_data = pres.json()
    print(f"Products Page Total Items: {prod_data['total']}")
    assert prod_data["total"] == 6
    pids = [p["product"]["product_id"] for p in prod_data["items"]]
    print(f"Product IDs on Products Page: {pids}")
    assert "PROD-9001" in pids
    assert "PROD-9002" in pids
    assert "PROD-9003" in pids

    # Detail check for PROD-9001
    det_res = requests.get(f"{BASE_URL}/api/products/PROD-9001")
    assert det_res.status_code == 200
    det = det_res.json()
    print(f"\nPROD-9001 Detail:")
    print(f"  Product Name: {det['product']['product_name']}")
    print(f"  Brand: {det['product']['brand']} | Mfr: {det['product']['manufacturer']}")
    print(f"  Attributes: {det.get('attributes')}")
    print(f"  Validation Confidence: {det['validation']['confidence']}")

    print("\n=== 5. VERIFYING REVIEW QUEUE POPULATION FROM UPLOADED CSV ===")
    qres = requests.get(f"{BASE_URL}/api/review/queue")
    assert qres.status_code == 200
    qitems = qres.json()
    print(f"Review Queue Total Items: {len(qitems)}")
    for qitem in qitems:
        print(f"  * Review ID: {qitem['review_id']} | Product: {qitem['product_id']}:{qitem['attribute_name']} | Conf: {qitem['confidence_score']} | Status: {qitem['review_status']}")

    print("\n=== 6. PERFORMING HUMAN REVIEW ACTION ===")
    if qitems:
        target_review = qitems[0]
        rid = target_review["review_id"]
        edit_payload = {
            "edited_value": "Pure Tungsten Carbide",
            "reason": "Expert review: Updated to full manufacturer grade specification",
            "reviewer_id": "Lead Data Specialist"
        }
        act_res = requests.post(f"{BASE_URL}/api/review/{rid}/edit", json=edit_payload)
        assert act_res.status_code == 200
        print(f"Review Edit Action Succeeded: {act_res.json()['message']}")

        # Verify updated product detail
        updated_det = requests.get(f"{BASE_URL}/api/products/{target_review['product_id']}").json()
        print(f"Updated Product Detail Attribute: {updated_det['attributes'].get(target_review['attribute_name'])}")
        print(f"Review History Length: {len(updated_det.get('review_history', []))}")
        assert len(updated_det.get('review_history', [])) > 0

    print("\n========================================================")
    print("ALL END-TO-END PIPELINE UPLOAD & SYNC CHECKS PASSED!")
    print("========================================================")

if __name__ == "__main__":
    test_e2e_upload_pipeline()
