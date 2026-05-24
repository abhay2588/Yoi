import subprocess

# Put your YouTube Live URL here
YOUTUBE_URL = "https://www.youtube.com/live/wEXiONQFddg"
OUTPUT_FILE = "live.m3u8"

def get_stream_url():
    try:
        # Run yt-dlp to extract the direct m3u8 link
        result = subprocess.run(
            ["yt-dlp", "-g", YOUTUBE_URL],
            capture_output=True,
            text=True,
            check=True
        )
        
        m3u8_url = result.stdout.strip()
        
        if m3u8_url:
            playlist_content = f"#EXTM3U\n#EXTINF:-1, Live Channel\n{m3u8_url}\n"
            with open(OUTPUT_FILE, "w") as f:
                f.write(playlist_content)
            print("Successfully extracted link and updated live.m3u8")
        else:
            print("yt-dlp ran, but returned an empty string.")
            
    except subprocess.CalledProcessError as e:
        print(f"yt-dlp failed with error: {e.stderr}")

if __name__ == "__main__":
    get_stream_url()
