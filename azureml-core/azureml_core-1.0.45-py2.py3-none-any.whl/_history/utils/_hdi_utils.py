# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

import os

module_logger = logging.getLogger(__name__)


class HdiConfig:

    def __init__(self):
        self.spark = None
        self.hadoop_config = None
        self.file_system = None
        self.dfs_cwd = None


def get_hdi_config():
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    hadoop_config = spark._sc._jsc.hadoopConfiguration()

    dfs_cwd = spark._sc._gateway.jvm.org.apache.hadoop.fs.Path(".")
    file_system = dfs_cwd.getFileSystem(hadoop_config)

    hdi_config = HdiConfig()
    hdi_config.spark = spark
    hdi_config.hadoop_config = hadoop_config
    hdi_config.dfs_cwd = dfs_cwd
    hdi_config.file_system = file_system
    return hdi_config


def get_hdispark_working_dir():
    hdi_config = get_hdi_config()
    file_system = hdi_config.file_system

    staging = file_system.getWorkingDirectory().toString()
    module_logger.debug("Running HDI/Spark job in {0}".format(staging))
    return staging


def set_hdispark_working_dir(directory):
    hdi_config = get_hdi_config()
    spark = hdi_config.spark
    file_system = hdi_config.file_system

    # Set the DFS working directory to the the location of the DFS project copy.
    path = spark._sc._gateway.jvm.org.apache.hadoop.fs.Path(directory)
    file_system.setWorkingDirectory(path)


def upload_from_hdfs(run_tracker, directory):
    module_logger.debug("Called upload_from_hdfs")
    hdi_config = get_hdi_config()
    spark = hdi_config.spark
    file_system = hdi_config.file_system

    path = spark._sc._gateway.jvm.org.apache.hadoop.fs.Path(directory)
    aa = file_system.listFiles(path, True)
    paths = []
    while aa.hasNext():
        path = aa.next().getPath().toString()
        path = spark._sc._gateway.jvm.org.apache.hadoop.fs.Path(path)  # fs.open(..) takes Path despite string message
        paths.append(path)
    module_logger.debug("HDFS upload got {} paths".format(len(paths)))
    try:
        import subprocess
        streams = []
        relative_paths = []
        for path in paths:
            proc = subprocess.Popen(["hadoop", "fs", "-cat", path.toString()], stdout=subprocess.PIPE)
            stream = proc.stdout
            streams.append(stream)
            relative_path = path.toString().split("outputs/")[1]
            relative_path = os.path.join("outputs", relative_path)
            relative_paths.append(relative_path)

        for path in relative_paths:
            run_tracker.upload_file(path, path)
        module_logger.debug("Uploaded {} streams".format(len(paths)))
    except Exception as ee:
        print(ee)
        module_logger.exception("Error uploading streams")
        raise ee
    module_logger.debug("Uploaded HDFS streams")


def get_working_prefix(working_dir, container_uri, track_prefix):
    module_logger.debug("Calculating prefix from container {0} and cwd {1}".format(
        container_uri, working_dir))
    project_prefix = working_dir.replace(container_uri, "").lstrip('/')
    module_logger.debug("Project prefix is {0}".format(project_prefix))
    res = "{0}/{1}".format(project_prefix, track_prefix)
    module_logger.debug("Storage outputs prefix: {0}".format(res))
    return res
