#!/bin/bash

# Directory where videos will be saved
# Change to your specified download directory
TARGET_DIR="~/Downloads"

# File with one m3u8 URL per line
URL_LIST="m3u8_list.txt"

# Check if ffmpeg is available
if ! command -v ffmpeg &> /dev/null; then
  echo "❌ ffmpeg not found. Please install it with 'brew install ffmpeg'"
  exit 1
fi

# Check if file exists
if [ ! -f "$URL_LIST" ]; then
  echo "❌ URL list file '$URL_LIST' not found."
  exit 1
fi

# Download each video
# Change for your specified download filename
i=1
while IFS= read -r url; do
  if [[ -z "$url" ]]; then
    continue
  fi
  filename="video_$i.mp4"
  echo "Downloading $url to $TARGET_DIR/$filename"
  ffmpeg -i "$url" -c copy "$TARGET_DIR/$filename"

  # for overwriting if error
  # ffmpeg -y -i "$url" -c copy "$TARGET_DIR/$filename"

  ((i++))
done < "$URL_LIST"

echo "✅ Done downloading all videos!"
