#!/usr/bin/env python3
import os
import json
import singer
import datetime
import time

from singer import utils, metadata
from tap_annie.api_annie import app_rating, product_sales, product_store_metrics
from tap_annie.checker import check_date


REQUIRED_CONFIG_KEYS = ["android_account_id", "android_product_id", "ios_account_id", "ios_product_id", "API_key"]
LOGGER = singer.get_logger()

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

# Load schemas from schemas folder
def load_schemas():
    schemas = {}

    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = json.load(file)

    return schemas
    
def load_metadata(schema,key_properties=None,replication_keys=None):
    return [
            {
                "metadata":{
                    'replication-method':'INCREMENTAL',
                    'selected': True,
                    'schema-name':schema,
                    'valid-replication-keys': replication_keys,
                    'table-key-properties': key_properties,
                    "inclusion": "available",
                },
                "breadcrumb": []
            }
        ]

def discover():
    raw_schemas = load_schemas()
    streams = []

    for schema_name, schema in raw_schemas.items():

        # TODO: populate any metadata and stream's key properties here..
        stream_metadata = []
        stream_key_properties = []

        if schema_name=="app_ratings":
            replication_keys=['country']
            key_properties=['country']
            stream_metadata=load_metadata(schema_name,key_properties,replication_keys)

        if schema_name=="product_sales":
            replication_keys=['country']
            key_properties=['country']
            stream_metadata=load_metadata(schema_name,key_properties,replication_keys)

        if schema_name=="product_store_metrics":
            replication_keys=['country']
            key_properties=['country']
            stream_metadata=load_metadata(schema_name,key_properties,replication_keys)
        # create and add catalog entry
        catalog_entry = {
            'stream': schema_name,
            'tap_stream_id': schema_name,
            'schema': schema,
            'metadata' : stream_metadata,
            'key_properties': key_properties
        }
        streams.append(catalog_entry)

    return {'streams': streams}

def get_selected_streams(catalog):
    '''
    Gets selected streams.  Checks schema's 'selected' first (legacy)
    and then checks metadata (current), looking for an empty breadcrumb
    and mdata with a 'selected' entry
    '''
    selected_streams = []
    for stream in catalog['streams']:
        stream_metadata = metadata.to_map(stream['metadata'])
        # stream metadata will have an empty breadcrumb
        if metadata.get(stream_metadata, (), "selected"):
            selected_streams.append(stream['tap_stream_id'])

    return selected_streams

def sync(config, state, catalog):
    selected_stream_ids = get_selected_streams(catalog)
    
    # Loop over streams in catalog
    for stream in catalog['streams']:
        stream_id = stream['tap_stream_id']
        stream_schema = stream['schema']

        API_key = config['API_key']
        ios_account_id = config['ios_account_id']
        ios_product_id = config['ios_product_id']
        android_account_id = config['android_account_id']
        android_product_id = config['android_product_id']
        delta_import = config['delta_import']
        reload_data = config['reload_data']
        days = 2
        if stream_id in selected_stream_ids:
            # TODO: sync code for stream goes here...
            singer.write_schema(stream_id, stream_schema, stream['key_properties'])
            records = handle(stream_id, stream_schema, API_key, ios_account_id, ios_product_id, android_account_id, android_product_id, delta_import, reload_data, days)
            if len(records)==0:
                LOGGER.info("{}: There is no data to stream".format(stream_id))
            else:    
                for record in records:  
                    singer.write_record(stream_id, record)
            LOGGER.info('Syncing stream:' + stream_id)
    return

def handle_key(stream_id, key, record):
    if stream_id == "app_ratings":
        parts = ['current_ratings','all_ratings']
        for part in parts:
            if part in key:
                key = key.replace(part+"_","")
                temp = record.get(part)
                if temp is not None:
                    return temp.get(key)
                else:
                    return None
        return record.get(key)
    if stream_id == "product_sales":
        key_array = key.split("_")
        if len(key_array) > 1:
            for i in range(0,len(key_array)):
                if i==len(key_array)-1:
                    return record.get(key_array[i])
                else:
                    record = record[key_array[i]]

        return record.get(key_array[0])
    if stream_id == "product_store_metrics":
        return record.get(key)


def handle(stream_id, stream_schema, API_key, ios_account_id, ios_product_id, android_account_id, android_product_id, check_delta_import, reload_data, days):
    filename = "credential.json" #provide information to check the date on GBQ
    project_id = "ga360-173318" 
    if stream_id == "app_ratings":
        if reload_data is not False:
            return []
        corrected_records = []
        product_ids = [ios_product_id, android_product_id]
        for product_id in product_ids:
            repsonse = app_rating(product_id, API_key)
            while repsonse['code'] != 200:
                LOGGER.error(repsonse['error'])
                repsonse = app_rating(product_id, API_key)
                time.sleep(30)

            records = repsonse['ratings']
            platform = "iOS" if product_id == "577251728" else "Android"
            for record in records:
                temp = {}
                for key in stream_schema['properties']:
                    if key == "platform":
                        temp.update({key: platform})
                    else:
                        data_1 = handle_key(stream_id, key, record)
                        if data_1 is None:
                            if stream_schema['properties'][key]['type'][1] == "string":
                                data_1 = ""
                            data_1 = 0
                        temp.update({key: data_1})
                corrected_records.append(temp)
        return corrected_records











    if stream_id =="product_sales":

        end_date = (datetime.datetime.now()- datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        start_date = end_date
 
        if reload_data is not False:
            try:
                sub_day = int(reload_data)
                now = datetime.datetime.now()- datetime.timedelta(days=sub_day)
                start_date = "{}-{}-{}".format(now.year,now.month,now.day)
            except:
                LOGGER.error("Reload value is not correct")

        corrected_records = []
        product_ids = [ios_product_id, android_product_id]
        
        #Handle data
        for product_id in product_ids:
            account_id = "534323" if product_id == "577251728" else "537092"
            platform = "iOS" if product_id == "577251728" else "Android"        
            if check_delta_import is not False: #Load delta and check previous days
                n = 1
                while n < 10:
                    date_to_check = (datetime.datetime.now()- datetime.timedelta(days=days+n)).strftime('%Y-%m-%d')
                    LOGGER.info("Checking sales_list - {} - {}".format(date_to_check, platform))
                    result = check_date(date_to_check, filename, project_id, platform)
                    if result == 0:
                        LOGGER.info("There is missing data of {} - platform {}".format( date_to_check, platform))
                        repsonse = product_sales(account_id, product_id, API_key, date_to_check, date_to_check, check_delta_import)
                        sales_list = repsonse['sales_list']
                        for record in sales_list:
                            temp = {}
                            for key in stream_schema['properties']:
                                if key == "platform":
                                        temp.update({key: platform})
                                else:
                                    data_1 = handle_key(stream_id, key, record)
                                    if data_1 is None:
                                        if stream_schema['properties'][key]['type'][1] == "string":
                                            data_1 = ""
                                        data_1 = 0
                                    if stream_schema['properties'][key]['type'][1] == "string":
                                        data_1 =  str(data_1)      
                                    if stream_schema['properties'][key]['type'][1] == "integer":
                                        try:
                                            data_1 =  int(data_1)
                                        except:
                                            raise                        
                                    temp.update({key: data_1})
                                    if key == "date":
                                        temp.update({key: data_1+"T00:00:00Z"}) 
                            corrected_records.append(temp)
                    n+=1

            LOGGER.info("--------------------")
            LOGGER.info("{}---{}---{}".format(start_date,end_date, platform))
            LOGGER.info("--------------------")
            time.sleep(5)
            repsonse = product_sales(account_id, product_id, API_key, start_date, end_date, check_delta_import)

            sales_list = repsonse['sales_list']
            for record in sales_list:
                temp = {}
                for key in stream_schema['properties']:
                    if key == "platform":
                            temp.update({key: platform})
                    else:
                        data_1 = handle_key(stream_id, key, record)
                        if data_1 is None:
                            if stream_schema['properties'][key]['type'][1] == "string":
                                data_1 = ""
                            data_1 = 0
                        if stream_schema['properties'][key]['type'][1] == "string":
                            data_1 =  str(data_1)      
                        if stream_schema['properties'][key]['type'][1] == "integer":
                            try:
                                data_1 =  int(data_1)
                            except:
                                raise                        
                        temp.update({key: data_1})
                        if key == "date":
                            temp.update({key: data_1+"T00:00:00Z"}) 
                corrected_records.append(temp)
        return corrected_records








    if stream_id =="product_store_metrics":
        end_date = (datetime.datetime.now()- datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        start_date = end_date

        if reload_data is not False:
            try:
                sub_day = int(reload_data)
                now = datetime.datetime.now()- datetime.timedelta(days=sub_day)
                start_date = "{}-{}-{}".format(now.year,now.month,now.day)
            except:
                LOGGER.error("Reload value is not correct")

        corrected_records = []
        product_ids = [ios_product_id, android_product_id]

        for product_id in product_ids:
            account_id = "534323" if product_id == "577251728" else "537092"
            platform = "iOS" if product_id == "577251728" else "Android"

            if check_delta_import is not False:
                n = 1
                while n < 10:
                    date_to_check = (datetime.datetime.now()- datetime.timedelta(days=days+n)).strftime('%Y-%m-%d')
                    LOGGER.info("Checking metrics_list - {} - {}".format(date_to_check, platform))
                    result = check_date(date_to_check, filename, project_id, platform)
                    if result == 0:
                        LOGGER.info("There is missing data of {} - platform {}".format( date_to_check, platform))
                        repsonse = product_store_metrics(account_id, product_id, API_key, date_to_check, date_to_check, check_delta_import)
                        metrics_list = repsonse['metrics_list']
                        for record in metrics_list:
                            temp = {}
                            for key in stream_schema['properties']:
                                if key == "platform":
                                        temp.update({key: platform})
                                else:
                                    data_1 = handle_key(stream_id, key, record)
                                    if data_1 is None:
                                        if stream_schema['properties'][key]['type'][1] == "string":
                                            data_1 = ""
                                        data_1 = 0
                                    if stream_schema['properties'][key]['type'][1] == "string":
                                        data_1 =  str(data_1)      
                                    if stream_schema['properties'][key]['type'][1] == "integer":
                                        try:
                                            data_1 =  int(data_1)
                                        except:
                                            raise                        
                                    temp.update({key: data_1})
                                    if key == "date":
                                        temp.update({key: data_1+"T00:00:00Z"})
                            corrected_records.append(temp)
                    n+=1

            LOGGER.info("--------------------")
            LOGGER.info("{}---{}---{}".format(start_date,end_date, platform))
            LOGGER.info("--------------------")
            time.sleep(5)

            repsonse = product_store_metrics(account_id, product_id, API_key, start_date, end_date, check_delta_import)
            
            metrics_list = repsonse['metrics_list']
            for record in metrics_list:
                temp = {}
                for key in stream_schema['properties']:
                    if key == "platform":
                            temp.update({key: platform})
                    else:
                        data_1 = handle_key(stream_id, key, record)
                        if data_1 is None:
                            if stream_schema['properties'][key]['type'][1] == "string":
                                data_1 = ""
                            data_1 = 0
                        if stream_schema['properties'][key]['type'][1] == "string":
                            data_1 =  str(data_1)      
                        if stream_schema['properties'][key]['type'][1] == "integer":
                            try:
                                data_1 =  int(data_1)
                            except:
                                raise                        
                        temp.update({key: data_1})
                        if key == "date":
                            temp.update({key: data_1+"T00:00:00Z"})
                corrected_records.append(temp)
        return corrected_records

@utils.handle_top_exception(LOGGER)
def main():

    # Parse command line arguments
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover()
        print(json.dumps(catalog, indent=2))
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog =  discover()

        sync(args.config, args.state, catalog)

if __name__ == "__main__":
    main()
