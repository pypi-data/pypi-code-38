import logging
import os
import signal
import sys
from os.path import exists

import click
import yaml
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

import esgf_scraper.ext.dblite as dblite
from esgf_scraper import conf
from esgf_scraper.items import DatasetSearchItem
from esgf_scraper.postprocess import run_postprocessing
from esgf_scraper.spiders.download import DownloadSpider
from esgf_scraper.sqlite import get_queue, queue_names
from esgf_scraper.utils import print_items

logger = logging.getLogger("esgf-scraper")
signal.signal(signal.SIGINT, signal.default_int_handler)


def arglist_to_dict(arglist):
    res = dict(x.split("=", 1) for x in arglist)

    def _process_arg(v):
        if v.startswith("[") and v.endswith("]"):
            return [i.strip() for i in v[1:-1].split(",")]
        return v

    return {k: _process_arg(v) for k, v in res.items()}


@click.group(help="Download data from ESGF archives")
@click.option(
    "--config",
    "-c",
    help="Path to configuration filename. Defaults to looking in the current directory and home directory for a "
    "file named `esgf_scraper.conf`",
)
@click.option(
    "--log-level",
    "-l",
    help="Specify the level below which log messages are dropped. Defaults to WARNING. ",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="WARNING",
)
@click.version_option()
def cli(config, log_level):
    if "SCRAPY_SETTINGS_MODULE" not in os.environ:
        os.environ["SCRAPY_SETTINGS_MODULE"] = "esgf_scraper.settings"
    scrapy_settings = get_project_settings()
    # Update some defaults
    if config is not None:
        conf.load_from_file(config)

    try:
        scrapy_settings["FILES_STORE"] = conf["base_dir"]
    except KeyError:
        pass
    if scrapy_settings["FILES_STORE"] is None:
        raise ValueError("No valid `FILES_STORE` configuration")
    scrapy_settings["LOG_LEVEL"] = log_level
    configure_logging(scrapy_settings, install_root_handler=True)
    logging.basicConfig()

    conf.update({"scrapy": scrapy_settings})


def load_filters(ctx, _, filename):
    if filename is None:
        return
    if not exists(filename):
        ctx.fail("Could not load file: {}".format(filename))
    with open(filename) as fh:
        f = yaml.load(fh, Loader=yaml.SafeLoader)
        if "filters" not in f:
            ctx.fail("Filter file does not contain a 'filters' key")
        return f["filters"]


@cli.command("search", help="Search for files on ESGF")
@click.option("--add/--no-add", default=False, help="Add to the files to be downloaded")
@click.option(
    "--filter",
    "-f",
    multiple=True,
    help="facets to filter. Of the format NAME=VALUE where value can be a string or a list of strings and name is a valid "
    "esgf facet. This argument can be passed many times. The results in this case will be an AND of the various filters",
)
@click.option(
    "--limit",
    "-l",
    type=click.INT,
    default=None,
    help="Limit the number of results to search",
)
@click.option(
    "--filter-file",
    type=str,
    default=None,
    callback=load_filters,
    help="File containing a list of filters. The file should be in the same format as the configuration file (YAML) and contain"
    " a 'filters' key with a list of filters to apply.",
)
def search_func(add, filter, limit, filter_file):
    if filter_file:
        filters = filter_file
    else:
        filters = [arglist_to_dict(filter)] if len(filter) else None
    crawl_process = CrawlerProcess(conf["scrapy"])
    crawl_process.crawl("search", add=add, filters=filters, limit=limit)
    crawl_process.start()

    sys.exit(int(crawl_process.bootstrap_failed))


@cli.command("download")
@click.option(
    "--requeue",
    default=False,
    is_flag=True,
    help="Requeues any previously failed items before running the postprocessing steps",
)
def download_func(requeue):
    queue = get_queue("download_queue")
    failed_queue = get_queue("failed_download_queue")

    if requeue:
        while len(failed_queue):
            obj = failed_queue.popleft()
            logger.info("requeuing {} for downloading".format(obj))
            queue.append(obj, deduplicate=True)

    download_spider = DownloadSpider()
    return_val = download_spider.start()

    sys.exit(int(return_val))


@cli.command(
    "verify",
    help="Queue datasets to be reverified. The hash of the file on disk will be checked and redownloaded if needed.",
)
@click.option(
    "--filter",
    "-f",
    multiple=True,
    help="facets to filter. Of the format NAME=VALUE where value can be a string or a list of strings and name is a valid "
    "esgf facet. This argument can be passed many times. The results in this case will be an AND of the various filters",
)
@click.option(
    "--downloaded/--not-downloaded",
    default=None,
    help="Limit to returning datasets which have (or have not) been successfully downloaded and verified",
)
def verify_func(filter, downloaded):
    queue = get_queue("download_queue")
    ds = dblite.open(DatasetSearchItem, autocommit=True)
    filters = arglist_to_dict(filter)
    criteria = {k: 'r/"{}"/'.format(v) for k, v in filters.items()}
    if downloaded is not None:
        if downloaded:
            criteria["verified_at"] = "$NOT NULL$"
        else:
            criteria["verified_at"] = None

    items = list(ds.get(criteria=criteria))
    for item in items:
        queue.append({"instance_id": item["instance_id"]}, deduplicate=True)

    print("Added {} items to queue for validation".format(len(items)))


@cli.command("list", help="List information about tracked datasets")
@click.option(
    "--filter",
    "-f",
    multiple=True,
    help="facets to filter. Of the format NAME=VALUE where value can be a string or a list of strings and name is a valid "
    "esgf facet. This argument can be passed many times. The results in this case will be an AND of the various filters",
)
@click.option(
    "--columns",
    "-c",
    multiple=True,
    help="Comma separated list of columns to show. This defaults to the using the configuration value 'default_cols' if no values"
    "are provided. See the documentation for a full list of columns which can be displayed.",
)
@click.option(
    "--limit",
    "-l",
    type=click.INT,
    default=None,
    help="Limit the number of results to search",
)
@click.option(
    "--verified/--not-verified",
    default=None,
    help="Limit to returning datasets which have (or have not) been successfully downloaded and verified",
)
def list_func(filter, columns, limit, verified):
    ds = dblite.open(DatasetSearchItem, autocommit=True)

    filters = arglist_to_dict(filter)
    cols = columns.split(",") if len(columns) else conf.get("default_cols", "all")
    criteria = {k: 'r/"{}"/'.format(v) for k, v in filters.items()}
    if verified is not None:
        if verified:
            criteria["verified_at"] = "$NOT NULL$"
        else:
            criteria["verified_at"] = None
    items = list(ds.get(criteria=criteria, limit=limit))

    print_items(items, cols)


@cli.command(
    "postprocess",
    help="Postprocess any items. The postprocessing steps are configured in the config file.",
)
@click.option(
    "--requeue",
    default=False,
    is_flag=True,
    help="Requeues any previously failed items before running the postprocessing steps",
)
def postprocess_func(requeue):
    queue = get_queue("postprocess_queue")
    failed_queue = get_queue("failed_postprocess_queue")
    ds = dblite.open(DatasetSearchItem, autocommit=True)

    if requeue:
        while len(failed_queue):
            obj = failed_queue.popleft()
            logger.info("requeuing {} for postprocessing".format(obj))
            queue.append(obj, deduplicate=True)

    while len(queue):
        logger.info("{} items remaining".format(len(queue)))
        obj = queue.popleft()

        try:
            item = ds.get(criteria=obj, limit=1)
            assert item is not None
            run_postprocessing(item)
        except Exception:
            logger.exception("Failed to postprocess item: {}".format(obj))
            failed_queue.append(obj)


def validate_queue(ctx, _, value):
    def check_queue(q):
        if q not in queue_names:
            ctx.fail("Unknown queue: {}".format(value))

    if value is not None:
        if isinstance(value, str):
            check_queue(value)
        else:
            for q in value:
                check_queue(q)
    return value


@cli.command(
    "queues", help="Display information about the number of items in the queues"
)
@click.option(
    "--clear",
    default=None,
    type=str,
    callback=validate_queue,
    help="Clears a queue. Datasets can be requeued to the download_queue by using the "
    "`verify` command.",
)
@click.option(
    "--move",
    default=None,
    nargs=2,
    type=str,
    callback=validate_queue,
    help="Moves items from one queue to another.",
)
def queue_func(clear, move):
    if move:
        source_queue = get_queue(move[0])
        target_queue = get_queue(move[1])
        while len(source_queue):
            obj = source_queue.popleft()
            logger.info("requeuing {}".format(obj))
            target_queue.append(obj, deduplicate=True)

    if clear:
        source_queue = get_queue(clear)
        while len(source_queue):
            source_queue.popleft()

    counts = []
    for queue_name in queue_names:
        queue = get_queue(queue_name)

        counts.append({"queue": queue_name, "item_count": len(queue)})

    print_items(counts, cols=["queue", "item_count"], show_index=False)


if __name__ == "__main__":
    cli()
