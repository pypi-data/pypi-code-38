# -*- coding: utf-8 -*-


# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Modified by:
# Written by Karsten Hopp <karsten@redhat.com>
#            Petr Šabata <contyk@redhat.com>

"""SCM handler functions."""

import os
import subprocess as sp
import re
import tempfile
import shutil
import datetime

from module_build_service import log, conf
from module_build_service.errors import (
    Forbidden,
    ValidationError,
    UnprocessableEntity,
    ProgrammingError,
)
from module_build_service.utils.general import scm_url_schemes, retry


class SCM(object):
    "SCM abstraction class"

    # Assuming git for HTTP schemas
    types = scm_url_schemes()

    def __init__(self, url, branch=None, allowed_scm=None, allow_local=False):
        """
        Initialize the SCM object using the specified SCM URL.

        If url is not in the list of allowed_scm, an error will be raised.

        :param str url: The unmodified scmurl
        :param str branch: The optional source control branch. This defaults to "master" when git
            is used.
        :param list allowed_scm: The optional list of allowed SCM URL prefixes
        :param bool allow_local: Allow SCM URLs that start with "file://"
        :raises: Forbidden or ValidationError
        """

        if allowed_scm:
            if not (
                url.startswith(tuple(allowed_scm)) or (allow_local and url.startswith("file://"))
            ):
                raise Forbidden("%s is not in the list of allowed SCMs" % url)

        # If we are given the option for the git protocol or the http(s) protocol,
        # then just use http(s)
        if re.match(r"(git\+http(?:s)?:\/\/)", url):
            url = url[4:]
        url = url.rstrip("/")

        self.url = url
        self.sourcedir = None

        # once we have more than one SCM provider, we will need some more
        # sophisticated lookup logic
        for scmtype, schemes in SCM.types.items():
            if self.url.startswith(schemes):
                self.scheme = scmtype
                break
        else:
            raise ValidationError("Invalid SCM URL: %s" % url)

        # git is the only one supported SCM provider atm
        if self.scheme == "git":
            match = re.search(r"^(?P<repository>.*/(?P<name>[^?]*))(\?#(?P<commit>.*))?", url)
            self.repository = match.group("repository")
            self.name = match.group("name")
            self.repository_root = self.repository[: -len(self.name)]
            if self.name.endswith(".git"):
                self.name = self.name[:-4]
            self.commit = match.group("commit")
            self.branch = branch if branch else "master"
            self.version = None
        else:
            raise ValidationError("Unhandled SCM scheme: %s" % self.scheme)

    def verify(self):
        """
        Verifies that the information provided by a user in SCM URL and branch
        matches the information in SCM repository. For example verifies that
        the commit hash really belongs to the provided branch.

        :raises ValidationError
        """
        if not self.sourcedir:
            raise ProgrammingError("Do .checkout() first.")

        found = False
        branches = SCM._run(
            ["git", "branch", "-r", "--contains", self.commit], chdir=self.sourcedir
        )[1]
        for branch in branches.decode("utf-8").split("\n"):
            branch = branch.strip()
            if branch[len("origin/"):] == self.branch:
                found = True
                break
        if not found:
            raise ValidationError("Commit %s is not in branch %s." % (self.commit, self.branch))

    def scm_url_from_name(self, name):
        """
        Generates new SCM URL for another module defined by a name. The new URL
        is based on the root of current SCM URL.
        """
        if self.scheme == "git":
            return self.repository_root + name + ".git"

        return None

    @staticmethod
    def _run_without_retry(cmd, chdir=None, log_stdout=False):
        proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, cwd=chdir)
        stdout, stderr = proc.communicate()
        if log_stdout and stdout:
            log.debug(stdout)
        if stderr:
            log.warning(stderr)
        if proc.returncode != 0:
            raise UnprocessableEntity(
                "Failed on %r, retcode %r, out %r, err %r" % (cmd, proc.returncode, stdout, stderr)
            )
        return proc.returncode, stdout, stderr

    @staticmethod
    @retry(
        timeout=conf.scm_net_timeout,
        interval=conf.scm_net_retry_interval,
        wait_on=UnprocessableEntity,
    )
    def _run(cmd, chdir=None, log_stdout=False):
        return SCM._run_without_retry(cmd, chdir, log_stdout)

    def checkout(self, scmdir):
        """Checkout the module from SCM.

        :param str scmdir: The working directory
        :returns: str -- the directory that the module was checked-out into
        :raises: RuntimeError
        """
        # TODO: sanity check arguments
        if self.scheme == "git":
            self.sourcedir = "%s/%s" % (scmdir, self.name)

            module_clone_cmd = [
                "git", "clone", "-q", "--no-checkout", self.repository, self.sourcedir
            ]
            module_checkout_cmd = ["git", "checkout", "-q", self.commit]
            # perform checkouts
            SCM._run(module_clone_cmd, chdir=scmdir)
            try:
                SCM._run(module_checkout_cmd, chdir=self.sourcedir)
            except RuntimeError as e:
                if (
                    e.message.endswith(' did not match any file(s) known to git.\\n"')
                    or "fatal: reference is not a tree: " in e.message
                ):
                    raise UnprocessableEntity(
                        "checkout: The requested commit hash was not found within the repository. "
                        "Perhaps you forgot to push. The original message was: %s" % e.message
                    )
                raise

            timestamp = SCM._run(["git", "show", "-s", "--format=%ct"], chdir=self.sourcedir)[1]
            dt = datetime.datetime.utcfromtimestamp(int(timestamp))
            self.version = dt.strftime("%Y%m%d%H%M%S")
        else:
            raise RuntimeError("checkout: Unhandled SCM scheme.")
        return self.sourcedir

    def get_latest(self, ref=None):
        """ Get the latest commit hash based on the provided git ref

        :param ref: a string of a git ref (either a branch or commit hash). This defaults to
            self.branch.
        :returns: a string of the latest commit hash
        :raises: RuntimeError
        """
        if ref is None:
            ref = self.branch

        if self.scheme == "git":
            log.debug("Getting/verifying commit hash for %s" % self.repository)
            try:
                # This will fail if `ref` is not a branch name, but this works for commit hashes.
                # If the ref is not a branch, then fallback to `get_full_commit_hash`. We do not
                # want to retry here, since if it's a commit, it would block for a very long time.
                cmd = ["git", "ls-remote", "--exit-code", self.repository, "refs/heads/" + ref]
                log.debug("Checking to see if the ref %s is a branch with `%s`", ref, " ".join(cmd))
                _, output, _ = SCM._run_without_retry(cmd)
            except UnprocessableEntity:
                log.debug("The ref %s is not a branch. Checking to see if it's a commit hash", ref)
                # The call below will either return the commit hash as is (if a full one was
                # provided) or the full commit hash (if a short hash was provided). If ref is not
                # a commit hash, then this will raise an exception.
                return self.get_full_commit_hash(commit_hash=ref)
            else:
                # git-ls-remote prints output like this, where the first commit
                # hash is what to return.
                # bf028e573e7c18533d89c7873a411de92d4d913e	refs/heads/master
                return output.split()[0].decode("utf-8")
        else:
            raise RuntimeError("get_latest: Unhandled SCM scheme.")

    def get_full_commit_hash(self, commit_hash=None):
        """
        Takes a shortened commit hash and returns the full hash
        :param commit_hash: a shortened commit hash. If not specified, the
        one in the URL will be used
        :return: string of the full commit hash
        """
        if commit_hash:
            commit_to_check = commit_hash
        elif self._commit:
            commit_to_check = self._commit
        else:
            try:
                # If self._commit was None, then calling `self.commit` will resolve the ref based
                # on the branch
                return self.commit
            except UnprocessableEntity:
                # If there was an exception resolving the ref based on the branch (could be the
                # default branch that doesn't exist), then there is not enough information to get
                # the commit hash
                raise RuntimeError('No commit hash was specified for "{0}"'.format(self.url))

        if self.scheme == "git":
            log.debug(
                "Getting the full commit hash on %s from %s", self.repository, commit_to_check)
            td = None
            try:
                td = tempfile.mkdtemp()
                SCM._run(["git", "clone", "-q", self.repository, td, "--bare"])
                cmd = ["git", "rev-parse", commit_to_check]
                log.debug(
                    "Running `%s` to get the full commit hash for %s",
                    " ".join(cmd),
                    commit_to_check
                )
                output = SCM._run(cmd, chdir=td)[1]
            finally:
                if td and os.path.exists(td):
                    shutil.rmtree(td)

            if output:
                return str(output.decode("utf-8").strip("\n"))

            raise UnprocessableEntity(
                'The full commit hash of "{0}" for "{1}" could not be found'.format(
                    commit_hash, self.repository)
            )
        else:
            raise RuntimeError("get_full_commit_hash: Unhandled SCM scheme.")

    def get_module_yaml(self):
        """
        Get full path to the module's YAML file.

        :return: path as a string
        :raises UnprocessableEntity
        """
        if not self.sourcedir:
            raise ProgrammingError("Do .checkout() first.")

        path_to_yaml = os.path.join(self.sourcedir, (self.name + ".yaml"))
        try:
            with open(path_to_yaml):
                return path_to_yaml
        except IOError:
            log.error(
                "get_module_yaml: The SCM repository doesn't contain a modulemd file. "
                "Couldn't access: %s" % path_to_yaml
            )
            raise UnprocessableEntity("The SCM repository doesn't contain a modulemd file")

    @staticmethod
    def is_full_commit_hash(scheme, commit):
        """
        Determines if a commit hash is the full commit hash. For instance, if
        the scheme is git, it will determine if the commit is a full SHA1 hash
        :param scheme: a string containing the SCM type (e.g. git)
        :param commit: a string containing the commit
        :return: boolean
        """
        if scheme == "git":
            sha1_pattern = re.compile(r"^[0-9a-f]{40}$")
            return bool(re.match(sha1_pattern, commit))
        else:
            raise RuntimeError("is_full_commit_hash: Unhandled SCM scheme.")

    @property
    def commit(self):
        """The commit ID, for example the git hash, or None."""
        if not self._commit:
            self._commit = self.get_latest(self.branch)

        return self._commit

    @commit.setter
    def commit(self, s):
        self._commit = str(s) if s else None
