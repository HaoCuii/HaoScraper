import asyncio
from playwright.async_api import async_playwright

async def create_session(hashtag):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})

        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page = await context.new_page()
        await page.goto(f"https://www.tiktok.com/tag/{hashtag}", timeout=60000)

        try:
            print("Waiting for content to load. Solve any captchas if needed...")
            await page.wait_for_selector("div[data-e2e='challenge-item']", timeout=120000)
            print("Content loaded successfully")
        except:
            print("Timed out waiting for content")
            await browser.close()
            return

        await context.storage_state(path="session.json")
        print("Session saved. You can close this window.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(create_session("ugc"))