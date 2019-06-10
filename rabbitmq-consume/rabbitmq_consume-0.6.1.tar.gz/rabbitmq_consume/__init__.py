from .Consumption import Consumption, StopWorkerException, StopListeningException
from .Consumer import Consumer, LOGGER

import rmq_consume
def main():
    """Entry point for the consume script"""
    rmq_consume.main()
