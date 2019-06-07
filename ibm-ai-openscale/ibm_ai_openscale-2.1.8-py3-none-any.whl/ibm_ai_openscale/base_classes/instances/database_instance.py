# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from .instance import Instance

class DatabaseInstance(Instance):
    def __init__(self, credentials, database_type):
        Instance.__init__(self, credentials)
        self._database_type = database_type

    def _get_payload(self):
        return {
          "database_type": self._database_type,
          "credentials": self.credentials
        }