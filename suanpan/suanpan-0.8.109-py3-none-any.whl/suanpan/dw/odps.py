# coding=utf-8
from __future__ import absolute_import, print_function

import pandas
from odps import ODPS
from odps.df import DataFrame
from odps.df.expr.expressions import CollectionExpr

from suanpan.log import logger


class OdpsDataWarehouse(object):
    DEFAULT_ODPS_PROJECT_NAME = "None"

    DTYPE_SQLTYPE_MAPPING = {
        "int8": "int",
        "int16": "int",
        "int32": "int",
        "int64": "bigint",
        "float32": "double",
        "float64": "double",
        "class": "string",
        "datetime": "datetime",
    }

    def __init__(
        self,  # pylint: disable=unused-argument
        odpsAccessId,
        odpsAccessKey,
        odpsEndpoint,
        odpsProject,
        **kwargs
    ):
        self.odpsAccessId = odpsAccessId
        self.odpsAccessKey = odpsAccessKey
        self.odpsEndpoint = odpsEndpoint
        self.odpsProject = odpsProject

        self._connection = self.connect()

    def connect(self):
        connection = ODPS(
            access_id=self.odpsAccessId,
            secret_access_key=self.odpsAccessKey,
            endpoint=self.odpsEndpoint,
            project=self.odpsProject,
        )
        return connection

    def testConnection(self, connection):
        connection.execute_sql("select current_timestamp()")
        logger.info("Odps connected...")

    def readTable(
        self,
        table,
        partition=None,
        database=DEFAULT_ODPS_PROJECT_NAME,  # pylint: disable=unused-argument
    ):
        df = (
            DataFrame(self._connection.get_table(table).get_partition(partition))
            if partition
            else DataFrame(self._connection.get_table(table))
        )

        if df.count() == 0:
            return self._createEmptyPandasDF(self.getColumnsFromOdps(df))

        return df.to_pandas()

    def writeTable(
        self,
        table,
        data,
        partition=None,
        database=DEFAULT_ODPS_PROJECT_NAME,  # pylint: disable=unused-argument
        overwrite=True,
    ):
        isOdpsDataFrame = isinstance(data, CollectionExpr)
        if isOdpsDataFrame:
            self._persistData(table, data, partition, database, overwrite)
        else:
            if data.size == 0:
                columns = self.getColumns(data)
                self.dropTable(table)
                self.createTable(table, columns)
            else:
                data = DataFrame(data)
                self._persistData(table, data, partition, database, overwrite)

    def createTable(self, table, columns):
        self.execute(
            u"create table if not exists {table} ({columns})".format(
                table=table,
                columns=u",".join(
                    [
                        u"{} {}".format(column["name"], column["type"])
                        for column in columns
                    ]
                ),
            )
        )

    def dropTable(self, table):
        self._connection.delete_table(table, if_exists=True)

    def execute(self, sql):
        try:
            self._connection.execute_sql(sql)
        except Exception as e:
            logger.error("SQL: {}".format(sql))
            raise e

    def getColumns(self, data):
        return [
            {"name": name.split(".")[-1], "type": self.toSqlType(dtype)}
            for name, dtype in data.dtypes.items()
        ]

    def getColumnsFromOdps(self, df):
        return [
            {"name": column.name.split(".")[-1], "type": str(column.type).lower()}
            for column in df.schema.columns
        ]

    def toSqlType(self, dtype):
        typeName = self.shortenDatetimeType(dtype.name)
        return self.DTYPE_SQLTYPE_MAPPING.get(typeName, "string")

    def shortenDatetimeType(self, typeName):
        datatimeType = "datetime"
        return datatimeType if typeName.startswith(datatimeType) else typeName

    def _persistData(
        self,
        table,
        data,
        partition=None,
        database=DEFAULT_ODPS_PROJECT_NAME,  # pylint: disable=unused-argument
        overwrite=True,
    ):
        if partition:
            data.persist(
                table,
                partition=partition,
                drop_partition=overwrite,
                create_partition=True,
                odps=self._connection,
            )
        else:
            data.persist(
                table,
                partition=partition,
                drop_table=overwrite,
                create_table=True,
                odps=self._connection,
            )

    def _createEmptyPandasDF(self, columns):
        columnNames = [column["name"] for column in columns]
        df = pandas.DataFrame(columns=columnNames)
        for column in columns:
            name = column["name"]
            dType = column["type"]

            if dType == "string":
                df[name] = df[name].astype("object")
            else:
                df[name] = df[name].astype(dType)
        return df
