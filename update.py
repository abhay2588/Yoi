import subprocess
import json
import requests
import os
import concurrent.futures

# The URL to your static Jokr playlist
JOKR_PLAYLIST_URL = "https://raw.githubusercontent.com/abhay2588/jokr/main/yoi"
OUTPUT_FILE = "live.m3u8"

# Fetches the local proxy port established by Xray in the workflow
PROXY = os.environ.get("PROXY_URL")

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
    {"url": "https://www.youtube.com/@MashaBearEN/live", "group": "Cartoons", "logo": "", "id": "mashabear"},
    {"url": "https://www.youtube.com/@BoomerangUK/live", "group": "Cartoons", "logo": "", "id": "tomandjerry"},
    {"url": "https://www.youtube.com/@NASA/live", "group": "Science & Space", "logo": "", "id": "nasa"},
    {"url": "https://www.youtube.com/@liveiss/live", "group": "Science & Space", "logo": "", "id": "isslive"},
    {"url": "https://www.youtube.com/@SpaceX/live", "group": "Science & Space", "logo": "", "id": "SpaceX"},
    {"url": "https://www.youtube.com/@EuropeanSpaceAgency/live", "group": "Science & Space", "logo": "", "id": "EuropeanSpaceAgency"},
    {"url": "https://www.youtube.com/@ExploreAfrica/live", "group": "Nature", "logo": "", "id": "exploreafrica"},
    {"url": "https://www.youtube.com/@MontereyBayAquarium/live", "group": "Nature", "logo": "", "id": "montereybay"},
    {"url": "https://www.youtube.com/@earthcam/live", "group": "Nature", "logo": "", "id": "earthcam"},
    {"url": "https://www.youtube.com/@explorebears/live", "group": "Nature", "logo": "", "id": "explorebears"},
    {"url": "https://www.youtube.com/@ExploreBirds/live", "group": "Nature", "logo": "", "id": "ExploreBirds"},
    {"url": "https://www.youtube.com/@ExploreLiveNatureCams/live", "group": "Nature", "logo": "", "id": "ExploreLiveNatureCams"},
    {"url": "https://www.youtube.com/@ChillhopMusic/live", "group": "Music", "logo": "", "id": "ChillhopMusic"}
]

# This is the worker function that processes a single channel
def process_channel(channel):
    print(f"Started: {channel['url']}")
    try:
        command = ["yt-dlp", "--socket-timeout", "45", "--cookies", "cookies.txt", "--remote-components", "ejs:github", "-J"]
        
        if PROXY:
            command.extend(["--proxy", PROXY])
            
        command.append(channel['url'])

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        
        video_data = json.loads(result.stdout.strip())
        channel_name = video_data.get("uploader", "Unknown Channel")
        m3u8_url = video_data.get("manifest_url") or video_data.get("url")
        
        if m3u8_url:
            print(f"  -> Success: {channel_name}")
            return f'#EXTINF:-1 tvg-id="{channel["id"]}" tvg-logo="{channel["logo"]}" group-title="{channel["group"]}", {channel_name}\n{m3u8_url}\n\n'
        else:
            print(f"  -> No manifest: {channel['url']}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"  -> Timeout: {channel['url']}")
        return None
    except Exception as e:
        print(f"  -> Failed: {channel['url']}")
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

    # Here is the magic: We run up to 10 channels concurrently
    extracted_links = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # executor.map keeps the channels in the exact order of your list
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
