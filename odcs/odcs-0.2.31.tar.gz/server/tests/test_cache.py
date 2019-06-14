# Copyright (c) 2018  Red Hat, Inc.
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
# Written by Jan Kaluza <jkaluza@redhat.com>

import time
import os
from mock import patch

from .utils import ModelsBaseTest
from odcs.server import db, conf
from odcs.server.cache import KojiTagCache
from odcs.server.models import Compose
from odcs.common.types import (
    COMPOSE_RESULTS, COMPOSE_STATES, PungiSourceType)


class TestKojiTagCache(ModelsBaseTest):

    def setUp(self):
        super(TestKojiTagCache, self).setUp()
        self.cache = KojiTagCache()

    def test_cached_compose_dir(self):
        c = Compose.create(
            db.session, "me", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 3600)
        ret = self.cache.cached_compose_dir(c)
        expected = os.path.join(conf.target_dir, "koji_tag_cache/f26-0--x86_64")
        self.assertEqual(ret, expected)

    def test_compose_dir_flags(self):
        c = Compose.create(
            db.session, "me", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 3600, flags=1)
        ret = self.cache.cached_compose_dir(c)
        expected = os.path.join(conf.target_dir, "koji_tag_cache/f26-1--x86_64")
        self.assertEqual(ret, expected)

    def test_compose_dir_sigkeys(self):
        c = Compose.create(
            db.session, "me", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 3600, flags=1,
            sigkeys="a b c")
        ret = self.cache.cached_compose_dir(c)
        expected = os.path.join(conf.target_dir, "koji_tag_cache/f26-1-a-b-c-x86_64")
        self.assertEqual(ret, expected)

    def test_compose_dir_sigkeys_arches_unsorted(self):
        c = Compose.create(
            db.session, "me", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 3600, flags=1,
            sigkeys="c b a", arches="i686 x86_64")
        ret = self.cache.cached_compose_dir(c)
        expected = os.path.join(conf.target_dir, "koji_tag_cache/f26-1-a-b-c-i686-x86_64")
        self.assertEqual(ret, expected)

    @patch("os.path.exists")
    def test_is_cached(self, exists):
        c = Compose.create(
            db.session, "me", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 3600)

        for cached in [True, False]:
            exists.return_value = cached
            ret = self.cache.is_cached(c)
            self.assertEqual(ret, cached)
            exists.assert_called_once_with(
                os.path.join(conf.target_dir, "koji_tag_cache/f26-0--x86_64"))
            exists.reset_mock()

    @patch("shutil.copytree")
    def test_reuse_cached(self, copytree):
        c = Compose.create(
            db.session, "me", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 3600)
        db.session.add(c)
        db.session.commit()
        self.cache.reuse_cached(c)
        copytree.assert_called_once_with(
            os.path.join(conf.target_dir, "koji_tag_cache/f26-0--x86_64"),
            os.path.join(conf.target_dir, "koji_tag_cache/odcs-1-1-19700101.n.0"),
            symlinks=True)

    @patch("shutil.copytree")
    @patch("os.path.realpath")
    @patch("shutil.rmtree")
    def test_update_cache(self, rmtree, realpath, copytree):
        realpath.return_value = "/tmp/real/path"
        c = Compose.create(
            db.session, "me", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 3600)
        db.session.add(c)
        db.session.commit()
        for done in [True, False]:
            c.state = COMPOSE_STATES["done"] if done else COMPOSE_STATES["failed"]
            self.cache.update_cache(c)
            if done:
                copytree.assert_called_once_with(
                    "/tmp/real/path",
                    os.path.join(conf.target_dir, "koji_tag_cache/f26-0--x86_64"),
                    symlinks=True)
            else:
                copytree.assert_not_called()
            copytree.reset_mock()
            rmtree.assert_not_called()

    @patch("shutil.copytree")
    @patch("os.path.realpath")
    @patch("shutil.rmtree")
    @patch("os.path.exists")
    def test_update_cache_rmtree_if_exists(self, exists, rmtree, realpath, copytree):
        realpath.return_value = "/tmp/real/path"
        c = Compose.create(
            db.session, "me", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 3600)
        c.state = COMPOSE_STATES["done"]
        db.session.add(c)
        db.session.commit()

        self.cache.update_cache(c)
        rmtree.assert_called_once_with(
            os.path.join(conf.target_dir, "koji_tag_cache/f26-0--x86_64"))

    @patch("os.listdir")
    @patch("os.path.getmtime")
    @patch("shutil.rmtree")
    def test_remove_old_koji_tag_cache_data(self, rmtree, getmtime, listdir):
        now = time.time()
        listdir.return_value = ["foo", "bar"]
        # Default timeout is 30 days, so set 31 for first dir and 29 for
        # second dir.
        getmtime.side_effect = [now - 31 * 24 * 3600, now - 29 * 24 * 3600]

        self.cache.remove_old_koji_tag_cache_data()
        rmtree.assert_called_once_with(
            os.path.join(self.cache.cache_dir, "foo"))

    @patch("os.listdir")
    @patch("os.path.getmtime")
    @patch("shutil.rmtree")
    def test_remove_old_koji_tag_cache_data_getmtime_raises(
            self, rmtree, getmtime, listdir):
        listdir.return_value = ["foo", "bar"]
        getmtime.side_effect = OSError("path does not exist")

        self.cache.remove_old_koji_tag_cache_data()
        rmtree.assert_not_called()
