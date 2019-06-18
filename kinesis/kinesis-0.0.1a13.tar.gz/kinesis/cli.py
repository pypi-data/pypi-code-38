import argparse
import atexit
import json
import os
import sys
import time
from datetime import datetime
from pygments import highlight
from pygments.formatters import TerminalFormatter  # pylint: disable-msg=E0611
from pygments.lexers import JsonLexer  # pylint: disable-msg=E0611
from kinesis import settings
from kinesis.consumer import KinesisConsumer
from kinesis.streams import list_streams_by_region
from kinesis.producer import KinesisProducer
from kinesis.__version__ import VERSION


def start_producing(args):

    producer = KinesisProducer(stream_name=args.stream)

    if not os.path.isfile(args.file):
        print("File not found: '%s'" % args.file)
        exit(1)

    with open(args.file, "r") as file_read:
        file_loaded = file_read.read()

    start_time = time.time()
    for _ in range(int(args.repeat)):
        producer.put_record(file_loaded)
    print("Time Elapsed: %f seconds" % (time.time() - start_time))


def start_consuming(args):
    consumer = KinesisConsumer(stream_name=args.stream)
    records_consumed = 0
    for record in consumer:
        records_consumed += 1
        message = record.get("Data")
        try:
            message = json.dumps(json.loads(message.decode()), indent=4, sort_keys=True)
            settings.RECORDS_CAPTURED.append(json.loads(message))
        except ValueError:
            settings.RECORDS_CAPTURED.append(message.decode())
        finally:
            print(highlight(message, JsonLexer(), TerminalFormatter()))
        print()
        print("Records consumed: %s" % records_consumed)
        print()


def list_streams(args):
    list_streams_by_region(args)


def exit_handler():
    """Manage cleanup when being asked to quit."""

    # If there are captured messages and the capture flag is set to true,
    # dump messages as a JSONArray
    if settings.RECORDS_CAPTURED and "capture" in get_args() and get_args().capture:
        json_dumped_file = "{}/{}_{}.json".format(
            settings.CAPTURES_FOLDER, get_args().stream, datetime.utcnow().isoformat()
        )
        print("")
        print("Dumping consumed messages into: %s" % json_dumped_file)
        print("")
        with open(json_dumped_file, "w") as outfile:
            json.dump(
                list(settings.RECORDS_CAPTURED), outfile, sort_keys=True, indent=4
            )
    print("Bye...")
    try:
        sys.exit(os.EX_OK)
    except SystemExit:
        os._exit(os.EX_OK)


def get_args():
    """Parse args."""

    parser = argparse.ArgumentParser(
        prog="kinesis", description="Communicate with AWS Kinesis"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=VERSION, help="kinesis help"
    )

    subparsers = parser.add_subparsers(help="sub-command help")

    # "consume" sub-command
    parser_consume = subparsers.add_parser("consume", help="consume help")
    parser_consume.add_argument("-c", "--capture", dest="capture", action="store_true")
    parser_consume.add_argument(
        "-n", "--no-color", dest="no_color", action="store_true"
    )
    parser_consume.add_argument(
        "-s", "--stream", type=str, required=True, help="kinesis stream"
    )
    parser_consume.set_defaults(func=start_consuming)

    # "produce" sub-command
    parser_produce = subparsers.add_parser("produce", help="consume help")
    parser_produce.add_argument(
        "-s", "--stream", type=str, required=True, help="kinesis stream"
    )
    parser_produce.add_argument(
        "-f", "--file", required=True, type=str, help="read file and send to kinesis"
    )
    parser_produce.add_argument(
        "-r",
        "--repeat",
        default=1,
        type=int,
        help="how many times to repeat producing records",
    )
    parser_produce.set_defaults(func=start_producing)

    # "list-streams" sub-command
    parser_list_streams = subparsers.add_parser(
        "list-streams", help="list-streams help"
    )

    parser_list_streams.set_defaults(func=list_streams)

    return parser.parse_args()


def main():
    """CLI starts here."""

    # Initalize global cli settings
    settings.init()
    # Parse arguments
    parsed_args = get_args()
    atexit.register(exit_handler)

    try:
        if "func" in parsed_args:
            parsed_args.func(parsed_args)
        else:
            argparse.ArgumentParser().print_help()
    except KeyboardInterrupt:
        exit_handler()


if __name__ == "__main__":
    main()
