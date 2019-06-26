__all__ = ['EscapeJSe']


def _escape_js_template_tags(s):
    """
    Jinja Filter to escape javascript template variables.
    """

    return '{{ ' + str(s) + ' }}'


class EscapeJSe:
    """
    Flask extension. Registers 'jse' jinja filter to escape curly braces for
    use in javascript frameworks.
    """
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.jinja_env.filters['jse'] = _escape_js_template_tags
