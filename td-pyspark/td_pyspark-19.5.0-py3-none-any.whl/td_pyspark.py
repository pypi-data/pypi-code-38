from pyspark.sql import SQLContext, DataFrame


class TDSparkContext:
    """
    Treasure Data Spark Context
    """

    def __init__(self, spark):
        self.spark = spark
        self.sqlContext = SQLContext(spark.sparkContext)
        self.sc = spark.sparkContext
        self.td = self.sc._jvm.com.treasuredata.spark.TDSparkContext.apply(self.sqlContext._ssql_ctx)
        self.context_db = "information_schema"

    def df(self, table):
        return self.spark.read.format("com.treasuredata.spark").load(table)

    def __to_df(self, sdf):
        return DataFrame(sdf, self.sqlContext)

    def presto(self, sql):
        sdf = self.td.presto(sql, self.context_db)
        return self.__to_df(sdf)

    def execute_presto(self, sql):
        self.td.executePresto(sql, self.context_db)

    def table(self, table):
        return TDTable(self.td.table(table), self.sc, self.sqlContext)

    def db(self, name):
        return TDDatabase(self.td.db(name), self.sc, self.sqlContext)

    def set_log_level(self, log_level):
        self.td.setLogLevel(log_level)

    def use(self, name):
        self.context_db = name

#    def to_pydf(self, sdf):
#        return self.__to_df(sdf)


class TDDatabase:
    def __init__(self, db, sc, sqlContext):
        self.db = db
        self.sc = sc
        self.sqlContext = sqlContext

    def exists(self):
        return self.db.exists()

    def create_if_not_exists(self):
        self.db.createIfNotExists()

    def drop_if_exists(self):
        self.db.dropIfExists()

    def table(self, table):
        return TDTable(self.db.table(table), self.sc, self.sqlContext)


class TDTable:
    def __init__(self, table, sc, sqlContext):
        self.table = table
        self.sc = sc
        self.sqlContext = sqlContext

    def __new_table(self, table):
        return TDTable(table, self.sc, self.sqlContext)

    def within(self, duration):
        return self.__new_table(self.table.within(duration))

    def drop_if_exists(self):
        self.table.dropIfExists()

    def create_if_not_exists(self):
        self.table.createIfNotExists()

    def exists(self):
        return self.table.exists()

    def within_unixtime_range(self, from_unixtime, to_unixtime):
        return self.__new_table(self.table.withinUnixTimeRange(from_unixtime, to_unixtime))

    def within_utc_time_range(self, from_string, to_string):
        return self.__new_table(self.table.withinTimeRange(from_string, to_string, self.sc._jvm.java.time.ZoneOffset.UTC))

#    def within_time_range(self, from_string, to_string, timezone):
#        return self.__new_table(self.table.withinTimeRange(from_string, to_string, self.sc._jvm.java.time.ZoneOffset.UTC))

    def __to_pydf(self, sdf):
        return DataFrame(sdf, self.sqlContext)

    def df(self):
        return self.__to_pydf(self.table.df())
