# Wistia m3u8 Video Scrapper

Downloading streamed or embedded videos on a Wistia-hosted platform  
Or honestly any platform with some minimal edits

## Setup and Usage Instructions

1. `git clone git@github.com:rjdw/m3u8_wistia_scrapper.git`
2. `cd m3u8_wistia_scrapper`
3. `python -m venv venv` and `source ./venv/bin/activate`
4. `pip install -r requirements.txt`
5. Install ffmpeg
    - [ffmpeg homepage](https://www.ffmpeg.org/)
    - check CLI tool with `ffmpeg --version`
6. `playwright install`

### Usage

1. `python append_m3u8_urls.py "{TARGET_URL}"`
    - This generates `m3u8_list.txt` file
    - Generated file from web scrapper contains all streamed and embedded
    video urls from Wistia platform.
    - Easy to edit this to other platforms, just look at code.
2. `python download_all_concurrent.py`
    - Goes through generated list and downloads them concurrently.
    - WILL OVERWRITE SAME NAME FILES (files named `video_{i}.mp4` for i-th video)
    - Edit `MAX_WORKERS` for more threads.
    - Edit download TARGET_DIR and filename for specifics
3. Extra:
    - `download_all_videos.sh` for bash script
        - might need `chmod +x download_all_videos.sh`
    - `download_all_videos.py` for non-concurrent Python script if your computer is potato or you dislike speed.
        
