"""Test manual mode."""

# Standard library modules
import logging

# Project modules
from custombot import Bot

log_formatter = logging.Formatter(
    "%(asctime)s [%(module)-15s %(levelname)-8s]     %(message)s",
    style='%'
)
# Get root logger and set level to DEBUG
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
# ConsoleHandler (log to terminal)
ConsoleHandler = logging.StreamHandler()
ConsoleHandler.setFormatter(log_formatter)
ConsoleHandler.setLevel(logging.DEBUG)
# Add ConsoleHandler to root_logger
root_logger.addHandler(ConsoleHandler)
davtebot = Bot.get('335545766:AAGA84QCWFp3pGc1KT7cYN9Rl1Hj5Rbudu8', 'bot.db')
davtetest = Bot.get('279769259:AAEwkSmizL65z74zs7E0Y13J2W0la9f4y30')
Bot.run_manual_mode()
