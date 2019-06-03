"""
Most of this stuff from
https://github.com/mozilla/python_mozetl/blob/master/tests/conftest.py
"""
import pyspark
import pytest
from pytest import fixture


@fixture
def spark():
    spark = pyspark.sql.SparkSession.builder.appName("test").getOrCreate()
    yield spark
    spark.stop()


class DataFrameFactory:
    """Create a dataframe given a base dictionary and schema."""

    def __init__(self, spark_session):
        self.spark = spark_session

    def create_dataframe(self, snippets, base, schema=None):
        """Generate a dataframe in the shape of the base dictionary where every
        row has column values overwritten by the snippets.

        :snippets list[dict]: a list of fields to overwrite in the base
            dictionary
        :base dict: a base instantiation of a row in the dataset
        :schema pyspark.sql.types.StructType: schema for the dataset
        """
        # the dataframe should have at least one item
        if not snippets:
            snippets = [dict()]

        samples = []
        for snippet in snippets:
            sample = base.copy()
            if snippet is None:
                snippet = {}
            sample.update(snippet)
            samples.append(sample)

        # if no schema is provided, the schema will be inferred
        return self.spark.createDataFrame(samples, schema)

    def create_dataframe_with_key(
        self, snippets, base, key, key_func=None, schema=None
    ):
        """Generate dataframe with autoincrementing key function"""

        def generate_keys():
            num = 0
            while True:
                yield str(num)
                num += 1

        # default key function
        if not key_func:
            key_func = generate_keys

        if not snippets:
            snippets = [dict()]

        # update each snippet with new key
        gen = key_func()
        for i in range(len(snippets)):
            snippets[i].update({key: next(gen)})

        return self.create_dataframe(snippets, base, schema)


@pytest.fixture()
def dataframe_factory(spark):
    """A factory object for generating test datasets.

    This fixture provides methods for generating data from a base document
    and a list of columns to modify.

    Example usage:

        from functools import partial
        import pytest

        @pytest.fixture
        def base_document():
            return {"uid": 1}

        @pytest.fixture
        def generate_data(dataframe_factory, base_document):
            return partial(dataframe_factory.create_dataframe,
                base=base_document)

        def test_3_unique_uids(generate_data):
            data = generate_data([
                {"uid": 1},
                {"uid": 2},
                {"uid": 3}
            ])
            assert data.count() == 3
    """
    return DataFrameFactory(spark)
