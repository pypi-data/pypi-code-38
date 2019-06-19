'''
 Copyright 2013-2019 Cofense, Inc.  All rights reserved.

 This software is provided by PhishMe, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
 including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
 disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
 consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
 this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.
'''
from __future__ import unicode_literals, absolute_import


import json
import logging
import sys
import sqlite3


# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]


class SQLite(object):
    """

    """

    def __init__(self, location, data_retention_days):
        """
        Initialize a SQLite object

        :param str location: Filesystem location to write SQLite database to
        :param int data_retention_days: Number of days to retain data in SQLite database
        """

        self.db_location = location
        self.data_retention_days = data_retention_days
        self.logger = logging.getLogger(__name__)
        self.updated_threat_intel = False

        self.con = sqlite3.connect(self.db_location)

        # Create tables if they don't already exist
        with self.con:
            cur = self.con.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS threats(
                    threat_type TEXT,
                    threat_id INTEGER,
                    last_modified INTEGER,
                    json TEXT,
                    revision INTEGER DEFAULT 1,
                    UNIQUE(threat_type, threat_id) ON CONFLICT REPLACE
                )
                """
                        )

        # Delete any old ThreatReport IDs.
        self.updated_threat_intel = self._apply_retention()

    def add_threat_id(self, intel):
        """
        Add PhishMe Intelligence ThreatReport ID data to SQLite database

        :param intel: PhishMe Intelligence ThreatReport ID data object
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        :return: None
        """

        with self.con:
            cur = self.con.cursor()
            sql_insert_threat = """INSERT INTO threats
                                    (threat_type, threat_id, last_modified, json, revision)
                                VALUES
                                    (:threat_type, :threat_id, :last_modified, :json, (COALESCE((SELECT revision FROM threats WHERE threat_type="malware" AND threat_id=:threat_id), 0) + 1)
                                )"""

            values = {
                'threat_type': 'malware',
                'threat_id': intel.threat_id,
                'last_modified': intel.last_published,
                'json': json.dumps(intel.json)
            }

            cur.execute(sql_insert_threat, values)

    def get_threats(self):
        """
        Generator method to return ThreatReport ID JSON data from SQLite database

        :return: (generator) ThreatReport ID JSON data
        :rtype: dict
        """

        with self.con:
            dummy = self.con.cursor()

            for result in self.con.execute('SELECT '
                                                'threat_id, '
                                                'json, '
                                                'revision '
                                             'FROM '
                                                'threats '
                                             'WHERE '
                                                'threat_type = "malware" '
                                             'ORDER BY '
                                                'threat_id'):

                json_data = json.loads(result[1])

                yield json_data

    def _apply_retention(self):
        """
        Delete all items in SQLite database outside retention policy.

        :return: Whether or not rows were deleted
        :rtype: bool
        """

        # Delete all items older than TTL from config file
        rows_deleted = self.con.execute('DELETE FROM '
                                        'threats '
                                   'WHERE '
                                        'datetime(last_modified / 1000, "unixepoch") < datetime("now", "-' + str(self.data_retention_days) + ' day")').rowcount

        self.logger.info('Deleted ' + str(rows_deleted) + ' ThreatReport IDs from sqlite db over ' + str(self.data_retention_days) + ' days old.')

        # Recover lost space
        self.con.execute('VACUUM')

        # If rows were deleted, report it.
        if rows_deleted > 0:
            return True
        else:
            return False
