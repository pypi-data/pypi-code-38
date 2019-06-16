import serial
import serial.tools.list_ports

from .shared import init_logger


def main():
    logger = init_logger("ports lister")

    ports = serial.tools.list_ports.comports()
    logger.info("found {} ports".format(len(ports)))
    for index, port in enumerate(ports):
        logger.info("\t[{}] = '{}' ('{}')".format(index, port.device, port.description))


if __name__ == "__main__":
    main()
    exit(0)
