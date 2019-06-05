"""File downloader

A collections of functions for downloading large binary files in a relatively performant manner
and verifying their contents.
"""

import logging
import shutil
import tempfile
from os import makedirs
from os.path import dirname, exists

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from urllib3.util.retry import Retry

from esgf_scraper import conf
from esgf_scraper.checksum import md5sum, sha1sum, sha256sum
from esgf_scraper.utils import BlockTimer

logger = logging.getLogger(__name__)
CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_PERIOD = 10


def _calc_MB_per_s(b, s):
    return b / 1024 / 1024 / s


class DownloadResult:
    SUCCESS = 0
    VERIFIED = 1

    # Error codes
    FAILED_DOWNLOAD = -1
    CHECKSUM_FAILURE = -2
    UNKNOWN_ERROR = -99

    @staticmethod
    def get_human_readable(code):
        if code == DownloadResult.SUCCESS:
            return "Downloaded"
        elif code == DownloadResult.VERIFIED:
            return "Verified"
        elif code == DownloadResult.FAILED_DOWNLOAD:
            return "Failed (Download)"
        elif code == DownloadResult.VERIFIED:
            return "Failed (Checksum)"
        elif code == DownloadResult.VERIFIED:
            return "Failed (Unknown)"


def requests_retry_session(
    retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_checksum(fname_or_buff, checksum_type):
    fname_or_buff = (
        open(fname_or_buff, "rb") if isinstance(fname_or_buff, str) else fname_or_buff
    )
    fname_or_buff.seek(0)
    if checksum_type.lower() == "md5":
        return md5sum(fname_or_buff)
    elif checksum_type.lower() == "sha1":
        return sha1sum(fname_or_buff)
    elif checksum_type.lower() == "sha256":
        return sha256sum(fname_or_buff)

    raise ValueError("Unknown checksum type: " + checksum_type)


def verify_file(fname_or_buff, expected_checksum, checksum_type):
    """
    Verifies that a file exists and the checksum is what is expected

    Parameters
    ----------
    fname_or_buff : str or file-like
        The file object or filename to calculate a checksum from. If a filename is provided, an
        additional check that the file exists on disk is performed.
    expected_checksum
        The checksum
    checksum_type : str
        The checksum algorithm used to calculate the checksum. Options include "md5", "sha1" and "sha256"
    Returns
    -------
    True if the file exists with the correct checksum

    """
    opened_file = False
    try:
        if isinstance(fname_or_buff, str):
            if not exists(fname_or_buff):
                return False
            opened_file = True
            fname_or_buff = open(fname_or_buff, "rb")

        checksum = get_checksum(fname_or_buff, checksum_type)
        checksum_matches = expected_checksum == checksum
        if not checksum_matches:
            logger.error(
                "checksum for existing file {} did not match expected value of {}:{}".format(
                    fname_or_buff, checksum_type, expected_checksum
                )
            )
        return checksum_matches
    finally:
        if opened_file:
            fname_or_buff.close()


def _maybe_log(t, target, downloaded, size):
    elapsed = t.elapsed()
    if elapsed > target:
        logger.info(
            "{:.2f}MB/{.2f}MB ({:.2f}MB/s)".format(
                downloaded / 1024 / 1024,
                int(size) / 1024 / 1024,
                _calc_MB_per_s(downloaded, elapsed),
            )
        )
        return (elapsed % LOG_PERIOD + 1) * LOG_PERIOD
    return target


def download_file(url, target_path, checksum=None, checksum_type=None, size=None):
    with tempfile.TemporaryFile(conf.get("temp_dir", None)) as temp_fp:
        logger.info("Downloading: {}".format(url))
        try:
            with BlockTimer() as t:
                target = LOG_PERIOD
                with requests_retry_session().get(url, stream=True) as r:
                    r.raise_for_status()

                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        _maybe_log(t, target, temp_fp.tell(), size)

                        if chunk:  # filter out keep-alive new chunks
                            temp_fp.write(chunk)
        except (ConnectionError, HTTPError, RequestException, Timeout):
            logger.exception("An exception occurred downloading: {}".format(url))
            return DownloadResult.FAILED_DOWNLOAD
        except Exception:
            # Catch any unknown exceptions
            logger.exception("A unknown exception occurred downloading: {}".format(url))
            raise
        finally:
            logger.info(
                "finished download in {:.2f}s ({:.2f}MB/s): {}".format(
                    t.interval, _calc_MB_per_s(temp_fp.tell(), t.interval), url
                )
            )
        if checksum is not None:
            downloaded_checksum = get_checksum(temp_fp, checksum_type)
            if downloaded_checksum != checksum:
                return DownloadResult.CHECKSUM_FAILURE
        _write_target_file(target_path, temp_fp)
        logger.debug("wrote file to {}".format(target_path))

        return DownloadResult.SUCCESS


def _write_target_file(target_path, temp_fp):
    target_dir = dirname(target_path)
    if not exists(target_dir):
        makedirs(target_dir)
        logger.info("Creating directory {}".format(target_dir))
    with open(target_path, "wb") as out_fp:
        temp_fp.seek(0)
        shutil.copyfileobj(temp_fp, out_fp)
