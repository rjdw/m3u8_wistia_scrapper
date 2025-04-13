import subprocess
import os
from pathlib import Path

# === CONFIGURATION ===
M3U8_LIST_PATH = "m3u8_list.txt"
TARGET_DIR = Path("~/Downloads")
FAILED_LOG = TARGET_DIR / "failed_downloads.txt"
LOG_FILE = TARGET_DIR / "download_log.txt"

# === Ensure target directory exists ===
TARGET_DIR.mkdir(parents=True, exist_ok=True)

# === Load URLs ===
with open(M3U8_LIST_PATH, "r") as f:
    urls = [line.strip() for line in f if line.strip().startswith("http")]

print(f"Found {len(urls)} .m3u8 URLs")

# === Initialize logs ===
FAILED_LOG.write_text("")
LOG_FILE.write_text("")

# === Download each video ===
for i, url in enumerate(urls, start=1):
    filename = TARGET_DIR / f"video_{i}.mp4"
    print(f"[{i}] Downloading: {url} | to file: {filename}")
    LOG_FILE.write_text(f"[{i}] {url}\n")

    # Run ffmpeg
    result = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", url, "-c", "copy", str(filename)],
        capture_output=True,
        text=True
    )

    # Check result
    if result.returncode != 0:
        print(f"❌ Failed to download video {i}")
        with FAILED_LOG.open("a") as f:
            f.write(f"[{i}] {url}\n")
            f.write(result.stderr + "\n\n")
    else:
        print(f"✅ Video {i} downloaded successfully")

print("✅ All done.")
