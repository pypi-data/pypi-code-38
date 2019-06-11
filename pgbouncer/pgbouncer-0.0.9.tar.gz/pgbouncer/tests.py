#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from contextlib import closing

import fixtures
from postgresfixture import ClusterFixture
from postgresfixture.cluster import PG_VERSIONS
import psycopg2
import testscenarios
import testtools

from pgbouncer.fixture import PGBouncerFixture


class TestFixture(testscenarios.WithScenarios, testtools.TestCase):

    scenarios = sorted(
        (version, {'version': version}) for version in PG_VERSIONS)

    def setUp(self):
        super(TestFixture, self).setUp()
        datadir = self.useFixture(fixtures.TempDir()).path
        self.dbname = 'test_pgbouncer'
        self.cluster = self.useFixture(
            ClusterFixture(datadir, version=self.version))
        self.cluster.createdb(self.dbname)
        with closing(self.cluster.connect()) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute('DROP USER IF EXISTS user1')
                cur.execute('CREATE USER user1')
        self.bouncer = PGBouncerFixture()
        self.bouncer.databases[self.dbname] = 'host=' + datadir
        self.bouncer.users['user1'] = ''

    def connect(self, host=None):
        return psycopg2.connect(
            host=(self.bouncer.host if host is None else host),
            port=self.bouncer.port, database=self.dbname,
            user='user1')

    def test_dynamic_port_allocation(self):
        self.useFixture(self.bouncer)
        self.connect().close()

    def test_stop_start_facility(self):
        # Once setup the fixture can be stopped, and started again, retaining
        # its configuration. [Note that dynamically allocated ports could
        # potentially be used by a different process, so this isn't perfect,
        # but its pretty reliable as a test helper, and manual port allocation
        # outside the dynamic range should be fine.
        self.useFixture(self.bouncer)
        self.bouncer.stop()
        self.assertRaises(psycopg2.OperationalError, self.connect)
        self.bouncer.start()
        self.connect().close()

    def test_unix_sockets(self):
        unix_socket_dir = self.useFixture(fixtures.TempDir()).path
        self.bouncer.unix_socket_dir = unix_socket_dir
        self.useFixture(self.bouncer)
        # Connect to pgbouncer via a Unix domain socket. We don't
        # care how pgbouncer connects to PostgreSQL.
        self.connect(host=unix_socket_dir).close()

    def test_is_running(self):
        # The is_running property indicates if pgbouncer has been started and
        # has not yet exited.
        self.assertFalse(self.bouncer.is_running)
        with self.bouncer:
            self.assertTrue(self.bouncer.is_running)
        self.assertFalse(self.bouncer.is_running)

    def test_dont_start_if_already_started(self):
        # If pgbouncer is already running, don't start another one.
        self.useFixture(self.bouncer)
        bouncer_pid = self.bouncer.process.pid
        self.bouncer.start()
        self.assertEqual(bouncer_pid, self.bouncer.process.pid)
