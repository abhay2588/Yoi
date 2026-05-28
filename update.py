import subprocess
import json
import requests
import os
import concurrent.futures

# The URL to your static Jokr playlist
JOKR_PLAYLIST_URL = "https://raw.githubusercontent.com/abhay2588/jokr/main/yoi"
OUTPUT_FILE = "live.m3u8"

# Fetches proxies from your GitHub Action environment
PROXY = os.environ.get("PROXY_URL")               # Layer 1: Indian VMESS
WARP_PROXY = os.environ.get("WARP_PROXY_URL")     # Layer 2: Cloudflare WARP

# Your YouTube channels
CHANNELS = [
    # --- NEWS (HINDI & REGIONAL) ---
    {"url": "https://www.youtube.com/@aajtak/live", "group": "News", "logo": "", "id": "aajtak"},
    {"url": "https://www.youtube.com/@abpnews/live", "group": "News", "logo": "", "id": "abpnews"},
    {"url": "https://www.youtube.com/@zeenews/live", "group": "News", "logo": "", "id": "zeenews"},
    {"url": "https://www.youtube.com/@timesnownavbharat/live", "group": "News", "logo": "", "id": "timesnownavbharat"},
    {"url": "https://www.youtube.com/@TV9Bharatvarsh/live", "group": "News", "logo": "", "id": "TV9Bharatvarsh"},
    {"url": "https://www.youtube.com/@ndtvindia/live", "group": "News", "logo": "", "id": "ndtvindia"},
    {"url": "https://www.youtube.com/@news18india/live", "group": "News", "logo": "", "id": "news18india"},
    {"url": "https://www.youtube.com/@nmfnews/live", "group": "News", "logo": "", "id": "nmfnews"},
    {"url": "https://www.youtube.com/@bharat24/live", "group": "News", "logo": "", "id": "bharat24"},
    {"url": "https://www.youtube.com/@indiatv/live", "group": "News", "logo": "", "id": "indiatv"},
    {"url": "https://www.youtube.com/@bbchindi/live", "group": "News", "logo": "", "id": "bbchindi"},
    {"url": "https://www.youtube.com/@DDnews/live", "group": "News", "logo": "", "id": "DDnews"},
    {"url": "https://www.youtube.com/@republicbharat/live", "group": "News", "logo": "", "id": "republicbharat"},
    {"url": "https://www.youtube.com/@news24/live", "group": "News", "logo": "", "id": "news24"}, 
    {"url": "https://www.youtube.com/@TimesNow/live", "group": "News", "logo": "", "id": "TimesNow"}, 
    {"url": "https://www.youtube.com/@TheLallantop/live", "group": "News", "logo": "", "id": "TheLallantop"},  
    {"url": "https://www.youtube.com/@indiatoday/live", "group": "News", "logo": "", "id": "indiatoday"}, 
    {"url": "https://www.youtube.com/@ndtv/live", "group": "News", "logo": "", "id": "ndtv"},
    {"url": "https://www.youtube.com/@RepublicWorld/live", "group": "News", "logo": "", "id": "republicworld"},
    {"url": "https://www.youtube.com/@hindustantimes/live", "group": "News", "logo": "", "id": "hindustantimes"},
    {"url": "https://www.youtube.com/@NewsX/live", "group": "News", "logo": "", "id": "newsx"},
    {"url": "https://www.youtube.com/@IBC24/live", "group": "News", "logo": "", "id": "ibc24"},
    {"url": "https://www.youtube.com/@ZeeMPCG/live", "group": "News", "logo": "", "id": "zeempcg"},
    {"url": "https://www.youtube.com/@News18MPCG/live", "group": "News", "logo": "", "id": "news18mpcg"},

    # --- NEWS (INTERNATIONAL) ---
    {"url": "https://www.youtube.com/@WION/live", "group": "News", "logo": "", "id": "WION"},
    {"url": "https://www.youtube.com/@cnnnews18/live", "group": "News", "logo": "", "id": "cnnnews18"},
    {"url": "https://www.youtube.com/@Firstpost/live", "group": "News", "logo": "", "id": "Firstpost"},
    {"url": "https://www.youtube.com/@ABCNews/live", "group": "News", "logo": "", "id": "abcnews"},
    {"url": "https://www.youtube.com/@livenowfox/live", "group": "News", "logo": "", "id": "livenowfox"},

    # --- CARTOONS ---
    {"url": "https://www.youtube.com/@SpongeBobOfficial/live", "group": "Cartoons", "logo": "", "id": "spongebob"},
    {"url": "https://www.youtube.com/@PeppaPigOfficial/live", "group": "Cartoons", "logo": "", "id": "peppapig"},
    {"url": "https://www.youtube.com/@WBKids/live", "group": "Cartoons", "logo": "", "id": "wbkids"},
    {"url": "https://www.youtube.com/@MashaBearHINDi/live", "group": "Cartoons", "logo": "", "id": "MashaBearHINDi"},
    {"url": "https://www.youtube.com/@CartoonitoFrance/live", "group": "Cartoons", "logo": "", "id": "CartoonitoFrance"},
    {"url": "https://www.youtube.com/@mrbeananimated/live", "group": "Cartoons", "logo": "", "id": "mrbeananimated"},
    {"url": "https://www.youtube.com/@oddbods/live", "group": "Cartoons", "logo": "", "id": "oddbods"},
    {"url": "https://www.youtube.com/@smurfs/live", "group": "Cartoons", "logo": "", "id": "smurfs"},
    {"url": "https://www.youtube.com/@TalkingFriends/live", "group": "Cartoons", "logo": "", "id": "talkingtom"},
    {"url": "https://www.youtube.com/@AngryBirds/live", "group": "Cartoons", "logo": "", "id": "AngryBirds"},
    {"url": "https://www.youtube.com/@dckids/live", "group": "Cartoons", "logo": "", "id": "dckids"},
    {"url": "https://www.youtube.com/@ShauntheSheep/live", "group": "Cartoons", "logo": "", "id": "shaunthesheep"},
    {"url": "https://www.youtube.com/@MorphleTV/live", "group": "Cartoons", "logo": "", "id": "morphle"},
    {"url": "https://www.youtube.com/@Teletubbies/live", "group": "Cartoons", "logo": "", "id": "teletubbies"},

    # --- SCIENCE & SPACE ---
    {"url": "https://www.youtube.com/@NASA/live", "group": "Science & Space", "logo": "", "id": "nasa"},
    {"url": "https://www.youtube.com/@SpaceX/live", "group": "Science & Space", "logo": "", "id": "SpaceX"},
    {"url": "https://www.youtube.com/@Sen/live", "group": "Science & Space", "logo": "", "id": "Sen"},

    # --- MUSIC ---
    {"url": "https://www.youtube.com/@LofiGirl/live", "group": "Music", "logo": "", "id": "lofigirl"},
    {"url": "https://www.youtube.com/@ChillhopMusic/live", "group": "Music", "logo": "", "id": "ChillhopMusic"}
]

def run_extractor(channel_url, proxy_to_use):
    command = [
        "yt-dlp", 
        "--socket-timeout", "7", 
        "--cookies", "cookies.txt", 
        "--remote-components", "ejs:github", 
        # NEW MAGIC FIX: Spoof iOS and Android TV clients to bypass IP blocking
        "--extractor-args", "youtube:client=ios,android", 
        "-J"
    ]
    if proxy_to_use:
        command.extend(["--proxy", proxy_to_use])
    command.append(channel_url)
    return subprocess.run(command, capture_output=True, text=True, check=True, timeout=12)

def process_channel(channel):
    print(f"Started: {channel['url']}")
    result = None
    
    # --- DIRECT BYPASS FOR GLOBAL CHANNELS ---
    if channel['group'] in ["Cartoons", "Science & Space", "Music"]:
        try:
            result = run_extractor(channel['url'], None)
        except Exception:
            print(f"  -> Direct failed for {channel['id']}. Falling back to proxy pipeline...")

    # --- LAYER 1: INDIAN VMESS NODE ---
    if not result and PROXY:
        try:
            result = run_extractor(channel['url'], PROXY)
        except Exception:
            print(f"  -> VMESS failed for {channel['id']}. Routing to Cloudflare WARP...")

    # --- LAYER 2: CLOUDFLARE WARP ---
    if not result and WARP_PROXY:
        try:
            result = run_extractor(channel['url'], WARP_PROXY)
        except Exception:
            print(f"  -> WARP failed for {channel['id']}. Trying Direct as last resort...")
            
    # --- LAYER 3: FINAL CATCH-ALL (Direct) ---
    if not result:
        try:
            result = run_extractor(channel['url'], None)
        except Exception:
            print(f"  -> FATAL: All routes failed for: {channel['url']}")
            return None

    try:
        video_data = json.loads(result.stdout.strip())
        channel_name = video_data.get("uploader", "Unknown Channel")
        m3u8_url = video_data.get("manifest_url") or video_data.get("url")
        if m3u8_url:
            print(f"  -> Success: {channel_name}")
            return f'#EXTINF:-1 tvg-id="{channel["id"]}" tvg-logo="{channel["logo"]}" group-title="{channel["group"]}", {channel_name}\n{m3u8_url}\n\n'
        else:
            return None
    except json.JSONDecodeError:
        return None

def update_playlist():
    print(f"Fetching base playlist from {JOKR_PLAYLIST_URL}...")
    try:
        response = requests.get(JOKR_PLAYLIST_URL)
        response.raise_for_status()
        base_content = response.text
    except Exception as e:
        print(f"Failed to fetch Jokr playlist: {e}")
        base_content = "#EXTM3U\n\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        if not base_content.strip().startswith("#EXTM3U"):
            f.write("#EXTM3U\n\n")
        f.write(base_content)
        if not base_content.endswith("\n"):
            f.write("\n\n")
    
    print("Base playlist saved. Spawning multi-thread extractors...")

    extracted_links = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(process_channel, CHANNELS)
        for res in results:
            if res:
                extracted_links.append(res)

    print("Extraction complete. Writing to file...")
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for link in extracted_links:
            f.write(link)
    print("Playlist updated successfully!")

if __name__ == "__main__":
    update_playlist()            
