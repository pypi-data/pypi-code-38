# coding=utf-8
from __future__ import absolute_import, print_function

from odps import ODPS
from pyspark.sql.types import (
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
)

from suanpan.spark.odpsops import OdpsOps

HIVE_DB_NAME_CONF = "spark.hadoop.fs.hive.db.name"
DEFAULT_HIVE_DB_NAME_CONF = "default"

ODPS_HIVE_TYPE_MAPPING = {
    "BIGINT": LongType,
    "DOUBLE": DoubleType,
    "FLOAT": FloatType,
    "DECIMAL": DecimalType,
    "INT": IntegerType,
    "SMALLINT": IntegerType,
    "TINYINT": IntegerType,
}


def odpsTypeToHiveType(odpsType):
    hiveType = ODPS_HIVE_TYPE_MAPPING.get(odpsType, StringType)
    return hiveType()


def readTable(spark, table, partition=None):
    db = spark.sparkContext._conf.get(  # pylint: disable=protected-access
        HIVE_DB_NAME_CONF, DEFAULT_HIVE_DB_NAME_CONF
    )
    sql = u"select * from {}.{}".format(db, table)

    if partition and partition.strip():
        conditions = u" and ".join(x.strip() for x in partition.split(","))
        sql = u"{} where {}".format(sql, conditions)

    return spark.sql(sql)


def writeTable(spark, table, data):
    dotCount = table.count(".")
    if dotCount > 1:
        raise Exception("Table format error")

    if dotCount == 0:
        db = spark.sparkContext._conf.get(  # pylint: disable=protected-access
            HIVE_DB_NAME_CONF, DEFAULT_HIVE_DB_NAME_CONF
        )
        table = u"{}.{}".format(db, table)

    data.write.mode("overwrite").saveAsTable(table)


def readOdpsTable(
    spark,
    accessId,
    accessKey,
    odpsUrl,
    tunnelUrl,
    project,
    table,
    partition=None,
    numPartitions=None,
    cols=None,
    bytesCols=None,
    batchSize=1,
):
    cols = cols or []
    bytesCols = bytesCols or []
    isPartition = bool(partition)

    odpsOps = OdpsOps(spark.sparkContext, accessId, accessKey, odpsUrl, tunnelUrl)
    odpsSchema = odpsOps.getTableSchema(project, table, isPartition)
    columnNames = [
        StructField(col[0], odpsTypeToHiveType(str(col[1]).upper()), True)
        for col in odpsSchema
    ]
    schema = StructType(columnNames)

    data = (
        odpsOps.readPartitionTable(
            project, table, partition, numPartitions, cols, bytesCols, batchSize
        )
        if partition
        else odpsOps.readNonPartitionTable(
            project, table, numPartitions, cols, bytesCols, batchSize
        )
    )

    return spark.createDataFrame(data, schema)


def writeOdpsTable(
    spark,
    accessId,
    accessKey,
    odpsUrl,
    tunnelUrl,
    project,
    table,
    data,
    partition=None,
    overwrite=False,
):
    odps = ODPS(accessId, accessKey, project, odpsUrl)
    odpsOps = OdpsOps(spark.sparkContext, accessId, accessKey, odpsUrl, tunnelUrl)
    if partition:
        odpsOps.saveToPartitionTable(
            project,
            table,
            partition,
            data.rdd.map(list),
            isCreatePt=True,
            isOverWrite=overwrite,
        )
    else:
        if overwrite:
            schema = odps.get_table(table, project).schema
            odps.delete_table(table, project=project, if_exists=True)
            odps.create_table(table, schema, project, if_not_exists=True)
        odpsOps.saveToNonPartitionTable(project, table, data.rdd.map(list))
