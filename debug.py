import requests
import json
import time
from datetime import datetime

# Test dengan 1 token
TOKEN = input("Paste 1 token untuk test: ").strip()
PROXY = input("Paste proxy (format ip:port:user:pass atau kosong): ").strip()

if PROXY:
    parts = PROXY.split(':')
    if len(parts) == 4:
        proxy_url = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    else:
        proxy_url = f"http://{PROXY}"
    proxies = {"http": proxy_url, "https": proxy_url}
else:
    proxies = None

# Headers (gunakan Chrome 144)
headers = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'authorization': f'Bearer {TOKEN}',
    'content-type': 'application/json',
    'origin': 'chrome-extension://bonfdkhbkkdoipfojcnimjagphdnfedb',
    'priority': 'u=1, i',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'none',
    'sec-fetch-storage-access': 'active',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'x-app-version': '0.2.5',
    'x-device-id': 'test-device-12345',
    'x-device-model': 'PC x86 - Chrome 144',
    'x-device-os': 'Windows 19.0.0',
    'x-device-type': 'extension',
    'x-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'x-s': 'f',
    'x-user-language': 'en-GB',
    'x-cpu-architecture': 'x86_64',
    'x-cpu-model': 'AMD Ryzen 7 5800X 8-Core Processor',
    'x-cpu-processor-count': '16',
    'x-device-name': 'windows pc'
}

print("\n" + "="*60)
print("🧪 DATAHIVE DEBUG TEST")
print("="*60)

# Test 1: Configuration
print("\n1️⃣ Testing /api/configuration...")
try:
    resp = requests.get('https://api.datahive.ai/api/configuration', 
                       headers=headers, proxies=proxies, timeout=30)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        config = resp.json()
        print(f"   ✅ Config loaded:")
        print(f"      - Min version: {config.get('min_extension_version')}")
        print(f"      - Job delay: {config.get('job_execution_delay')}s")
        print(f"      - Installation reward: {config.get('extension_installation_reward_points')}")
    else:
        print(f"   ❌ Failed: {resp.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Ping
print("\n2️⃣ Testing /api/ping...")
try:
    headers_ping = headers.copy()
    headers_ping['Content-Length'] = '0'
    resp = requests.post('https://api.datahive.ai/api/ping',
                        headers=headers_ping, data='', proxies=proxies, timeout=30)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Ping successful:")
        print(f"      - Status: {data.get('status')}")
        print(f"      - Uptime: {data.get('uptime')}")
    elif resp.status_code == 401:
        print(f"   ❌ Token expired or invalid!")
    else:
        print(f"   ❌ Failed: {resp.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get Job
print("\n3️⃣ Testing /api/job (checking for available jobs)...")
print("   Waiting for job... (this may take 1-2 minutes)")

etag = None
for attempt in range(12):  # Try for 2 minutes
    try:
        job_headers = headers.copy()
        if etag:
            job_headers['if-none-match'] = etag
        
        resp = requests.get('https://api.datahive.ai/api/job',
                           headers=job_headers, proxies=proxies, timeout=30)
        
        # Save etag
        if 'etag' in resp.headers:
            etag = resp.headers['etag']
        
        print(f"   [{attempt+1}/12] Status: {resp.status_code}, Body: {resp.text[:50]}...")
        
        if resp.status_code == 200 and resp.text and resp.text != 'null':
            job_data = resp.json()
            if 'id' in job_data:
                print(f"\n   🎉 GOT A JOB!")
                print(f"      - Job ID: {job_data['id']}")
                print(f"      - URL: {job_data.get('vars', {}).get('url', 'N/A')}")
                print(f"      - Timeout: {job_data.get('vars', {}).get('timeout', 'N/A')}")
                
                # Test 4: Submit fake result
                print("\n4️⃣ Testing job submission...")
                payload = {
                    "result": {
                        "pageData": {
                            "fields": {
                                "title": "Test",
                                "createdAt": "2024-01-01T00:00:00Z",
                                "question": {"body": "test", "upvotes": "1", "tags": [], "comments": []},
                                "answers": []
                            }
                        }
                    },
                    "metadata": {
                        "perfMetrics": {
                            "jobId": job_data['id'],
                            "duration": 1500,
                            "statistics": {"cpu": {"min": 5, "max": 10, "avg": 7}, "memory": {"min": 30, "max": 35, "avg": 33}},
                            "metrics": {"start": {"cpu": 5, "memory": 30}, "end": {"cpu": 0, "memory": 35}}
                        },
                        "context": "extension"
                    }
                }
                
                submit_resp = requests.post(f'https://api.datahive.ai/api/job/{job_data["id"]}',
                                           headers=headers, json=payload, proxies=proxies, timeout=30)
                
                print(f"   Status: {submit_resp.status_code}")
                print(f"   Response: {submit_resp.text}")
                
                if submit_resp.status_code == 200:
                    print(f"   ✅ Job submission accepted!")
                else:
                    print(f"   ❌ Job submission failed!")
                
                break
        elif resp.status_code == 304:
            print(f"   ⏭️  No new jobs (cached)")
        
        time.sleep(10)  # Wait 10s between checks
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        time.sleep(10)
else:
    print(f"\n   ⏱️ No jobs received after 2 minutes")
    print(f"   This is normal - jobs are distributed randomly")

print("\n" + "="*60)
print("🏁 TEST COMPLETE")
print("="*60)
print("\n📝 What to check:")
print("1. If ping fails → Check token validity")
print("2. If jobs never come → Normal, they're distributed randomly")
print("3. If job submission fails → Check the error message")
print("4. Dashboard should show this test device as 'active'")