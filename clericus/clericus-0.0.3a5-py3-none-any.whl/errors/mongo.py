from pymongo.errors import DuplicateKeyError
from dataclasses import dataclass


@dataclass
class ParsedDuplicateKeyError:
    collectionName: str
    indexName: str


def parseDuplicateKeyError(error: DuplicateKeyError):
    """
        Parse an error message string from mongo where the
        error is formatted like:
            'E11000 duplicate key error collection: test.user index: uniqueEmail dup key: { : ";E7C/E1\nz1W)AG?1\x08-EA\x01\x17" }'
    """

    msg = error.details["errmsg"]

    prefix = "E11000 duplicate key error "

    if not msg.startswith(prefix):
        #this isn't parsable
        raise error

    try:
        # should be the second and fourth words after the prefix
        parts = msg[len(prefix):].split(" ")
        return ParsedDuplicateKeyError(
            collectionName=parts[1],
            indexName=parts[3],
        )
    except:
        raise error