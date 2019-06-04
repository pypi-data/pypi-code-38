# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: test_git
#         Desc: 测试git相关操作函数
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-03 23:28
#=============================================================================
"""
import os
import mock
import pytest

from plum_tools.utils.utils import cd
from plum_tools.utils.git import get_current_branch_name
from plum_tools.utils.git import check_is_git_repository
from plum_tools.utils.git import check_repository_modify_status
from plum_tools.utils.git import check_repository_stash

from tests.common import make_temp_dir


@pytest.mark.parametrize("mock_data, data", [
    ("release-1.0.0", "release-1.0.0"),
    ("release-1.0.0 ", "release-1.0.0"),
    ("release-1.0.0  ", "release-1.0.0"),
    (" release-1.0.0", "release-1.0.0"),
    ("  release-1.0.0", "release-1.0.0"),
])
def test_get_current_branch_name(mock_data, data):
    with mock.patch("plum_tools.utils.git.run_cmd", return_value=mock_data) as m:
        assert get_current_branch_name() == data
        m.assert_called_with("git rev-parse --abbrev-ref HEAD")


def test_check_is_git_repository_with_is_repository():
    with make_temp_dir() as temp_dir:
        with cd(temp_dir):
            os.makedirs(".git")
        assert check_is_git_repository(temp_dir)


def test_check_is_git_repository_with_empty_directory():
    with make_temp_dir() as temp_dir:
        assert not check_is_git_repository(temp_dir)


def test_check_is_git_repository_with_not_repository():
    with make_temp_dir() as temp_dir:
        with cd(temp_dir):
            with open(".git", "w+") as f:
                f.write("")
        assert not check_is_git_repository(temp_dir)


@pytest.mark.parametrize("status_output", [
    '"git pull"',
    '"git push"',
])
def test_check_repository_modify_status_with_pull_or_push(status_output):
    with mock.patch("plum_tools.utils.git.run_cmd", return_value=status_output) as m:
        with make_temp_dir() as temp_dir:
            assert check_repository_modify_status(temp_dir)
        m.assert_called_with("git status")


@pytest.mark.parametrize("status_output, short_output, result", [
    ("", "", False),
    ("", "xx", True),
])
def test_check_repository_modify_status(status_output, short_output, result):
    def run_cmd(cmd):
        data = {
            "git status": status_output,
            "git status -s": short_output
        }
        return data[cmd]

    with mock.patch("plum_tools.utils.git.run_cmd", new=run_cmd):
        with make_temp_dir() as temp_dir:
            r, output = check_repository_modify_status(temp_dir)
            assert result == r
            assert output == status_output


@pytest.mark.parametrize("stash_output, result", [
    ("", False),
    ("xx", True),
])
def test_check_repository_stash(stash_output, result):
    with mock.patch("plum_tools.utils.git.run_cmd", return_value=stash_output) as m:
        with make_temp_dir() as temp_dir:
            r, output = check_repository_stash(temp_dir)
            assert result == r
            assert output == stash_output
            m.assert_called_with("git stash list")
