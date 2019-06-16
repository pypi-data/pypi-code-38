import argparse


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-u",
        "--uart",
        action="store",
        dest="uart_name",
        type=str,
        help="uart name",
        required=True
    )

    parser.add_argument(
        "-s",
        "--speed",
        action="store",
        dest="uart_speed",
        help="uart speed",
        type=int,
        default=115200
    )

    parser.add_argument(
        "-a",
        "--address",
        action="store",
        dest="device_address",
        help="device address",
        type=int,
        default=0x01
    )

    return parser.parse_args()


def get_scaner_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-u",
        "--uart",
        action="store",
        dest="uart_name",
        type=str,
        help="uart name",
        required=True
    )

    parser.add_argument(
        "-s",
        "--speed",
        action="store",
        dest="uart_speed",
        help="uart speed",
        type=int,
        default=115200
    )

    parser.add_argument(
        "-d",
        "--delay",
        action="store",
        dest="wait_delay",
        help="wait delay",
        type=float,
        default=0.15
    )

    parser.add_argument(
        "-m",
        "--min",
        action="store",
        dest="min_address",
        help="min address for search",
        type=int,
        default=1
    )

    parser.add_argument(
        "-x",
        "--max",
        action="store",
        dest="max_address",
        help="max address for search",
        type=int,
        default=0xff - 1
    )

    return parser.parse_args()
