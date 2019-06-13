from pathlib import Path

from devo.utils import render_template_env_to_target


def generate_gitlab_ci(ctx, force):
    render_template_env_to_target('ci', Path.cwd(), ctx, force)


def generate_skaffold(ctx, force):
    render_template_env_to_target('skaffold', Path.cwd(), ctx, force)


def generate_k8s(ctx, force):
    k8s_target = Path.cwd() / 'k8s'
    render_template_env_to_target('k8s', k8s_target, ctx, force)


def generate_project(ctx, force):
    project_target = Path.cwd() / ctx['project_name']
    render_template_env_to_target('project', project_target, ctx, force)

