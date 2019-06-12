from mlcore.datahelper.s3.s3_data_helper import S3DataHelper
from mlcore.datahelper.s3.mllearningdb.s3_path_helper import ETLPathHelper, JobPathHelper, RawDataPathHelper
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
    
    def get_latest_s3folder(self, s3folders):
        '''
        get latest s3 folder with _SUCCESS file
        '''
        if len(s3folders)==0:
            return None

        s3folders.sort(key=lambda x:x, reverse=True)
        for i in range(0, len(s3folders)):
            # if (Not _SUCCESS file) and (have corresponding _SUCCESS file)
            s3folder = s3folders[i]
            s3keys = self.get_keys(s3folder)
            s3_success_key = '%s%s' % (s3folder, '_SUCCESS')
            #self.logger.info('s3keys = %s, s3_success_key=%s' % (s3keys, s3_success_key))
            if s3_success_key in s3keys:
                return s3folder

        return None

    def write_es_rates(self, data_dict):
        if len(data_dict)==0:
            self.logger.warn('Empty input of es rate')
            return

        # upload data to s3
        dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        path = RawDataPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_es_rates_dirs(update_time_str=dt_now_str)

        # write local file and upload
        self.mkdir(path['local_dir'])

        json_data = {}
        json_data['data'] = data_dict
        with open('%s%s.json' % (path['local_dir'], dt_now_str), 'w') as fp:
            json.dump(json_data, fp)
        # upload 
        self.upload_folder(path['s3folder'], path['local_dir'])
        # FIXME
        self.delete_folder(path['s3folder_latest'])
        self.upload_folder(path['s3folder_latest'], path['local_dir'])
        # remove local file
        self.rmdir(path['local_dir']) 


    def write_vm_list(self, data_dict):
        if len(data_dict)==0:
            self.logger.warn('Empty input of vm list')
            return

        # upload data to s3
        dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        path = RawDataPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_vm_list_dirs(update_time_str=dt_now_str)

        # write local file and upload
        self.mkdir(path['local_dir'])

        json_data = {}
        json_data['data'] = data_dict
        with open('%s%s.json' % (path['local_dir'], dt_now_str), 'w') as fp:
            json.dump(json_data, fp)
        # upload
        self.upload_folder(path['s3folder'], path['local_dir'])
        # FIXME
        self.delete_folder(path['s3folder_latest'])
        self.upload_folder(path['s3folder_latest'], path['local_dir'])
        # remove local file
        self.rmdir(path['local_dir'])  

    def write_vm_nearby(self, data_dict):
        if len(data_dict)==0:
            self.logger.warn('Empty input of vm nearby')
            return

        # upload data to s3
        dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        path = RawDataPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_vm_nearby_dirs(update_time_str=dt_now_str)

        # write local file and upload
        self.mkdir(path['local_dir'])

        json_data = {}
        json_data['data'] = data_dict
        with open('%s%s.json' % (path['local_dir'], dt_now_str), 'w') as fp:
            json.dump(json_data, fp)
        # upload
        self.upload_folder(path['s3folder'], path['local_dir'])
        # FIXME
        self.delete_folder(path['s3folder_latest'])
        self.upload_folder(path['s3folder_latest'], path['local_dir'])
        # remove local file
        self.rmdir(path['local_dir'])  

    def get_es_rates_s3folder(self):
        path = RawDataPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_es_rates_dirs()
        s3folder_latest = path['s3folder_latest']
        if self.is_object_exist('%s%s' % (s3folder_latest, '_SUCCESS')) == True:
            # return latest
            s3folder = s3folder_latest
        else:
            # no latest => search snapshot
            prefix = path['s3prefix']
            s3folders = self.get_folder_prefixes(prefix)
            s3folder = self.get_latest_s3folder(s3folders)

        if s3folder == None:
            self.logger.warn('No es_rates')
            return None
        else:
            self.logger.info('get es_rates s3folder = %s' % s3folder)
            return s3folder

    def get_vm_list_s3folder(self):
        path = RawDataPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_vm_list_dirs()
        s3folder_latest = path['s3folder_latest']
        if self.is_object_exist('%s%s' % (s3folder_latest, '_SUCCESS')) == True:
            # return latest
            s3folder = s3folder_latest
        else:
            # no latest => search snapshot
            prefix = path['s3prefix']
            s3folders = self.get_folder_prefixes(prefix)
            s3folder = self.get_latest_s3folder(s3folders)
        
        if s3folder == None:
            self.logger.warn('No vm_list')
            return None
        else:
            self.logger.info('get vm_list s3folder = %s' % s3folder)
            return s3folder

    def get_vm_nearby_s3folder(self):
        path = RawDataPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_vm_nearby_dirs()
        s3folder_latest = path['s3folder_latest']
        if self.is_object_exist('%s%s' % (s3folder_latest, '_SUCCESS')) == True:
            # return latest
            s3folder = s3folder_latest
        else:
            # no latest => search snapshot
            prefix = path['s3prefix']
            s3folders = self.get_folder_prefixes(prefix)
            s3folder = self.get_latest_s3folder(s3folders)

        if s3folder == None:
            self.logger.warn('No vm_nearby')
            return None
        else:
            self.logger.info('get vm_nearby s3folder = %s' % s3folder)
            return s3folder

    def get_es_rates(self):
        s3folder = self.get_es_rates_s3folder()

        if s3folder is None:
            self.logger.warn('No es_rates')
            return []
        
        path = RawDataPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_es_rates_dirs(
            update_time_str=s3folder.split('/')[-2])

        self.download_folder(path['s3folder'], path['local_dir'])

        # read local files
        files = os.listdir(path['local_dir'])
        data = None
        for file in files:
            if file[-5:] != '.json':
                continue
            local_path = '%s%s' % (path['local_dir'], file)
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
        
        path = RawDataPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_vm_list_dirs(
            update_time_str=s3folder.split('/')[-2])

        self.download_folder(path['s3folder'], path['local_dir'])

        # read local files
        files = os.listdir(path['local_dir'])
        data = None
        for file in files:
            if file[-5:] != '.json':
                continue
            local_path = '%s%s' % (path['local_dir'], file)
            with open(local_path) as fp:
                json_data = json.load(fp)
                data = json_data['data']
        
        # remove local files
        self.rmdir(path['local_dir'])

        self.logger.info('Read %s logs from vm_list' % (len(data)))
        
        if len(data)==0:
            self.logger.warn('Empty vm_list.')
        else:
            self.logger.info('vm_list[0] = %s' % data[0])
        return data

    def get_vm_nearby(self):
        s3folder = self.get_vm_nearby_s3folder()

        if s3folder is None:
            self.logger.warn('No vm_nearby')
            return []
        
        path = RawDataPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_vm_nearby_dirs(
            update_time_str=s3folder.split('/')[-2])

        self.download_folder(path['s3folder'], path['local_dir'])

        # read local files
        files = os.listdir(path['local_dir'])
        data = None
        for file in files:
            if file[-5:] != '.json':
                continue
            local_path = '%s%s' % (path['local_dir'], file)
            with open(local_path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(path['local_dir'])

        self.logger.info('Read %s logs from vm_nearby' % (len(data)))
        if len(data)==0:
            self.logger.warn('Empty vm_nearby.')
        else:
            self.logger.info('vm_nearby[0] = %s' % data[0])
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

    def get_latest_job_s3folder(self, s3folders, update_time_str=''):
        '''
        get latest s3 folder with _SUCCESS file
        '''
        if len(s3folders)==0:
            return None

        def filter_folder_by_time(s3folders, filter_time_str):
            if filter_time_str=='':
                return s3folders

            filter_s3folders = []
            for s3folder in s3folders:
                time_str = s3folder.split('/')[-2]
                if datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S') <= datetime.strptime(filter_time_str, '%Y-%m-%dT%H:%M:%S'):
                    filter_s3folders.append(s3folder)
            return filter_s3folders
 
        s3folders = filter_folder_by_time(s3folders, update_time_str)

        return self.get_latest_s3folder(s3folders)

    def get_demand_prediction_result_s3folder(self, job_name, dt_hour_str, update_time_str=''):
        '''
        get latest (before 'update_time_str') demand prediction result in given 'dt_hour_str'
        '''
        job_path = JobPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_dirs_by_demand_prediction_name(job_name, dt_hour_str)
        job_prefix = job_path['s3prefix']
        s3folders = self.get_folder_prefixes(job_prefix)
        
        s3folder = self.get_latest_job_s3folder(s3folders, update_time_str=update_time_str)

        # return a folder 
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

        job_path = JobPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_dirs_by_demand_prediction_name(
            job_name,
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-2])
        
        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        return job_path['local_dir']

    def upload_demand_prediction_result_by_job_name(
        self, 
        job_name,
        dt_hour_str, 
        local_dir):

        update_time_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        job_path = JobPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_dirs_by_demand_prediction_name(
            job_name,
            dt_hour_str, 
            update_time_str=update_time_str)

        # upload
        self.upload_folder(job_path['s3folder'], local_dir)

    def download_demand_prediction_result(self, dt_hour_str, update_time_str=''):

        return self.download_demand_prediction_result_by_job_name(
            'demand_prediction', 
            dt_hour_str, 
            update_time_str=update_time_str)


    def upload_demand_prediction_result(self, dt_hour_str, local_dir):
        
        return self.upload_demand_prediction_result_by_job_name(
            'demand_prediction',
            dt_hour_str, 
            local_dir)

    #####################################################
    #
    #   etl
    #
    #####################################################

    def get_latest_etl_s3folder(self, s3folders):
        '''
        get latest s3 folder with _SUCCESS file
        '''

        return self.get_latest_s3folder(s3folders)

    #####################################################
    # Vm Status
    #####################################################

    def get_latest_vm_status_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_vm_status_dirs(dt_hour_str)
        s3folder_latest = job_path['s3folder_latest']
        if self.is_object_exist('%s%s' % (s3folder_latest, '_SUCCESS')) == True:
            # return latest
            s3folder = s3folder_latest
        else:
            # no latest => search snapshot
            job_prefix = job_path['s3prefix']
            s3folders = self.get_folder_prefixes(job_prefix)
            s3folder = self.get_latest_etl_s3folder(s3folders)

        # return a folder 
        if s3folder == None:
            self.logger.warn('No latest vm_status')
            return None
        else:
            self.logger.info('get latest vm_status s3folder = %s' % s3folder)
            return s3folder

    def get_latest_vm_status(self, dt_hour_str):
        s3folder = self.get_latest_vm_status_s3folder(dt_hour_str)
        if s3folder is None:
            self.logger.warn('No latest_vm_status in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_vm_status_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-2])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        # read local files
        files = os.listdir(job_path['local_dir'])
        data = []
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                #data.extend(json_data['data'])
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        if isinstance(data, list)==False:
            data = [data]
        self.logger.info('Read %s logs from vm_status in %s' % (len(data), dt_hour_str))
        self.logger.info('vm_status[0] = %s' % data[0])
        return data

    def write_vm_status(self, item_dict_list, incremental=True):
        if (len(item_dict_list))==0:
            self.logger.warn('Empty input of vm status')
            return

        # data preprocessing
        dict_dt_hour = {}
        for item_dict in item_dict_list:
            dt_hour_str = self.get_dt_str_by_timestamp(item_dict['snap_time'])['dt_hour_str']
            if dt_hour_str in dict_dt_hour:
                dict_dt_hour[dt_hour_str].append(item_dict)
            else:
                dict_dt_hour[dt_hour_str] = [item_dict]

        # upload data to s3
        response = []
        for dt_hour_str, item_list in dict_dt_hour.items():
            etl_key = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_etl_key('vm_status')

            if incremental==True:
                # get latest data and join with current item list
                new_list = item_list + self.get_latest_vm_status(dt_hour_str)
                # remove duplicate
                new_list = list({i['_id']:i for i in new_list}.values())        # TODO: should adopt 'snapshot_id' later
            else:
                new_list = item_list

            self.logger.info('write %s vm_status in %s' % (len(new_list), dt_hour_str))
            response.append(self.write_etl_data(etl_key, new_list, dt_hour_str))

        return response

    #####################################################
    # Battery Swap Log
    #####################################################

    def get_latest_battery_swap_log_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_battery_swap_log_dirs(dt_hour_str)
        s3folder_latest = job_path['s3folder_latest']
        if self.is_object_exist('%s%s' % (s3folder_latest, '_SUCCESS')) == True:
            # return latest
            s3folder = s3folder_latest
        else:
            # no latest => search snapshot
            job_prefix = job_path['s3prefix']
            s3folders = self.get_folder_prefixes(job_prefix)
            s3folder = self.get_latest_etl_s3folder(s3folders)

        # return a folder 
        if s3folder == None:
            self.logger.warn('No latest battery_swap_log')
            return None
        else:
            self.logger.info('get latest battery_swap_log s3folder = %s' % s3folder)
            return s3folder

    def get_latest_battery_swap_log(self, dt_hour_str):
        s3folder = self.get_latest_battery_swap_log_s3folder(dt_hour_str)
        if s3folder is None:
            self.logger.warn('No latest_battery_swap_log in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_battery_swap_log_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-2])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        # read local files
        files = os.listdir(job_path['local_dir'])
        data = []
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        if isinstance(data, list)==False:
            data = [data]
        self.logger.info('Read %s logs from battery_swap_log in %s' % (len(data), dt_hour_str))
        self.logger.info('battery_swap_log[0] = %s' % data[0])
        return data

    def write_battery_swap_log(self, item_dict_list, incremental=True):
        if (len(item_dict_list))==0:
            self.logger.warn('Empty input of battey swap log')
            return []

        # data preprocessing
        dict_dt_hour = {}
        for item_dict in item_dict_list:
            dt_hour_str = self.get_dt_str_by_timestamp(item_dict['exchange_time'])['dt_hour_str']
            if dt_hour_str in dict_dt_hour:
                dict_dt_hour[dt_hour_str].append(item_dict)
            else:
                dict_dt_hour[dt_hour_str] = [item_dict]
        
        # upload data to s3
        response = []
        for dt_hour_str, item_list in dict_dt_hour.items():
            etl_key = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_etl_key('battery_swap_log')

            if incremental==True:
                # get latest data and join with current item list
                new_list_all = item_list + self.get_latest_battery_swap_log(dt_hour_str)
                # remove duplicate
                #new_list = list({i['_id']:i for i in new_list}.values())    # TODO: should adopt 'swap_id' later
                new_list = list({i['swap_id']:i for i in new_list_all}.values())
                if len(new_list_all) != len(new_list):
                    self.logger.warn('found duplicate battery_swap_log in %s: total # = %s, unique #= %s' % (dt_hour_str, len(new_list_all), len(new_list)))
            else:
                new_list = item_list
            
            self.logger.info('write %s battery_swap_log in %s' % (len(new_list), dt_hour_str))
            response.append(self.write_etl_data(etl_key, new_list, dt_hour_str))

        return response

    #####################################################
    # general etl (by Vm-Hour)
    #####################################################

    def get_latest_etl_data_s3folder(self, etl_key, dt_hour_str):
        job_path = ETLPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_dirs_by_etl_key(etl_key, dt_hour_str)
        s3folder_latest = job_path['s3folder_latest']
        if self.is_object_exist('%s%s' % (s3folder_latest, '_SUCCESS')) == True:
            # return latest
            s3folder = s3folder_latest
        else:
            # no latest => search snapshot
            job_prefix = job_path['s3prefix']
            s3folders = self.get_folder_prefixes(job_prefix)
            s3folder = self.get_latest_etl_s3folder(s3folders)

        # return a folder 
        if s3folder == None:
            self.logger.warn('No latest %s' % etl_key)
            return None
        else:
            self.logger.info('get latest %s s3folder = %s' % (etl_key, s3folder))
            return s3folder

    def get_latest_etl_data(self, etl_key, dt_hour_str):
        s3folder = self.get_latest_etl_data_s3folder(etl_key, dt_hour_str)

        if s3folder is None:
            self.logger.warn('No latest_%s in %s', (etl_key, dt_hour_str))
            return []

        job_path = ETLPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_dirs_by_etl_key(
            etl_key,
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-2])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])
        
        # read local files
        files = os.listdir(job_path['local_dir'])
        data = None
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from %s in %s' % (len(data), etl_key, dt_hour_str))
        return data 
    
    def write_etl_data(self, etl_key, data, dt_hour_str):
        dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        etl_path = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_dirs_by_etl_key(etl_key, dt_hour_str, update_time_str=dt_now_str)
        # write local file and upload
        self.mkdir(etl_path['local_dir'])
        json_data = {}
        json_data['data'] = data
        with open('%s%s.json' % (etl_path['local_dir'], dt_now_str), 'w') as fp:
            json.dump(json_data, fp)
        # upload
        self.upload_folder(etl_path['s3folder'], etl_path['local_dir'])
        # FIXME
        self.delete_folder(etl_path['s3folder_latest'])
        self.upload_folder(etl_path['s3folder_latest'], etl_path['local_dir'])
        # remove local file
        self.rmdir(etl_path['local_dir'])

        return {
            'partition': dt_hour_str,
            's3key': etl_path['s3folder'],
            's3fullpath': 's3://%s/%s' % (self.s3write['s3bucket'], etl_path['s3folder']),
            's3key_latest': etl_path['s3folder_latest'],
            's3fullpath_latest': 's3://%s/%s' % (self.s3write['s3bucket'], etl_path['s3folder_latest']),
        }

    #####################################################
    # specific etl (by Vm-Hour)
    #####################################################

    def get_latest_vm_battery_count_all_s3folder(self, dt_hour_str):
        etl_key = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_etl_key('vm_battery_count_all')
        return self.get_latest_etl_data_s3folder(etl_key, dt_hour_str)

    def get_latest_vm_battery_count_s3folder(self, dt_hour_str):
        etl_key = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_etl_key('vm_battery_count')
        return self.get_latest_etl_data_s3folder(etl_key, dt_hour_str)

    def get_latest_vm_exchange_count_s3folder(self, dt_hour_str):
        etl_key = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_etl_key('vm_exchange_count')
        return self.get_latest_etl_data_s3folder(etl_key, dt_hour_str)
    
    def get_latest_vm_battery_count_all(self, dt_hour_str):
        etl_key = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_etl_key('vm_battery_count_all')
        return self.get_latest_etl_data(etl_key, dt_hour_str)

    def get_latest_vm_battery_count(self, dt_hour_str):
        s3folder = self.get_latest_vm_battery_count_s3folder(dt_hour_str)

        if s3folder is None:
            self.logger.warn('No latest_vm_battery_count in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_vm_battery_count_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-2])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])
        
        # read local files
        files = os.listdir(job_path['local_dir'])
        data = None
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from vm_battery_count in %s' % (len(data), dt_hour_str))
        #self.logger.info('vm_battery_count.keys() = %s' % list(data.keys()))
        return data 

    def get_latest_vm_exchange_count(self, dt_hour_str):
        s3folder = self.get_latest_vm_exchange_count_s3folder(dt_hour_str)

        if s3folder is None:
            self.logger.warn('No latest_vm_exchange_count in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper(s3baseprefix=self.s3read['s3baseprefix']).get_vm_exchange_count_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-2])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        # read local files
        files = os.listdir(job_path['local_dir'])
        data = []
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from vm_exchange_count in %s' % (len(data), dt_hour_str))
        self.logger.info('vm_exchange_count[0] = %s' % data[0])
        return data 

    def write_vm_battery_count_all(self, data, dt_hour_str):
        if len(data)==0:
            self.logger.warn('Empty input of vm_battery_count_all')
            return []
        etl_key = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_etl_key('vm_battery_count_all')
        self.logger.info('write %s vm_battery_count_all in %s' % (len(data), dt_hour_str))
        return [self.write_etl_data(etl_key, data, dt_hour_str)]

    def write_vm_battery_count(self, data, dt_hour_str):
        if len(data)==0:
            self.logger.warn('Empty input of vm_battery_count')
            return []
        etl_key = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_etl_key('vm_battery_count')
        self.logger.info('write %s vm_battery_count in %s' % (len(data), dt_hour_str))
        return [self.write_etl_data(etl_key, data, dt_hour_str)]

    def write_vm_exchange_count(self, data, dt_hour_str):
        if len(data)==0:
            self.logger.warn('Empty input of vm_exchange_count')
            return []
        etl_key = ETLPathHelper(s3baseprefix=self.s3write['s3baseprefix']).get_etl_key('vm_exchange_count')
        self.logger.info('write %s vm_exchange_count in %s' % (len(data), dt_hour_str))
        return [self.write_etl_data(etl_key, data, dt_hour_str)]

    
    #####################################################
    #
    #   general
    #
    #####################################################

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

    
