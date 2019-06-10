# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 SerialLab Corp.  All rights reserved.
from quartet_masterdata.models import Company, Location


class DBProxy:
    """
    Performs common database operations.
    """

    def get_epcis_master_data_locations(self, sgln_list: []):
        """
        Will create a list of vocabulary elements for gs1 locations
        :return: A dictionary with the key being the sgln and a dictionary
        as the value.
        """
        db_records = {}
        for sgln in sgln_list:
            location = self._partner_by_sgln(sgln=sgln)
            if location and len(location) > 0:
                # there will only ever be one
                db_records[sgln] = location[0]
        return db_records

    def _partner_by_sgln(self, sgln: str):
        qd = Company.objects.filter(SGLN=sgln)
        partner = None
        if qd.exists():
            partner = qd.values()
        else:
            qd = Location.objects.filter(SGLN=sgln)
            if qd.exists():
                partner = qd.values()
        return partner
