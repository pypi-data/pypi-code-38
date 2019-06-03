"""Package for saving and loading RabbitMQ messages.
"""

from message import Message
from pika_message import PikaMessage
from queue import _Queue
from rabbit import _Rabbit
from rabbit_config import _RabbitConfig
from reader import Reader
from writer import Writer

NAME = "rabbit_droppings"
VERSION = "1.0.0"
