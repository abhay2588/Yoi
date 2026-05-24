import subprocess
import json
import requests

# The URL to your static Jokr playlist
JOKR_PLAYLIST_URL = "https://raw.githubusercontent.com/abhay2588/jokr/main/yoi"
OUTPUT_FILE = "live.m3u8"

# Your YouTube channels
CHANNELS = [
    {
        "url": "https://www.youtube.com/@aajtak/live",
        "group": "News",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Aaj_Tak_logo.png",
        "id": "aajtak"
    },
    {
        "url": "https://www.youtube.com/@abpnews/live",
        "group": "News",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/2/28/ABP_News_logo.png",
        "id": "abpnews"
    },
    {
        "url": "https://www.youtube.com/@LofiGirl/live",
        "group": "Music",
        "logo": "https://upload.wikimedia.org/wikipedia/en/2/28/Lofi_Girl_logo.jpg",
        "id": "lofigirl"
    },
    {
        "url": "https://www.youtube.com/@zeenews/live",
        "group": "News",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/4/41/Zee_News_2022.svg",
        "id": "zeenews"
    },
    {
        "url": "https://www.youtube.com/@timesnownavbharat/live",
        "group": "News",
        "logo": "",
        "id": "timesnownavbharat"
    },
    {
        "url": "https://www.youtube.com/@TV9Bharatvarsh/live",
        "group": "News",
        "logo": "",
        "id": "TV9Bharatvarsh"
    },
    {
        "url": "https://www.youtube.com/@ndtvindia/live",
        "group": "News",
        "logo": "",
        "id": "ndtvindia"
    },
    {
        "url": "https://www.youtube.com/@news18india/live",
        "group": "News",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/3/30/News18_India_logo.svg",
        "id": "news18india"
    },
    {
        "url": "https://www.youtube.com/@nmfnews/live",
        "group": "News",
        "logo": "",
        "id": "nmfnews"
    },
    {
        "url": "https://www.youtube.com/@bharat24/live",
        "group": "News",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Bharat24express.png",
        "id": "bharat24"
    },
    {
        "url": "https://www.youtube.com/@indiatv/live",
        "group": "News",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/2/2b/India_TV_logo.svg",
        "id": "indiatv"
    },
    {
        "url": "https://www.youtube.com/@bbchindi/live",
        "group": "News",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/f/ff/BBC_News.svg",
        "id": "bbchindi"
    },
    {
        "url": "https://www.youtube.com/@DDnews/live",
        "group": "News",
        "logo": "",
        "id": "DDnews"
    },
    {
        "url": "https://www.youtube.com/@republicbharat/live",
        "group": "News",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/0/07/Republic_Bharat_Logo.png",
        "id": "republicbharat"
    }
]

def update_playlist():
    print(f"Fetching base playlist from {JOKR_PLAYLIST_URL}...")
    
    try:
        # Step 1: Download your Jokr playlist
        response = requests.get(JOKR_PLAYLIST_URL)
        response.raise_for_status()
        base_content = response.text
    except Exception as e:
        print(f"Failed to fetch Jokr playlist: {e}")
        base_content = "#EXTM3U\n\n"

    # Step 2: Save the Jokr content into our output file first
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Ensure it has the M3U header if it doesn't already
        if not base_content.strip().startswith("#EXTM3U"):
            f.write("#EXTM3U\n\n")
        f.write(base_content)
        # Add a gap before appending YouTube links
        if not base_content.endswith("\n"):
            f.write("\n\n")
    
    print("Base playlist saved. Now extracting YouTube links...")

    # Step 3: Append the fresh YouTube links to the bottom
    for channel in CHANNELS:
        print(f"\nProcessing: {channel['url']}")
        try:
            result = subprocess.run(
                ["yt-dlp", "--cookies", "cookies.txt", "--remote-components", "ejs:github", "-J", channel['url']],
                capture_output=True,
                text=True,
                check=True
            )
            
            video_data = json.loads(result.stdout.strip())
            channel_name = video_data.get("uploader", "Unknown Channel")
            m3u8_url = video_data.get("manifest_url") or video_data.get("url")
            
            if m3u8_url:
                playlist_content = f'#EXTINF:-1 tvg-id="{channel["id"]}" tvg-logo="{channel["logo"]}" group-title="{channel["group"]}", {channel_name}\n{m3u8_url}\n\n'
                
                # Append 'a' to add to the bottom of the Jokr list
                with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                    f.write(playlist_content)
                    
                print(f"  -> Successfully added {channel_name}")
            else:
                print(f"  -> Could not extract manifest for {channel['url']}.")
                
        except subprocess.CalledProcessError:
            print(f"  -> Failed to process {channel['url']}. Skipping...")
        except json.JSONDecodeError:
            print(f"  -> Failed to parse JSON for {channel['url']}.")

if __name__ == "__main__":
    update_playlist()
