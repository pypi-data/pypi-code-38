import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from devo.exceptions import OverwriteException


TEMPLATE_DIR = Path(__file__).parent / 'templates'


def get_template_env(subdir):
    path = str(TEMPLATE_DIR / subdir)
    return Environment(loader=FileSystemLoader(path),
                       keep_trailing_newline=True,
                       trim_blocks=True)


def render_template_env_to_target(env, target_dir, ctx, force):
    env = get_template_env(env)

    templates_to_render = []
    overwrites = []

    for template in env.list_templates():
        data = env.get_template(template).render(**ctx)
        if data:
            output = target_dir / template
            templates_to_render.append((output, data))

    for path, _ in templates_to_render:
        if path.exists() and not force:
            overwrites.append(str(path))

    if overwrites and not force:
        raise OverwriteException('Files exist already', overwrites)

    for path, data in templates_to_render:
        if not path.parent.exists():
            os.makedirs(path.parent)
        path.write_text(data)

