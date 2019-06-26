import sys
import pytest
from vcver.scm.git import Git


@pytest.mark.linux
@pytest.mark.parametrize(
    "inp, out",
    [
        ("/a/b", False),
        ("/a", False),
        ("/a/b/..", False),
        ("/x/", False),
        ("/..", False),
    ],
)
@pytest.mark.usefixtures("no_fs")
def test_linux_is_repo(inp, out):
    """Fails when non-repo case is not detected for linux."""
    assert Git.is_repo(inp) == out


@pytest.mark.win32
@pytest.mark.parametrize(
    "inp, out",
    [
        ("c:\\a\\b", False),
        ("c:\\a", False),
        ("c:\\x\\..", False),
        ("c:\\f\\", False),
        ("c:\\..", False),
    ],
)
@pytest.mark.usefixtures("no_fs")
def test_win32_is_repo(inp, out):
    """Fails when non-repo case is not detected for win32."""
    assert Git.is_repo(inp) == out
