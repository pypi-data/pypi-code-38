from datahelper.s3.s3_data_helper import S3DataHelper
from datahelper.s3.ml_learningdb import s3_path_helper as S3PathHelper
from datahelper.s3.ml_learningdb.s3_path_helper import ETLPathHelper, JobPathHelper, RawDataPathHelper
from datetime import datetime
import json
import os

import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')


class DataHelper(S3DataHelper):

    def __init__(self, config):

        self.config = config['mlcore']['datahelper']['s3']['mllearningdb']
        super().__init__(self.config)
        self.logger = logging.getLogger(self.__class__.__name__)

    def connect(self):
        super().connect()

    #####################################################
    #
    #   updated data
    #
    #####################################################

    def get_latest_s3key(self, keys):
        if len(keys)==0:
            return None

        keys.sort(key=lambda x:x, reverse=True)
        for i in range(0, len(keys)):
            # if (Not _SUCCESS file) and (have corresponding _SUCCESS file)
            s3key = keys[i]
            s3_success_key = '%s%s' % ('/'.join(s3key.split('/')[:-1]), '/_SUCCESS')
            if s3key[-8:]!='_SUCCESS' and s3_success_key in keys:
                return s3key

        return None

    def write_es_rates(self, data_dict):
        if len(data_dict)==0:
            self.logger.warn('Empty input of es rate')
            return

        # upload data to s3
        dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        path = RawDataPathHelper().get_es_rates_dirs(update_time_str=dt_now_str)

        # write local file and upload
        self.mkdir(path['local_dir'])

        json_data = {}
        json_data['data'] = data_dict
        with open('%s/%s.json' % (path['local_dir'], dt_now_str), 'w') as fp:
            json.dump(json_data, fp)
        # upload
        self.upload_folder(path['s3folder'], path['local_dir'])
        # remove local file
        self.rmdir(path['local_dir']) 


    def write_vm_list(self, data_dict):
        if len(data_dict)==0:
            self.logger.warn('Empty input of vm list')
            return

        # upload data to s3
        dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        path = RawDataPathHelper().get_vm_list_dirs(update_time_str=dt_now_str)

        # write local file and upload
        self.mkdir(path['local_dir'])

        json_data = {}
        json_data['data'] = data_dict
        with open('%s/%s.json' % (path['local_dir'], dt_now_str), 'w') as fp:
            json.dump(json_data, fp)
        # upload
        self.upload_folder(path['s3folder'], path['local_dir'])
        # remove local file
        self.rmdir(path['local_dir'])   

    def get_es_rates_s3folder(self):
        # get key
        path = RawDataPathHelper().get_es_rates_dirs()
        prefix = path['s3prefix']
        keys = self.get_keys(prefix)
        s3path = self.get_latest_s3key(keys)

        if s3path == None:
            self.logger.warn('No es_rates')
            return []
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get es_rates s3folder = %s' % s3folder)
            return s3folder

    def get_vm_list_s3folder(self):
        # get key
        path = RawDataPathHelper().get_vm_list_dirs()
        prefix = path['s3prefix']
        keys = self.get_keys(prefix)
        s3path = self.get_latest_s3key(keys)

        if s3path == None:
            self.logger.warn('No vm_list')
            return []
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get vm_list s3folder = %s' % s3folder)
            return s3folder

    def get_es_rates(self):
        s3folder = self.get_es_rates_s3folder()

        if s3folder is None:
            self.logger.warn('No es_rates')
            return []
        
        path = RawDataPathHelper().get_es_rates_dirs(
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(path['s3folder'], path['local_dir'])

        # read local files
        files = os.listdir(path['local_dir'])
        data = None
        for file in files:
            if file[-5:] != '.json':
                continue
            local_path = '%s/%s' % (path['local_dir'], file)
            with open(local_path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(path['local_dir'])

        self.logger.info('Read es_rates = %s' % data)
        return data

    def get_vm_list(self):
        s3folder = self.get_vm_list_s3folder()

        if s3folder is None:
            self.logger.warn('No vm_list')
            return []
        
        path = RawDataPathHelper().get_vm_list_dirs(
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(path['s3folder'], path['local_dir'])

        # read local files
        files = os.listdir(path['local_dir'])
        data = None
        for file in files:
            if file[-5:] != '.json':
                continue
            local_path = '%s/%s' % (path['local_dir'], file)
            with open(local_path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(path['local_dir'])

        self.logger.info('Read %s logs from vm_list' % (len(data)))
        self.logger.info('vm_list[0] = %s' % data[0])
        return data

    #####################################################
    #
    #   jobs
    #
    #####################################################

    def filter_by_time(self, keys, filter_time_str):
        filter_keys = []
        for key in keys:
            time_str = key.split('/')[-2]
            if datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S') <= datetime.strptime(filter_time_str, '%Y-%m-%dT%H:%M:%S'):
                filter_keys.append(key)
        return filter_keys

    def get_latest_job_s3key(self, job_keys):
        if len(job_keys)==0:
            return None
        job_keys.sort(key=lambda x:x, reverse=True)
        for i in range(0, len(job_keys)):
            # if (Not _SUCCESS file) and (have corresponding _SUCCESS file)
            s3key = job_keys[i]
            s3_success_key = '%s%s' % ('/'.join(s3key.split('/')[:-1]), '/_SUCCESS')
            if s3key[-8:]!='_SUCCESS' and s3_success_key in job_keys:
                return s3key

        return None 

    def get_demand_prediction_result_s3folder(self, job_name, dt_hour_str, update_time_str=''):
        '''
        get latest (before 'update_time_str') demand prediction result in given 'dt_hour_str'
        '''
        job_path = JobPathHelper().get_dirs_by_demand_prediction_name(job_name, dt_hour_str)
        job_prefix = job_path['s3prefix']
        job_keys = self.get_keys(job_prefix)
        if len(job_keys)==0:
            return None
        if update_time_str!='':
            job_keys = self.filter_by_time(job_keys, update_time_str)
        s3path = self.get_latest_job_s3key(job_keys)
        # return a folder 
        s3folder = s3path[:s3path.rfind('/')]
        update_time_str = s3folder.split('/')[-1]
        self.logger.info('get demand_prediction_result s3folder = %s' % s3folder)
        return s3folder

    def download_demand_prediction_result_by_job_name(
        self, 
        job_name, 
        dt_hour_str, 
        update_time_str=''):

        s3folder = self.get_demand_prediction_result_s3folder(
            job_name,
            dt_hour_str,
            update_time_str=update_time_str)

        if s3folder is None:
            if update_time_str=='':
                self.logger.warn('No demand_prediction_result in %s for %s' % (dt_hour_str, job_name))
            else:
                self.logger.warn('No demand_prediction_result in %s for %s (before %s)' % (dt_hour_str, job_name, update_time_str))
            return []

        job_path = JobPathHelper().get_dirs_by_demand_prediction_name(
            job_name,
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])
        
        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        return job_path['local_dir']

    def upload_demand_prediction_result_by_job_name(
        self, 
        job_name,
        dt_hour_str, 
        local_dir):

        update_time_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        job_path = JobPathHelper().get_dirs_by_demand_prediction_name(
            job_name,
            dt_hour_str, 
            update_time_str=update_time_str)

        # upload
        self.upload_folder(job_path['s3folder'], local_dir)

    def download_demand_prediction_result(self, dt_hour_str, update_time_str=''):
        s3folder = self.get_demand_prediction_result_s3folder(
            dt_hour_str,
            update_time_str=update_time_str)

        if s3folder is None:
            if update_time_str=='':
                self.logger.warn('No demand_prediction_result in %s' % dt_hour_str)
            else:
                self.logger.warn('No demand_prediction_result in %s (before %s)' % (dt_hour_str, update_time_str))
            return []

        job_path = JobPathHelper().get_demand_prediction_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])
        
        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        return job_path['local_dir']

    def upload_demand_prediction_result(self, dt_hour_str, local_dir):
        update_time_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        job_path = JobPathHelper().get_demand_prediction_dirs(
            dt_hour_str, 
            update_time_str=update_time_str)

        # upload
        self.upload_folder(job_path['s3folder'], local_dir)

    #####################################################
    #
    #   etl
    #
    #####################################################

    def get_latest_etl_s3key(self, etl_keys):
        if len(etl_keys)==0:
            return None

        etl_keys.sort(key=lambda x:x, reverse=True)
        for i in range(0, len(etl_keys)):
            # if (Not _SUCCESS file) and (have corresponding _SUCCESS file)
            s3key = etl_keys[i]
            s3_success_key = '%s%s' % ('/'.join(s3key.split('/')[:-1]), '/_SUCCESS')
            if s3key[-8:]!='_SUCCESS' and s3_success_key in etl_keys:
                return s3key

        return None

    #####################################################
    # Vm Status
    #####################################################

    def get_latest_vm_status_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper().get_vm_status_dirs(dt_hour_str)
        job_prefix = job_path['s3prefix']
        etl_keys = self.get_keys(job_prefix)
        s3path = self.get_latest_etl_s3key(etl_keys)
        # return a folder 
        if s3path == None:
            self.logger.warn('No latest vm_status')
            return None
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get latest vm_status s3folder = %s' % s3folder)
            return s3folder

    def get_latest_vm_status(self, dt_hour_str):
        s3folder = self.get_latest_vm_status_s3folder(dt_hour_str)
        if s3folder is None:
            self.logger.warn('No latest_vm_status in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper().get_vm_status_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        # read local files
        files = os.listdir(job_path['local_dir'])
        data = []
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s/%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                #data.extend(json_data['data'])
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from vm_status in %s' % (len(data), dt_hour_str))
        self.logger.info('vm_status[0] = %s' % data[0])
        return data

    def write_vm_status(self, item_dict_list):
        if (len(item_dict_list))==0:
            self.logger.warn('Empty input of vm status')
            return
        # data preprocessing
        dict_dt_hour = {}
        for item_dict in item_dict_list:
            dt_hour_str = self.get_dt_str_by_timestamp(item_dict['snap_time'])['dt_hour_str']
            #[_, dt_hour_str, _] = self.timestamp_to_dt_str(item_dict['snap_time'])
            if dt_hour_str in dict_dt_hour:
                dict_dt_hour[dt_hour_str].append(item_dict)
            else:
                dict_dt_hour[dt_hour_str] = [item_dict]

        # upload data to s3
        dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        #[dt_now_str, _, _] = self.timestamp_to_dt_str(int(datetime.now().timestamp()))
        for dt_hour_str, item_list in dict_dt_hour.items():
            etl_key = ETLPathHelper().get_etl_key('vm_status')

            # get latest data and join with current item list
            new_list = item_list + self.get_latest_vm_status(dt_hour_str)
            # remove duplicate
            new_list = list({i['_id']:i for i in new_list}.values())
            self.logger.info('write %s vm_status in %s' % (len(new_list), dt_hour_str))
            
            self.write_etl_data(new_list, dt_hour_str, etl_key)
            # etl_path = ETLPathHelper().get_vm_status_dirs(dt_hour_str, update_time_str=dt_now_str)

            # # write local file and upload
            # self.mkdir(etl_path['local_dir'])
            # json_data = {}
            # json_data['data'] = item_list
            # with open('%s/%s.json' % (etl_path['local_dir'], dt_now_str), 'w') as fp:
            #     json.dump(json_data, fp)
            # # upload
            # self.upload_folder(etl_path['s3folder'], etl_path['local_dir'])
            # # remove local file
            # self.rmdir(etl_path['local_dir'])   

    #####################################################
    # general sync table (by Vm-Hour)
    #####################################################

    def get_latest_battery_swap_log_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper().get_battery_swap_log_dirs(dt_hour_str)
        job_prefix = job_path['s3prefix']
        etl_keys = self.get_keys(job_prefix)
        s3path = self.get_latest_etl_s3key(etl_keys)
        # return a folder 
        if s3path == None:
            self.logger.warn('No latest battery_swap_log')
            return None
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get latest battery_swap_log s3folder = %s' % s3folder)
            return s3folder

    def get_latest_battery_swap_log(self, dt_hour_str):
        s3folder = self.get_latest_battery_swap_log_s3folder(dt_hour_str)
        if s3folder is None:
            self.logger.warn('No latest_battery_swap_log in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper().get_battery_swap_log_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        # read local files
        files = os.listdir(job_path['local_dir'])
        data = []
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s/%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from battery_swap_log in %s' % (len(data), dt_hour_str))
        self.logger.info('battery_swap_log[0] = %s' % data[0])
        return data

    def write_battery_swap_log(self, item_dict_list):
        if (len(item_dict_list))==0:
            self.logger.warn('Empty input of battey swap log')
            return
        # data preprocessing
        dict_dt_hour = {}
        for item_dict in item_dict_list:
            dt_hour_str = self.get_dt_str_by_timestamp(item_dict['exchange_time'])['dt_hour_str']
            #[_, dt_hour_str, _] = self.timestamp_to_dt_str(item_dict['exchange_time'])
            if dt_hour_str in dict_dt_hour:
                dict_dt_hour[dt_hour_str].append(item_dict)
            else:
                dict_dt_hour[dt_hour_str] = [item_dict]
        
        # upload data to s3
        for dt_hour_str, item_list in dict_dt_hour.items():
            etl_key = ETLPathHelper().get_etl_key('battery_swap_log')
            # get latest data and join with current item list
            new_list = item_list + self.get_latest_battery_swap_log(dt_hour_str)
            # remove duplicate
            new_list = list({i['_id']:i for i in new_list}.values())    # TODO: should adopt 'swap_id' later
            self.logger.info('write %s battery_swap_log in %s' % (len(new_list), dt_hour_str))
            self.write_etl_data(new_list, dt_hour_str, etl_key)

    #####################################################
    # general etl (by Vm-Hour)
    #####################################################

    def get_latest_vm_battery_count_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper().get_vm_battery_count_dirs(dt_hour_str)
        job_prefix = job_path['s3prefix']
        etl_keys = self.get_keys(job_prefix)
        s3path = self.get_latest_etl_s3key(etl_keys)
        # return a folder 
        if s3path == None:
            self.logger.warn('No latest vm_battery_count')
            return None
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get latest vm_battery_count s3folder = %s' % s3folder)
            return s3folder

    def get_latest_vm_exchange_count_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper().get_vm_exchange_count_dirs(dt_hour_str)
        job_prefix = job_path['s3prefix']
        etl_keys = self.get_keys(job_prefix)
        s3path = self.get_latest_etl_s3key(etl_keys)
        # return a folder 
        if s3path == None:
            self.logger.warn('No latest vm_exchange_count')
            return None
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get latest vm_exchange_count s3folder = %s' % s3folder)
            return s3folder
    
    def get_latest_vm_battery_count(self, dt_hour_str):
        s3folder = self.get_latest_vm_battery_count_s3folder(dt_hour_str)

        if s3folder is None:
            self.logger.warn('No latest_vm_battery_count in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper().get_vm_battery_count_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])
        
        # read local files
        files = os.listdir(job_path['local_dir'])
        data = None
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s/%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from vm_battery_count in %s' % (len(data), dt_hour_str))
        self.logger.info('vm_battery_count.keys() = %s' % list(data.keys()))
        return data 

    def get_latest_vm_exchange_count(self, dt_hour_str):
        s3folder = self.get_latest_vm_exchange_count_s3folder(dt_hour_str)

        if s3folder is None:
            self.logger.warn('No latest_vm_exchange_count in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper().get_vm_exchange_count_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        # read local files
        files = os.listdir(job_path['local_dir'])
        data = []
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s/%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from vm_exchange_count in %s' % (len(data), dt_hour_str))
        self.logger.info('vm_exchange_count[0] = %s' % data[0])
        return data 

    def write_vm_battery_count(self, data, dt_hour_str):
        etl_key = ETLPathHelper().get_etl_key('vm_battery_count')
        self.write_etl_data(data, dt_hour_str, etl_key)

    def write_vm_exchange_count(self, data, dt_hour_str):
        etl_key = ETLPathHelper().get_etl_key('vm_exchange_count')
        self.write_etl_data(data, dt_hour_str, etl_key)

    def write_etl_data(self, data, dt_hour_str, etl_key):
        dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        etl_path = ETLPathHelper().get_dirs_by_etl_key(etl_key, dt_hour_str, update_time_str=dt_now_str)
        # write local file and upload
        self.mkdir(etl_path['local_dir'])
        json_data = {}
        json_data['data'] = data
        with open('%s/%s.json' % (etl_path['local_dir'], dt_now_str), 'w') as fp:
            json.dump(json_data, fp)
        # upload
        self.upload_folder(etl_path['s3folder'], etl_path['local_dir'])
        # remove local file
        self.rmdir(etl_path['local_dir'])

    
    #####################################################
    #
    #   general
    #
    #####################################################

    def timestamp_to_dt_str(self, timestamp):
        '''
        Return a date_string and time_string by given timestamp
        '''
        dt_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
        dt_hour_str = dt_str[:13]
        time_str = dt_str[-8:]
        return [dt_str, dt_hour_str, time_str]

    def get_dt_str_by_timestamp(self, timestamp):
        '''
        Return a string format dict by given timestamp
        '''
        dt_str = {}
        dt_str['dt'] = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
        dt_str['dt_hour_str'] = dt_str['dt'][:13]
        dt_str['dt_minute_str'] = dt_str['dt'][:16]
        dt_str['time_str'] = dt_str['dt'][-8:]
        return dt_str

    
