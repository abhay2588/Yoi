import yt_dlp
import requests
import os
import concurrent.futures

JOKR_PLAYLIST_URL = "https://raw.githubusercontent.com/abhay2588/jokr/main/yoi"
OUTPUT_FILE = "live.m3u8"

# --- THE DATA-SAVING PROXY WATERFALL ---
PROXIES = [None] 
for i in range(1, 6):
    p = os.environ.get(f"PROXY_{i}")
    if p:
        PROXIES.append(p)

# --- 2-CHANNEL TEST SETUP ---
CHANNELS = [
    {"url": "https://www.youtube.com/@aajtak/live", "group": "News", "logo": "", "id": "aajtak"},
    {"url": "https://www.youtube.com/@abpnews/live", "group": "News", "logo": "", "id": "abpnews"}
]

# --- SMART CACHE ENGINE ---
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
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(
            url,
            headers=headers,
            stream=True,
            allow_redirects=True,
            timeout=5
        )
        alive = r.status_code == 200
        r.close()
        return alive
    except Exception:
        return False

# --- NATIVE PYTHON EXTRACTOR ---
def run_extractor(channel_url, proxy_to_use):
    ydl_opts = {
        "cookiefile": "cookies.txt",
        
        # Keep verbose on to catch the exact cookie/client conflict
        "verbose": True,
        "quiet": False,
        "no_warnings": False,
        "simulate": True,

        "extractor_args": {
            "youtube": {
                # This perfectly mimics the CLI argument that worked in RDP
                "client": ["tv"] 
            }
        },

        "http_headers": {
            # Matching the RDP Xbox signature to pair with the TV client
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox Series X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edge/44.18363.8131"
        }
    }

    if proxy_to_use:
        ydl_opts["proxy"] = proxy_to_use

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(
                channel_url,
                download=False
            )

    except Exception as e:
        print(f"\n[!] Extractor failed: {e}\n")
        return None

def process_channel(channel):
    print(f"\n========================================")
    print(f"Started: {channel['id']}")
    print(f"========================================")

    cached_data = EXISTING_CACHE.get(channel["id"])

    if cached_data:
        if is_link_alive(cached_data["url"]):
            print(f"  -> Cache hit: {channel['id']} 🟢")
            return cached_data["block"]

    result = None

    for index, proxy in enumerate(PROXIES):
        try:
            if proxy is None:
                print(f"  -> Direct connection: {channel['id']}")
            else:
                print(f"  -> Proxy {index}: {channel['id']}")

            result = run_extractor(
                channel["url"],
                proxy
            )

            if result:
                break

        except Exception:
            result = None

    if not result:
        print(f"  -> Failed: {channel['id']} 🔴")
        return None

    try:
        channel_name = (
            result.get("uploader")
            or result.get("channel")
            or channel["id"]
        )

        m3u8_url = (
            result.get("manifest_url")
            or result.get("url")
        )

        if not m3u8_url:
            print(f"  -> No stream URL: {channel['id']} 🔴")
            return None

        print(f"  -> Success: {channel_name} 🟢")

        return (
            f'#EXTINF:-1 '
            f'tvg-id="{channel["id"]}" '
            f'tvg-logo="{channel["logo"]}" '
            f'group-title="{channel["group"]}", '
            f'{channel_name}\n'
            f'{m3u8_url}\n\n'
        )

    except Exception:
        return None

def update_playlist():
    print(f"Fetching base playlist from {JOKR_PLAYLIST_URL}...")
    try:
        response = requests.get(JOKR_PLAYLIST_URL)
        response.raise_for_status()
        base_content = response.text
    except Exception:
        base_content = "#EXTM3U\n\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        if not base_content.strip().startswith("#EXTM3U"):
            f.write("#EXTM3U\n\n")
        f.write(base_content)
        if not base_content.endswith("\n"):
            f.write("\n\n")
    
    print(f"Spawning Smart Extractors for Test Run...")
    extracted_links = []
    
    # Single worker to keep the verbose logs completely isolated
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = executor.map(process_channel, CHANNELS)
        for res in results:
            if res:
                extracted_links.append(res)

    print("\nExtraction complete. Writing to file...")
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for link in extracted_links:
            f.write(link)
    print("Playlist updated successfully!")

if __name__ == "__main__":
    update_playlist()
