import requests
from bamboo_lib.connectors.models import BaseDriver
import hashlib
import os
import sys
from bamboo_lib.logger import logger


class HttpDriver(BaseDriver):
    TYPE = 'HTTP Web Driver'

    def __init__(self, **kwargs):
        super(HttpDriver, self).__init__(**kwargs)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0'
        }

    def hit(self):
        logger.debug("HttpDriver hitting {}".format(self.uri))
        return requests.get(self.uri, headers=self.headers)

    def download(self, params=None, http_params=None, force=False):
        uri = self.uri
        uri = BaseDriver.resolve_params(uri, params).encode('utf-8')
        download_path = os.environ.get("BAMBOO_DOWNLOAD_FOLDER", "/tmp")
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        local_filename = os.path.join(download_path, hashlib.sha224(uri).hexdigest())
        logger.info("Hitting URL: {} ...".format(uri))
        # if already downloaded, dont redownload unless required
        if not force and os.path.isfile(local_filename):
            return local_filename

        with open(local_filename, "wb") as f:
            logger.info("Downloading {}".format(uri))

            response = requests.get(uri, stream=True, headers=self.headers)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
        return local_filename
