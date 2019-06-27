from pydoc import locate

__author__ = "Arijit Basu"
__email__ = "sayanarijit@gmail.com"
__homepage__ = "https://github.com/sayanarijit/pyramid_htmldoom"
__description__ = "htmldoom rendering library plugin for Pyramid"
__version__ = "v0.1.5"
__license__ = "MIT"
__all__ = [
    "__author__",
    "__email__",
    "__homepage__",
    "__description__",
    "__version__",
    "__license__",
    "HTMLDoomRenderer",
    "HTMLDoomRendererFactory",
]


class HTMLDoomRendererFactory:
    def __call__(self, info):
        name, package = info.name[:-3], info.package  # Ignoring .py extension

        def template_loader():
            name_with_package = f"{name}.Template"
            # if package:
            #     name_with_package = f"{package.__name__}.{name}.Template"

            renderer = locate(name_with_package)
            if not renderer:
                raise ValueError(f"renderer not found: {name_with_package}")
            return renderer

        return HTMLDoomRenderer(template_loader)


class HTMLDoomRenderer:
    def __init__(self, template_loader):
        self.template_loader = template_loader

    def __call__(self, value, system):
        try:
            data = dict(system, **value)
        except (TypeError, ValueError) as e:
            raise ValueError("renderer was passed non-dictionary as value: {e}")

        template = self.template_loader()
        return str(template(data))


def includeme(config):
    config.add_renderer(".py", HTMLDoomRendererFactory())
