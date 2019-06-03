import argparse
from dtest import Dtest
from .tests_processor import process_connections, process_datasets, process_tests


def main(args=None):
    parser = argparse.ArgumentParser(description='Test file')

    parser.add_argument('configuration_file', action='store', type=str,
                        help='The JSON file defining the Dtest, Spark, and tests configurations')

    args = parser.parse_args()

    import json

    with open(args.configuration_file, 'r') as read_file:
        definition = json.load(read_file)

    dt = Dtest(definition['message-broker-config'],
               definition['test-suite-metadata'])
    connection_dict = process_connections(definition['connections'])
    datasets_dict = process_datasets(
        connection_dict, definition['data-definitions'])
    tests_dict = process_tests(
        datasets_dict, definition['tests'], definition['spark-config'], dt)

    for t in tests_dict:
        print(tests_dict[t].sql)
        tests_dict[t].execute()

    dt.publish()
    print(connection_dict)
    print(datasets_dict)
    print(tests_dict)
