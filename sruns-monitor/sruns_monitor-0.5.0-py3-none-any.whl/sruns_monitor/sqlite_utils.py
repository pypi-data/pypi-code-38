# -*- coding: utf-8 -*-

import logging
import multiprocessing
import sqlite3
import time

import psutil

import sruns_monitor as srm
import sruns_monitor.utils as utils
import pdb

class Db:
    """
    An instance of this class has a connection (`sqlite3.Connection` instance) stored in an attribute
    `self.conn` and several methods that work on the custom database that supports the sequencing
    runs monitor. Note: according to https://sqlite.org/faq.html#q6, it says:

        Under Unix, you should not carry an open SQLite database across a fork() system call into
        the child process.

    There, applications that support multiprocessing, such as `sruns_monitor.monitor.Monitor` should
    make sure that each child process that needs this class makes its own instantiation rather than
    sharing one created in the main thread, for example. 
    """
    #: The name of the table that stores workflow state for each sequencing run. 
    TASKS_TABLE_NAME = "tasks"
    #: 'tasks' table attribute name that stores the name of the sequencing run. 
    TASKS_NAME = "name"
    #: 'tasks' table attribute name that stores the process ID of the workflow that is currently
    #: running or had run.
    TASKS_PID = "pid"
    #: 'tasks' table attribute name that stores the path to the gzip tarfile of the run directory.
    TASKS_TARFILE = "tarfile"
    #: 'tasks' table attribute name that stores the path to the gzip tarfile in a GCP Storage bucket.
    TASKS_GCP_TARFILE = "gcp_tarfile"

    # Constants to define the status of a record.
    #: Status value for a new sequencing run.                                                       
    RUN_STATUS_NEW = "new"                                                                          
    #: Status value for a sequencing run that is running in the workflow.                           
    RUN_STATUS_STARTING = "starting"                                                                
    #: Status value for a sequencing run that is 
    RUN_STATUS_RUNNING = "running"                                                                
    #: Status value for a sequencing run where the workflow is currently running for it and 
    #: w/o specification as to which task. 
    RUN_STATUS_TARRING = "tarring"                                                                  
    #: Status value for a sequencing run whose tarring task just completed                          
    RUN_STATUS_TARRING_COMPLETE = "tarring_complete"                                                
    #: Status value for a sequencing run that is in the uploading task                              
    RUN_STATUS_UPLOADING = "uploading"                                                              
    #: Status value for a sequencing run whose uploading task just completed                        
    RUN_STATUS_UPLOADING_COMPLETE = "uploading_complete"                                            
    #: Status value for a sequencing run that has completed the workflow.                           
    RUN_STATUS_COMPLETE = "complete"                                                                
    #: Status value for a sequencing run that is has partially gone through the workflow, and the   
    #: workflow is no longer running. For example, the tarfile task ran but the upload to GCP       
    #: task didn't because maybe it failed for some reason.                                         
    RUN_STATUS_NOT_RUNNING = "not_running" 

    logger = logging.getLogger(__name__)

    def __init__(self, dbname, lock=False, verbose=False):
        """
        Args:
            dbname: `str`. Name of the local database file. If it doesn't end with a .db exention,
                one will be added. 
            lock: `multiprocessing.synchronize.Lock` instance for synchronizing access to log streams. 
            verbose: `boolean`. True enables verbose logging. 
        """
        if not lock:
            lock = multiprocessing.Lock()
        #: A `multiprocessing.synchronize.Lock` instance for synchronizing access to log streams.
        self.lock = lock
        #: If True, then verbose logging is enabled.
        self.verbose = verbose
        if not dbname.endswith(".db"):
            dbname += ".db"
        self.dbname = dbname
        self.log(msg="Connecting to sqlite database {}".format(dbname), verbose=True)
        #: A `sqlite3.Connection` instance.  The specified database file is created if it doesn't 
        #: yet exist. See entry level details here:
        #: http://www.sqlitetutorial.net/sqlite-python/creating-database/
        self.conn = sqlite3.connect(database=dbname, timeout=5) # sec timeout is also the default
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS {table} (
                {name} text PRIMARY KEY,
                {pid} integer,
                {tarfile} text,
                {gcp_tarfile} text);
            """.format(table=self.TASKS_TABLE_NAME,  
                       name=self.TASKS_NAME, 
                       pid=self.TASKS_PID,
                       tarfile=self.TASKS_TARFILE,
                       gcp_tarfile=self.TASKS_GCP_TARFILE)
        with self.conn as conn:
            conn.execute(create_table_sql)

    def log(self, msg, verbose=False):
        if verbose and not self.verbose:
            return
        with self.lock:
            self.logger.debug(msg)

    def get_run_status(self, name):
        """
        Determines the state of the workflow for a given run based on the run record in the
        database.

        Args:
            name: `str`. The name of a sequencing run.

        Returns:
            `str`. One of the RUN_STATUS_* constants defined in this class. 
        """
        # Check for record in database
        rec = self.get_run(name)
        if not rec:
            return self.RUN_STATUS_NEW
        elif rec[self.TASKS_TARFILE] and rec[self.TASKS_GCP_TARFILE]:
            return self.RUN_STATUS_COMPLETE
        pid = rec[self.TASKS_PID]
        if not pid:
            return self.RUN_STATUS_NOT_RUNNING
        # Check if running
        try:
            process = utils.get_process(pid)
            if process:
                return self.RUN_STATUS_RUNNING
            else:
                return self.RUN_STATUS_NOT_RUNNING
        except psutil.NoSuchProcess:
            return self.RUN_STATUS_NOT_RUNNING

    def insert_run(self, name, pid=0, tarfile="", gcp_tarfile=""):
        """
        Creates a new record in the database. You most likely only need to set the name attribute
        since other attributes will be set by the workflow as it progresses. 

        Args:
            name: `str`. Value for the *name* attribute. Set this to the sequencing run name. 
            pid: `int`. Value for the *pid* attribute that should be the process ID of the workflow
                if running already. 
            tarfile: `str`. The name of the tarfile. Doesn't make sense to set if the workflow task
                that tars the run directory hasn't run yet. 
            gcp_tarfile: `str`. Blob name for the tarfile that is in GCP storage. Doesn't make sense
                to set if the workflow task that uploads the tarfile to GCP hasn't run yet. 

        Returns: None
 
        """
        sql = """
              INSERT INTO {table}({name_attr},{pid_attr},{tarfile_attr},{gcp_tarfile_attr})
              VALUES('{name}',{pid},'{tarfile}','{gcp_tarfile}');
              """.format(
                  table=self.TASKS_TABLE_NAME,
                  name_attr=self.TASKS_NAME,
                  pid_attr=self.TASKS_PID,
                  tarfile_attr=self.TASKS_TARFILE,
                  gcp_tarfile_attr=self.TASKS_GCP_TARFILE,
                  name=name,
                  pid=pid,
                  tarfile=tarfile,
                  gcp_tarfile=gcp_tarfile)
        self.log(msg=sql, verbose=True)
        with self.conn as conn:
            conn.execute(sql) # Returns the sqlite3.Cursor object. 

    def update_run(self, name, payload):
        update_str = ""
        for attr in payload:
            val = payload[attr]
            update_str += "{key}='{val}',".format(key=attr, val=val)
        update_str = update_str.rstrip(",")
        sql = "UPDATE {table} SET {updates} WHERE name='{name}';".format(
            table=self.TASKS_TABLE_NAME, 
            updates=update_str,
            name=name)
        self.log(msg=sql, verbose=True)
        with self.conn as conn:
            conn.execute(sql)
              
    def get_run(self, name):
        """
        Returns:
            `tuple`: A record whose name attribute has the supplied name exists. 
            `None`: No such record exists.
        """
        sql = "SELECT {name},{pid},{tarfile},{gcp_tarfile} FROM {table} WHERE {name}='{input_name}';".format(
            name=self.TASKS_NAME, 
            pid=self.TASKS_PID,
            tarfile=self.TASKS_TARFILE, 
            gcp_tarfile=self.TASKS_GCP_TARFILE, 
            table=self.TASKS_TABLE_NAME,
            input_name=name)

        self.log(msg=sql, verbose=True)
        res = self.conn.execute(sql).fetchone()
        if not res:
            return {}
        return {
            self.TASKS_NAME: res[0],
            self.TASKS_PID: res[1],
            self.TASKS_TARFILE: res[2],
            self.TASKS_GCP_TARFILE: res[3]
        }

    def delete_run(self, name):
        sql = "DELETE FROM {table} WHERE {name}='{input_name}';".format(
            table=self.TASKS_TABLE_NAME,
            name=self.TASKS_NAME, 
            input_name=name)
        self.log(msg=sql, verbose=True)

        with self.conn as conn:
            conn.execute(sql)

    def get_tables(self):
        sql = "SELECT name FROM sqlite_master where type='table';"
        res = self.conn.execute(sql)
        # res is a list of one item tuples of the form [('tasks',)]
        tables = []
        for i in res:
            tables.append(i[0])
        return tables
