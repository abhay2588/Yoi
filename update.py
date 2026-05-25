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

# The worker function that processes a single channel with a fallback
def process_channel(channel):
    print(f"Started: {channel['url']}")
    
    try:
        # Attempt 1: Try with the Primary Proxy
        result = run_extractor(channel['url'], PROXY)
        
    except Exception as e:
        # Attempt 2: If Primary fails, instantly try the Backup
        if BACKUP_PROXY:
            print(f"  -> Primary timeout for {channel['id']}. Trying Backup Proxy...")
            try:
                result = run_extractor(channel['url'], BACKUP_PROXY)
            except Exception as backup_e:
                print(f"  -> Backup also failed: {channel['url']}")
                return None
        else:
            print(f"  -> Failed: {channel['url']}")
            return None

    # If either proxy succeeded, process the JSON data
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
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
