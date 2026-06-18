import urllib.request
import urllib.error
import json

try:
    with open('backend/tests/fixtures/canonical_payload.json', 'r') as f:
        canonical_content = json.load(f)
except FileNotFoundError:
    print("MOCKING PAYLOAD")
    canonical_content = {
        "birth_data": {"name": "Test", "dob": "1990-01-01", "tob": "12:00:00", "pob": "Test City", "lat": 0.0, "lon": 0.0, "tz": 0.0},
        "planets": {},
        "houses": {}
    }
    
machine_index = {"native_info": {"name": "Test User"}}

payload = json.dumps({
    "canonical_content": canonical_content,
    "machine_index": machine_index
}).encode('utf-8')

print("Testing HTML endpoint...")
try:
    req = urllib.request.Request("http://localhost:8000/api/v1/generate-report?format=html", data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print(f"HTML Status: {response.status}")
except urllib.error.HTTPError as e:
    print(f"HTML Failed: {e.code} - {e.read()}")

print("Testing PDF endpoint...")
try:
    req = urllib.request.Request("http://localhost:8000/api/v1/generate-report?format=pdf", data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        content = response.read()
        print(f"PDF Status: {response.status}")
        print(f"PDF successfully generated! Size: {len(content)} bytes")
except urllib.error.HTTPError as e:
    print(f"PDF Generation failed: {e.code} - {e.read().decode()}")
