from pathlib import Path
from typing import Mapping, Optional

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    is_,
)

from microcosm_sagemaker.testing.bytes_extractor import ExtractorMatcherPair


def identity(x):
    return x


def directory_comparison(
    gold_dir: Path,
    actual_dir: Path,
    matchers: Optional[Mapping[Path, ExtractorMatcherPair]] = None,
):
    """
    Recursively checks the contents of `actual_dir` against the expected
    contents in `gold_dir`.  It is also possible to leave certain files out of
    the gold dir, and instead specify an (extractor, matcher) pair that should
    be used to extract and match the contents of the given file instead.

    """
    matchers = matchers or dict()

    actual_paths = sorted([
        subpath.relative_to(actual_dir)
        for subpath in actual_dir.glob('**/*')
    ])
    gold_paths = sorted([
        subpath.relative_to(gold_dir)
        for subpath in gold_dir.glob('**/*')
    ])

    assert_that(actual_paths, contains(*gold_paths))

    for path in gold_paths:
        gold_path = gold_dir / path
        actual_path = actual_dir / path

        if gold_path.is_dir():
            assert_that(actual_path.is_dir(), is_(True))
        else:
            if path in matchers:
                extractor, matcher_constructor = matchers[path]
            else:
                extractor, matcher_constructor = ExtractorMatcherPair(
                    identity,
                    lambda x: is_(equal_to(x)),
                )

            assert_that(
                extractor(actual_path.read_bytes()),
                matcher_constructor(
                    extractor(gold_path.read_bytes()),
                ),
                path,
            )
