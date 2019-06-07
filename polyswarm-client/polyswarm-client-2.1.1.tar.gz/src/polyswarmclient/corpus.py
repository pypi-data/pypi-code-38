import logging
import os
import tempfile
import urllib.request
from subprocess import check_call

logger = logging.getLogger(__name__)  # Initialize logger

MALICIOUS_BOOTSTRAP_URL = os.getenv('MALICIOUS_BOOTSTRAP_URL')
ARCHIVE_PASSWORD = os.getenv('ARCHIVE_PASSWORD')


class DownloadToFileSystemCorpus(object):
    def __init__(self, base_dir=None):
        self.url = MALICIOUS_BOOTSTRAP_URL
        self.base_dir = base_dir if base_dir else tempfile.mkdtemp(suffix="malware-corpus")
        self.truth_fname = "truth.db"
        self.truth_db_pth = os.path.join(self.base_dir, self.truth_fname)

    @property
    def mal_path(self):
        return os.path.join(self.base_dir, "malicious")

    @property
    def benign_path(self):
        return os.path.join(self.base_dir, "benign")

    def download_and_unpack(self):
        logger.info("Downloading to {0}".format(self.base_dir))
        for is_mal, package_name in [(True, "malicious.tgz.gpg"), (False, "benign.tgz.gpg")]:

            mal_dir = self.mal_path if is_mal else self.benign_path
            archive_path = os.path.join(mal_dir, package_name)
            archive_dst = mal_dir
            if not os.path.isdir(archive_dst):
                os.makedirs(archive_dst, exist_ok=True)
            archive_tgz = archive_path.rstrip(".gpg")
            r = urllib.request.urlretrieve("{0}/{1}".format(self.url, package_name), archive_path)
            check_call(["gpg", "--batch", "--passphrase", ARCHIVE_PASSWORD, "--decrypt",
                        "--no-use-agent", "--cipher-algo", "AES256",
                        "--yes", "-o", archive_tgz, archive_path])
            # can do with python tar file, but being lazy
            check_call(["tar", "xf", archive_tgz, "-C", archive_dst])
            os.unlink(archive_tgz)
            os.unlink(archive_path)

    def _get_pth_listing(self, p):
        artifacts = []
        for root, dirs, files in os.walk(p):
            for f in files:
                artifacts.append(os.path.join(root, f))
        return artifacts

    def get_malicious_file_list(self):
        return self._get_pth_listing(self.mal_path)

    def get_benign_file_list(self):
        return self._get_pth_listing(self.benign_path)

    def download_truth(self):
        u = "{0}/{1}".format(self.url, self.truth_fname)
        logger.info("Fetching truth database {0}".format(u))
        r = urllib.request.urlretrieve(u, self.truth_db_pth)
