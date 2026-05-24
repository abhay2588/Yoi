import requests
import re

# Replace with your target channel
YOUTUBE_URL = "https://www.youtube.com/@aajtak/live" 
OUTPUT_FILE = "live.m3u8"

def get_m3u8():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(YOUTUBE_URL, headers=headers)
        response.raise_for_status()
        
        match = re.search(r'"hlsManifestUrl":"(.*?)"', response.text)
        if match:
            m3u8_url = match.group(1).replace('\/', '/')
            playlist_content = f"#EXTM3U\n#EXTINF:-1, Live Channel\n{m3u8_url}\n"
            
            with open(OUTPUT_FILE, "w") as f:
                f.write(playlist_content)
                
            print(f"Successfully updated {OUTPUT_FILE}")
        else:
            print("Could not find hlsManifestUrl. Make sure the channel is live.")
            
    except Exception as e:
        print(f"Error fetching stream: {e}")

if __name__ == "__main__":
    get_m3u8()
