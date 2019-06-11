import shutil
from importlib import resources as importlib_resources

import jinja2

from tree_html import color_scheme_dict


def load_template(template_file: str) -> jinja2.Template:
    """Load a Jinja2 template from the package."""
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("tree_html", "templates"),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        keep_trailing_newline=True,
        autoescape=False,
    )
    return env.get_template(template_file)


def render_template(template_file: str, params: dict) -> str:
    return load_template(template_file).render(**params)


def copy_package_resource(package, resource, dest):
    with importlib_resources.path(package, resource) as resource_path:
        shutil.copy(resource_path, dest)


def copy_static_assets(out_dir, color_scheme):
    static_assets = [
        color_scheme_dict[color_scheme],
        "cd-icons.svg",
        "main.js",
        "util.js",
    ]

    out_dir = out_dir / "assets"
    out_dir.mkdir(exist_ok=True, parents=True)

    for asset in static_assets:
        dest = out_dir / asset if not ".css" in asset else out_dir / "style.css"
        copy_package_resource("tree_html.assets", asset, dest)
