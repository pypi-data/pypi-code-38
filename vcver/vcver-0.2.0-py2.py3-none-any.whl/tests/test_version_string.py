import pytest
from vcver.version_string import make_string_pep440_compatible


@pytest.mark.parametrize(
    "inp, out",
    [
        ("master", "master"),
        ("develop", "develop"),
        ("hotfix", "hotfix"),
        ("feature/foo", "featurefoo"),
        ("feature_bar", "featurebar"),
        ("feature+baz", "featurebaz"),
        ("feature/ABC-123", "featureABC123"),
    ],
)
def test_make_string_pep440_compatible(inp, out):
    assert make_string_pep440_compatible(inp) == out
