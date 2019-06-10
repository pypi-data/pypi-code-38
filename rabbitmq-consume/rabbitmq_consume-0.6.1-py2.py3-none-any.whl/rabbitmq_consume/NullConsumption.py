#!/usr/bin/env python

# Prepare environment
import sys

from rabbitmq_consume import Consumption, LOGGER

class NullConsumption(Consumption):

    def __init__(self,
                 properties,
                 body,
                 redelivered):
        pass


    def consume(self):
        LOGGER.info('BEGIN CONSUMPTION')
        LOGGER.info('END CONSUMPTION')
