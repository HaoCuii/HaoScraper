import json
import requests
import os

def load_videos(filename="tiktok.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def sort_by_views(videos, top_n=100):
    sorted_videos = sorted(videos, key=lambda x: x.get("views") or 0, reverse=True)
    return sorted_videos[:top_n]

def download_video(video_url, save_path):
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False

def download_top_videos(videos):
    os.makedirs("downloads", exist_ok=True)

    for i, video in enumerate(videos, 1):
        video_id = video.get("id")
        author = video.get("author", "unknown")
        views = video.get("views", 0)

        print(f"[{i}/{len(videos)}] Downloading video by {author} ({views:,} views)")

        video_url = f"https://www.tiktok.com/@{author}/video/{video_id}"

        filename = f"downloads/{i}_{video_id}.mp4"

        try:
            success = download_video(video_url, filename)
            if success:
                print(f"    Saved: {filename}")
            else:
                print(f"    Failed to download")
        except Exception as e:
            print(f"    Error: {e}")

if __name__ == "__main__":
    videos = load_videos()

    print(f"Loaded {len(videos)} videos")

    top_100 = sort_by_views(videos, top_n=100)

    print(f"\nTop 100 most viewed videos:")
    for i, v in enumerate(top_100[:10], 1):
        print(f"  {i}. {v.get('views', 0):,} views - {v.get('desc', '')[:50]}")

    proceed = input(f"\nDownload top {len(top_100)} videos? (y/n): ")

    if proceed.lower() == 'y':
        download_top_videos(top_100)
        print("\nDone!")
