# Url Shortener Library.

from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


class UrlShortener(object):
    """This object is used to hold the settings used for short url. Instances
    of :class:`UrlShortner` are *not* bound to specific apps, so you can
    create one in the main body of your code and then bind it to your
    app in a factory function.
    """

    def __init__(self, app=None, add_context_processor=True):
        if app is not None:
            self.init_app(app, add_context_processor)

    def setup_app(self, app, add_context_processor=True):  # pragma: no cover
        """
        This method has been deprecated. Please use
        :meth:`LoginManager.init_app` instead.
        """
        self.init_app(app, add_context_processor)

    def init_app(self, app, add_context_processor=True):
        """
        Configures an application.
        :param app: The :class:`flask.Flask` object to configure.
        :type app: :class:`flask.Flask`
        :param add_context_processor: Whether to add a context processor to
            the app that adds a `current_user` variable to the template.
            Defaults to ``True``.
        :type add_context_processor: bool
        """

        app.url_map.converters['regex'] = RegexConverter

        app.login_manager = self
        from lil_url.url_shortner import server_url
        from lil_url import DEFAULT_PREFIX
        app.add_url_rule('/{}/<regex("[a-zA-Z0-9_-]*"):slug>/'.format(DEFAULT_PREFIX), 'serve_short_url', server_url)
