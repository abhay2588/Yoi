import subprocess
import json
import requests
import os
import concurrent.futures

JOKR_PLAYLIST_URL = "https://raw.githubusercontent.com/abhay2588/jokr/main/yoi"
OUTPUT_FILE = "live.m3u8"

PROXIES = []
for i in range(1, 6):
    p = os.environ.get(f"PROXY_{i}")
    if p:
        PROXIES.append(p)

legacy_proxy = os.environ.get("BACKUP_PROXY_URL")
if legacy_proxy and legacy_proxy not in PROXIES:
    PROXIES.append(legacy_proxy)

CHANNELS = [
    {"url": "https://www.youtube.com/@aajtak/live", "group": "News", "logo": "", "id": "aajtak"},
    {"url": "https://www.youtube.com/@abpnews/live", "group": "News", "logo": "", "id": "abpnews"},
    {"url": "https://www.youtube.com/@zeenews/live", "group": "News", "logo": "", "id": "zeenews"},
    {"url": "https://www.youtube.com/@timesnownavbharat/live", "group": "News", "logo": "", "id": "timesnownavbharat"},
    {"url": "https://www.youtube.com/@TV9Bharatvarsh/live", "group": "News", "logo": "", "id": "TV9Bharatvarsh"},
    {"url": "https://www.youtube.com/@ndtvindia/live", "group": "News", "logo": "", "id": "ndtvindia"}
    # Truncated the list temporarily for faster debugging! We only need to test a few.
]

def load_existing_playlist():
    cache = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        blocks = content.split('\n\n')
        for block in blocks:
            if '#EXTINF' in block and 'tvg-id="' in block:
                try:
                    id_start = block.find('tvg-id="') + 8
                    id_end = block.find('"', id_start)
                    chan_id = block[id_start:id_end]
                    lines = block.strip().split('\n')
                    url = lines[-1]
                    if url.startswith('http'):
                        cache[chan_id] = {'block': block.strip() + '\n\n', 'url': url}
                except Exception:
                    pass
    return cache

EXISTING_CACHE = load_existing_playlist()

def is_link_alive(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.head(url, headers=headers, timeout=5)
        return r.status_code == 200
    except:
        return False

def run_extractor(channel_url, proxy_to_use):
    command = [
        "yt-dlp", 
        "--socket-timeout", "10", 
        "--cookies", "cookies.txt", 
        "--remote-components", "ejs:github", 
        "--extractor-args", "youtube:client=android", 
        "-J"
    ]
    if proxy_to_use:
        command.extend(["--proxy", proxy_to_use])
    command.append(channel_url)
    
    # We are capturing both standard output and standard error now
    return subprocess.run(command, capture_output=True, text=True, check=True, timeout=15)

def process_channel(channel):
    print(f"Started: {channel['id']}")
    
    cached_data = EXISTING_CACHE.get(channel['id'])
    if cached_data:
        if is_link_alive(cached_data['url']):
            print(f"  -> SUCCESS: Token alive. Bypassing extraction. 🟢")
            return cached_data['block']

    result = None
    
    # THE MULTI-PROXY WATERFALL WITH DEEP DEBUGGING
    if not result and PROXIES:
        for index, proxy in enumerate(PROXIES, start=1):
            try:
                print(f"  -> Hitting Proxy {index} for {channel['id']}...")
                result = run_extractor(channel['url'], proxy)
                if result:
                    break 
            
            # --- THE MAGIC DEBUG BLOCK ---
            except subprocess.CalledProcessError as e:
                error_output = e.stderr if e.stderr else e.stdout
                print(f"  -> [CRITICAL ERROR] Proxy {index} crashed! Reason:\n      {error_output.strip()}")
                result = None
            except subprocess.TimeoutExpired:
                print(f"  -> [TIMEOUT] Proxy {index} took too long to respond.")
                result = None
            except Exception as e:
                print(f"  -> [SYSTEM ERROR] Proxy {index} failed: {str(e)}")
                result = None

    try:
        if result:
            video_data = json.loads(result.stdout.strip())
            channel_name = video_data.get("uploader", "Unknown Channel")
            m3u8_url = video_data.get("manifest_url") or video_data.get("url")
            if m3u8_url:
                print(f"  -> Fetched fresh token: {channel_name} 🟢")
                return f'#EXTINF:-1 tvg-id="{channel["id"]}" tvg-logo="{channel["logo"]}" group-title="{channel["group"]}", {channel_name}\n{m3u8_url}\n\n'
    except Exception:
        pass
        
    return None

def update_playlist():
    print(f"Spawning Smart Extractors with {len(PROXIES)} active proxies...")
    extracted_links = []
    
    # Dropped to 1 worker so the logs print perfectly in order
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = executor.map(process_channel, CHANNELS)
        for res in results:
            if res:
                extracted_links.append(res)

    print("Playlist updated successfully! (Debug Mode)")

if __name__ == "__main__":
    update_playlist()
