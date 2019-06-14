import asyncio
import time

import aiohttp

from aioselenium import Remote
from keys import Keys

async def scraper(search):
    capabilities = {
            "browserName": "firefox",
        }

    command_executor = "http://test:test-password@selenium-cluster.synapsefi.com:4444/wd/hub"

    async with aiohttp.ClientSession() as session:
        remote = await Remote.create(command_executor, capabilities, session)
        async with remote as driver:
            await driver.set_window_size(1920, 1080)
            await driver.get("http://www.youtube.com")
            print('Loaded:',await driver.get_title())
            element = await driver.find_element_by_xpath('//input[@id="search"]')
            await element.send_keys(search, Keys.ENTER)
            video_titles = await driver.find_elements_by_xpath('//a[@id="video-title"]')
            for i, video_title in enumerate(video_titles):
                print(search, 'Search Result', i, await video_title.text())

async def main(search_fields):
    await asyncio.gather(*[scraper(search) for search in search_fields])

if __name__ == "__main__":
    s = time.perf_counter()

    search_fields = ["Soccer", "Guatemala", "Guitar", "Computer"]
    asyncio.run(main(search_fields))

    elapsed = time.perf_counter() - s
    print(f"Executed in {elapsed:0.2f} seconds.")
