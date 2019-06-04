import sys
import ast
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.types import *
from awsglue.context import GlueContext
from awsglue.job import Job
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'csv_path', 'output_folder',
                                     'schema', 'withHeader', 'separator',
                                     'compression', 'partitionBy', 'mode'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


def generate_structfield(field, datatype):
    """
    This method returns a StructField object
    """
    if datatype == "boolean":
        return StructField(field, BooleanType(), True)
    elif datatype == "double":
        return StructField(field, DoubleType(), True)
    elif datatype == "float":
        return StructField(field, FloatType(), True)
    elif datatype == "integer":
        return StructField(field, IntegerType(), True)
    elif datatype == "long":
        return StructField(field, LongType(), True)
    elif datatype == "null":
        return StructField(field, NullType(), True)
    elif datatype == "short":
        return StructField(field, ShortType(), True)
    elif datatype == "string":
        return StructField(field, StringType(), True)

def remove_invalid_characters(column_name):
    """
    This method removes unsupported characters from column name
    """
    for invalid_char in [" ", ",", ";", "{", "}", "(", ")", "\n", "\t", "="]:
        if invalid_char in column_name:
            column_name = column_name.replace(invalid_char, "")
    return column_name

mode = args["mode"]

partitionBy = ast.literal_eval(args["partitionBy"])

compression = args["compression"]
if compression == 'None':
    compression = None

separator = args["separator"]

if int(args["withHeader"]):
    is_header = True
else:
    is_header = False

output_folder = args["output_folder"]
schema = StructType()

for each_record in ast.literal_eval(args["schema"]):
    schema.add(generate_structfield(each_record[0], each_record[1].lower()))

csv_path = ast.literal_eval(args["csv_path"])

for each_file in csv_path:
    if len(schema):
        df = spark.read.csv(path=each_file, schema=schema, header=is_header, sep=separator)
    else:
        df = spark.read.csv(path=each_file, inferSchema=True, header=is_header, sep=separator)

    if output_folder == 'None':
        output_folder = "/".join(each_file.split("/")[:-1])

    existing_columns = df.columns
    cleaned_columns = map(remove_invalid_characters, existing_columns)
    # Replace unsupported column names from dataframe
    df = df.toDF(*cleaned_columns)
    df.write.parquet(path=output_folder, mode=mode, partitionBy=partitionBy, compression=compression)

job.commit()
