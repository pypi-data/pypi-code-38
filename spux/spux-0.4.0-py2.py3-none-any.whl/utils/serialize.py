
import cloudpickle

def save (obj):
    """Serialize an arbitrary Python object to a binary stream (array)."""

    stream = cloudpickle.dumps (obj)
    return stream

def load (stream):
    """De-serialize an arbitrary Python object from a binary stream (array)."""

    obj = cloudpickle.loads (stream)
    return obj

def state (size):
    """Construct a data container for a serialization stream with a specified size."""

    return bytearray (size)