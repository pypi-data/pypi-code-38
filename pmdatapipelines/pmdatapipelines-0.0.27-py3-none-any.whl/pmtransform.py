import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import io
import re
import json

def convert_string_to_object(content_string):

	def stream_content(content_string):
		for m in re.finditer('\}\n\{', content_string):
			yield m.start(), m.end()

	try:
		_i = 0
		content_object = []
		for i, j in stream_content(content_string):
			event = flatten_json(json.loads(content_string[_i:i+1]))
			content_object.append(event)
			_i = j-1

		event = flatten_json(json.loads(content_string[_i:]))
		content_object.append(event)
		return content_object

	except ValueError as e:
		return 'not valid json'


def flatten_json(y):
	out = {}

	def flatten(x, name=''):

		if name[:-1] == 'customParameters':
			for a in x:
				out['cp_' + a['group']] = a['item']
		if name[:-1] == 'userparameters':
			for a in x:
				out['up_' + a['group']] = a['item']
		elif name[:-1] == 'externaluserids':
			for a in x:
				out['extid_' + a['type']] = a['id']

		elif type(x) is dict:
			for a in x:
				flatten(x[a], name + a + '_')
		elif type(x) is list:
			i = 0
			for a in x:
				flatten(a, name + str(i) + '_')
				i += 1
		else:
			out[str(name[:-1])] = str(x)

	flatten(y)
	return out


def lower_keys(x):
	# print(x)
	if isinstance(x, list):
		return [lower_keys(v) for v in x]
	elif isinstance(x, dict):
		return dict((k.lower(), lower_keys(v)) for k,v in x.items())
	else:
		return x


def convert_object_to_parquet(content_object, b_io_buffer=io.BytesIO()):

	df = pd.DataFrame(content_object)
	# print("writing to pyarrow table")
	table = pa.Table.from_pandas(df.fillna('').astype(str))
	# print("writing to parquet")
	pq.write_table(table, b_io_buffer)

	return b_io_buffer