import subprocess
import json
import requests
import os
import concurrent.futures

# The URL to your static Jokr playlist
JOKR_PLAYLIST_URL = "https://raw.githubusercontent.com/abhay2588/jokr/main/yoi"
OUTPUT_FILE = "live.m3u8"

# Fetches both proxies from your GitHub Action environment
PROXY = os.environ.get("PROXY_URL")
BACKUP_PROXY = os.environ.get("BACKUP_PROXY_URL")

# Your YouTube channels
CHANNELS = [
    {"url": "https://www.youtube.com/@aajtak/live", "group": "News", "logo": "", "id": "aajtak"},

    {"url": "https://www.youtube.com/@abpnews/live", "group": "News", "logo": "", "id": "abpnews"},

    {"url": "https://www.youtube.com/@LofiGirl/live", "group": "Music", "logo": "", "id": "lofigirl"},

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

    {"url": "https://www.youtube.com/@WION/live", "group": "News", "logo": "", "id": "WION"},

    {"url": "https://www.youtube.com/@RepublicWorld/live", "group": "News", "logo": "", "id": "republicworld"},

    {"url": "https://www.youtube.com/@cnnnews18/live", "group": "News", "logo": "", "id": "cnnnews18"},

    {"url": "https://www.youtube.com/@Firstpost/live", "group": "News", "logo": "", "id": "Firstpost"},

    {"url": "https://www.youtube.com/@SpongeBobOfficial/live", "group": "Cartoons", "logo": "", "id": "spongebob"},

    {"url": "https://www.youtube.com/@PeppaPigOfficial/live", "group": "Cartoons", "logo": "", "id": "peppapig"},

    {"url": "https://www.youtube.com/@WBKids/live", "group": "Cartoons", "logo": "", "id": "wbkids"},

    {"url": "https://www.youtube.com/@MashaBearHINDi/live", "group": "Cartoons", "logo": "", "id": "MashaBearHINDi"},

    {"url": "https://www.youtube.com/@CartoonitoFrance/live", "group": "Cartoons", "logo": "", "id": "CartoonitoFrance"},

    {"url": "https://www.youtube.com/@NASA/live", "group": "Science & Space", "logo": "", "id": "nasa"},

    {"url": "https://www.youtube.com/@liveiss/live", "group": "Science & Space", "logo": "", "id": "isslive"},

    {"url": "https://www.youtube.com/@SpaceX/live", "group": "Science & Space", "logo": "", "id": "SpaceX"},

    {"url": "https://www.youtube.com/@mrbeananimated/live", "group": "Cartoons", "logo": "", "id": "mrbeananimated"},

    {"url": "https://www.youtube.com/@oddbods/live", "group": "Cartoons", "logo": "", "id": "oddbods"},

    {"url": "https://www.youtube.com/@smurfs/live", "group": "Cartoons", "logo": "", "id": "smurfs"},

    {"url": "https://www.youtube.com/@talkingtom/live", "group": "Cartoons", "logo": "", "id": "talkingtom"},

    {"url": "https://www.youtube.com/@AngryBirds/live", "group": "Cartoons", "logo": "", "id": "AngryBirds"},

    {"url": "https://www.youtube.com/@Sen/live", "group": "Science & Space", "logo": "", "id": "Sen"},

    {"url": "https://www.youtube.com/@dckids/live", "group": "Cartoons", "logo": "", "id": "dckids"},

    {"url": "https://www.youtube.com/@ChillhopMusic/live", "group": "Music", "logo": "", "id": "ChillhopMusic"}

]

# A helper function to build and run the yt-dlp command
def run_extractor(channel_url, proxy_to_use):
    command = ["yt-dlp", "--socket-timeout", "15", "--cookies", "cookies.txt", "--remote-components", "ejs:github", "-J"]
    
    if proxy_to_use:
        command.extend(["--proxy", proxy_to_use])
        
    command.append(channel_url)

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        timeout=20
    )

# The worker function that processes a single channel with Smart Routing
def process_channel(channel):
    print(f"Started: {channel['url']}")
    
    # ATTEMPT 1: Direct Connection (Uses GitHub's infinite free bandwidth)
    try:
        result = run_extractor(channel['url'], None)
    except Exception:
        
        # ATTEMPT 2: Fallback to Webshare Proxy
        print(f"  -> Direct blocked for {channel['id']}. Routing to Webshare...")
        if PROXY:
            try:
                result = run_extractor(channel['url'], PROXY)
            except Exception:
                
                # ATTEMPT 3: Fallback to Backup Proxy (If you added one)
                if BACKUP_PROXY:
                    print(f"  -> Primary proxy failed for {channel['id']}. Trying Backup...")
                    try:
                        result = run_extractor(channel['url'], BACKUP_PROXY)
                    except Exception:
                        print(f"  -> All routes failed: {channel['url']}")
                        return None
                else:
                    print(f"  -> Webshare failed: {channel['url']}")
                    return None
        else:
            return None

    # If any of the 3 routes succeeded, process the JSON data
    try:
        video_data = json.loads(result.stdout.strip())
        channel_name = video_data.get("uploader", "Unknown Channel")
        m3u8_url = video_data.get("manifest_url") or video_data.get("url")
        
        if m3u8_url:
            print(f"  -> Success: {channel_name}")
            return f'#EXTINF:-1 tvg-id="{channel["id"]}" tvg-logo="{channel["logo"]}" group-title="{channel["group"]}", {channel_name}\n{m3u8_url}\n\n'
        else:
            print(f"  -> No manifest: {channel['url']}")
            return None
            
    except json.JSONDecodeError:
        print(f"  -> Failed to parse JSON for {channel['url']}.")
        return None
