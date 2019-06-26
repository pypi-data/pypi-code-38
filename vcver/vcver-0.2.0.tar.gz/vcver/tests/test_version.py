import pytest
from vcver.scm.mock import MockSCM
from vcver.version import determine_version


@pytest.fixture
def scm_dict():
    return {
        "tag_version": "1.0",
        "commit_count": 20,
        "scm_change_id": "abc123",
        "branch": "master",
    }


@pytest.fixture
def scm(scm_dict):
    return MockSCM(scm_dict)


@pytest.mark.parametrize(
    "inp, expected",
    [
        ({}, "1.0.dev20+master.abc123"),
        ({"branch": "develop"}, "0.dev20+develop.abc123"),
        ({"branch": "hotfix"}, "0.dev20+hotfix.abc123"),
        ({"branch": "feature/ABC-123"}, "0.dev20+featureabc123.abc123"),
        ({"commit_count": 30}, "1.0.dev30+master.abc123"),
        ({"tag_version": "2.0b1"}, "2.0b1.dev20+master.abc123"),
        ({"tag_version": "2.0beta"}, "2.0b0.dev20+master.abc123"),
        ({"scm_change_id": "012345"}, "1.0.dev20+master.12345"),
    ],
)
def test_version(inp, expected, scm_dict):
    scm_dict.update(inp)
    scm = MockSCM(scm_dict)
    assert determine_version(scm) == expected


def test_custom_version_format(scm):
    assert (
        determine_version(scm, version_format="{main_version}.{commit_count}")
        == "1.0.20"
    )


def test_release_version_format(scm):

    assert (
        determine_version(
            scm,
            release_version_format="{main_version}.{commit_count}",
            is_release=False,
        )
        == "1.0.dev20+master.abc123"
    )

    assert (
        determine_version(
            scm, is_release=True, release_version_format="{main_version}.{commit_count}"
        )
        == "1.0.20"
    )


def test_is_release(scm):
    assert determine_version(scm, is_release=False) == "1.0.dev20+master.abc123"

    assert determine_version(scm, is_release=True) == "1.0"
