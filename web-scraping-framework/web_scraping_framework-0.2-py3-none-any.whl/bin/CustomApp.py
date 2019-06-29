from traceback import format_exc
from celery import Task
from contextlib import contextmanager
from functools import wraps
from sqlalchemy.exc import DatabaseError, InvalidRequestError
from sqlalchemy.orm.exc import StaleDataError
try:
    from CustomModels import TaskMasterTable
    from CustomModels import MachineRegistryTable
    from CustomModels import ConfigMasterTable
    from CustomModels import ResultSetTable
except:
    from bin.CustomModels import TaskMasterTable
    from bin.CustomModels import MachineRegistryTable
    from bin.CustomModels import ConfigMasterTable
    from bin.CustomModels import ResultSetTable

from datetime import datetime
from uuid import uuid4
import boto3

max_allowed_bulk_count = 500


@contextmanager
def session_cleanup(session):
    """
    create session.
    :param session:  session object
    :return:
    """
    try:
        yield
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def retry(fun):
    @wraps(fun)
    def _inner(*args, **kwargs):
        max_retries = kwargs.pop('max_retries', 3)

        for retries in range(max_retries):
            try:
                return fun(*args, **kwargs)
            except (DatabaseError, InvalidRequestError, StaleDataError):
                if retries + 1 >= max_retries:
                    raise

    return _inner


class CustomBackendCalls(Task):
    """
        Custom DB calls for all the tasks
    """

    # ////////////////////////MACHINE REGISTRY/////////////////////// #
    # /////////////////////////////////////////////////////////////// #
    # /////////////////////////////////////////////////////////////// #

    @staticmethod
    def upload_result_to_s3(result, keyname):
        """
        this function will upload result passed as argument to the amazon s3 database.
        :param result: result to be uploaded
        :param keyname: Object key for which the PUT operation was initiated.
        :return:
            True -> if uploaded successfully
            OR
            False -> if execution failed
        """
        try:
            client = boto3.client('s3')
            client.put_object(Body=result, Bucket='finapidata', Key=keyname)
            return True
        except Exception as e:
            print("failed to upload file")
            return False

    @retry
    def update_heartbeat(self, worker_id):
        """
         Will update heartbeat of registered machine
        :param worker_id:
        :return:
            True -> if heartbeat update successful
            OR
            False -> if heartbeat update failure
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "update machine_registry set flag='1' where worker_id= '{0}';"
                session.execute(query.format(worker_id))
                session.commit()
                print("heartbeat updated")
                return True
        except DatabaseError as e:
            print("Heartbeat update database error :", format_exc())
            return False
        except Exception as e:
            print("UNKNOWN ERROR : while updating heart beat")
            print(format_exc())
            return False

    # tested by vardhman OK
    @retry
    def register_machine(self, worker_id, ip_address, jobtype=0, meta="", flag=0):
        """
            Will register new machine
        :param ip_address: IP address of machine
        :param flag:
        :param meta: meta data about machine
        :param worker_id: unique ID for worker
        :param jobtype : unique ID for group of jobs
        :return:boolean
            True -> If register successful.
            OR
            False -> If register failure.
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                session.add(MachineRegistryTable(worker_id=worker_id, jobtype=jobtype, ip_address=ip_address, meta=meta,
                                                 flag=flag))
                session.commit()
                print("successfully registered machine")
                return True
        except DatabaseError as e:
            print("Machine registration database error :", format_exc())
            return False
        except Exception as e:
            print("UNKNOWN ERROR : while registration of machine")
            print(format_exc())
            return False

    # ////////////////////////Task Master Table/////////////////////// #
    # //////////////////////////////////////////////////////////////// #
    # //////////////////////////////////////////////////////////////// #

    # tested by Vardhman OK
    @retry
    def get_unprocessed_job_count(self, jobtype=0):
        """
        this function will return unprocessed job count
        :param jobtype: unique ID for group of jobs
        :return:
            True, unprocessed_job_count -> on successful execution
            OR
            False, None -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "select count(*) from task_master where lock=false and jobtype={0};"
                unprocessed_job_count = session.execute(query.format(jobtype)).fetchone()[0]
                # print("returned unprocessed jobs")
                return [True, unprocessed_job_count]
        except DatabaseError as e:
            print("Heartbeat update database error :", format_exc())
            return [False, None]
        except Exception as e:
            print("UNKNOWN ERROR : while updating heart beat")
            print(format_exc())
            return [False, None]

    @retry
    def set_worker_for_task(self, task_id, worker_id):
        """
        this function will distribute task in the queue to workers
        :param worker_id: unique ID for worker
        :param task_id: unique ID for task
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "update task_master set worker_id = '{0}' where uid = '{1}';"
                session.execute(query.format(worker_id, task_id))
                session.commit()
                print("Worker details updated for task")
                return True
        except DatabaseError as e:
            print("Set worker failed :", format_exc())
            return False
        except Exception as e:
            print("UNKNOWN ERROR : while updating heart beat")
            print(format_exc())
            return False

    @retry
    def lock_the_task(self, jobtype=0):
        """
            Will lock the task and return locked element uid and meta data
        :param jobtype: job type for which lock need to be done
        :return:
            [boolean_status,uid,meta]
                uid  : unique identifier of the task
                meta : dictionary containing meta data of job
            OR
            [False,None,None] -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query_lock = "select uid from task_master where lock=false and status=0 " \
                             "and jobtype={0} limit 1 for update "
                lock_uid = str(session.execute(query_lock.format(str(jobtype))).fetchone()[0])
                print(lock_uid)
                query_fetch_details = "update task_master set lock=true" \
                                      " where uid='{0}' returning meta;"
                return_meta = session.execute(query_fetch_details.format(str(lock_uid))).fetchone()[0]
                session.commit()
                return [True, lock_uid, return_meta]
        except DatabaseError as e:
            print("locking failed for given job type error :", format_exc())
            return [False, None, None]
        except Exception as e:
            print("UNKNOWN ERROR : while locking job")
            print(format_exc())
            return [False, None, None]

    @retry
    def bulk_lock_task(self, jobtype=0, count=10):
        """
            Will lock the number of tasks and return locked elements uid and meta data
        :param worker_id: UUID of registered worker
        :param jobtype: job type for which lock need to be done
        :param count: number of task to be locked by single worker
        :return:
            [True,[uid,meta]]
                uid  : unique identifier of the task
                meta : dictionary containing meta data of job
            OR
            [False, [None], [None]] -> if execution failed
        """
        try:
            if count > max_allowed_bulk_count:
                print("Use count less than max allowed count {0}".format(max_allowed_bulk_count))
                return [False, [None], [None]]
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query_lock = "select uid from task_master where lock=false and status=0 " \
                             "and jobtype={0} limit {1} for update "
                lock_uids = session.execute(query_lock.format(str(jobtype), count)).fetchall()
                lock_uid_updated = []
                for lock_uid in lock_uids:
                    lock_uid_updated.append(str(lock_uid[0]))
                del lock_uids
                query_fetch_details = "update task_master set lock=true" \
                                      " where uid in ({0}) returning uid,meta;"
                query_string = query_fetch_details.format(
                    ','.join("'" + lock_uid + "'" for lock_uid in lock_uid_updated))
                return_object_list = []
                return_meta_list = session.execute(query_string).fetchall()
                session.commit()
                for i in range(0, len(return_meta_list)):
                    return_object_list.append((str(return_meta_list[i][0]), return_meta_list[i][1]))
                del return_meta_list
                # print(return_object_list)
                return [True, return_object_list]
        except DatabaseError as e:
            print("locking failed for given job type error :", format_exc())
            return [False, [None], [None]]
        except Exception as e:
            print("UNKNOWN ERROR : while locking job")
            print(format_exc())
            return [False, [None], [None]]

    # tested by Vardhman OK
    @retry
    def update_task_status(self, uid, status):
        """
            Will update task status if needed
        :param uid:  task identifier
        :param status: new status value in integer
        :return: boolean
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "update task_master set status={0} where uid='{1}'"
                session.execute(query.format(status, uid))
                session.commit()
                # print("updated task successfully")
                return True
        except DatabaseError as e:
            print("task status update error :", format_exc())
            return False
        except Exception as e:
            print("UNKNOWN ERROR : while updating task status")
            print(format_exc())
            return False

    # tested by Vardhman OK
    @retry
    def insert_new_task(self, meta, jobtype=0):
        """
        Insert new task entry in task_master table.
        :param meta: meta data of task
        :param jobtype: jobtype of task
                Ex., 0001, 0002, 0003.
        :return:
            True  -> if task inserted successfully.
            OR
            False -> if task insertion failed.
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                uid = str(uuid4())
                session.add(TaskMasterTable(uid=uid, jobtype=jobtype, meta=meta))
                session.commit()
                ##print("inserted new task")
                return True
        except DatabaseError as e:
            print("task status update error :", format_exc())
            return False
        except Exception as e:
            print(format_exc())
            return False

    #
    @retry
    def bulk_insert_new_task(self, meta_list, jobtype=0):
        """
        insert multiple tasks in task_master at one shot.
        :param meta_list: list of meta of tasks to be inserted
        :param jobtype: jobtype of task
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        if meta_list is None:
            print("Error: meta list is None")
            return False
        if len(meta_list) > max_allowed_bulk_count:
            print("Max Allowed bulk count is {0}".format(str(max_allowed_bulk_count)))
            return False
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                object_add = []
                for meta in meta_list:
                    uid = str(uuid4())
                    object_add.append(TaskMasterTable(uid=uid, jobtype=jobtype, meta=meta))
                session.add_all(object_add)
                session.commit()
                return True
        except DatabaseError as e:
            print("task status update error :", format_exc())
            return False
        except Exception as e:
            print(format_exc())
            return False

    # tested by Vardhman OK
    @retry
    def get_task_status(self, uid):
        """
        returns status of the task.
        :param uid: unique id of task.
        :return:
            [True,return_status] -> on successful execution
            OR
            [False,None]         -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "select status from task_master where uid='{0}'"
                return_status = session.execute(query.format(uid)).fetchone()[0]
                # print("status returned successfully")
                return [True, return_status]
        except Exception as e:
            print(format_exc())
            return [False, None]

    @retry
    def update_error_id(self, uid, err_id):
        """
        Will update task status if needed
        :param err_id: Identifier for error
        :param uid:  task identifier
        :return: boolean
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "update task_master set error_id={0} where uid='{1}'"
                session.execute(query.format(err_id, uid))
                session.commit()
                print("updated error id successfully {0}".format(str(err_id)))
                return True
        except DatabaseError as e:
            print("task status update error :", format_exc())
            return False
        except Exception as e:
            print("UNKNOWN ERROR : while updating task status")
            print(format_exc())
            return False

    @retry
    def append_data_into_task_meta(self, task_id, data_to_append):
        """
        Will update meta b appending data in json.
        :param data_to_append: (dict) data to be append in meta
        :param task_id: unique ID for task
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "update task_master set meta = meta::jsonb || '{0}'::jsonb where uid = '{1}';"
                session.execute(query.format(str(data_to_append).replace("'", '"'), task_id))
                session.commit()
                print("Meta updated for task")
                return True
        except DatabaseError as e:
            print("Update meta failed :", format_exc())
            return False
        except Exception as e:
            print("UNKNOWN ERROR : while updating meta")
            print(format_exc())
            return False

    # ////////////////////////Result Master Table/////////////////////// #
    # ////////////////////////////////////////////////////////////////// #
    # ////////////////////////////////////////////////////////////////// #

    @retry
    def insert_result(self, uid, meta, jobtype, result_bytes, checksum):
        """
        Insert result into result_meta.
        :param uid: unique id for result.
        :param meta: meta data related with result.
        :param jobtype: jobtype of result.
        :param result_bytes: result content in binary format.
        :param checksum: SHA256 hashing of data.
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                session.add(
                    ResultSetTable(uid=uid, checksum=checksum, meta=meta, jobtype=jobtype, result_bytes=result_bytes))
                session.commit()
                print("inserted result successfully")
                return True
        except Exception as e:
            print(format_exc())
            return False

    @retry
    def bulk_insert_result(self, uid, meta):
        """
        insert set of results in one shot.
        :param uid: list of unique ids if result
        :param meta: list of meta of results
            * Note : id and meta of result must be at same index.
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        # not implemented
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                print("result bulk insert query")
                return True
        except Exception as e:
            print(format_exc())
            return False

    # tested by Vardhman OK
    @retry
    def get_result(self, uid):
        """
        get meta of specified result.
        :param uid: unique id of result.
        :return:
            [True,result] -> on successful execution
            OR
            [False,None]  -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "select meta from result_master where uid='{0}'"
                result = session.execute(query.format(uid)).fetchone()[0]
                # print("result returned successfully")
                return [True, result]
        except Exception as e:
            print(format_exc())
            return [False, None]

    @retry
    def compare_checksum(self, checksum):
        """
         Compare checksum in result_master table and return count of occurances of checksum.
        :param checksum: SHA256 hashing of data content.
        :return:
            [True, checksum_count] -> on successful execution
            OR
            [False, None]          -> if execution failed
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "select count(checksum) from result_master where checksum='{0}'"
                checksum_count = session.execute(query.format(str(checksum))).fetchone()[0]
                # print("checksum count returned successfully")
                return [True, checksum_count]
        except Exception as e:
            print(format_exc())
            return [False, None]

    @retry
    def update_outtime(self, checksum):
        """
        Update outtime in result_master table.
        :param checksum: SHA256 hashing of data content.
        :return:
            True  -> on successful execution.
            OR
            False -> if execution failed.
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "update result_master set outtime='{0}' where checksum='{1}'"
                session.execute(query.format(str(datetime.now()), str(checksum)))
                session.commit()
                # print("checksum count returned successfully")
                return True
        except Exception as e:
            print(format_exc())
            return False

    def append_data_into_result_meta(self, checksum, data_to_append):
        """
        Will update meta b appending data in json.
        :param checksum: SHA256 hashing of data content.
        :param data_to_append: (dict) data to be append in meta
        :return:
            True  -> on successful execution.
            OR
            False -> if execution failed.
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "update result_master set meta = meta::jsonb || '{0}'::jsonb where checksum = '{1}';"
                session.execute(query.format(str(data_to_append).replace("'", '"'), checksum))
                session.commit()
                print("Meta updated for result")
                return True
        except DatabaseError as e:
            print("Update meta failed :", format_exc())
            return False
        except Exception as e:
            print("UNKNOWN ERROR : while updating meta")
            print(format_exc())
            return False

    # ////////////////////////ConfigTable/////////////////////// #
    # ////////////////////////////////////////////////////////// #
    # ////////////////////////////////////////////////////////// #

    @retry
    def get_config(self, uid, is_all=True, key_name=None):
        """
            returns config stored in config table.
        :param uid: unique id of config
        :param is_all: True -> returns complete config data
                    False   -> returns specified key of config
        :param key_name: key name of config.
        :return:
            [True,config_value] ->  on successful execution.
            OR
            [False,None]        -> if execution failed.
        """
        try:
            query = ""
            cursor = None
            session = self.backend.ResultSession()
            with session_cleanup(session):
                if is_all is False and key_name is None:
                    print("Config key not supplied")
                    return False
                if is_all is False and key_name is not None:
                    query = "select meta->> {0} from config where uid = {1}"
                    cursor = session.execute(query.format(key_name, uid))
                if is_all is True:
                    query = "select meta from config where uid = {0}"
                    cursor = session.execute(query.format(uid))
                config_value = cursor.fetchone()[0]
                return [True, config_value]
        except Exception as e:
            print(format_exc())
            return [False, None]

    @retry
    def set_config(self, uid, key_name=None, value=None):
        """
        update config in config table.
        :param uid: unique ID for config.
        :param key_name: key which is to be extract
        :param value: value to be set
        :return:
            True  -> on successful execution.
            OR
            False -> if execution failed.
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                if key_name is None or value is None:
                    print("Config key and value are not supplied")
                    return False
                query = "update config set meta->> {0} = {1} where uid='{2}'"
                session.execute(query.format(key_name, value, uid))
                session.commit()
                return True
        except Exception as e:
            print(format_exc())
            return False

    # ////////////////////////InitMasterTable/////////////////////// #
    # ////////////////////////////////////////////////////////////// #
    # ////////////////////////////////////////////////////////////// #

    @retry
    def get_master_jobs(self, jobtype, ticker_filter=None):
        """
        Get jobs from init_master by jobtype.
        :param jobtype: unique ID for group of jobs.
        :param ticker_filter: ticker name filter for extract single job.
        :return:
            [True, data_element_list] ->  on successful execution.
            OR
            [False, None]             -> if execution failed.
        """
        try:
            session = self.backend.ResultSession()
            with session_cleanup(session):
                query = "select uid,meta from init_master where jobtype={0}".format(jobtype)
                if ticker_filter is not None:
                    query = query + "and meta->>'ticker' = '{0}'".format(str(ticker_filter))
                # print(query)
                results = session.execute(query).fetchall()
                # print(results)
                data_element_list = []
                for result in results:
                    data_element_list.append((str(result[0]), result[1]))
                # print("added to tasks")
                return [True, data_element_list]
        except Exception as e:
            print(format_exc())
            return [False, None]
