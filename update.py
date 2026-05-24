import subprocess
import json

# Add as many YouTube Live URLs as you want to this list. 
# Make sure each URL is in quotes and separated by a comma.
YOUTUBE_URLS = [
    "https://www.youtube.com/@aajtak/live",
    "https://www.youtube.com/@abpnews/live",
    "https://www.youtube.com/@LofiGirl/live",
    "https://www.youtube.com/@zeenews/live",
    "https://www.youtube.com/@news18india/live",
    "https://www.youtube.com/@bharat24/live",
    "https://www.youtube.com/@indiatv/live",
    "https://www.youtube.com/@bbchindi/live",
    "https://www.youtube.com/@republicbharat/live",
]

OUTPUT_FILE = "live.m3u8"

def update_playlist():
    # Step 1: Create a fresh file and write the standard M3U header
    with open(OUTPUT_FILE, "w") as f:
        f.write("#EXTM3U\n")

    # Step 2: Loop through every URL in your list
    for url in YOUTUBE_URLS:
        print(f"\nProcessing: {url}")
        try:
            result = subprocess.run(
                ["yt-dlp", "--cookies", "cookies.txt", "--remote-components", "ejs:github", "-J", url],
                capture_output=True,
                text=True,
                check=True
            )
            
            video_data = json.loads(result.stdout.strip())
            
            channel_name = video_data.get("uploader", "Unknown Channel")
            m3u8_url = video_data.get("manifest_url") or video_data.get("url")
            
            if m3u8_url:
                playlist_content = f"#EXTINF:-1, {channel_name}\n{m3u8_url}\n"
                
                # Step 3: Append (using 'a') the new channel to the file without deleting the others
                with open(OUTPUT_FILE, "a") as f:
                    f.write(playlist_content)
                    
                print(f"  -> Successfully added {channel_name}")
            else:
                print(f"  -> Could not extract manifest for {url}.")
                
        except subprocess.CalledProcessError as e:
            # If one channel is offline or errors out, it prints the error and moves to the next one
            print(f"  -> Failed to process {url}. Skipping... Error: {e.stderr.strip().splitlines()[-1] if e.stderr else 'Unknown'}")
        except json.JSONDecodeError:
            print(f"  -> Failed to parse JSON for {url}.")

if __name__ == "__main__":
    update_playlist()
