from auto_extract.crawling.crawler import Crawler
from auto_extract.crawling.regexes import re_count


class SteemitCrawler(Crawler):

    def __init__(self, pages, name, *args, **kwargs):
        pages = pages if isinstance(pages, list) else [pages]
        seed_urls = ["https://steemit.com/{}".format(page) for page in pages]
        super().__init__(seed_urls=seed_urls,
                         name="medium_{}".format(name),
                         all_required_regexes=[re_count("/", 5, 5)],
                         any_exclude_regexes=["#"],
                         *args, **kwargs)


# s = SteemitCrawler("@pylonnetwork", info_type="currency")
