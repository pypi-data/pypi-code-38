from jinja2 import FileSystemLoader, Environment
from .base import TemplateEngineBase


class TemplateEngine(TemplateEngineBase):
    """
    Jinja2 template engine.
    Accepts params:
    root - path to the loader root.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        root = self._params.get('root', str(self._md_file.parent))
        self._env = Environment(loader=FileSystemLoader(root))

    def build(self):
        """Build template with jinja and return resulting string"""
        template = self._env.from_string(self._content)
        return template.render(**self._context)
