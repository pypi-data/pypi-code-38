# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import Request

from esgf_scraper.items import ESGFFileItem


class ESGFRequest(Request):
    """A request to download from the ESGF
    """

    def __init__(self, item, *args, **kwargs):
        if not isinstance(item, ESGFFileItem):
            raise TypeError("item is expected to be an ESGFDownloadItem")
        self.item = item
        if "url" in kwargs:
            kwargs.pop("url")
        super(ESGFRequest, self).__init__(item["url"], *args, **kwargs)

    def replace(self, *args, **kwargs):
        """Create a new Request with the same attributes except for those
        given new values.
        """
        for x in [
            "method",
            "headers",
            "body",
            "cookies",
            "meta",
            "flags",
            "encoding",
            "priority",
            "dont_filter",
            "callback",
            "errback",
        ]:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop("cls", self.__class__)
        return cls(self.item, *args, **kwargs)
