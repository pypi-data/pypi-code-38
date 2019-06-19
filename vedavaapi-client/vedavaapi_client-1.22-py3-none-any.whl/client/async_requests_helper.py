import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

START_TIME = default_timer()

def fetch(session, url, set_progress):
    #  print(url)
    with session.get(url) as response:
        if response.status_code != 200:
            print("FAILURE::{0}".format(url))
            return None
        if set_progress is not None:
            set_progress()
        data = response.json()
        return data

async def get_data_asynchronous(urls, update_state=None):
    responses = []
    fetched_count = 0

    if update_state:
        task_id = update_state.__self__.request.id if update_state else None
        print(update_state, update_state.__self__.request.id)

    def set_progress():
        if not update_state:
            return
        nonlocal fetched_count
        fetched_count += 1
        #  print(update_state, update_state.__self__.request.id)
        update_state(task_id=task_id, state='PROGRESS', meta={"total_pages": len(urls), "resolved_pages": fetched_count, "status": "getting page details..."})

    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, url, set_progress) # Allows us to pass in multiple arguments to `fetch`
                )
                for url in urls
            ]
            for response in await asyncio.gather(*tasks):
                responses.append(response)

    return responses


def get_urls(urls, update_state=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_data_asynchronous(urls, update_state=update_state))
    loop.run_until_complete(future)
    return future.result()
