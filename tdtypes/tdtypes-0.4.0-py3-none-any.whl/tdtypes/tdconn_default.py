"Default Teradata connection function"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2018, Paresh Adhia"

# A connection module requires:
# -----------------------------
# 1) DB API names to be imported
# 2) dbconnect() function that returns a raw database connection

from teradatasql import *

def dbconnect(tdconn=None):
	"""Returns a raw database connection object

	Args:
		tdconn: An optional JSON object encoded as string that has connection information as
			expected by teradatasql.connect(). If omitted and if TDCONN environment variable
			is available, it will be used instead. Finally, a default value that uses dbc as
			host, user and password will be used.

	Returns:
		teraatasql.connect() object
	"""

	if tdconn is None:
		import os
		tdconn = os.environ.get('TDCONN', '{"host": "dbc", "user": "dbc", "password": "dbc"}')

	return connect(tdconn)
