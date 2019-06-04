import snowflake.connector
import pandas as pd


def get_data(query, user=None, password=None, account=None, warehouse=None, connection=None):
	"""
	Usage from Tweety:
		e.g. query_as_df('select * from analytics.twitter.tweets limit 100')
	"""

	# You can simply change this to your Snowflake username & password if you don't need to use 'DATALOADER'

	print(query)
	if connection is None:
		connection = snowflake.connector.connect(user=user, password=password, account=account)
		connection_is_temporary = True
	else:
		connection_is_temporary = False

	try:
		connection.cursor().execute(f"use warehouse {warehouse}")
		connection.cursor().execute(f"use database analytics")

		cur = connection.cursor().execute(query)
		df = pd.DataFrame.from_records(iter(cur), columns=[x[0] for x in cur.description])
		df.columns = [x.lower() for x in df.columns]
		return df
	finally:
		connection.cursor().close()
		if connection_is_temporary:
			connection.close()