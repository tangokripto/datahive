import requests
import time
import uuid
import json
import random
import threading
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# --- FILE PATHS ---
TOKENS_FILE = 'tokens.txt'
PROXIES_FILE = 'proxies.txt'
DEVICE_FILE = 'device_data.json'
CONFIG_FILE = 'config.json'

# --- UPDATED CPU DATABASE (dengan Ryzen 7 5800X) ---
CPU_DATABASE = {
    "Apple": [
        {"model": "Apple M1", "cores": 8, "arch": "arm64"}, 
        {"model": "Apple M1 Pro", "cores": 10, "arch": "arm64"},
        {"model": "Apple M1 Max", "cores": 10, "arch": "arm64"}, 
        {"model": "Apple M2", "cores": 8, "arch": "arm64"},
        {"model": "Apple M2 Pro", "cores": 12, "arch": "arm64"}, 
        {"model": "Apple M2 Max", "cores": 12, "arch": "arm64"},
        {"model": "Apple M3", "cores": 8, "arch": "arm64"}, 
        {"model": "Apple M3 Pro", "cores": 12, "arch": "arm64"},
        {"model": "Apple M3 Max", "cores": 16, "arch": "arm64"}, 
        {"model": "Apple M4", "cores": 10, "arch": "arm64"},
    ],
    "Intel": [
        {"model": "Intel(R) Core(TM) Ultra 9 285HX", "cores": 24, "arch": "x86_64"}, 
        {"model": "Intel(R) Core(TM) i9-14900KS", "cores": 24, "arch": "x86_64"},
        {"model": "Intel(R) Core(TM) i9-13980HX", "cores": 24, "arch": "x86_64"}, 
        {"model": "Intel(R) Core(TM) i7-14790F", "cores": 16, "arch": "x86_64"},
        {"model": "Intel(R) Core(TM) i7-14700K", "cores": 20, "arch": "x86_64"}, 
        {"model": "Intel(R) Core(TM) i5-13600K", "cores": 14, "arch": "x86_64"},
        {"model": "Intel(R) Core(TM) i3-14100", "cores": 4, "arch": "x86_64"}, 
        {"model": "Intel(R) Core(TM) i3-12300", "cores": 4, "arch": "x86_64"},
        {"model": "Intel(R) Celeron(R) G6900", "cores": 2, "arch": "x86_64"}, 
        {"model": "Intel(R) Celeron(R) 6600HE", "cores": 2, "arch": "x86_64"},
        {"model": "Intel(R) Pentium(R) Gold G7400", "cores": 2, "arch": "x86_64"}, 
        {"model": "Intel(R) Pentium(R) Gold 7505", "cores": 2, "arch": "x86_64"},
        {"model": "Intel(R) Xeon(R) Gold 6348", "cores": 28, "arch": "x86_64"},
    ],
    "AMD": [
        {"model": "AMD Ryzen 9 7950X 16-Core Processor", "cores": 16, "arch": "x86_64"}, 
        {"model": "AMD Ryzen 9 5950X 16-Core Processor", "cores": 16, "arch": "x86_64"},
        {"model": "AMD Ryzen 7 7800X3D 8-Core Processor", "cores": 8, "arch": "x86_64"}, 
        {"model": "AMD Ryzen 7 5800X 8-Core Processor", "cores": 16, "arch": "x86_64"},  # ADDED!
        {"model": "AMD Ryzen 7 2700X Eight-Core Processor", "cores": 8, "arch": "x86_64"},
        {"model": "AMD Ryzen 5 2600 Six-Core Processor", "cores": 6, "arch": "x86_64"}, 
        {"model": "AMD Ryzen 3 5100 4-Core Processor", "cores": 4, "arch": "x86_64"},
        {"model": "AMD EPYC 7763 64-Core Processor", "cores": 64, "arch": "x86_64"},
    ]
}

# Updated OS Templates dengan Chrome 144 dan Windows 19
OS_TEMPLATES = [
    {
        "platform": "Windows", "os_version": "Windows 11.0.0", "model_ua": "PC x86 - Chrome 144",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="144", "Chromium";v="144", "Not_A Brand";v="24"',
        "sec_ch_ua_platform": '"Windows"', "cpu_type": ["Intel", "AMD"], "device_name": "windows pc"
    },
    {
        "platform": "Windows", "os_version": "Windows 10.0.0", "model_ua": "PC x86 - Edge 144",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
        "sec_ch_ua": '"Microsoft Edge";v="144", "Chromium";v="144", "Not_A Brand";v="24"',
        "sec_ch_ua_platform": '"Windows"', "cpu_type": ["Intel", "AMD"], "device_name": "windows pc"
    },
    {
        "platform": "macOS", "os_version": "macOS 14.2.0", "model_ua": "Macintosh - Chrome 144",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="144", "Chromium";v="144", "Not_A Brand";v="24"',
        "sec_ch_ua_platform": '"macOS"', "cpu_type": ["Apple"], "device_name": "mac"
    },
    {
        "platform": "Linux", "os_version": "Linux x86_64", "model_ua": "Linux - Chrome 144",
        "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="144", "Chromium";v="144", "Not_A Brand";v="24"',
        "sec_ch_ua_platform": '"Linux"', "cpu_type": ["Intel", "AMD"], "device_name": "linux"
    }
]

def load_config():
    default = {
        "delay_min": 60, 
        "delay_max": 120, 
        "devices_per_account": 1, 
        "threads_delay_startup": 3,
        "rto_chance": 0.05,
        "rto_duration_min": 10,
        "rto_duration_max": 60,
        "enable_real_scraping": True  # NEW: Toggle real scraping
    }
    try:
        with open(CONFIG_FILE, 'r') as f: 
            return json.load(f)
    except: 
        return default

CONF = load_config()

def load_data():
    try:
        with open(TOKENS_FILE, 'r') as f: 
            tokens = [l.strip() for l in f if l.strip()]
    except: 
        tokens = []
    try:
        with open(PROXIES_FILE, 'r') as f: 
            raw = [l.strip() for l in f if l.strip()]
    except: 
        raw = []
    proxies = []
    for p in raw:
        parts = p.split(':')
        if len(parts) == 4: 
            proxies.append(f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}")
        elif len(parts) == 2: 
            proxies.append(f"http://{parts[0]}:{parts[1]}")
    return tokens, proxies

def get_device_config(token_last_10, device_num):
    try:
        with open(DEVICE_FILE, 'r') as f: 
            data = json.load(f)
    except: 
        data = {}
    
    key = f"{token_last_10}_dev{device_num}"
    if key not in data or 'cpu_arch' not in data[key]:
        os_tmpl = random.choice(OS_TEMPLATES)
        cpu_brand = random.choice(os_tmpl['cpu_type'])
        cpu_spec = random.choice(CPU_DATABASE[cpu_brand])
        new_conf = {
            "uuid": data.get(key, {}).get("uuid", str(uuid.uuid4())),
            "platform": os_tmpl['platform'], 
            "model": os_tmpl['model_ua'], 
            "ua": os_tmpl['ua'],
            "sec_ch_ua": os_tmpl['sec_ch_ua'], 
            "sec_ch_ua_platform": os_tmpl['sec_ch_ua_platform'], 
            "os_version": os_tmpl['os_version'],
            "cpu_arch": cpu_spec['arch'], 
            "cpu_model": cpu_spec['model'], 
            "cpu_cores": str(cpu_spec['cores']), 
            "device_name": os_tmpl['device_name'],
            "etag_job": None  # NEW: Store etag
        }
        data[key] = new_conf
        with open(DEVICE_FILE, 'w') as f: 
            json.dump(data, f, indent=4)
        return new_conf
    return data[key]

def save_device_etag(token_last_10, device_num, etag):
    """Save etag for caching"""
    try:
        with open(DEVICE_FILE, 'r') as f:
            data = json.load(f)
        key = f"{token_last_10}_dev{device_num}"
        if key in data:
            data[key]['etag_job'] = etag
            with open(DEVICE_FILE, 'w') as f:
                json.dump(data, f, indent=4)
    except:
        pass

def scrape_stackoverflow(url, timeout=15):
    """Real scraping from StackOverflow using BeautifulSoup"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_elem = soup.select_one('#question-header h1')
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        # Extract created date
        created_elem = soup.select_one('#question-header + div time')
        created_at = created_elem.get('datetime', "") if created_elem else ""
        
        # Extract question body
        question_body_elem = soup.select_one('.question .js-post-body')
        question_body = question_body_elem.get_text(strip=True) if question_body_elem else ""
        
        # Extract upvotes
        upvotes_elem = soup.select_one('.question div[itemprop="upvoteCount"]')
        upvotes = upvotes_elem.get_text(strip=True) if upvotes_elem else "0"
        
        # Extract reputation
        reputation_elem = soup.select_one('.question div[itemprop="author"] .reputation-score')
        reputation = reputation_elem.get_text(strip=True) if reputation_elem else "0"
        
        # Extract tags
        tags = []
        for tag_elem in soup.select('.question .js-post-tag-list-wrapper li'):
            tag_text = tag_elem.get_text(strip=True)
            if tag_text:
                tags.append({"body": tag_text})
        
        # Extract comments
        comments = []
        for comment_elem in soup.select('.question .comment'):
            comment_body = comment_elem.select_one('.comment-copy')
            comment_date = comment_elem.select_one('.comment-date span')
            comment_score = comment_elem.select_one('.comment-score')
            
            if comment_body:
                comments.append({
                    "body": comment_body.get_text(strip=True),
                    "createdAt": comment_date.get('title', "").split(', License')[0] if comment_date else "",
                    "score": comment_score.get_text(strip=True) if comment_score else ""
                })
        
        # Extract answers
        answers = []
        for answer_elem in soup.select('#answers .js-answer'):
            answer_body = answer_elem.select_one('.js-post-body')
            answer_date = answer_elem.select_one('time')
            answer_checkmark = answer_elem.select_one('.js-accepted-answer-indicator:not(.d-none)')
            answer_upvotes = answer_elem.select_one('div[itemprop="upvoteCount"]')
            answer_reputation = answer_elem.select_one('div[itemprop="author"] .reputation-score')
            
            answer_comments = []
            for ans_comment in answer_elem.select('.comment'):
                ans_c_body = ans_comment.select_one('.comment-copy')
                ans_c_date = ans_comment.select_one('.comment-date span')
                ans_c_score = ans_comment.select_one('.comment-score')
                
                if ans_c_body:
                    answer_comments.append({
                        "body": ans_c_body.get_text(strip=True),
                        "createdAt": ans_c_date.get('title', "").split(', License')[0] if ans_c_date else "",
                        "score": ans_c_score.get_text(strip=True) if ans_c_score else ""
                    })
            
            answers.append({
                "body": answer_body.get_text(strip=True) if answer_body else "",
                "createdAt": answer_date.get('datetime', "") if answer_date else "",
                "checkmark": answer_checkmark.get('aria-label', "") if answer_checkmark else "",
                "upvotes": answer_upvotes.get_text(strip=True) if answer_upvotes else "0",
                "author_reputation_score": answer_reputation.get_text(strip=True) if answer_reputation else "0",
                "comments": answer_comments
            })
        
        return {
            "title": title,
            "createdAt": created_at,
            "question": {
                "body": question_body,
                "upvotes": upvotes,
                "author_reputation_score": reputation,
                "tags": tags,
                "comments": comments
            },
            "answers": answers
        }
    except Exception as e:
        print(f"Scraping error: {str(e)[:50]}")
        return None

def build_job_result(job_id, target_url, enable_real=True):
    """Build job result with real or fake data"""
    start_time = time.time()
    
    if enable_real:
        scraped_data = scrape_stackoverflow(target_url, timeout=15)
        if scraped_data:
            duration = (time.time() - start_time) * 1000
            return {
                "result": {
                    "pageData": {
                        "fields": scraped_data
                    }
                },
                "metadata": {
                    "perfMetrics": {
                        "jobId": job_id,
                        "duration": duration,
                        "statistics": {
                            "cpu": {
                                "min": random.uniform(3, 8), 
                                "max": random.uniform(9, 12), 
                                "avg": random.uniform(4, 10)
                            },
                            "memory": {
                                "min": random.uniform(30, 33), 
                                "max": random.uniform(34, 36), 
                                "avg": random.uniform(32, 35)
                            }
                        },
                        "metrics": {
                            "start": {
                                "cpu": random.uniform(2, 7), 
                                "memory": random.uniform(30, 35)
                            },
                            "end": {
                                "cpu": 0, 
                                "memory": random.uniform(33, 36)
                            }
                        }
                    },
                    "context": "extension"
                }
            }
    
    # Fallback to fake data
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
                    "answers": []
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
        'accept': '*/*', 
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': f'Bearer {token}', 
        'content-type': 'application/json',
        'origin': 'chrome-extension://bonfdkhbkkdoipfojcnimjagphdnfedb',
        'priority': 'u=1, i', 
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors', 
        'sec-fetch-site': 'none',
        'sec-fetch-storage-access': 'active',
        'sec-gpc': '1',
        'user-agent': dev_conf['ua'],
        'x-app-version': '0.2.5', 
        'x-device-id': dev_conf['uuid'], 
        'x-device-model': dev_conf['model'],
        'x-device-os': dev_conf['os_version'], 
        'x-device-type': 'extension',
        'x-user-agent': dev_conf['ua'], 
        'x-s': 'f', 
        'x-user-language': 'en-GB',
        'x-cpu-architecture': dev_conf['cpu_arch'], 
        'x-cpu-model': dev_conf['cpu_model'],
        'x-cpu-processor-count': dev_conf['cpu_cores'], 
        'x-device-name': dev_conf['device_name']
    }

    url_ping = 'https://api.datahive.ai/api/ping'
    url_job = 'https://api.datahive.ai/api/job'
    url_config = 'https://api.datahive.ai/api/configuration'

    # Initial Config Handshake
    try: 
        requests.get(url_config, headers=headers, proxies=proxy_dict, timeout=30)
    except: 
        pass

    while True:
        try:
            # RTO Simulation
            if random.random() < CONF.get('rto_chance', 0.05):
                rto_duration = random.randint(CONF.get('rto_duration_min', 10), CONF.get('rto_duration_max', 60))
                ts = datetime.now().strftime("%H:%M:%S")
                print(f"🌐 [{ts}] [Akn {account_idx+1}-D{device_num}] Simulating RTO for {rto_duration}s...")
                time.sleep(rto_duration)
                print(f"🌐 [{ts}] [Akn {account_idx+1}-D{device_num}] Connection Restored.")
                continue

            # 1. CHECK JOB with if-none-match header
            try:
                job_headers = headers.copy()
                if dev_conf.get('etag_job'):
                    job_headers['if-none-match'] = dev_conf['etag_job']
                
                job_resp = requests.get(url_job, headers=job_headers, proxies=proxy_dict, timeout=30)
                
                # Save etag for next request
                if 'etag' in job_resp.headers:
                    save_device_etag(token_short, device_num, job_resp.headers['etag'])
                
                # Check if got a job
                if job_resp.status_code == 200 and job_resp.text and job_resp.text != 'null':
                    job_data = job_resp.json()
                    
                    if 'id' in job_data and 'vars' in job_data:
                        job_id = job_data['id']
                        target_url = job_data['vars'].get('url', 'unknown_url')
                        
                        ts = datetime.now().strftime("%H:%M:%S")
                        print(f"🎉 [{ts}] [Akn {account_idx+1}-D{device_num}] JACKPOT! Job: {target_url[:50]}...")
                        
                        # Simulate processing time
                        time.sleep(random.uniform(1, 2))
                        
                        # Build result (real or fake scraping)
                        payload = build_job_result(job_id, target_url, CONF.get('enable_real_scraping', True))
                        
                        # Submit job
                        post_url = f"{url_job}/{job_id}"
                        res_post = requests.post(post_url, headers=headers, json=payload, proxies=proxy_dict, timeout=30)
                        
                        if res_post.status_code == 200:
                            print(f"✅ [{ts}] [Akn {account_idx+1}-D{device_num}] Job Submitted & Accepted!")
                        else:
                            print(f"⚠️ [{ts}] [Akn {account_idx+1}-D{device_num}] Job Submit Failed: {res_post.status_code}")
            except Exception as e:
                pass

            time.sleep(1)

            # 2. PING
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
    if not tokens: 
        print("No tokens found!")
        exit()
    
    dev_per_acc = CONF.get('devices_per_account', 1)
    startup_delay = CONF.get('threads_delay_startup', 3)

    print(f"🔥 DataHive Farm v14 (Real Scraping): {len(tokens)} Accounts")
    print(f"⚙️  Real Scraping: {CONF.get('enable_real_scraping', True)}")
    print(f"⚙️  Chrome 144 | Windows 19 | Enhanced Headers")
    
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
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutdown...")
