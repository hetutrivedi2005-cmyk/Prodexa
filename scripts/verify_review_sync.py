import urllib.request
import json
import time

def test_sync():
    # 1. Fetch review queue to find PROD-0104:edge_profile
    req = urllib.request.Request('http://127.0.0.1:8000/api/review/queue')
    with urllib.request.urlopen(req) as resp:
        queue = json.loads(resp.read().decode('utf-8'))

    p104_edge = [item for item in queue if item.get('product_id') == 'PROD-0104' and item.get('attribute_name') == 'edge_profile'][0]
    rev_id = p104_edge['review_id']
    print('Found PROD-0104:edge_profile review item:', rev_id, '| status:', p104_edge.get('review_status'))

    # 2. Perform Edit Review to HET with reason
    payload = json.dumps({
        'reviewer_id': 'Product Specialist',
        'reason': 'Corrected based on manufacturer evidence',
        'edited_value': 'HET'
    }).encode('utf-8')

    edit_req = urllib.request.Request(
        f'http://127.0.0.1:8000/api/review/{rev_id}/edit',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(edit_req) as resp:
        edit_res = json.loads(resp.read().decode('utf-8'))
        print('Edit Response:', edit_res.get('status'), '| Message:', edit_res.get('message'))

    # 3. Verify Product Detail API
    req_detail = urllib.request.Request('http://127.0.0.1:8000/api/products/PROD-0104')
    with urllib.request.urlopen(req_detail) as resp:
        detail = json.loads(resp.read().decode('utf-8'))

    print('\n=== VERIFICATION OF PROD-0104 DETAIL ===')
    print('Overview Tab attribute edge_profile:', detail['attributes'].get('edge_profile'))
    print('Attributes Tab field edge_profile:', detail['fields'].get('edge_profile'))
    print('\nReview History Audit Trail:')
    for h in detail.get('review_history', []):
        attr = h.get('attribute_name')
        act = h.get('action')
        prev = h.get('old_value')
        new_v = h.get('new_value')
        reas = h.get('reason')
        rev = h.get('reviewer_id')
        print(f"  * {attr} -> {act} | Previous: '{prev}' | New: '{new_v}' | Reason: '{reas}' | Reviewer: {rev}")

    # 4. Verify Pending Queue
    req_pending = urllib.request.Request('http://127.0.0.1:8000/api/review/queue?status_filter=PENDING')
    with urllib.request.urlopen(req_pending) as resp:
        pending_queue = json.loads(resp.read().decode('utf-8'))
    pending_keys = [f"{i['product_id']}:{i['attribute_name']}" for i in pending_queue]
    print('\nIs PROD-0104:edge_profile still in Pending Queue?', 'PROD-0104:edge_profile' in pending_keys)

    # 5. Verify Disk Persistence
    with open('data/final/product.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    p104_disk = [p for p in products if p.get('product', {}).get('product_id') == 'PROD-0104'][0]
    print("Disk product.json attributes['edge_profile']:", p104_disk.get('attributes', {}).get('edge_profile'))

if __name__ == '__main__':
    test_sync()
