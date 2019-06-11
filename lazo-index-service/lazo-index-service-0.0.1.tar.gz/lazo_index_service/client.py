import grpc

from lazo_index_service.lazo_index_pb2 import \
    ColumnIdentifier, ColumnValue, Value
from lazo_index_service.lazo_index_pb2_grpc import LazoIndexStub


class LazoIndexClient:
    """
    Provides methods to index textual and categorical columns
    using a Lazo server.
    """

    def __init__(self, host='localhost', port=50051):
        channel = grpc.insecure_channel('%s:%d' % (host, port))
        self.stub = LazoIndexStub(channel)

    @staticmethod
    def make_column_value(value, dataset_id, column_name):
        return ColumnValue(
            value=value,
            column_identifier=ColumnIdentifier(
                dataset_id=dataset_id,
                column_name=column_name
            )
        )

    @staticmethod
    def make_value(value):
        return Value(value=value)

    def generate_stream_column_value(self, column_values, dataset_id, column_name):
        for value in column_values:
            yield self.make_column_value(str(value), str(dataset_id), str(column_name))

    def generate_stream_value(self, column_values):
        for value in column_values:
            yield self.make_value(str(value))

    def index_data(self, column_values, dataset_id, column_name):
        """
        Obtains a stream of values from a column and returns its
        corresponding Lazo sketch.

        :param column_values: array of string values
        :return: a tuple with number of permutations, hash_values,
        and the cardinality of the Lazo sketch
        """

        lazo_sketch_data = self.stub.IndexData(
            self.generate_stream_column_value(
                column_values, dataset_id, column_name
            )
        )

        return (
            lazo_sketch_data.number_permutations,
            lazo_sketch_data.hash_values,
            lazo_sketch_data.cardinality
        )

    def query_data(self, column_values):
        """
        Obtains a stream of values from an input column, queries the Lazo index,
        and returns all the datasets that intersect with that input column.
        :param column_values: array of string values
        :return: a list of tuples containing the dataset identifier, the column name,
        and the maximum containment threshold.
        """

        lazo_query_results = self.stub.QueryData(
            self.generate_stream_value(column_values)
        )

        results = []
        for query_result in lazo_query_results.query_results:
            results.append((
                query_result.column.dataset_id,
                query_result.column.column_name,
                query_result.max_threshold
            ))

        return results
