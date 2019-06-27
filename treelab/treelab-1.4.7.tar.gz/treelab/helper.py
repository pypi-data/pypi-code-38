from uuid import uuid4
import time
from datetime import datetime


def generate_id():
    return uuid4().hex


def timestamp():
    return str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
