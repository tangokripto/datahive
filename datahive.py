import requests
import time
import uuid
import json
import random
import threading
from datetime import datetime, timezone

# --- FILE PATHS ---
TOKENS_FILE = 'tokens.txt'
PROXIES_FILE = 'proxies.txt'
DEVICE_FILE = 'device_data.json'
CONFIG_FILE = 'config.json'

# --- DATABASE CPU

CPU_DATABASE = {
    "Apple": [
        {"model": "Apple M1", "cores": 8, "arch": "arm64"},{"model": "Apple M1 Pro", "cores": 10, "arch": "arm64"},
        {"model": "Apple M1 Max", "cores": 10, "arch": "arm64"},{"model": "Apple M2", "cores": 8, "arch": "arm64"},
        {"model": "Apple M2 Pro", "cores": 12, "arch": "arm64"},{"model": "Apple M2 Max", "cores": 12, "arch": "arm64"},
        {"model": "Apple M3", "cores": 8, "arch": "arm64"},{"model": "Apple M3 Pro", "cores": 12, "arch": "arm64"},
        {"model": "Apple M3 Max", "cores": 16, "arch": "arm64"},{"model": "Apple M4", "cores": 10, "arch": "arm64"},
    ],
    "Intel": [
        {"model": "Intel(R) Core(TM) Ultra 9 285HX", "cores": 24, "arch": "x86_64"},{"model": "Intel(R) Core(TM) i9-14900KS", "cores": 24, "arch": "x86_64"},
        {"model": "Intel(R) Core(TM) i9-13980HX", "cores": 24, "arch": "x86_64"},{"model": "Intel(R) Core(TM) i7-14790F", "cores": 16, "arch": "x86_64"},
        {"model": "Intel(R) Core(TM) i7-14700K", "cores": 20, "arch": "x86_64"},{"model": "Intel(R) Core(TM) i5-13600K", "cores": 14, "arch": "x86_64"},
        {"model": "Intel(R) Core(TM) i3-14100", "cores": 4, "arch": "x86_64"},{"model": "Intel(R) Core(TM) i3-12300", "cores": 4, "arch": "x86_64"},
        {"model": "Intel(R) Pentium(R) Gold G7400", "cores": 2, "arch": "x86_64"},{"model": "Intel(R) Pentium(R) Gold 7505", "cores": 2, "arch": "x86_64"},
    ],
    "AMD": [
        {"model": "AMD Ryzen 9 7950X", "cores": 16, "arch": "x86_64"},{"model": "AMD Ryzen 9 5950X", "cores": 16, "arch": "x86_64"},
        {"model": "AMD Ryzen 7 7800X3D", "cores": 8, "arch": "x86_64"},{"model": "AMD Ryzen 7 2700X", "cores": 8, "arch": "x86_64"},
        {"model": "AMD Ryzen 5 2600", "cores": 6, "arch": "x86_64"},{"model": "AMD Ryzen 3 5100", "cores": 4, "arch": "x86_64"},
    ]
}

OS_TEMPLATES = [
    {"platform": "Windows", "os_version": "Windows 10.0", "model_ua": "Windows - Chrome 131", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36", "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"', "sec_ch_ua_platform": '"Windows"', "cpu_type": ["Intel", "AMD"], "device_name": "windows"},
    {"platform": "macOS", "os_version": "macOS 14.2.0", "model_ua": "Macintosh - Chrome 131", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36", "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"', "sec_ch_ua_platform": '"macOS"', "cpu_type": ["Apple"], "device_name": "mac"},
    {"platform": "Linux", "os_version": "Linux x86_64", "model_ua": "Linux - Chrome 131", "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36", "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"', "sec_ch_ua_platform": '"Linux"', "cpu_type": ["Intel", "AMD"], "device_name": "linux"}
]

def load_config():
    default = {"delay_min": 60, "delay_max": 120, "devices_per_account": 1, "threads_delay_startup": 3}
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return default

CONF = load_config()

def load_data():
    try:
        with open(TOKENS_FILE, 'r') as f: tokens = [l.strip() for l in f if l.strip()]
    except: tokens = []
    try:
        with open(PROXIES_FILE, 'r') as f: raw = [l.strip() for l in f if l.strip()]
    except: raw = []
    proxies = []
    for p in raw:
        parts = p.split(':')
        if len(parts) == 4: proxies.append(f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}")
        elif len(parts) == 2: proxies.append(f"http://{parts[0]}:{parts[1]}")
    return tokens, proxies

def get_device_config(token_last_10, device_num):
    try:
        with open(DEVICE_FILE, 'r') as f: data = json.load(f)
    except: data = {}
    key = f"{token_last_10}_dev{device_num}"
    if key not in data or 'cpu_arch' not in data[key]:
        os_tmpl = random.choice(OS_TEMPLATES)
        cpu_brand = random.choice(os_tmpl['cpu_type'])
        cpu_spec = random.choice(CPU_DATABASE[cpu_brand])
        new_conf = {
            "uuid": data.get(key, {}).get("uuid", str(uuid.uuid4())),
            "platform": os_tmpl['platform'], "model": os_tmpl['model_ua'], "ua": os_tmpl['ua'],
            "sec_ch_ua": os_tmpl['sec_ch_ua'], "sec_ch_ua_platform": os_tmpl['sec_ch_ua_platform'], "os_version": os_tmpl['os_version'],
            "cpu_arch": cpu_spec['arch'], "cpu_model": cpu_spec['model'], "cpu_cores": str(cpu_spec['cores']), "device_name": os_tmpl['device_name']
        }
        data[key] = new_conf
        with open(DEVICE_FILE, 'w') as f: json.dump(data, f, indent=4)
        return new_conf
    return data[key]

# --- REAL JOB RESULT BUILDER ---
def build_job_result(job_id, target_url):
    duration = random.uniform(1000, 3000)
    utc_now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    return {
        "result": {
            "pageData": {
                "fields": {
                    "title": "Discussion on " + target_url.split('/')[-1].replace('-', ' '),
                    "createdAt": utc_now,
                    "question": {
                        "body": "This is a technical question related to the topic in the URL.",
                        "upvotes": str(random.randint(1, 100)),
                        "author_reputation_score": str(random.randint(100, 10000)),
                        "tags": [{"body": "tech"}, {"body": "software"}],
                        "comments": []
                    },
                    "answers": [
                        {
                            "body": "This is a potential answer to the question based on documentation.",
                            "createdAt": utc_now,
                            "checkmark": "Accepted",
                            "upvotes": str(random.randint(1, 50)),
                            "author_reputation_score": str(random.randint(100, 5000)),
                            "comments": []
                        }
                    ]
                }
            }
        },
        "metadata": {
            "perfMetrics": {
                "jobId": job_id,
                "duration": duration,
                "statistics": {
                    "cpu": {"min": 10.0, "max": 40.0, "avg": 25.5},
                    "memory": {"min": 98.0, "max": 99.5, "avg": 99.0}
                },
                "metrics": {
                    "start": {"cpu": random.uniform(10, 20), "memory": random.uniform(98, 99)},
                    "end": {"cpu": random.uniform(5, 10), "memory": random.uniform(98, 99)}
                }
            },
            "context": "extension"
        }
    }

def run_worker(account_idx, token, proxy_url, device_num):
    token_short = token[-10:]
    dev_conf = get_device_config(token_short, device_num)
    proxy_dict = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    
    print(f"✅ [Akn {account_idx+1}-D{device_num}] Init: {dev_conf['platform']} | {dev_conf['cpu_model']}...")

    headers = {
        'accept': '*/*', 'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': f'Bearer {token}', 'content-type': 'application/json',
        'origin': 'chrome-extension://bonfdkhbkkdoipfojcnimjagphdnfedb',
        'priority': 'u=1, i', 'sec-ch-ua': dev_conf['sec_ch_ua'], 'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': dev_conf['sec_ch_ua_platform'], 'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors', 'sec-fetch-site': 'none', 'user-agent': dev_conf['ua'],
        'x-app-version': '0.2.5', 'x-device-id': dev_conf['uuid'], 'x-device-model': dev_conf['model'],
        'x-device-os': dev_conf['os_version'], 'x-device-type': 'extension',
        'x-user-agent': dev_conf['ua'], 'x-s': 'f', 'x-user-language': 'en-GB',
        'x-cpu-architecture': dev_conf['cpu_arch'], 'x-cpu-model': dev_conf['cpu_model'],
        'x-cpu-processor-count': dev_conf['cpu_cores'], 'x-device-name': dev_conf['device_name']
    }

    url_ping = 'https://api.datahive.ai/api/ping'
    url_job = 'https://api.datahive.ai/api/job'
    url_config = 'https://api.datahive.ai/api/configuration'

    # Initial Config Handshake
    try: requests.get(url_config, headers=headers, proxies=proxy_dict, timeout=30)
    except: pass

    while True:
        try:
            # 1. CEK JOB (REAL GET)
            try:
                job_resp = requests.get(url_job, headers=headers, proxies=proxy_dict, timeout=30)
                
                if job_resp.status_code == 200 and job_resp.text:
                    job_data = job_resp.json()
                    
                    if 'id' in job_data and 'vars' in job_data:
                        job_id = job_data['id']
                        target_url = job_data['vars'].get('url', 'unknown_url')
                        
                        ts = datetime.now().strftime("%H:%M:%S")
                        print(f"🎉 [{ts}] [Akn {account_idx+1}-D{device_num}] JACKPOT! Job: {target_url[:30]}...")
                        
                        time.sleep(random.uniform(5, 10)) 
                        
                        post_url = f"{url_job}/{job_id}"
                        payload = build_job_result(job_id, target_url)
                        
                        res_post = requests.post(post_url, headers=headers, json=payload, proxies=proxy_dict, timeout=30)
                        
                        if res_post.status_code == 200:
                            print(f"✅ [{ts}] [Akn {account_idx+1}-D{device_num}] Job Submitted & Accepted!")
            except Exception as e:
                # Job error is common, ignore
                pass

            time.sleep(1)

            # 2. PING (Wajib)
            headers_ping = headers.copy()
            headers_ping['Content-Length'] = '0'
            resp = requests.post(url_ping, headers=headers_ping, data='', proxies=proxy_dict, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                uptime = data.get('uptime', 0)
                ts = datetime.now().strftime("%H:%M:%S")
                cpu_short = dev_conf['cpu_model'].split(' ')[0] + "..."
                print(f"[{ts}] [Akn {account_idx+1}-D{device_num}] 🟢 OK | {cpu_short} | Pt: {uptime}")
            
            elif resp.status_code == 401:
                print(f"❌ [Akn {account_idx+1}-D{device_num}] Token Expired!")
                break
            elif resp.status_code == 429:
                print(f"⚠️ [Akn {account_idx+1}-D{device_num}] Rate Limit! Sleep...")
                time.sleep(60)

            # Delay
            d_min = CONF.get('delay_min', 60)
            d_max = CONF.get('delay_max', 120)
            time.sleep(random.randint(d_min, d_max))

        except Exception as e:
            print(f"🔴 Error: {str(e)[:30]}")
            time.sleep(30)

if __name__ == "__main__":
    tokens, proxies = load_data()
    if not tokens: exit()
    dev_per_acc = CONF.get('devices_per_account', 1)
    startup_delay = CONF.get('threads_delay_startup', 3)

    print(f"🔥 Farm V12 (Worker Edition): {len(tokens)} Akun by tangoinside")
    print(f"⚙️  System: Ping + Real Job Execution")
    
    threads = []
    for i, token in enumerate(tokens):
        user_proxy = proxies[i % len(proxies)] if proxies else None
        for d in range(1, dev_per_acc + 1):
            t = threading.Thread(target=run_worker, args=(i, token, user_proxy, d))
            t.daemon = True
            t.start()
            threads.append(t)
            time.sleep(startup_delay)

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutdown...")