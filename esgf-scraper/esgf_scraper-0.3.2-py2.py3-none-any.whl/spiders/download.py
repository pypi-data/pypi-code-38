import logging
import multiprocessing
import threading
from datetime import datetime
from logging.handlers import QueueHandler
from os.path import join
from queue import Empty
from time import sleep

import esgf_scraper.ext.dblite as dblite
from esgf_scraper import conf
from esgf_scraper.downloader import DownloadResult, download_file, verify_file
from esgf_scraper.items import DatasetSearchItem
from esgf_scraper.sqlite import get_queue
from esgf_scraper.utils import BlockTimer

logger = logging.getLogger(__name__)


def process_download(url, output_dir, filename, checksum, checksum_type, size):
    out_filename = join(conf["base_dir"], output_dir, filename)
    try:
        with BlockTimer() as t:
            # Check for an existing file
            if verify_file(out_filename, checksum, checksum_type):
                logger.info(
                    "Verified checksum of existing file: {}".format(out_filename)
                )
                res = DownloadResult.VERIFIED
            else:
                res = download_file(url, out_filename, checksum, checksum_type, size)
            return res
    except Exception:
        logger.exception("Failed processing {} with an unknown exception".format(url))
        return DownloadResult.UNKNOWN_ERROR
    finally:
        logger.info("Request for {} took {:.2f}s".format(url, t.interval))


class LoggedProcess(multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        self.log_queue = kwargs.pop("log_queue", None)
        super(LoggedProcess, self).__init__(*args, **kwargs)

    def run(self):
        if self.log_queue is not None:
            qh = QueueHandler(self.log_queue)
            root = logging.getLogger()
            root.setLevel(logging.DEBUG)
            root.handlers = [qh]


class Consumer(LoggedProcess):
    def __init__(self, task_queue, result_queue, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def success(self, item):
        self.result_queue.put({"result": "success", "item": item})

    def failure(self, item):
        self.result_queue.put({"result": "failed", "item": item})

    def run(self):
        super(Consumer, self).run()
        while True:
            # If a keyboard interrupt occurs jump try and listen again
            try:
                next_task = self.task_queue.get()
            except KeyboardInterrupt:
                continue
            logger.debug("Received {}".format(next_task))
            try:
                if next_task is None:
                    # Poison pill means shutdown
                    logger.info("{} terminating".format(self.name))
                    break
                res = []
                for f in next_task["files"]:
                    res.append(
                        process_download(
                            f["url"],
                            size=f["size"],
                            output_dir=next_task["output_dir"],
                            filename=f["filename"],
                            checksum=f["checksum"],
                            checksum_type=f["checksum_type"],
                        )
                    )
                if all([r >= 0 for r in res]):
                    self.success(next_task)
                else:
                    self.failure(next_task)
            except Exception:
                logger.exception("Unknown exception occurred")
                self.failure(next_task)
            finally:
                logger.debug("Ack {}".format(next_task))
                self.task_queue.task_done()

        return


class ResultConsumer(LoggedProcess):
    def __init__(self, result_queue, *args, **kwargs):
        super(ResultConsumer, self).__init__(*args, **kwargs)
        self.result_queue = result_queue
        self.failed_queue = get_queue("failed_download_queue")
        self.ds = dblite.open(DatasetSearchItem, autocommit=True)

    def update_item_times(self, item):
        item["verified_at"] = datetime.utcnow().isoformat()
        if item["downloaded_at"] is None:
            item["downloaded_at"] = datetime.utcnow().isoformat()
        logger.info("Updating verified_at value for {}".format(item["instance_id"]))
        self.ds.put(item)

    def run(self):
        super(ResultConsumer, self).run()
        logger.info("Starting results consumer")
        while True:
            # If a keyboard interrupt occurs jump try and listen again
            try:
                next_task = self.result_queue.get()
            except KeyboardInterrupt:
                continue

            logger.debug("Received {}".format(next_task))
            try:
                if next_task is None:
                    # Poison pill means shutdown
                    logger.info("{} terminating".format(self.name))
                    break

                raw_item = next_task["item"]
                if next_task["result"] == "success":
                    item = self.ds.get(
                        criteria={"instance_id": raw_item["instance_id"]}, limit=1
                    )
                    self.update_item_times(item)
                else:
                    logger.error(
                        "Download failed {}. requeuing".format(raw_item["instance_id"])
                    )
                    self.failed_queue.append(raw_item, deduplicate=True)
            except Exception:
                logger.exception("Failed to process results for {}".format(next_task))
                self.failed_queue.append(next_task["item"], deduplicate=True)
            finally:
                logger.debug("Ack {}".format(next_task))
                self.result_queue.task_done()
        return True


def logger_thread(q):
    while True:
        record = q.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)


class DownloadSpider:
    """
    Processes the download queue

    Any instances which are queued up to download are processed with this spider. The scraper makes a query to determine what files
    are available for a given instance id. Then the files are downloaded in the `ESGFDownloadPipeline`.
    """

    catch_all = None

    def __init__(self, **kwargs):
        super(DownloadSpider, self).__init__(**kwargs)
        self.queue = get_queue("download_queue")

        self.consumers = {}
        self.task_queue = {}
        self.log_queue = multiprocessing.Queue()
        self.results = multiprocessing.JoinableQueue()
        self.results_consumer = ResultConsumer(self.results, log_queue=self.log_queue)
        self.create_pool()

    def create_pool(self):
        downloads_conf = conf.get("downloads")
        if downloads_conf is None:
            logger.warning(
                "No configuration for 'downloads' found. Defaulting to a single download thread"
            )
        host_limits = downloads_conf.get("host_limits", {})
        n = downloads_conf["n"]
        self.consumers = {}
        consumer_count = 0

        for k in host_limits:
            self.task_queue[k] = multiprocessing.JoinableQueue()
            self.consumers[k] = [
                Consumer(self.task_queue[k], self.results, log_queue=self.log_queue)
                for _ in range(host_limits[k])
            ]
            consumer_count = consumer_count + host_limits[k]
        if consumer_count >= n:
            logger.warning("No catch all consumers are being created")

        # Create the catch all queues and consumers
        self.task_queue[self.catch_all] = multiprocessing.JoinableQueue()
        self.consumers[self.catch_all] = [
            Consumer(self.task_queue[self.catch_all], self.results)
            for _ in range(n - consumer_count)
        ]

    def join(self):
        for k in self.task_queue:
            self.task_queue[k].join()

    def maybe_join(self):
        for k in self.task_queue:
            q = self.task_queue[k]
            if not q.empty():
                return False

        return True

    def log_queues(self):
        lens = ["{}~{}".format(k, self.task_queue[k].qsize()) for k in self.task_queue]
        return logger.info("Queue sizes: {}".format(", ".join(lens)))

    def cleanup(self):
        logger.info("Joining consumers")
        self.join()

        self.results.put(None)
        logger.info("Waiting for results to be processed")
        self.results.join()

        # Tidy up logger
        self.log_queue.put(None)
        self.lp.join()

    def start(self):
        # start the logger
        self.lp = threading.Thread(target=logger_thread, args=(self.log_queue,))
        self.lp.start()

        try:
            logger.info(
                "Beginning to queue {} items for download".format(len(self.queue))
            )
            while len(self.queue):

                obj = self.queue.popleft()

                # determine the appropriate queue
                host_name = obj["host"]
                key = host_name if host_name in self.task_queue else self.catch_all
                self.task_queue[key].put(obj)

            # Add end of queue markers
            for w in self.task_queue:
                for i in range(len(self.consumers[w])):
                    self.task_queue[w].put(None)

            logger.info("Starting consumers")
            for w in self.consumers:
                for c in self.consumers[w]:
                    c.start()
            self.results_consumer.start()

            # Check if it is time to join
            while not self.maybe_join():
                self.log_queues()
                sleep(15)

            self.cleanup()

            return 0
        except KeyboardInterrupt:
            logging.warning("Attempting to perform a warm shutdown")
            failed_queue = get_queue("failed_download_queue")
            for w in self.task_queue:
                logging.warning("Attempting to cleanup queue {}".format(w))
                q = self.task_queue[w]
                try:
                    while True:
                        item = q.get(block=False)
                        if item is not None:
                            failed_queue.append(item, deduplicate=True)
                            logging.info("Moving {} to failed queue".format(item))
                        q.task_done()
                except Empty:
                    for i in range(len(self.consumers[w])):
                        if self.consumers[w][i].is_alive():
                            logging.info("Adding pill to {}".format(w))
                            self.task_queue[w].put(None)

            self.cleanup()
            logging.warning("Successfully shutdown")
            return 1
        except Exception:
            # try and recover queues
            logger.exception("An exception occurred")

            return 1
