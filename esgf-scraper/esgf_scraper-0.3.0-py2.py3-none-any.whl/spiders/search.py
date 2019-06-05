import json
import logging
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit

import scrapy

import esgf_scraper.ext.dblite as dblite
from esgf_scraper import conf
from esgf_scraper.items import DatasetDetailItem, DatasetSearchItem, ESGFFileItem

logger = logging.getLogger(__name__)

ESGF_NODE = "esgf-node.llnl.gov"


def create_search_url(**kwargs):
    kwargs.setdefault("format", "application/solr+json")
    kwargs.setdefault("offset", 0)
    kwargs.setdefault("limit", 100)
    kwargs.setdefault("latest", True)
    kwargs.setdefault("type", "Dataset")
    kwargs.setdefault("replica", False)

    return "https://{}/esg-search/search?{}".format(
        ESGF_NODE, urlencode(kwargs, doseq=True)
    )


def process_details_item(instance_id):
    def _parse(response):
        url_components = urlsplit(response.url)
        response.selector.remove_namespaces()
        path = response.selector.xpath(
            '//service[@serviceType="HTTPServer"]/@base'
        ).get()
        assert path
        data_url = "{}://{}{}".format(
            url_components.scheme, url_components.netloc, path
        )
        output_dir = "/".join(
            instance_id.split(".")
        )  # The instance id is the . separated equiv of the folder directory

        # Find all the files to download
        files = []
        for dataset in response.selector.xpath("/catalog/dataset/dataset"):
            dataset_rel_url = dataset.xpath("@urlPath").get()
            # Skip aggregations
            is_aggregation = dataset.xpath("@name").get().endswith(".aggregation")

            # Some aggregations don't list a urlPath
            if dataset_rel_url:
                url = urljoin(data_url, dataset_rel_url)
                size = dataset.xpath("property[@name='size']/@value").get()
                logger.info(
                    "Found file {}. Size {:.2f}MB".format(url, int(size) / 1000 / 1000)
                )
                files.append(
                    ESGFFileItem(
                        url=url,
                        checksum=dataset.xpath(
                            "property[@name='checksum']/@value"
                        ).get(),
                        checksum_type=dataset.xpath(
                            "property[@name='checksum_type']/@value"
                        ).get(),
                        size=size,
                        filename=dataset.xpath("@name").get(),
                    )
                )
            elif not is_aggregation:
                logger.error("Could not get url from dataset: {}".format(dataset.get()))

        # This item will be queued up for future download
        yield DatasetDetailItem(
            instance_id=instance_id,
            output_dir=output_dir,
            files=files,
            host=url_components.netloc,
        )

    return _parse


class SearchSpider(scrapy.Spider):
    name = "search"

    def __init__(self, *args, **kwargs):
        if isinstance(kwargs["filters"], dict):
            kwargs["filters"] = kwargs["filters"]
        else:
            kwargs["filters"] = conf["filters"]
        super(SearchSpider, self).__init__(*args, **kwargs)
        self.count = 0
        self.ds = dblite.open(DatasetSearchItem, autocommit=True)

    def start_requests(self):
        for filters in self.filters:
            yield scrapy.Request(url=create_search_url(**filters), callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body)

        resp = data["response"]
        logger.info(
            "reading {}-{}/{} documents".format(
                resp["start"], resp["start"] + len(resp["docs"]), resp["numFound"]
            )
        )

        for d in resp["docs"]:
            # This will be written to the db in the StoreItemPipeline
            item = DatasetSearchItem(d)
            yield item

            # Find information about the files to download
            yield scrapy.Request(
                d["url"][0], callback=process_details_item(item["instance_id"])
            )

            # Keep track of number of downloads
            self.count = self.count + 1
            if self.limit is not None and self.count >= self.limit:
                logger.info("reached limit. Stopping")
                return

        if resp["start"] + len(resp["docs"]) < resp["numFound"]:
            yield scrapy.Request(self.get_next_url(response.url))

    def get_next_url(self, old_url):
        url = urlsplit(old_url)
        qs = parse_qs(url.query)

        # update the offset
        offset = int(qs["offset"][0]) if "offset" in qs else 0
        limit = int(qs["limit"][0]) if "limit" in qs else 0
        qs["offset"] = offset + limit

        return create_search_url(**qs)
