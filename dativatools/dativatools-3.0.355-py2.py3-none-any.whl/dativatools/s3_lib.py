import datetime
import gc
import boto3
import botocore
import os
import boto3.session
import sys
from .common_utility_tool import CommonUtility
from .log import Logger
from .database_management_tool import DatabaseManagement
from boto.s3.connection import S3Connection


class S3Lib:
    def __init__(self, section, path=None, filename=None, logger_obj=None):
        self.config = section
        log_obj = Logger()
        if path and filename:
            self.logger_obj = log_obj.__get_logger__(path, filename)
        elif logger_obj:
            self.logger_obj = logger_obj

        self.dbc_obj = DatabaseManagement(logger_obj=self.logger_obj)
        self.cu_obj = CommonUtility(logger_obj=self.logger_obj)

    # -------------------------------------------------------------------------
    #    Args: config, section_list
    #    Returns: Flag, success/failure message
    #    Raises: Raises exception if some condition is failed.
    #    Desc: This function is used to validate connection details provided in config_dict
    # -------------------------------------------------------------------------
    def validation(self, config, section_list=None):
        try:
            if section_list is None:
                section_list = config.keys()
            for section in section_list:
                for field in config[section].keys():
                    if field.split('_')[-1] == 'optional':
                        continue
                    elif len(config[section][field]) == 0:
                        message = "Field:{0} field in section {1} is not populated".format(field, section)
                        return False, message
            return True, "Fields have been validated successfully"
        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: path
    #    Returns: Flag, list of files
    #    Raises: Raises exception if some condition is failed.
    #    Desc: This function checks if directory provided is valid and return list of files
    # -------------------------------------------------------------------------
    def check_path_exists(self, path):
        if os.path.isdir(path):
            file_list = []
            for dirpath, subdirs, files in os.walk(path):
                for each_file in files:
                    file_list.append(os.path.join(dirpath, each_file))
        elif os.path.isfile(path):
            file_list = [path]
        else:
            return False, []
        return True, file_list

    # -------------------------------------------------------------------------
    #    Args: config
    #    Returns: Flag, message,connection object
    #    Raises: Raises exception if some condition is failed.
    #    Desc: This function creates a connection with s3
    # -------------------------------------------------------------------------
    def get_connection(self, config):
        try:
            credentials = config['credentials']
            if credentials['environment_variables'] == 'no':
                con = boto3.resource('s3', aws_access_key_id=credentials['aws_access_key_id_optional'], aws_secret_access_key=credentials['aws_secret_access_key_optional'])
                return True, "Connection is created", con
            elif credentials['environment_variables'].lower() == 'yes' and len(credentials['profile_name_optional']) != 0:
                session = boto3.session.Session(profile_name=credentials['profile_name_optional'])
                con = session.resource('s3')
                return True, "Connection is created", con
            elif credentials['environment_variables'].lower() == 'yes':
                con = boto3.resource('s3')
                return True, "Connection is created", con
            else:
                return False, "invalid option provided in envrioment_variables section", None
        except Exception as e:
            return False, e.__str__(), None

    # -------------------------------------------------------------------------
    #    Returns: bucket
    #    Raises: Raises exception if some condition is failed.
    #    Desc: This function connects to S3 and returns bucket connection
    # -------------------------------------------------------------------------
    def get_s3_bucket(self):
        try:
            # Reading bucket name from bucket URL
            bucketname = self.config['credentials']['bucket_name']

            # Connection to s3 bucket
            aws_connection = S3Connection(self.config['credentials']['aws_access_key_id_optional'], self.config['credentials']['aws_secret_access_key_optional'])
            
            # Get bucket
            bucket = aws_connection.get_bucket(bucketname)
            
            return bucket
        except Exception as e:
            self.logger_obj.error(e.__str__())
            return None

    # -------------------------------------------------------------------------
    #    Args: flag,message
    #    Desc: This function checks status after each step of s3 connection
    # -------------------------------------------------------------------------
    def check_flag(self, flag, message):
        if not flag:
            self.logger_obj.error(message)
            sys.exit()
        else:
            self.logger_obj.info(message)
        return

    # -------------------------------------------------------------------------
    #    Args: con, bucket_name
    #    Returns: flag, bucket
    #    Raises: Raises exception error occurs when connecting to bucket
    #    Desc: This function connects to bucket and returns bucket object
    # -------------------------------------------------------------------------
    def connect_bucket(self, con, bucket_name):
        bucket = con.Bucket(bucket_name)
        exists = True
        try:
            con.meta.client.head_bucket(Bucket=bucket_name)
            return exists, bucket
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            exists = False
            error_code = e.response['Error']['Code']
            message = error_code + ": Error Code was recieved when trying to connect to bucket"
            if int(error_code) == 404:
                message = "Bucket does not exist"
        return exists, message

    # -------------------------------------------------------------------------
    #    Args: con, config, file_list
    #    Returns: flag, message
    #    Raises: Raises exception if some condition is failed.
    #    Desc: Uploads files to s3 from server
    # -------------------------------------------------------------------------
    def put_all(self, con, config, file_list):
        try:
            bucket_name = config['credentials']['bucket_name']
            source_path = config['credentials']['source_path']
            destination_path = config['credentials']['destination_path_optional']
            flag, bucket = self.connect_bucket(con, bucket_name)
            if os.path.isdir(source_path):
                for transfer_file in file_list:
                    with open(transfer_file, 'rb') as data:
                        file_name = os.path.relpath(transfer_file, source_path)
                        key = os.path.join(destination_path, file_name)
                        bucket.upload_fileobj(data, key)
            else:
                for transfer_file in file_list:
                    with open(transfer_file, 'rb') as data:
                        file_name = transfer_file.split('/')[-1]
                        key = os.path.join(destination_path, file_name)
                        bucket.upload_fileobj(data, key)
            return True, "Upload Successful"
        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: con, config
    #    Returns: flag, message
    #    Raises: Raises exception if some condition is failed.
    #    Desc: Downloads files from s3
    # -------------------------------------------------------------------------
    def get_all(self, con, config):
        try:
            bucket_name = config['credentials']['bucket_name']
            source_path = config['credentials']['source_path']
            if source_path[-1] != '/' and source_path.find('.') == -1:
                source_path = source_path + "/"
            destination_path = config['credentials']['destination_path_optional']
            length_source_path = len(source_path)
            flag, bucket = self.connect_bucket(con, bucket_name)
            for obj in bucket.objects.filter(Prefix=source_path):
                file_key = obj.key
                filename = file_key[length_source_path:]
                req_dest_path = '/'.join(os.path.join(destination_path, filename).split('/')[:-1])
                if not os.path.exists(req_dest_path):
                    os.mkdir(req_dest_path)
                bucket.download_file(file_key, os.path.join(destination_path, filename))
            return True, "Upload Successful"
        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: tablename, sub_dir, loading_limit, date("YYYY-mm-dd")
    # Returns: True if succesfull and the list of files copied to DB.
    #  Raises: Raises exception if some condition is failed.
    #    Desc: BulkLoad csv files from s3
    # -------------------------------------------------------------------------
    def copy_data(self, tablename, sub_dir, loading_limit=None, date=None):
        #  This function is used to copy data from s3 and load to the database
        try:
            # get S3 bucket
            bucket = self.get_s3_bucket()

            filetype = "csv"
            actual_table = tablename.replace("_info", "")
            sqlcount = ('\nselect PG_LAST_COPY_COUNT();')
            
            # generate file_filter, for limiting files to copy
            if date is not None:
                file_filter = sub_dir + '/' + actual_table + '/' + actual_table + "_" + date
            else:
                file_filter = sub_dir + '/' + actual_table + '/' + actual_table
            
            # filter bucket list
            Keys = list(bucket.list(prefix=file_filter))
            if loading_limit and len(Keys)>= loading_limit:
                Keys = Keys[:loading_limit]

            copyscriptpath = ('{0}{1}/copy.sql').format(self.config['scriptfile'], tablename)
            myfile = open(copyscriptpath, 'r')
            copy_columns = myfile.read()
            myfile.close()
            copy_lst = []
            # loop to read each filename of current table from bucket
            for key in Keys:

                # Checking manifest file in each file of current table from s3 bucket
                if(file_filter in key.name and filetype in key.name):
                    self.logger_obj.info_s3(key.name ,'Start Copying data into table {0} from s3'.format(tablename), key.size)
                    filename = self.config['s3bucketURL'] + key.name
                    # Copy query statement
                    sql = ("{0} \nFROM '{1}{2}' \nCREDENTIALS \n'aws_access_key_id={3};aws_secret_access_key={4}' \ncsv \nGZIP \nDELIMITER '|' \nTIMEFORMAT as 'epochsecs' \nIGNOREHEADER 1 \nEMPTYASNULL \nNULL AS '\\N';").format(copy_columns, self.config['s3bucketURL'], key.name, self.config['credentials']['aws_access_key_id_optional'], self.config['credentials']['aws_secret_access_key_optional'])
                    sql = sql + sqlcount
                    copycount = self.dbc_obj.execute_query(sql, self.config['insight_reduced'], tablename, 'copy')
                    self.cu_obj.log_to_csv(self.config['csv_path'], 'copy', datetime.datetime.utcnow(), copycount, tablename, filename)
                    #self.logger_obj.info_s3(key.name, 'copycount: {0}'.format(copycount), copycount)
                    self.logger_obj.info_s3(key.name, 'Data copied data into table {0} from s3'.format(tablename), copycount, status="completed")
                    copy_lst.append(key)
                else:
                    pass

            return True, copy_lst

        except Exception as e:
            self.logger_obj.exception(e.__str__())
            msgexp = self.cu_obj.get_detail_exception()
            self.cu_obj.log_error_to_database(tablename, 'CommonUtilityTool', 'copy', 'copy_data', msgexp, self.config['insight_reduced'])
            self.cu_obj.send_email(self.config['email_config'], 'Reduced', tablename, 'CommonUtilityTool', 'copy_data', msgexp)
            raise

    # -------------------------------------------------------------------------
    #    Args: tablename, config_dict
    #  Raises: Raises exception if some condition is failed.
    #    Desc: Unload data from amazon redshift
    # -------------------------------------------------------------------------
    def unload_table(self, tablename, con):
        #  This function is used to unload data from database to s3 bucket
        try:
            self.logger_obj.info(('Start unloading data into s3 bucket {0} from database').format(tablename))
            sql = ("UNLOAD ('SELECT * FROM {0}') \nTo '{1}{0}' \nWITH CREDENTIALS \n 'aws_access_key_id={2};aws_secret_access_key={3}' \nmanifest \nGZIP \nALLOWOVERWRITE \nESCAPE \nNULL AS '\\N';").format(tablename, self.config['s3bucketURL'], self.config['credentials']['aws_access_key_id_optional'], self.config['credentials']['aws_secret_access_key_optional'])
            sqlcount = ('\nselect pg_last_unload_count();')
            sql = sql + sqlcount
            # Call ExecuteQuery method to run query
            unloadcount = self.dbc_obj.execute_query(sql, self.config['insight_reduced'], tablename, 'unload')
            self.cu_obj.log_to_csv(self.config['csv_path'], 'unload', datetime.utcnow(), unloadcount, tablename, '')
            self.logger_obj.info(('table {0} is unloaded successfully').format(tablename))

        except Exception as e:
            self.logger_obj.exception(e.__str__())
            msgexp = self.cu_obj.get_detail_exception()
            self.cu_obj.log_error_to_database(self.config['insight_reduced'], 'common_function', 'unload_table', tablename, msgexp)
            self.cu_obj.send_email(self.config['email_config'], 'Reduced', tablename, 'CommonUtilityTool', 'unload_table', msgexp)
            raise

    # -------------------------------------------------------------------------
    #    Args: file_list, list of file names to backup
    # Returns: True if succesfull
    #  Raises: Raises exception if some condition is failed.
    #    Desc: Backup CSV files on S3
    # -------------------------------------------------------------------------
    def backup_data(self, file_list):
        try:
            bucket = self.get_s3_bucket()

            # loop over and move files to backup
            for key in file_list:
                dest_keyname = self.config['backup_on_s3'] + key.name
                bucket.copy_key(dest_keyname, bucket.name, key.name)
                self.logger_obj.info_s3(key.name, "Files successfully moved to backup location{}".format(dest_keyname), key.size, status="completed")
                key.delete()
                gc.collect()
            else:
                return True, "Files successfully moved to backup"

            return False, 'Unable to perform backup'

        except Exception as e:
            self.logger_obj.exception(e.__str__())
            msgexp = self.cu_obj.get_detail_exception()
            tablename = ', '.join(file_list)
            self.cu_obj.log_error_to_database(tablename, 'CommonUtilityTool', 'backup', 'backup_data', msgexp, self.config['insight_reduced'])
            self.cu_obj.send_email(self.config['email_config'], 'Reduced', tablename, 'CommonUtilityTool', 'backup_data', msgexp)
            raise

    # -------------------------------------------------------------------------
    #    Args: file_list, list of file names to backup
    # Returns: True if succesfull
    #  Raises: Raises exception if some condition is failed.
    #    Desc: Delete files from S3 bucket
    # -------------------------------------------------------------------------
    def delete_files(self, file_list):
        try:
            bucket = self.get_s3_bucket()

            # loop over and move files to backup
            for key in file_list:
                bucket.delete_key(key.name)
                key.delete()
                gc.collect()
            else:
                return True, "Files successfully moved to backup"

            return False, 'Unable to perform backup'

        except Exception as e:
            self.logger_obj.exception(e.__str__())
            msgexp = self.cu_obj.get_detail_exception()
            tablename = ', '.join(file_list)
            self.cu_obj.log_error_to_database(tablename, 'CommonUtilityTool', 'backup', 'backup_data', msgexp, self.config['insight_reduced'])
            self.cu_obj.send_email(self.config['email_config'], 'Reduced', tablename, 'CommonUtilityTool', 'backup_data', msgexp)
            raise
