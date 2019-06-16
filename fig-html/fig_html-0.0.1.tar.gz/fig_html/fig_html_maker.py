import os
import shutil

from jinja2 import PackageLoader
from jinja2 import Environment

import fig_html
from fig_html.utils.path import _RelativePathManager


class HTMLMaker(object):
    """
    Example
    -------
    >>> from fig_html import HTMLMaker
    >>> root_dir = "./tests/outputs"
    >>> HTMLMaker().make(root_dir)
    """
    def __init__(self):
        self._VERBOSE = False

    def make(self, root_dir: str) -> None:
        """
        root_dir : str
            directory where figures were saved
            i.e. root_dir = "./outputs"
        """
        self._copy_static_files(root_dir)
        self._make_html_in_dirs(root_dir, root_dir)

    def _make_html_in_dirs(self, root_dir: str, fig_path: str) -> None:
        """to make html in fig_path recursively
        """
        self._make_html_in_dir(root_dir, fig_path)

        sub_dirs = _RelativePathManager(root_dir).get_child_dir_path(fig_path)
        for sub_dir in sub_dirs:
            self._make_html_in_dirs(root_dir, sub_dir)

    def _make_html_in_dir(self, root_dir: str, fig_path: str) -> None:
        html_renderer = _HTMLRenderer(root_dir)
        html_str = html_renderer.render(fig_path)
        basename = os.path.basename(fig_path)
        html_savename = os.path.join(fig_path, basename + ".html")
        html_renderer.save(html_str, html_savename)

        if self._VERBOSE:
            print(f"--- {html_savename} saved ---")

    def _copy_static_files(self, root_dir: str) -> None:
        destination_path = os.path.join(root_dir, "_static")
        os.makedirs(destination_path, exist_ok=True)

        # only basestyle.css so far
        source_css_path = os.path.join(fig_html.__path__[0], "templates/basestyle.css")
        shutil.copyfile(source_css_path, os.path.join(destination_path, "basestyle.css"))


class _HTMLRenderer(object):
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def _get_template(self, template_name: str="base"):
        assert isinstance(template_name, str)
        assert template_name in ("base")

        template_basename = template_name + ".html"
        pl = PackageLoader('fig_html', 'templates')
        jinja2_env = Environment(loader=pl)

        globals_vals = {}
        globals_vals["root_dir"] = self.root_dir

        template = jinja2_env.get_template(template_basename, globals=globals_vals)
        return template

    def render(self, fig_path: str) -> str:
        path_manager = _RelativePathManager(self.root_dir)
        fignames = path_manager.get_fignames(fig_path)
        lower_dirname_html_pair = path_manager.get_lower_dirname_html_pair(fig_path)
        parent_html = path_manager.get_parent_dir_html(fig_path)
        css_path = path_manager.get_css_path(fig_path)

        rendering_params = {}
        rendering_params["template_name"] = "base"
        rendering_params["title"] = os.path.basename(fig_path)

        template = self._get_template(rendering_params["template_name"])
        html_str = template.render(title=rendering_params["title"],
                                    fignames=fignames,
                                    lower_dirname_html_pair=lower_dirname_html_pair,
                                    parent_html=parent_html,
                                    css_path=css_path)

        return html_str

    def save(self, html_str: str, savename: str) -> None:
        with open(savename, "w") as html:
            html.write(html_str)