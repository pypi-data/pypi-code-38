from pathlib import Path
from typing import Mapping, Optional

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    is_,
)

from microcosm_sagemaker.testing.bytes_extractor import ExtractorMatcherPair


def _identity(x):
    return x


def _is_hidden(path: Path) -> bool:
    return path.name.startswith(".")


def directory_comparison(
    gold_dir: Path,
    actual_dir: Path,
    matchers: Optional[Mapping[Path, ExtractorMatcherPair]] = None,
    ignore_hidden: bool = True,
):
    """
    Recursively checks the contents of `actual_dir` against the expected
    contents in `gold_dir`.  It is also possible to leave certain files out of
    the gold dir, and instead specify an (extractor, matcher) pair that should
    be used to extract and match the contents of the given file instead.

    By default, this function ignores hidden files.  This functionality is
    useful when you expect an empty directory, because git won't allow checking
    in an empty directory.  In this situation you can add an empty `.keep` file
    to the directory to make sure it is checked in.

    """
    if matchers is None:
        matchers = dict()

    assert_that(gold_dir.exists(), is_(True))
    assert_that(actual_dir.exists(), is_(True))

    actual_paths = sorted([
        subpath.relative_to(actual_dir)
        for subpath in actual_dir.glob('**/*')
        if not (ignore_hidden and _is_hidden(subpath))  # exclude hidden files if ignore_hidden is True
    ])
    gold_paths = sorted([
        subpath.relative_to(gold_dir)
        for subpath in gold_dir.glob('**/*')
        if not (ignore_hidden and _is_hidden(subpath))  # exclude hidden files if ignore_hidden is True
    ])

    assert_that(actual_paths, contains(*gold_paths))

    for path in gold_paths:
        gold_path = gold_dir / path
        actual_path = actual_dir / path

        if gold_path.is_dir():
            assert_that(actual_path.is_dir(), is_(True))
        else:
            assert_that(actual_path.is_dir(), is_(False))
            if path in matchers:
                extractor, matcher_constructor = matchers[path]
            else:
                extractor, matcher_constructor = ExtractorMatcherPair(
                    _identity,
                    lambda x: is_(equal_to(x)),
                )

            assert_that(
                extractor(actual_path.read_bytes()),
                matcher_constructor(
                    extractor(gold_path.read_bytes()),
                ),
                path,
            )
