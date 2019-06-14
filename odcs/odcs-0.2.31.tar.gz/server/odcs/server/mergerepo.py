# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

import os
import requests
from xml.etree import ElementTree
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from six.moves.urllib.parse import urlparse
from distutils.spawn import find_executable

from flufl.lock import Lock

from odcs.server import log, conf
from odcs.server.utils import makedirs, execute_cmd


class MergeRepo(object):
    def __init__(self, compose):
        self.compose = compose

    def _download_file(self, path, url):
        """
        Downloads repodata file, stores it into `path`/repodata and returns
        its content.

        :param str path: Path to store the file to.
        :param str url: URL of file to download.
        :rtype: str
        :return: content of downloaded file.
        """
        log.info("%r: Downloading %s", self.compose, url)
        r = requests.get(url)
        r.raise_for_status()

        filename = os.path.basename(url)
        makedirs(os.path.join(path, "repodata"))
        with open(os.path.join(path, "repodata", filename), "wb") as f:
            f.write(r.content)
        return r.content

    def _download_repodata(self, path, baseurl):
        """
        Downloads the repodata from `baseurl` to `path`.

        :param str path: Path to store the file to.
        :param str baseurl: Base URL of repository to download.
        """
        # In case we already have the repodata downloaded, read the repomd.xml,
        # so we can later check if the repodata changed or not.
        last_repomd = None
        repodata_path = os.path.join(path, "repodata")
        repomd_path = os.path.join(repodata_path, "repomd.xml")
        if os.path.exists(repomd_path):
            with open(repomd_path, "r") as f:
                last_repomd = f.read()

        # Download the repomd.xml.
        repomd_url = os.path.join(baseurl, "repodata", "repomd.xml")
        repomd = self._download_file(path, repomd_url)
        tree = ElementTree.fromstring(repomd)

        # In case the repomd.xml did not change since the last compose, use
        # the existing repodata to save lot of time downloading other repodata
        # files.
        if repomd == last_repomd:
            log.info("%r: Reusing cached repodata for %s",
                     self.compose, baseurl)
            return

        # In case the repomd.xml changed, remove everything from the repodata
        # directory except the just downloaded repomd.xml.
        for f in os.listdir(repodata_path):
            if f == "repomd.xml":
                continue
            os.unlink(os.path.join(repodata_path, f))

        # Parse the repomd.xml and download all the repodata files needed
        # to merge the repos.
        ns = "{http://linux.duke.edu/metadata/repo}"
        with ThreadPoolExecutor(5) as downloader:
            for data in tree.findall('%sdata' % ns):
                if data.get("type").endswith("_db"):
                    continue
                data_location = data.find("%slocation" % ns).get("href")
                data_url = os.path.join(baseurl, data_location)
                downloader.submit(self._download_file, path, data_url)

    def run(self, arch, repos, repo_name):
        """
        Merges multiple RPM repositories and stores the output to
        `os.path.join(compose.result_repo_dir, repo_name, arch)`.

        Raises an RuntimeError in case of error.

        :param str arch: Architecture of RPMs in repositories.
        :param list repos: List of URLs pointing to repos to merge.
        :param str repo_name: Name of the repository defining the subdirectory
            in `compose.result_repo_dir`.
        """
        # Multiple MergeRepo tasks can be running in the same time, so the
        # pulp_repo_cache must be protected by lock.
        # This list holds the lock for each pulp repo we merge.
        locks = []

        # Contains paths to per pulp repo pulp_repo_cache sub-directories.
        repo_paths = []

        parsed_url = urlparse(repos[0])
        repo_prefix = "%s://%s" % (parsed_url.scheme, parsed_url.hostname)
        repo_prefix = repo_prefix.strip("/") + "/"

        # Generate the pulp_repo_cache structure and locks for each repo.
        for repo in repos:
            repo_path = os.path.join(
                conf.target_dir, "pulp_repo_cache", repo.replace(repo_prefix, ""))
            repo_paths.append(repo_path)
            makedirs(repo_path)

            lock = Lock(os.path.join(repo_path, "lock"))
            lock.lifetime = timedelta(minutes=30)
            locks.append(lock)
        try:
            # Lock the locks and download the repodata.
            for lock in locks:
                lock.lock()
            for repo, repo_path in zip(repos, repo_paths):
                self._download_repodata(repo_path, repo)

            log.info("%r: Starting mergerepo_c: %r", self.compose, repo_paths)
            mergerepo_exe = find_executable('mergerepo_c')
            if not mergerepo_exe:
                raise RuntimeError("mergerepo_c is not available on system")

            result_repo_dir = os.path.join(self.compose.result_repo_dir, repo_name, arch)
            makedirs(result_repo_dir)

            args = [mergerepo_exe, "--method", "nvr", "-o",
                    result_repo_dir]
            args += ["--repo-prefix-search", os.path.join(conf.target_dir, "pulp_repo_cache")]
            args += ["--repo-prefix-replace", repo_prefix]
            for repo in repo_paths:
                args.append("-r")
                args.append(repo)

            execute_cmd(args)
        finally:
            for lock in locks:
                if lock.is_locked:
                    lock.unlock()
