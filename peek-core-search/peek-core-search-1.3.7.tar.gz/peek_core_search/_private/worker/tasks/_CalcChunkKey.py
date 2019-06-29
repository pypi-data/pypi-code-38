import logging

logger = logging.getLogger(__name__)

INDEX_BUCKET_COUNT = 8192
OBJECT_BUCKET_COUNT = 8192


def makeSearchIndexChunkKey(key: str) -> int:
    """ Make Chunk Key

    This is simple, and provides a reasonable distribution

    :param key:

    :return: chunkKey

    """

    if not key:
        raise Exception("key is None or zero length")

    bucket = 0
    for char in key:
        bucket = ((bucket << 5) - bucket) + ord(char)
        bucket = bucket | 0  # This is in the javascript code.

    bucket = bucket & (INDEX_BUCKET_COUNT - 1)

    return bucket


def makeSearchObjectChunkKey(key: int) -> int:
    """ Make Chunk Key

    This is simple, and provides a reasonable distribution

    :param key:

    :return: chunkKey

    """

    if key is None:
        raise Exception("key is None")

    bucket = key & (OBJECT_BUCKET_COUNT - 1)

    return bucket
