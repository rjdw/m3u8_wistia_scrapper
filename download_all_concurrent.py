import subprocess
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIGURATION ===
M3U8_LIST_PATH = "m3u8_list.txt"
TARGET_DIR = Path("~/Downloads")
FAILED_LOG = TARGET_DIR / "failed_downloads.txt"
LOG_FILE = TARGET_DIR / "download_log.txt"
MAX_WORKERS = 2  # <== Number of videos to download in parallel

# === Ensure target directory exists ===
TARGET_DIR.mkdir(parents=True, exist_ok=True)

# === Load URLs ===
with open(M3U8_LIST_PATH, "r") as f:
    urls = [line.strip() for line in f if line.strip().startswith("http")]

print(f"Found {len(urls)} .m3u8 URLs")

# === Clear old logs ===
FAILED_LOG.write_text("")
LOG_FILE.write_text("")

# === Download function ===
def download_video(i, url):
    filename = TARGET_DIR / f"video_{i}.mp4"
    log_line = f"[{i}] Downloading: {url} → {filename}\n"

    with LOG_FILE.open("a") as logf:
        logf.write(log_line)

    result = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", url, "-c", "copy", str(filename)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        error_msg = f"❌ Failed to download [{i}]: {url}\n{result.stderr}\n\n"
        with FAILED_LOG.open("a") as f:
            f.write(error_msg)
        return f"❌ [{i}] Failed"
    else:
        return f"✅ [{i}] Downloaded"

# === ThreadPoolExecutor to run N in parallel ===
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(download_video, i + 1, url) for i, url in enumerate(urls)]

    for future in as_completed(futures):
        print(future.result())

print("✅ All downloads attempted.")
