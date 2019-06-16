import os
import sys
import requests
import hashlib
import io
import time

from bamboo_lib.logger import logger
from bamboo_lib.models import PipelineStep
from bamboo_lib.connectors.models import BaseDriver
from bamboo_lib.exceptions import DownloadFailedException
class HttpDriver(BaseDriver):
    TYPE = 'HTTP Web Driver'

    def __init__(self, **kwargs):
        self.timeout = kwargs.get("timeout", None)
        self.max_retries = kwargs.get("max_retries", None)
        self._num_retries = 0
        self.backoff_time_wait = int(kwargs.get("backoff_time_wait", 5)) # time in seconds
        # self.backoff_strategy = 'EXPONENTIAL'
        super(HttpDriver, self).__init__(**kwargs)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0'
        }

    def hit(self):
        logger.debug("HttpDriver hitting {}".format(self.uri))
        return requests.get(self.uri, headers=self.headers)

    def save_to_disk(self, io_handle, content, callback, params):
        logger.info("Saving web asset to disk (using callback={})....".format(callback is not None))
        content = io.BytesIO(content)
        if callback:
            if isinstance(callback, PipelineStep):
                content = callback(content, params)
            else:
                content = callback(content)
        if isinstance(content, str):
            content = content.encode("utf-8")
        elif isinstance(content, io.BytesIO):
            content = content.read()
        elif isinstance(content, io.StringIO):
            content = content.getvalue().encode("utf-8")
        io_handle.write(content)

    def download(self, params=None, http_params=None, force=False, callback=None):
        uri = self.uri
        uri = BaseDriver.resolve_params(uri, params).encode('utf-8')
        download_path = os.environ.get("BAMBOO_DOWNLOAD_FOLDER", "/tmp")
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        local_filename = os.path.join(download_path, hashlib.sha224(uri).hexdigest())
        logger.info("Hitting URL: {} ...".format(uri))
        # if already downloaded, dont redownload unless required
        if not force and os.path.isfile(local_filename):
            logger.info("Reading web asset from local cache...")
            return local_filename

        inmemory_buffer = io.BytesIO()
        try:
            response = requests.get(uri, stream=True, headers=self.headers, timeout=self.timeout)
        except requests.exceptions.Timeout:
            logger.error("Request to {} timed out.".format(uri))
            if self.max_retries and self._num_retries < self.max_retries:
                self._num_retries += 1
                # wait
                logger.info("Going to retry (retry #{}) request, but first going to sleep...".format(self._num_retries))
                sleep_time = pow(self.backoff_time_wait, self._num_retries)
                logger.info("Sleeping for {} seconds before retrying...".format(sleep_time))
                time.sleep(sleep_time)
                return self.download(params, http_params, force, callback)
            else:
                raise DownloadFailedException("Download failed. Request timed out and retry limit ({}) exceeded.".format(self.max_retries))
        with open(local_filename, "wb") as f:
            logger.info("Downloading {}".format(uri))
            total_length = response.headers.get('content-length')
            if total_length is None:  # no content length header
                self.save_to_disk(f, response.content, callback, params)
            else:
                dl = 0
                total_length = int(total_length)
                # in the case of the chunked response
                # write everything to buffer, then apply callback fn
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    inmemory_buffer.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
                self.save_to_disk(f, inmemory_buffer.getvalue(), callback, params)
        inmemory_buffer.close()
        return local_filename
