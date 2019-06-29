import logging

logger = logging.getLogger(__name__)

BUCKET_COUNT = 8192

def makeChunkKey(modelSetKey: str, key: str) -> str:
    """ Make Chunk Key

    This is simple, and provides a reasonable distribution
ß
    :param modelSetKey:
    :param key:

    :return: chunkKey

    """

    if not modelSetKey:
        raise Exception("modelSetKey is None or zero length")

    if not key:
        raise Exception("key is None or zero length")

    bucket = 0
    for char in key:
        bucket = ((bucket << 5) - bucket) + ord(char)
        bucket = bucket | 0  # This is in the javascript code.

    bucket = bucket & (BUCKET_COUNT - 1)

    return '%s.%s' % (modelSetKey, bucket)

