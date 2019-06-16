import binascii
import random
from collections import defaultdict, namedtuple

import serial

from terminaltables import AsciiTable

from tools_shared.cmd_line_parser import get_args

from tqdm import tqdm

from vrc_t70.communicator import VrcT70Communicator
from vrc_t70.limitations import MAX_TRUNKS_COUNT

from .shared import init_logger


SensorTemperatureData = namedtuple(
    typename="SensorData",
    field_names=["sensor_address", "temperature", "trunk_number", "sensor_index"]
)


def print_sensors_per_trunk_count(sensors_count_per_trunk, logger, skip_empty_trunks = True):
    table_data = [["Trunk Name", "Sensors Count"]]
    for trunk_number, sensors_count in enumerate(sensors_count_per_trunk, 1):
        if skip_empty_trunks and (not sensors_count):
            continue

        table_data.append(
            [
                "Trunk-{}".format(trunk_number),
                sensors_count
            ]
        )

    table = AsciiTable(table_data)
    logger.info("sensors per trunks:\n{}\n".format(table.table))


def print_sensors_per_trunk_count_protocol_data(sensors_count_per_trunk, logger, skip_empty_trunks = True):
    table_data = [["Trunk Name", "Sensors Count"]]
    for sensors_data in sensors_count_per_trunk:
        if skip_empty_trunks and (not sensors_data.sensors_count()):
            continue
        table_data.append(
            [
                "Trunk-{}".format(sensors_data.trunk_number()),
                sensors_data.sensors_count()
            ]
        )

    table = AsciiTable(table_data)
    logger.info("sensors per trunks:\n{}\n".format(table.table))


def print_sensors_data(sensors_data, logger):
    sensors_per_trunk = defaultdict(list)
    for item in sensors_data:
        sensors_per_trunk[item.trunk_number].append(item)

    for trunk_number in sorted(sensors_per_trunk.keys()):
        sensors_on_trunk = sensors_per_trunk[trunk_number]
        sensors_on_trunk = sorted(sensors_on_trunk, key=(lambda x: x.sensor_index))

        table_data = [["Index", "Temperature", "Address"]]
        for sensor_data in sensors_on_trunk:
            table_data.append(
                [
                    sensor_data.sensor_index,
                    round(sensor_data.temperature, 2),
                    my_hexlify(sensor_data.sensor_address)
                ]
            )

        table = AsciiTable(table_data)
        logger.info("data for Trunk-{}:\n{}\n".format(trunk_number, table.table))


def main():
    args = get_args()
    logger = init_logger("temp reader")
    logger.debug("app started")

    uart = init_serial(args.uart_name, args.uart_speed)
    communicator = VrcT70Communicator(uart, controller_address=args.device_address)

    logger.info("initializing communication with device {0} [0x{0:02x}]...".format(args.device_address))
    logger.info("\tping")
    communicator.ping()

    new_session_id = random_byte_array(4)
    logger.debug("\tinitializing session id with {}".format(my_hexlify(new_session_id)))
    r = communicator.set_session_id(new_session_id)

    assert r.session_id() == new_session_id

    r = communicator.get_session_id()
    logger.debug("\tsession_id = {}".format(my_hexlify(r.session_id())))
    assert r.session_id() == new_session_id

    logger.debug("scanning for sensors on trunks...")
    sensors_count_per_trunk = rescan_devices_on_all_trunks(communicator, logger)
    print_sensors_per_trunk_count(sensors_count_per_trunk, logger)

    logger.info("bulk data processing commands")
    sensors_data = list()
    for trunk_number, sensors_count in enumerate(tqdm(sensors_count_per_trunk, unit="trunks"), 1):
        temperatures = communicator.get_temperature_on_trunk(trunk_number)
        assert temperatures.temperatures_count() == sensors_count

        addresses = communicator.get_sensors_unique_addresses_on_trunk(trunk_number)
        assert sensors_count == addresses.sensors_count()

        for sensor_index in range(sensors_count):
            is_connected = temperatures.is_connected(sensor_index)
            assert is_connected

            temperature = temperatures.temperature(sensor_index)

            assert not addresses.is_error_detected(sensor_index)
            unique_address = addresses.sensor_unique_address(sensor_index)

            sensor_data = SensorTemperatureData(
                sensor_address=unique_address,
                temperature=temperature,
                trunk_number=trunk_number,
                sensor_index=sensor_index
            )

            sensors_data.append(sensor_data)

    print_sensors_data(sensors_data, logger)

    logger.info("simple data processing commands")
    sensors_data = list()
    for trunk_number, sensors_count in enumerate(tqdm(sensors_count_per_trunk, unit="trunk"), 1):
        for sensor_index in range(sensors_count):
            r = communicator.get_temperature_on_sensor_on_trunk(trunk_number, sensor_index)
            temperature = r.temperature()

            r = communicator.get_sensor_unique_address_on_trunk(trunk_number, sensor_index)
            unique_address = r.unique_address()

            sensor_data = SensorTemperatureData(
                sensor_address=unique_address,
                temperature=temperature,
                trunk_number=trunk_number,
                sensor_index=sensor_index
            )

            sensors_data.append(sensor_data)

    print_sensors_data(sensors_data, logger)

    logger.info("retrieving sensors count")
    sensors_count_per_trunk = list()
    for trunk_number in tqdm(range(1, MAX_TRUNKS_COUNT + 1), unit="trunks"):
        r = communicator.get_sensors_count_on_trunk(trunk_number)
        sensors_count_per_trunk.append(r)

    print_sensors_per_trunk_count_protocol_data(sensors_count_per_trunk, logger)

    uart.close()
    logger.info("application finished")
    return 0


def rescan_devices_on_all_trunks(communicator, logger):
    res = []

    logger.info("Rescanning devices on trunks")

    for trunk_number in tqdm(range(1, MAX_TRUNKS_COUNT + 1), unit="trunsk"):
        r = communicator.rescan_sensors_on_trunk(trunk_number)
        res.append(r.sensors_count())

    return res


def init_serial(uart_name, uart_speed):
    return serial.Serial(
        uart_name,
        baudrate=uart_speed,
        bytesize=serial.EIGHTBITS,
        timeout=1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )


def my_hexlify(data):
    return binascii.hexlify(data).decode("ascii")


def random_byte_array(length):
    return bytearray((random.getrandbits(8) for _ in range(length)))


if __name__ == "__main__":
    res = main()
    exit(res)
