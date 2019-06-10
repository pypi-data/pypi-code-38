from jkutils.git import git_revision_hash


def test_git():
    assert git_revision_hash() != "Not found"
