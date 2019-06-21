import boto3
from botocore.exceptions import ClientError
from urllib.parse import unquote

def parse_s3_event(event):

	try:
		s3_event = event['Records'][0]['s3']
		s3_key = unquote(s3_event['object']['key'])
		s3_bucket_name = s3_event['bucket']['name']
		return { 'type': 's3_event', 's3_key': s3_key, 's3_bucket_name': s3_bucket_name }
	except:
		print(event)
		if 's3_key' in event and 's3_bucket_name' in event:
			print('manual_event')
			s3_key = event['s3_key']
			s3_bucket_name = event['s3_bucket_name']
			return { 'type': 'manual_event', 's3_key': s3_key, 's3_bucket_name': s3_bucket_name }
		else:
			raise KeyError('did not find s3_key and s3_bucket_name in event')


def upload_transformed_data_to_s3(b_io_buffer, source_s3_key, source_s3_bucket_name):

	target_s3_key = s3key.replace("raw", "transformed")
	target_s3_bucket_name = source_s3_bucket_name
	b_io_buffer.seek(0)
	try:
		target_bucket.upload_fileobj(b_io_buffer, target_s3_key)
		return 'success'
	except ClientError as e:
		raise Exception(e.response['Error']['Code'])


def upload_converted_data_to_s3(b_io_buffer, source_s3_key, source_s3_bucket_name):

	target_s3_key = s3key.replace("transformed", "queryable")
	target_s3_bucket_name = source_s3_bucket_name
	b_io_buffer.seek(0)
	try:
		target_bucket.upload_fileobj(b_io_buffer, target_key)
		return 'success'
	except ClientError as e:
		raise Exception(e.response['Error']['Code'])


def add_new_partition(s3_bucket_name, s3_key, table_name, database_name):

	# Initiate Glue and Athena clients
	glue_client = boto3.client('glue')
	response = glue_client.get_partitions(
		DatabaseName=database_name,
		TableName=table_name,
	)
	athena_client = boto3.client('athena')

	# Get existing partitions from glue-table
	existing_partition_values = []
	for p in response['Partitions']:
		existing_partition_values.append(p['Values'])

	# Extract the partitions from the new file
	s3_key_parts = s3_key.split('/')
	s3_key_location = '/'.join(s3_key_parts[:-1])
	new_partition = []
	for part in s3_key_parts:
		if '=' in part:
			new_partition.append(part.split('='))
	print(new_partition)

	# If there are no partitions in the s3-key, return and exit
	if len(new_partition) == 0:
		print('no partitions to add')
		return

	# Check if partition already exist in the table.
	# If partition already in the table, return and exit lambda-function
	new_partition_values = []
	for key, value in new_partition:
		new_partition_values.append(value)
	if new_partition_values in existing_partition_values:
		print(new_partition_values, 'already in existsing partitions')
		print(existing_partition_values)
		return

	print("adding new partition")
	# build the athena query
	athena_query = '''
	ALTER TABLE {} ADD
	'''.format(table_name)
	partition_string = ''
	for key, value in new_partition:
		partition_string += '{} = \'{}\', '.format(key, value)
	partition_string = partition_string[:-2]
	athena_query += 'PARTITION (' + partition_string + ')' + '\n'
	athena_query += 'LOCATION \'s3://{}/{}\''.format(s3_bucket_name, s3_key_location)
	athena_query += ';'
	athena_client = boto3.client('athena')
	response = athena_client.start_query_execution(
		QueryString = athena_query,
		QueryExecutionContext={
			"Database": database_name
		},
		ResultConfiguration = {
			"OutputLocation": "s3://{}/athena_output".format(s3_bucket_name)
		}
	)

	print(response)
	return