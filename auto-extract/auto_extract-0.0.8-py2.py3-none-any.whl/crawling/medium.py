from auto_extract.crawling.crawler import Crawler
from auto_extract.crawling.regexes import re_count


class MediumCrawler(Crawler):

    def __init__(self, pages, name, *args, **kwargs):
        pages = pages if isinstance(pages, list) else [pages]
        seed_urls = ["https://medium.com/{}/latest".format(page) for page in pages]
        super().__init__(seed_urls=seed_urls,
                         name="medium_{}".format(name),
                         any_exclude_regexes=["/about", "/archive",
                                              "/welcome", "/tagged", "/trending"],
                         all_required_regexes=[re_count("/", 4, 4)],
                         *args, **kwargs)
