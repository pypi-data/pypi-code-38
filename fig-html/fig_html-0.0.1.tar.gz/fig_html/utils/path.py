import os
from pathlib import Path


class _RelativePathManager(object):
    """to get relative path for embedding html
    """
    def __init__(self, root_dir):
        """
        """
        assert isinstance(root_dir, str)
        self.root_dir = root_dir

        self._VERBOSE = False

    def get_fignames(self, fig_path: str) -> list:
        """
        >>> root_dir = "./tests/outputs"
        >>> fig_path = "./tests/outputs/correlation"
        >>> _RelativePathManager(root_dir).get_fignames(fig_path)
        ['./fig1.png', './fig2.png', './fig3.png']
        """
        p = Path(fig_path)
        fignames = list(p.glob("*.png"))
        fignames_str = [ "./" + str(figname.relative_to(fig_path)) for figname in fignames]
        fignames_str = sorted(fignames_str)
        if self._VERBOSE:
            print("--- get_fignames ---")
            print(f"fig_path : {fig_path},\nfignames_str : {fignames_str}")

        return fignames_str

    def get_css_path(self, fig_path: str) -> str:
        """
        >>> root_dir = "./tests/outputs"
        >>> fig_path = "./tests/outputs/scatter"
        >>> _RelativePathManager(root_dir).get_css_path(fig_path)
        '../_static/basestyle.css'
        """
        css_path = os.path.relpath(self.root_dir, fig_path)
        css_path = os.path.join(css_path, "_static/basestyle.css")

        if self._VERBOSE:
            print("--- get_css_path ---")
            print(f"fig_path : {fig_path},\ncss_path : {css_path}")

        return css_path

    def get_lower_dir_htmls(self, fig_path: str) -> list:
        """
        fig_path : str
            i.e. fig_path = "./outputs"

        >>> root_dir = "./tests/outputs"
        >>> _RelativePathManager(root_dir).get_lower_dir_htmls(root_dir)
        ['./correlation/correlation.html', './histogram/histogram.html']
        """
        p = Path(fig_path)
        html_paths = list(p.glob("*/*.html"))
        html_paths = [os.path.join("./", str(html_path.relative_to(fig_path))) for html_path in html_paths]

        if self._VERBOSE:
            print("--- get_lower_dir_htmls ---")
            print(f"fig_path : {fig_path},\nhtml_paths : {html_paths}")

        return html_paths

    def get_parent_dir_html(self, fig_path: str) -> str:
        """
        >>> root_dir = "./tests/outputs"
        >>> fig_path = "./tests/outputs/scatter"
        >>> _RelativePathManager(root_dir).get_parent_dir_html(fig_path)
        '../../../tests/outputs/outputs.html'
        """
        p = Path(fig_path)

        if self.root_dir == fig_path:
            parent_htmls = list(p.glob("*.html"))
            if len(parent_htmls) == 0:
                basename = os.path.basename(fig_path) + ".html"
                parent_htmls.append(os.path.join(fig_path, basename))
        else:
            parent_htmls = list(p.parent.glob("*.html"))

        assert len(parent_htmls) == 1, f"too many html file in {str(p.parent)} : {parent_htmls}"
        parent_html = parent_htmls[0]

        for _ in range(len(Path(fig_path).parts)): # back to ./
            parent_html = os.path.join("../", str(parent_html))

        if self._VERBOSE:
            print("--- get_parent_dir_html ---")
            print(f"fig_path : {fig_path},\nparent_html : {parent_html}")

        return parent_html

    def get_child_dir_path(self, fig_path: str, relative_from_fig_path: bool=False) -> list:
        """
        >>> root_dir = "./outputs"
        >>> _RelativePathManager(root_dir).get_child_dir_path(root_dir)
        ['./outputs/correlation', './outputs/histogram']
        """
        p = Path(fig_path)
        child_paths = [elem for elem in list(p.glob("*")) if elem.is_dir()]
        child_paths = ["./" + str(child_path) for child_path in child_paths]

        if len(child_paths) > 0:
            exclude_name_list = ["_static"]
            for exclude_name in exclude_name_list:
                exclude_path = os.path.join(fig_path, exclude_name)
                if exclude_path in child_paths:
                    child_paths.remove(exclude_path)

        if relative_from_fig_path:
            child_paths = [os.path.relpath(child_path, fig_path) for child_path in child_paths]

        if self._VERBOSE:
            print("--- get_child_dir_path ---")
            print(f"fig_path : {fig_path},\nchild_paths : {child_paths}")

        return child_paths

    def get_dirnames_from_htmls(self, html_paths: list) -> list:
        """
        >>> root_dir = "./tests/outputs"
        >>> _RelativePathManager(root_dir).get_dirnames_from_htmls(["./tests/outputs/test.html"])
        ['outputs']
        """
        dirnames = [ os.path.basename(os.path.dirname(html_path)) for html_path in html_paths ]

        if self._VERBOSE:
            print("--- get_dirnames_from_htmls ---")
            print(f"html_paths : {html_paths},\ndirnames : {dirnames}")

        return dirnames

    def get_lower_dirname_html_pair(self, fig_path: str) -> list:
        child_dir_paths = self.get_child_dir_path(fig_path, relative_from_fig_path=True)

        lower_dirname_html_pair = []
        for child_dir_path in child_dir_paths:
            child_dirname = os.path.basename(child_dir_path)
            html_path = os.path.join(child_dir_path, child_dirname + ".html")
            lower_dirname_html_pair.append((child_dirname, html_path))


        if self._VERBOSE:
            print("--- get_lower_dirname_html_pair ---")
            print(f"fig_path : {fig_path},\nlower_dirname_html_pair : {lower_dirname_html_pair}")

        return lower_dirname_html_pair


        

