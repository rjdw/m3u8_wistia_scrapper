import asyncio
import re
import sys
from playwright.async_api import async_playwright

# CHANGE ME if you want a different output location
M3U8_LIST_PATH = "m3u8_list.txt"

# Change to true if necessary
NEEDS_LOGIN = False
# Your login credentials
EMAIL = ""
PASSWORD = ""
LOGIN_URL = ""

async def run(target_url):
    found_urls = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)

        # Spoofing 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            java_script_enabled=True,
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        if (NEEDS_LOGIN):
            print("Logging in...")
            await page.goto(LOGIN_URL, wait_until="load")

            await page.fill('input[name="email"]', EMAIL)
            await page.fill('input[name="password"]', PASSWORD)
            await page.click('button[type="submit"]')
            await page.wait_for_url("**/dashboard", timeout=10000)
            print("Logged in successfully!")

        print(f"Navigating to target url: {target_url}")
        await page.goto(target_url, wait_until="load")
        await asyncio.sleep(3)

        # Listen for top-level .ts segment requests (sometimes they leak here too)
        def capture_request(request):
            url = request.url
            if ".m3u8/" in url and ".ts" in url:
                match = re.match(r"(.*\.m3u8)/", url)
                if match:
                    base_m3u8 = match.group(1)
                    found_urls.add(base_m3u8)

        page.on("request", capture_request)
        page.on("response", lambda res: capture_request(res.request))

        # Wait for Wistia iframes
        iframe_elements = await page.query_selector_all("iframe.wistia_embed")

        if not iframe_elements:
            print("No Wistia iframes found on the page.")
            await browser.close()
            return

        print(f"Found {len(iframe_elements)} Wistia iframes. Attaching listeners...")

        # Looping until we get all the lazy loading to send url requests
        sleep_per_click=0
        num_videos = len(iframe_elements)

        # Sometimes we could have multiple urls per video
        urls_per_video = 1
        while ((urls_per_video * num_videos) > len(found_urls)):
            sleep_per_click+=1.5
            for idx, iframe_element in enumerate(iframe_elements):
                wistia_frame = await iframe_element.content_frame()

                if wistia_frame is None:
                    print(f"Could not access iframe #{idx + 1}")
                    continue

                print(f"Attached to iframe #{idx + 1}")

                def capture_iframe_request(request, i=idx):
                    url = request.url
                    print(f"[iframe {i + 1}] request: {url}")
                    if ".m3u8/" in url and ".ts" in url:
                        match = re.match(r"(.*\.m3u8)/", url)
                        if match:
                            base_m3u8 = match.group(1)
                            found_urls.add(base_m3u8)

                wistia_frame.on("request", capture_iframe_request)
                wistia_frame.on("response", lambda res, i=idx: capture_iframe_request(res.request, i))

                # Try clicking inside iframe
                try:
                    # Click a bunch and wait a bunch and hope the lazy loader comes
                    await wistia_frame.click("body", timeout=3000)
                    await asyncio.sleep(sleep_per_click)

                    await wistia_frame.click("body", timeout=3000)
                    await asyncio.sleep(sleep_per_click)

                    await wistia_frame.click("body", timeout=3000)
                    await asyncio.sleep(sleep_per_click)

                    print(f"Clicked inside iframe #{idx + 1}")
                except:
                    print(f"Could not click inside iframe #{idx + 1}")
                await asyncio.sleep(3)


        # Let video load and network activity happen
        await asyncio.sleep(3)
        await browser.close()

    # Save URLs
    if found_urls:
        with open(M3U8_LIST_PATH, "a") as f:
            for u in sorted(found_urls):
                f.write(u + "\n")
        print(f"Saved {len(found_urls)} .m3u8 URLs to {M3U8_LIST_PATH}")
    else:
        print("No .m3u8 URLs found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python append_m3u8_with_login.py <target_url>")
        sys.exit(1)

    url_arg = sys.argv[1]
    asyncio.run(run(url_arg))
