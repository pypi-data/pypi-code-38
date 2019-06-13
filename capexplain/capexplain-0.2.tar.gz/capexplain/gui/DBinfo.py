"""
get information of databases for corresponding connection
"""
import psycopg2
import pandas as pd 
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s line %(lineno)d: %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

# logging.basicConfig(level=logging.DEBUG,
# 	format='%(asctime)s %(levelname)s line %(lineno)d: %(message)s')


class DBinfo:

	def __init__(self,conn=None):
		self.conn = conn

	def get_table_name(self):  # get table names in current connection

		extract_table_query = """
							  SELECT table_name
							  FROM information_schema.tables
							  WHERE table_schema='public'
							  AND table_type='BASE TABLE';
		                    """
		df_tables = pd.read_sql(extract_table_query, self.conn)

		return (df_tables['table_name'].values.tolist())

	def get_attribute(self,table_name):  # return the attributes of a table as a list

		extract_table_attrs_query = "select CONCAT_WS (' : ', column_name , data_type) as attribute from information_schema.columns where table_name =" + '\''+table_name +'\''
		df_attributes = pd.read_sql(extract_table_attrs_query,self.conn)

		return (df_attributes['attribute'].values.tolist())

	def get_db_info(self):

		extract_table_query = """
							  SELECT table_name
							  FROM information_schema.tables
							  WHERE table_schema='public'
							  AND table_type='BASE TABLE';
		                    """
		df_tables = pd.read_sql(extract_table_query, self.conn)
		df_list = df_tables['table_name'].values.tolist()
		table_dict = dict.fromkeys(df_list,0)
		for table in df_list:
			extract_table_attrs_query = "select column_name as attribute from information_schema.columns where table_name = " + '\''+table+'\''
			table_name_attr = pd.read_sql(extract_table_attrs_query,self.conn)
			table_name_attr_list = table_name_attr['attribute'].values.tolist()
			table_dict[table] = table_name_attr_list

		return table_dict

	def get_db_data_type(self,table_name):

		pg_numeric_list = ['smallint','integer','bigint','decimal','numeric','real','double precision','smallserial','serial','bigserial']
		pg_int_list = ['smallint','integer','bigint','smallserial','serial','bigserial']
		pg_float_list = ['decimal','numeric','real','double precision']
		data_type_query = "SELECT column_name, data_type FROM information_schema.columns"+\
		                  " WHERE table_name = \'"+table_name+"\';"
		data_type_df = pd.read_sql(data_type_query,self.conn)
		logger.debug(data_type_df)
		data_type_list = data_type_df.values.tolist()
		column_name_list = data_type_df.column_name.values.tolist()

		query_data_convert_dict = dict.fromkeys(column_name_list,None)
		plot_data_convert_dict = dict.fromkeys(column_name_list, None)


		for n in data_type_list:
			if(n[1] in pg_numeric_list):
				plot_data_convert_dict[n[0]] = 'numeric'
				if(n[1] in pg_int_list):
					query_data_convert_dict[n[0]]='int'
				else:
					query_data_convert_dict[n[0]]='float'
			else:
				query_data_convert_dict[n[0]] = 'str'
				plot_data_convert_dict[n[0]]='str'

		logger.debug(plot_data_convert_dict)
		logger.debug(query_data_convert_dict)


		return plot_data_convert_dict,query_data_convert_dict


if __name__ == "__main__":
	conn = psycopg2.connect(dbname="antiprov",user="antiprov",host="127.0.0.1",port="5432",password='1234')
	dbinfo = DBinfo(conn)

	dbinfo.get_db_data_type('pub')













