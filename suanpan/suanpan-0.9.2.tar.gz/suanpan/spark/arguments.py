# coding=utf-8
from __future__ import absolute_import, print_function

from pyspark2pmml import PMMLBuilder
from pyspark.ml import PipelineModel

from suanpan import arguments as base
from suanpan.spark import db, io
from suanpan.utils import json

Int = base.Int
String = base.String
Float = base.Float
Bool = base.Bool
List = base.List
ListOfInt = base.ListOfInt
ListOfString = base.ListOfString
ListOfFloat = base.ListOfFloat
ListOfBool = base.ListOfBool
Json = base.Json
IntOrFloat = base.IntOrFloat
IntFloatOrString = base.IntFloatOrString
BoolOrString = base.BoolOrString
BoolOrInt = base.BoolOrInt


class SparkArg(base.Arg):
    pass


class Table(SparkArg):
    def __init__(self, key, table, partition, sortColumns=None):
        super(Table, self).__init__(key)
        sortColumns = sortColumns or "{}SortColumns".format(table)
        self.table = String(key=table, required=True)
        self.partition = String(key=partition)
        self.sortColumns = ListOfString(key=sortColumns, default=[])

    def addParserArguments(self, parser):
        self.table.addParserArguments(parser)
        self.partition.addParserArguments(parser)
        self.sortColumns.addParserArguments(parser)

    def load(self, args):
        self.table.load(args)
        self.partition.load(args)
        self.sortColumns.load(args)
        self.value = dict(
            table=self.table.value,
            partition=self.partition.value,
            sortColumns=self.sortColumns.value,
        )

    def format(self, context):
        self.value = db.readTable(context.spark, self.table.value, self.partition.value)
        self.value = self.value.sort(self.sortColumns.value)
        return self.value

    def save(self, context, result):
        data = result.value
        db.writeTable(context.spark, self.table.value, data)
        self.logSaved(self.table.value)


class SparkModel(SparkArg):
    def __init__(self, key, **kwargs):
        kwargs.update(required=True)
        super(SparkModel, self).__init__(key, **kwargs)

    def format(self, context):
        self.value = PipelineModel.load(io.getStoragePath(context.spark, self.value))
        return self.value

    def save(self, context, result):
        spark = context.spark

        modelPath = io.getStoragePath(spark, self.value)
        pmmlPath = modelPath + "/pmml"

        result.value.model.write().overwrite().save(modelPath)
        with io.open(spark, pmmlPath, mode="w") as file:
            pmmlBuilder = PMMLBuilder(
                spark.sparkContext, result.value.data, result.value.model
            ).putOption(result.value.classifier, "compact", True)
            pmml = pmmlBuilder.buildByteArray()
            file.write(pmml)


class PmmlModel(SparkArg):
    def __init__(self, key, **kwargs):
        kwargs.update(required=True)
        super(PmmlModel, self).__init__(key, **kwargs)

    def format(self, context):
        spark = context.spark

        pmmlPath = self.pmml_path(spark)
        with io.open(spark, pmmlPath, mode="r") as file:
            self.value = file.read()

        return self.value

    def pmml_path(self, spark):
        modelPath = io.getStoragePath(spark, self.value)
        pmmlPath = modelPath + "/pmml"
        return pmmlPath


class OdpsTable(SparkArg):
    def __init__(
        self,
        key,
        accessId,
        accessKey,
        odpsUrl,
        tunnelUrl,
        project,
        table,
        partition,
        overwrite,
        numPartitions,
    ):
        super(OdpsTable, self).__init__(key)
        self.accessId = String(key=accessId, required=True)
        self.accessKey = String(key=accessKey, required=True)
        self.odpsUrl = String(key=odpsUrl, required=True)
        self.tunnelUrl = String(key=tunnelUrl, required=True)
        self.project = String(key=project, required=True)
        self.table = String(key=table, required=True)
        self.partition = String(key=partition)
        self.overwrite = Bool(key=overwrite, default=False)
        self.numPartitions = Int(key=numPartitions, default=2)

    def addParserArguments(self, parser):
        self.accessId.addParserArguments(parser)
        self.accessKey.addParserArguments(parser)
        self.odpsUrl.addParserArguments(parser)
        self.tunnelUrl.addParserArguments(parser)
        self.project.addParserArguments(parser)
        self.table.addParserArguments(parser)
        self.partition.addParserArguments(parser)
        self.overwrite.addParserArguments(parser)
        self.numPartitions.addParserArguments(parser)

    def load(self, args):
        self.accessId.load(args)
        self.accessKey.load(args)
        self.odpsUrl.load(args)
        self.tunnelUrl.load(args)
        self.project.load(args)
        self.table.load(args)
        self.partition.load(args)
        self.overwrite.load(args)
        self.numPartitions.load(args)
        self.value = dict(
            accessId=self.accessId.value,
            accessKey=self.accessKey.value,
            odpsUrl=self.odpsUrl.value,
            tunnelUrl=self.tunnelUrl.value,
            table=self.table.value,
            partition=self.partition.value,
            overwrite=self.overwrite.value,
            numPartitions=self.numPartitions.value,
        )

    def format(self, context):
        self.value = db.readOdpsTable(
            context.spark,
            accessId=self.accessId.value,
            accessKey=self.accessKey.value,
            odpsUrl=self.odpsUrl.value,
            tunnelUrl=self.tunnelUrl.value,
            project=self.project.value,
            table=self.table.value,
            partition=self.partition.value,
            numPartitions=self.numPartitions.value,
        )
        return self.value

    def save(self, context, result):
        db.writeOdpsTable(
            context.spark,
            accessId=self.accessId.value,
            accessKey=self.accessKey.value,
            odpsUrl=self.odpsUrl.value,
            tunnelUrl=self.tunnelUrl.value,
            project=self.project.value,
            table=self.table.value,
            data=result.value,
            partition=self.partition.value,
            overwrite=self.overwrite.value,
        )


class Visual(SparkArg):
    def __init__(self, key, **kwargs):
        kwargs.update(required=True)
        super(Visual, self).__init__(key, **kwargs)

    def save(self, context, result):
        spark = context.spark

        visualPath = io.getStoragePath(spark, self.value) + "/part-00000"
        with io.open(spark, visualPath, mode="w") as file:
            file.write(result.value)


class JsonFile(SparkArg):
    def format(self, context):
        spark = context.spark

        jsonPath = self.filePath(spark)
        with io.open(spark, jsonPath, mode="r") as file:
            self.value = json.load(file)
            return self.value

    def save(self, context, result):
        spark = context.spark

        jsonPath = self.filePath(spark)
        with io.open(spark, jsonPath, mode="w") as file:
            json.dump(result.value, file)

    def filePath(self, spark):
        dataPath = io.getStoragePath(spark, self.value)
        jsonPath = "{}/data.json".format(dataPath)
        return jsonPath
