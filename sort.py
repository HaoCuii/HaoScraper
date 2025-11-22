import json
import os
import yt_dlp

def load_videos(filename="tiktok.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def sort_by_views(videos, top_n=100):
    sorted_videos = sorted(videos, key=lambda x: x.get("views") or 0, reverse=True)
    return sorted_videos[:top_n]

def download_video(video_id, output_path):
    video_url = f"https://www.tiktok.com/@placeholder/video/{video_id}"

    ydl_opts = {
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return True
    except:
        return False

def download_top_videos(videos):
    os.makedirs("downloads", exist_ok=True)

    for i, video in enumerate(videos, 1):
        video_id = video.get("id")
        author = video.get("author", "unknown")
        views = video.get("views", 0)

        print(f"[{i}/{len(videos)}] Downloading video by {author} ({views:,} views)")

        output_path = f"downloads/{i}_{video_id}.mp4"

        try:
            success = download_video(video_id, output_path)
            if success:
                print(f"Saved: {output_path}")
            else:
                print(f"Failed to download")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    videos = load_videos()

    print(f"Loaded {len(videos)} videos")

    top_100 = sort_by_views(videos, top_n=100)

    for i, v in enumerate(top_100[:10], 1):
        print(f"  {i}. {v.get('views', 0):,} views - {v.get('desc', '')[:50]}")

    sorted_output = []
    for v in top_100:
        sorted_output.append({
            "views": v.get("views", 0),
            "description": v.get("desc", ""),
            "author": v.get("author", ""),
            "id": v.get("id", "")
        })

    with open("sorted_videos.json", "w", encoding="utf-8") as f:
        json.dump(sorted_output, f, indent=4, ensure_ascii=False)

    print(f"\nSaved sorted list to sorted_videos.json")

    proceed = input(f"\nDownload top {len(top_100)} videos? (y/n): ")

    if proceed.lower() == 'y':
        download_top_videos(top_100)
        print("\nDone!")
