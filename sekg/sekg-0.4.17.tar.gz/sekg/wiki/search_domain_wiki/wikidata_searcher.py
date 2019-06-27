#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import time
import aiohttp
import async_timeout
import pickle
from pathlib import Path
import json
import traceback
from sekg.wiki.WikiDataItem import WikiDataItem


# if sys.platform == 'win32':
#     loop = asyncio.ProactorEventLoop()
#     asyncio.set_event_loop(loop)

# import wikipedia


class AsyncWikiSearcher:
    API_URL = 'https://www.wikidata.org/w/api.php'

    def __init__(self, proxy_server=None, pool_size=63, stride=60):
        self.proxy_server = proxy_server
        self.semaphore = asyncio.Semaphore(pool_size)
        self.title_cache = {}
        self.item_cache = {}
        self.stride = stride

    async def __fetch_titles(self, query, limit=5):
        if query in self.title_cache:
            return self.title_cache[query]
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srprop': 'snippet',
            'srlimit': limit,
            'srsearch': query
        }
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(10):
                        async with session.get(self.API_URL, params=params, proxy=self.proxy_server) as response:
                            json_data = await response.json()
                            result = [
                                {"pageid": item["pageid"], "title": item["title"], "snippet": item.get("snippet", "")}
                                for item in json_data["query"]["search"]]
                            self.title_cache[query] = result
                            # print("[Done] query: {}".format(query))
                            return result
        except Exception:
            print("[Failed] query: {}".format(query))
            traceback.print_exc()
            return []

    async def __fetch_entity(self, title):
        if title in self.item_cache:
            return self.item_cache[title]
        params = {
            'ids': title,
            'format': 'json',
            'action': 'wbgetentities'
        }
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(10):
                        async with session.get(self.API_URL, params=params, proxy=self.proxy_server) as response:
                            json_data = await response.json()
                            self.item_cache[title] = WikiDataItem(title,
                                                                  init_at_once=False).init_wikidata_item_from_json(
                                json_data)
                            # print("[Done] title: {}".format(title))
                            return json_data
        except Exception:
            print("[Failed] title: {}".format(title))
            traceback.print_exc()
            return {}

    def save(self, title_save_path=None, item_save_path=None):
        print("Save...")
        if title_save_path is not None:
            with Path(title_save_path).open("wb") as f:
                pickle.dump(self.title_cache, f)
        if item_save_path is not None:
            with Path(item_save_path).open("wb") as f:
                pickle.dump(self.item_cache, f)

    def clear(self):
        del self.item_cache
        del self.title_cache
        self.item_cache = {}
        self.title_cache = {}

    def search_title(self, queries):
        loop = asyncio.get_event_loop()
        tasks = [self.__fetch_titles(q) for q in queries]
        loop.run_until_complete(asyncio.gather(*tasks))
        return self.title_cache

    def fetch_item(self, ids):
        loop = asyncio.get_event_loop()
        tasks = [self.__fetch_entity(_id) for _id in ids]
        loop.run_until_complete(asyncio.gather(*tasks))
        # for k, v in self.item_cache:
        #     self.item_cache[k] = WikiDataItem(k, init_at_once=False).init_wikidata_item_from_json(v)
        return self.item_cache

    def init_from_cache(self, title_save_path=None, item_save_path=None):
        print("Init from cache...")
        if title_save_path is not None and Path(title_save_path).exists():
            with Path(title_save_path).open("rb") as f:
                title_cache = pickle.load(f)
                self.title_cache = dict(self.title_cache, **title_cache)
        if item_save_path is not None and Path(item_save_path).exists():
            with Path(item_save_path).open("rb") as f:
                item_cache = pickle.load(f)
                self.item_cache = dict(self.item_cache, **item_cache)

    def item_cache_size(self):
        return len(self.item_cache)

    def title_cache_size(self):
        return len(self.title_cache)

    def __repr__(self):
        return "<AsyncWikiSearcher title=%r item=%r>" % (self.title_cache_size(), self.item_cache_size())


if __name__ == '__main__':
    searcher = AsyncWikiSearcher(proxy_server="http://127.0.0.1:1080")
    start = time.time()
    with Path("terms.txt").open("r", encoding="utf-8") as f:
        terms = [line.strip() for line in f]
    searcher.search_title(["apple", "orange"])
    searcher.save(title_save_path="titles.bin")
    ids = {item["title"] for v in searcher.title_cache.values() for item in v}
    searcher.fetch_item(ids)
    searcher.save(item_save_path="items.bin")
    # result = searcher.summary()
    end = time.time()
    print("cost time:", end - start)
