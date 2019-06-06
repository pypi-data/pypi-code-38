import json
from typing import (
    Callable,
    Generic,
    NamedTuple,
    TypeVar,
)

from hamcrest.core.base_matcher import BaseMatcher


T = TypeVar('T')


class ExtractorMatcherPair(NamedTuple, Generic[T]):
    """
    Contains a pair of extractor and matcher which is used during testing.  The
    extractor will be applied to the raw bytes of a file output during testing,
    as well as to the raw bytes of the gold version of the file.  The output of
    the extractor applied to the gold file will then be passed to
    `matcher_constructor`, which will create a matcher based on the gold file.

    """
    # NB: We cannot use a dataclass due to python/mypy#5485
    extractor: Callable[[bytes], T]
    matcher_constructor: Callable[[T], BaseMatcher]


def json_extractor(raw_bytes):
    return json.loads(raw_bytes.decode())
