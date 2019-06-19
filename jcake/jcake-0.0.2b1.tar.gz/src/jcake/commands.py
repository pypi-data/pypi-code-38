#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import stat
import shutil

from .workspace import get_or_create_worksapce


#
# ========================================================
#                  create command
# ========================================================
#

GIT_REPOSITORY_URI = "git@git.kanzhun-inc.com:liulong/zhipin-graph.git"


TMPL_ROOT_DIR = "zhipin-graph"
TMPL_DIR = "template"


COMMON_TMPL_RELPATH = os.path.join(TMPL_ROOT_DIR, TMPL_DIR)
MODULE_TMPL_RELPATH = os.path.join(TMPL_ROOT_DIR, "module", TMPL_DIR)
OCEANUS_SERVICE_TMPL_RELPATH = os.path.join(
    TMPL_ROOT_DIR,
    "oceanus-service",
    TMPL_DIR
)


def _rm_repository(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)


def clone_repository(workspace):
    """
    clone git项目(基准项目，提供cookiecutter模板)

    Args:
      workspace: 工作空间

    """
    from .repository import git_clone

    cur_path = os.getcwd()
    os.chdir(workspace)

    if os.path.exists(TMPL_ROOT_DIR):
        _rm_repository(TMPL_ROOT_DIR)

    try:
        git_clone(GIT_REPOSITORY_URI)
    except Exception as error:
        if 'already exists' in error.output:
            pass
        else:
            raise error

    os.chdir(cur_path)


def create_common(workspace, project_name):
    """
    创建所有项目的公共部分，对应zhipin-graph的模板为: zhipin-graph/template

    """
    from cookiecutter.main import cookiecutter

    cur_path = os.getcwd()
    os.chdir(workspace)

    generate_common_path = cookiecutter(
        COMMON_TMPL_RELPATH,
        no_input=True,
        overwrite_if_exists=True,
        extra_context={
            "project_name": project_name
        }
    )
    os.chdir(cur_path)
    return generate_common_path


def create_project(workspace, template_path):
    from cookiecutter.main import cookiecutter

    project_dir_path = cookiecutter(template_path)
    project_name = os.path.basename(project_dir_path)
    common_dir = create_common(workspace, project_name)

    files = os.listdir(common_dir)
    for f in files:
        shutil.move(os.path.join(common_dir, f), project_dir_path)
    shutil.rmtree(common_dir)

    return project_dir_path


def create(isfor_ms):
    """
    创建项目

    Args:
      isfor_ms: 是否创建微服务项目

    Returns:
      创建好的项目路径

    """
    workspace = get_or_create_worksapce()
    clone_repository(workspace)

    if isfor_ms:
        project_template_path = os.path.join(
            workspace,
            OCEANUS_SERVICE_TMPL_RELPATH
        )
    else:
        project_template_path = os.path.join(workspace, MODULE_TMPL_RELPATH)

    return create_project(
        workspace,
        project_template_path
    )
