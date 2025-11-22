import asyncio
import os
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright

class TikTokScraper:
    def __init__(self):
        self.videos = []
        self.unique_ids = set()
        self.target_limit = 0

    async def handle_response(self, response):
        if len(self.videos) >= self.target_limit:
            return

        if ("item_list" in response.url or "search/item" in response.url) and response.status == 200:
            try:
                data = await response.json()
                batch = data.get("itemList", []) or data.get("aweme_list", [])

                if batch:
                    new_count = 0
                    for video in batch:
                        if len(self.videos) >= self.target_limit:
                            break

                        vid_id = video.get("id")
                        if vid_id not in self.unique_ids:
                            self.unique_ids.add(vid_id)

                            raw_time = video.get("createTime")
                            try:
                                readable_date = datetime.fromtimestamp(int(raw_time)).strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                readable_date = "Unknown"

                            stats = video.get("stats", {}) or video.get("statistics", {})
                            author = video.get("author", {})

                            clean_vid = {
                                "id": vid_id,
                                "desc": video.get("desc", ""),
                                "create_time": readable_date,
                                "timestamp": raw_time,
                                "likes": stats.get("diggCount") or stats.get("digg_count"),
                                "views": stats.get("playCount") or stats.get("play_count"),
                                "author": author.get("nickname", "") if isinstance(author, dict) else ""
                            }

                            self.videos.append(clean_vid)
                            new_count += 1

                    if new_count > 0:
                        print(f"Captured {new_count} new videos. Progress: {len(self.videos)}/{self.target_limit}")
            except:
                pass

    async def scrape_single_hashtag(self, page, hashtag, per_hashtag_limit=200):
        print(f"\nScraping #{hashtag}...")
        initial_count = len(self.videos)

        await page.goto(f"https://www.tiktok.com/tag/{hashtag}")
        await page.wait_for_timeout(3000)

        no_new_data = 0
        last_count = len(self.videos)
        iterations = 0
        max_iterations = 50

        while (len(self.videos) - initial_count) < per_hashtag_limit and iterations < max_iterations:
            iterations += 1

            await page.keyboard.press("End")
            await page.wait_for_timeout(2000)

            if len(self.videos) == last_count:
                no_new_data += 1
                await page.mouse.wheel(0, -100)
                await page.wait_for_timeout(500)
                await page.mouse.wheel(0, 100)
            else:
                no_new_data = 0

            last_count = len(self.videos)

            if no_new_data > 8:
                print(f"Reached end of #{hashtag} feed")
                break

        videos_from_this_tag = len(self.videos) - initial_count
        print(f"Got {videos_from_this_tag} unique videos from #{hashtag}")
        return videos_from_this_tag

    async def scrape_multiple(self, hashtags, total_limit=500):
        if not os.path.exists("session.json"):
            print("session.json file not found.")
            return

        self.target_limit = total_limit
        start_time = time.time()

        print(f"Starting multi-hashtag scrape")
        print(f"Hashtags: {', '.join(['#' + h for h in hashtags])}")
        print(f"Target: {total_limit} unique videos")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )

            context = await browser.new_context(
                storage_state="session.json",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            page = await context.new_page()
            page.on("response", self.handle_response)

            per_hashtag_limit = total_limit // len(hashtags)

            for hashtag in hashtags:
                if len(self.videos) >= total_limit:
                    print(f"\nReached total limit of {total_limit} videos")
                    break

                await self.scrape_single_hashtag(page, hashtag, per_hashtag_limit)
                await page.wait_for_timeout(2000)

            await browser.close()

        end_time = time.time()
        elapsed = end_time - start_time

        filename = "tiktok.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.videos, f, indent=4, ensure_ascii=False)

        print("\n" + "="*40)
        print(f"Scrape complete")
        print(f"Total unique videos: {len(self.videos)}")
        print(f"Hashtags scraped: {len(hashtags)}")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Saved: {filename}")
        print("="*40)

        return filename

if __name__ == "__main__":
    scraper = TikTokScraper()

    hashtags = [
        "ugc",
        "ugccreator",
        "ugcbeginner",
        "ugcproducts",
        "ugccontentcreator"
    ]

    asyncio.run(scraper.scrape_multiple(hashtags, total_limit=500))