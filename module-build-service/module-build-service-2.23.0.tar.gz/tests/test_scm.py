# Copyright (c) 2017  Red Hat, Inc.
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
# Written by Ralph Bean <rbean@redhat.com>

import os
import shutil
import tempfile

import pytest

import module_build_service.scm
from module_build_service.errors import ValidationError, UnprocessableEntity

base_dir = os.path.join(os.path.dirname(__file__), "scm_data")
repo_url = "file://" + base_dir + "/testrepo"


class TestSCMModule:
    def setup_method(self, test_method):
        self.tempdir = tempfile.mkdtemp()
        self.repodir = self.tempdir + "/testrepo"

    def teardown_method(self, test_method):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_simple_local_checkout(self):
        """ See if we can clone a local git repo. """
        scm = module_build_service.scm.SCM(repo_url)
        scm.checkout(self.tempdir)
        files = os.listdir(self.repodir)
        assert "foo" in files, "foo not in %r" % files

    def test_local_get_latest_is_sane(self):
        """ See that a hash is returned by scm.get_latest. """
        scm = module_build_service.scm.SCM(repo_url)
        latest = scm.get_latest("master")
        target = "5481faa232d66589e660cc301179867fb00842c9"
        assert latest == target, "%r != %r" % (latest, target)

    def test_local_get_latest_commit_hash_is_sane(self):
        """ See that a hash is returned by scm.get_latest. """
        scm = module_build_service.scm.SCM(repo_url)
        latest = scm.get_latest("5481f")
        target = "5481faa232d66589e660cc301179867fb00842c9"
        assert latest == target, "%r != %r" % (latest, target)

    def test_local_get_latest_unclean_input(self):
        """ Ensure that shell characters aren't handled poorly.

        https://pagure.io/fm-orchestrator/issue/329
        """
        scm = module_build_service.scm.SCM(repo_url)
        assert scm.scheme == "git", scm.scheme
        fname = tempfile.mktemp(suffix="mbs-scm-test")
        try:
            scm.get_latest("master; touch %s" % fname)
        except UnprocessableEntity:
            assert not os.path.exists(fname), "%r exists!  Vulnerable." % fname

    def test_local_extract_name(self):
        scm = module_build_service.scm.SCM(repo_url)
        target = "testrepo"
        assert scm.name == target, "%r != %r" % (scm.name, target)

    def test_local_extract_name_trailing_slash(self):
        scm = module_build_service.scm.SCM(repo_url + "/")
        target = "testrepo"
        assert scm.name == target, "%r != %r" % (scm.name, target)

    def test_verify(self):
        scm = module_build_service.scm.SCM(repo_url)
        scm.checkout(self.tempdir)
        scm.verify()

    def test_verify_unknown_branch(self):
        with pytest.raises(UnprocessableEntity):
            scm = module_build_service.scm.SCM(repo_url, "unknown")
            # Accessing the commit property will cause the commit to be resolved, causing an
            # exception
            scm.commit

    def test_verify_commit_in_branch(self):
        target = "7035bd33614972ac66559ac1fdd019ff6027ad21"
        scm = module_build_service.scm.SCM(repo_url + "?#" + target, "dev")
        scm.checkout(self.tempdir)
        scm.verify()

    def test_verify_commit_not_in_branch(self):
        target = "7035bd33614972ac66559ac1fdd019ff6027ad21"
        scm = module_build_service.scm.SCM(repo_url + "?#" + target, "master")
        scm.checkout(self.tempdir)
        with pytest.raises(ValidationError):
            scm.verify()

    def test_verify_unknown_hash(self):
        target = "7035bd33614972ac66559ac1fdd019ff6027ad22"
        scm = module_build_service.scm.SCM(repo_url + "?#" + target, "master")
        with pytest.raises(UnprocessableEntity):
            scm.checkout(self.tempdir)

    def test_get_module_yaml(self):
        scm = module_build_service.scm.SCM(repo_url)
        scm.checkout(self.tempdir)
        scm.verify()
        with pytest.raises(UnprocessableEntity):
            scm.get_module_yaml()

    def test_get_latest_incorrect_component_branch(self):
        scm = module_build_service.scm.SCM(repo_url)
        with pytest.raises(UnprocessableEntity):
            scm.get_latest("foobar")

    def test_get_latest_component_branch(self):
        ref = "5481faa232d66589e660cc301179867fb00842c9"
        branch = "master"
        scm = module_build_service.scm.SCM(repo_url)
        commit = scm.get_latest(branch)
        assert commit == ref

    def test_get_latest_component_ref(self):
        ref = "5481faa232d66589e660cc301179867fb00842c9"
        scm = module_build_service.scm.SCM(repo_url)
        commit = scm.get_latest(ref)
        assert commit == ref

    def test_get_latest_incorrect_component_ref(self):
        scm = module_build_service.scm.SCM(repo_url)
        with pytest.raises(UnprocessableEntity):
            scm.get_latest("15481faa232d66589e660cc301179867fb00842c9")
