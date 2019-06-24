import logging
from io import StringIO
from typing import Callable, List, Optional
import mistune
from flask import Response, Flask, abort, request
from flask import send_from_directory, render_template_string
from prometheus_flask_exporter import PrometheusMetrics


AuthCheck = Callable[[], bool]


class CommonRoutes:
    def __init__(
        self,
        app: Flask,
        auth_checks: List[AuthCheck]=[],
        layout_template: Optional[str]='layout.html',
        layout_block: Optional[str]='content',
    ) -> None:
        """ Initialise common routes for the `app` Flask application.
        :param auth_checks: list of checks used by ensure_user_is_authorised.
        :param layout_template: template used for docs (None=ignore).
        :param layout_block: template block used for docs (None=ignore).
        """
        self.app = app
        self.enable_varz()
        self.enable_healthz()
        self.enable_logz()
        self.enable_docz()
        self.auth_checks = auth_checks
        self.layout_template = layout_template
        self.layout_block = layout_block

    def ensure_user_is_authorised(self) -> None:
        """ Ensure that user is allowed to view internal endpoints.
        This metod will raise HTTP 403 to block bad requests, otherwise
        it will do nothing.
        It can be extended with a list of auth_checks:

        is_admin = lambda: request.remote_addr == '127.0.0.1'
        mworks = CommonRoutes(app, auth_checks=[is_admin])
        """
        for is_authorised in self.auth_checks:
            if not is_authorised():
                abort(403)

    def enable_varz(self) -> None:
        """ Enable a /varz route. It's used for monitoring and statistics.
        Varz is a standard path used by monitoring systems. This format is
        understood by standard software, like prometheus (or borgmon).
        Users of mworks can easily track their own variables:

        mworks = CommonRoutes(app)
        var = mworks.metrics.info('var_name', 'Var description')
        var.set(1337)
        """
        def check_varz_auth():
            """ Sadly, PrometheusMetrics doesn't support authentication,
            so we need this little hack
            """
            if request.path == '/varz':
                self.ensure_user_is_authorised()

        self.app.before_request(check_varz_auth)
        self.metrics = PrometheusMetrics(self.app, path='/varz')

    def enable_healthz(self) -> None:
        """ Enable a /healthz route. It's used for service health-checks.
        Healthz is a standard path used for service health checks. It should
        return HTTP 200 code if the application is healthy, and 500 otherwise.
        """
        def get_healthz():
            # do not check authorisation - this is a public endpoint
            return ("ok", 200)

        self.app.route('/healthz')(get_healthz)

    def enable_logz(self) -> None:
        """ Enable a /logz route. It provides easy access to the service logs.
        Data in logs can be pretty senstive, so remember to restrict access to
        the intranet.
        """
        stream = StringIO()
        log = logging.getLogger()
        handler = logging.StreamHandler(stream)
        log.addHandler(handler)

        def get_logz():
            self.ensure_user_is_authorised()
            text = stream.getvalue()
            return Response(text, mimetype='text/plain')

        self.app.route('/logz')(get_logz)

    def enable_docz(self) -> None:
        """ Enable a /docz/ route. It provides easy access to the docs.
        Documentation can contain internal data, so we authorise user before.
        """
        def send_markdown_file(path: str) -> str:
            """ Send markdown file or 404. path is not validated, so ensure
            it is not controlled by the potential attacker
            """
            try:
                with open(path, "r") as readmef:
                    content = mistune.markdown(readmef.read())
                if self.layout_template is None or self.layout_block is None:
                    return content
                template = f"""
                    {{% extends '{self.layout_template}' %}}
                    {{% block {self.layout_block} %}}
                    {content}
                    {{% endblock {self.layout_block} %}}
                """
                return render_template_string(template)
            except FileNotFoundError:
                abort(404)

        def get_docz():
            self.ensure_user_is_authorised()
            readme_path = f"{self.app.root_path}/../README.md"
            return send_markdown_file(readme_path)

        def get_doc_content(filename):
            self.ensure_user_is_authorised()
            doc_root = f"{self.app.root_path}/../doc/"
            if filename.endswith('.md'):
                md_path = f"{doc_root}/{filename}"
                return send_markdown_file(md_path)
            return send_from_directory(doc_root, filename)

        self.app.route('/docz/')(get_docz)
        self.app.route('/docz/doc/<filename>')(get_doc_content)
