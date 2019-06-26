# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)
from dativa.tools.aws import S3Client
from dativa.tools.aws import TaskQueue
import logging
from os import path
import time

try:
    import boto3
except ImportError:
    boto3 = None

logger = logging.getLogger("dativa.tools.aws")


class S3Csv2ParquetConversionError(Exception):
    """
    A generic class for reporting errors in the athena client
    """

    def __init__(self, reason):
        Exception.__init__(self, ' S3Csv2ParquetConversion failed: reason {}'.format(reason))
        self.reason = reason


class S3Csv2Parquet(TaskQueue):
    """
    This class contains functionality to convert csv files to parquet using glue jobs.
    """

    def __init__(self, region, template_location, max_jobs=5,
                 glue_role='AWSGlueServiceRoleDefault', retry_limit=3):
        """
        ## Parameters
        - region - str,
                   AWS region in which glue job is to be run
        - template_location - str,
                              S3 bucket Folder in which template scripts are
                              located or need to be copied.
                              format s3://bucketname/folder/file.csv

        - glue_role - str,
                      Name of the glue role which need to be assigned to the
                      Glue Job.
        - max_jobs - int, default 5
                     Maximum number of jobs the can run concurrently in the queue
        - retry_limit - int, default 3
                        Maximum number of retries allowed per job on failure
        """

        # Glue does not allow more than three runs of the same job
        if not boto3:
            raise ImportError("boto3 must be installed to run S3Csv2Parquet")

        super(S3Csv2Parquet, self).__init__(max_jobs, retry_limit, max_tasks_same_name=3)

        self.glue = boto3.client(service_name='glue', region_name=region,
                                 endpoint_url='https://glue.{}.amazonaws.com'.format(region))
        self.max_jobs = max_jobs
        self.glue_role = glue_role
        self.template_location = template_location
        self.s3_client = S3Client()
        # Copy template files to s3
        self._upload_template()

    def convert(self, csv_path, output_folder=None, schema=None, name="parquet_csv_convert",
                allocated_capacity=2, delete_csv=False, separator=",",
                with_header=1, compression=None, partition_by=None, mode='append'):
        """
        Create a job in glue.

        ## Parameters
        - csv_path - str or list of str for multiple files,
                     s3 location of the csv file
                     format s3://bucketname/folder/file.csv
                     Pass a list for multiple files
        - output_folder - str, default set to folder where csv files are located 
                          s3 location at which paraquet file should be copied
                          format s3://bucketname/folder
        - schema - list of tuples,
                   If not specified scema is inferred from the file
                   format [(column1, datatype), (column2, datatype)]
                   Supported datatypes are boolean, double, float, integer,
                   long, null, short, string
        - name - str, default 'parquet_csv_convert'
                 Name to be assigned to glue job

        - allocated_capacity - int, default 2
                               The number of AWS Glue data processing units (DPUs) to allocate to this Job.
                               From 2 to 100 DPUs can be allocated
        - delete_csv - boolean, default False
                       If set source csv files are deleted post successful completion of job
        - separator - character, default ','
                      Delimiter character in csv files
        - with_header- int, default 1
                      Specifies whether to treat the first line as a header
                      Can take values 0 or 1
        - compression - str, default None
                        If not specified compression is not applied.
                        Can take values snappy, gzip, and lzo
        - partition_by - list of str, default None
                         List containing columns to partition data by
        - mode - str, default append
                 Options include:
                 overwrite: will remove data from output_folder before writing out
                            converted file.
                 append: Will write out to  output_folder without deleting existing
                         data.
                 ignore: Silently ignore this operation if data already exists.

        """

        if schema is None:
            schema = []

        if isinstance(csv_path, str):
            csv_path = [csv_path]

        self._validate_parameter(csv_path, output_folder, schema,
                                 allocated_capacity, with_header, delete_csv,
                                 compression, partition_by, mode, separator)

        logger.info("Adding job {} to queue ".format(name))
        job = self.add_task(name=name,
                            args={'role': self.glue_role,
                                  'command': {'Name': 'glueetl',
                                              'ScriptLocation': path.join(self.template_location,
                                                                          'csv_parquet_template.py')},
                                  'allocated_capacity': allocated_capacity,
                                  'csv_path': csv_path,
                                  'output_folder': output_folder,
                                  'schema': schema,
                                  'delete_csv': delete_csv,
                                  'separator': separator,
                                  'withHeader': with_header,
                                  'execution_property': {'MaxConcurrentRuns': min(self.max_jobs, 3)},
                                  'compression': compression,
                                  'partition_by': partition_by,
                                  'mode': mode
                                  })

        return job

    def _trigger_task(self, task):
        """
        This method creates/updates a job in glue and triggers its execution
        """
        try:
            job_list = self.glue.get_jobs()["Jobs"]
            # If Job with same name exists it is updated else we create a new job
            for job in job_list:
                if job['Name'] == task.name:
                    logging.info("Updating job {}".format(task.name))
                    self.glue.update_job(JobName=task.name,
                                         JobUpdate={"Role": task.arguments['role'],
                                                    "Command": task.arguments['command'],
                                                    "AllocatedCapacity": task.arguments['allocated_capacity'],
                                                    "ExecutionProperty": task.arguments['execution_property']})
                    break
            else:
                logging.info("Creating new job job {}".format(task.name))
                self.glue.create_job(Name=task.name,
                                     Role=task.arguments['role'], Command=task.arguments['command'],
                                     AllocatedCapacity=task.arguments['allocated_capacity'],
                                     ExecutionProperty=task.arguments['execution_property'])
        except self.glue.exceptions.AccessDeniedException as e:
            logging.error("Failed to create/update job due to  {}".format(e.args[0]))
            raise e
        """
        Calls to the startjobrun api sometime returns ConcurrentRunsExceededException exception
        although active queue contains less that 3 tasks associated with a single job.
        In case ConcurrentRunsExceededException we retry calling startjobrun API
        """
        while True:
            try:
                task.id = self.glue.start_job_run(JobName=task.name,
                                                  Arguments={
                                                      '--csv_path': str(task.arguments['csv_path']).replace(' ', ''),
                                                      '--output_folder': str(task.arguments['output_folder']),
                                                      '--schema': str(task.arguments['schema']).replace(' ', ''),
                                                      '--separator': task.arguments['separator'],
                                                      '--withHeader': str(task.arguments['withHeader']),
                                                      '--compression': str(task.arguments['compression']),
                                                      '--partitionBy': str(task.arguments['partition_by']),
                                                      '--mode': task.arguments['mode']})['JobRunId']
                logger.info("Execution of Job {} has started".format(task.name))
                task.is_active = True
                break
            except self.glue.exceptions.ConcurrentRunsExceededException:
                logger.info("Attempt to run job raised ConcurrentRunsExceededException")
                logger.info("Will reattempt to start job in 30 secs")
                time.sleep(30)

    def _update_task_status(self, task):
        """
        Gets the status of the query, and updates its status in the queue.
        Any queries that fail are reset to pending so they will be run a second time
        """

        logger.debug("...checking status of job {0}".format(task.name))
        job_run = self.glue.get_job_run(JobName=task.name,
                                        RunId=task.id)['JobRun']
        status = job_run['JobRunState']
        if status == "RUNNING":
            task.is_complete = False
        elif status == "SUCCEEDED":
            task.is_complete = True
            if task.arguments['delete_csv']:
                for each_file in task.arguments['csv_path']:
                    s3_bucket = each_file.split("/")[2]
                    file_path = "/".join(each_file.split("/")[3:])
                    self.s3_client.delete_files(s3_bucket, file_path)
        else:
            task.error = job_run['ErrorMessage']

    def _upload_template(self):
        """
        Upload template files to s3 if they have been changed
        """

        s3_bucket = self.template_location.split("/")[2]
        template_path = "/".join(self.template_location.split("/")[3:])
        template_file_local = path.join(path.dirname(path.abspath(__file__)),
                                        "template_scripts")
        key_list = boto3.client("s3").list_objects(Bucket=s3_bucket,
                                                   Prefix=path.join(template_path,
                                                                    "csv_parquet_template.py"))

        """ Check if template file is available in s3 and size matches with the
            one present in dativa tools package"""
        if ("Contents" not in key_list.keys()) or \
                (key_list['Contents'][0]['Size'] != path.getsize(template_file_local)):
            local_template_path = path.join(path.dirname(path.abspath(__file__)), "template_scripts")
            self.s3_client.put_folder(local_template_path, s3_bucket, template_path)

    @staticmethod
    def _validate_parameter(csv_path, output_folder, schema,
                            allocated_capacity, with_header, delete_csv,
                            compression, partition_by, mode, separator):
        """
        This method validates if parameters passed to the convert method
        are correct.
        """

        for each_file in csv_path:
            if each_file[:5] != "s3://":
                logging.error("csv_path {} is not of format "
                              "s3://bucketname/folder".format(each_file))
                raise S3Csv2ParquetConversionError("csv_path {} is not of "
                                                   "format s3://bucketname/folder".format(each_file))

        if not isinstance(output_folder, str) and output_folder is not None:
            logging.error("output_folder must be of type string got {} instead".format(str(type(output_folder))))
            raise S3Csv2ParquetConversionError("output_folder must be of type string got {} instead".
                                               format(str(type(output_folder))))

        if output_folder is not None and output_folder[:5] != "s3://":
            logging.error("output_folder {} is not of format "
                          "s3://bucketname/folder".format(output_folder))
            raise S3Csv2ParquetConversionError("output_folder {} is not of "
                                               "format s3://bucketname/folder".
                                               format(output_folder))

        if not isinstance(schema, list):
            logging.error("schema parameter must be of format '[('column1', 'datatype')]'")
            raise S3Csv2ParquetConversionError("schema parameter must be of format '[('column1', 'datatype')]'")

        supported_datatypes = ['boolean', 'double', 'float', 'integer', 'long', 'null', 'short', 'string']
        for each_pair in schema:
            if each_pair[1].lower() not in supported_datatypes:
                logging.error("Datatypes listed in schema must be one of the following {}".
                              format(",".join(supported_datatypes)))
                logging.error("{} is not supported".format(each_pair[1]))
                raise S3Csv2ParquetConversionError("Datatypes listed in schema must be one of the following {}".
                                                   format(",".join(supported_datatypes)))

        if allocated_capacity > 100 or allocated_capacity < 2:
            logging.error("allocated capacity should be in range 2-100")
            raise S3Csv2ParquetConversionError("allocated capacity should be in range 2-100")

        if with_header not in [0, 1]:
            logging.error("{} is not a valid value for with_header it can only "
                          "take integer values 1 and 0".format(with_header))
            raise S3Csv2ParquetConversionError("{} is not a valid value for "
                                               "with_header it can only take "
                                               "integer values 1 and 0".format(with_header))

        if not isinstance(delete_csv, bool):
            logging.error("{} is not a valid value for delete_csv."
                          "It can only take boolean values")
            raise S3Csv2ParquetConversionError("{} is not a valid value for delete_csv."
                                               "It can only take boolean values")

        compression_methods = ['snappy', 'gzip', 'lzo']
        if compression is not None and compression not in compression_methods:
            logging.error("Compression must be of type {}".
                          format(",".join(compression_methods)))
            raise S3Csv2ParquetConversionError("Compression must be of type {}".
                                               format(",".join(compression_methods)))

        if not isinstance(partition_by, list) and partition_by is not None:
            logging.error("partition_by parameter must be of type list")
            raise S3Csv2ParquetConversionError("partition_by parameter must be of type list")

        supported_modes = ['append', 'overwrite', 'error', 'ignore']
        if mode not in supported_modes:
            logging.error("mode {} is not formatted".format(mode))
            logging.error("mode must be one of type {}".format(",".join(supported_modes)))
            raise S3Csv2ParquetConversionError("mode must be one of type {}".
                                               format(",".join(supported_modes)))

        if not isinstance(separator, str):
            logging.error("seperator must be of type string got {} instead".format(str(type(separator))))
            raise S3Csv2ParquetConversionError("seperator must be of type string got {} instead".
                                               format(str(type(separator))))

        if mode == 'overwrite' and output_folder is None:
            logging.error("For mode:overwrite output_folder parameter must be specified and"
                          "\n cannot be a parent directory of the csv_files")
            raise S3Csv2ParquetConversionError("For mode:overwrite output_folder parameter must be specified and"
                                               "\n cannot be a parent directory of the csv_files")
        if mode == 'overwrite':
            for each_csv_file in csv_path:
                if each_csv_file.startswith(output_folder):
                    logging.error("For mode:overwrite output_folder cannot be a"
                                  "\n parent directory of the csv_files")
                    raise S3Csv2ParquetConversionError("For mode:overwrite output_folder cannot be a"
                                                       "\n parent directory of the csv_files")
