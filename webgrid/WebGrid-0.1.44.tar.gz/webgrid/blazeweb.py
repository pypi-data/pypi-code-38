from __future__ import absolute_import

import io
import warnings
from os import path

from blazeweb.content import getcontent
from blazeweb.globals import ag, rg, user
from blazeweb.routing import abs_static_url
from blazeweb.templating.jinja import content_filter
from blazeweb.utils import abort
from blazeweb.wrappers import StreamResponse
import jinja2 as jinja
from jinja2.exceptions import TemplateNotFound
from sqlalchemybwc import db as sabwc_db
from webgrid import BaseGrid


class WebGrid(object):
    jinja_loader = jinja.PackageLoader('webgrid', 'templates')

    def __init__(self, db=None, component='webgrid'):
        self.init_db(db or sabwc_db)
        self.component = component
        ag.tplengine.env.filters['wg_safe'] = content_filter
        self.jinja_environment = jinja.Environment(
            loader=self.jinja_loader,
            autoescape=True
        )

    def init_db(self, db):
        self.db = db

    def sa_query(self, *args, **kwargs):
        return self.db.sess.query(*args, **kwargs)

    def request_args(self):
        return rg.request.args

    def web_session(self):
        return user

    def flash_message(self, category, message):
        user.add_message(category, message)

    def request(self):
        return rg.request

    def static_path(self):
        return path.join(path.dirname(__file__), 'static')

    def static_url(self, url_tail):
        return abs_static_url('component/webgrid/{0}'.format(url_tail))

    def file_as_response(self, data_stream, file_name, mime_type):
        rp = StreamResponse(data_stream)
        rp.headers['Content-Type'] = mime_type
        rp.headers['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
        abort(rp)

    def xls_as_response(self, wb, file_name):
        warnings.warn(
            'xls_as_response is deprecated. Use file_as_response instead',
            DeprecationWarning
        )
        data = io.BytesIO()
        wb.save(data)
        data.seek(0)
        self.file_as_response(data, file_name, 'application/vnd.ms-excel')

    def render_template(self, endpoint, **kwargs):
        try:
            return getcontent(endpoint, **kwargs)
        except TemplateNotFound:
            if ':' in endpoint:
                raise
            return getcontent('{0}:{1}'.format(self.component, endpoint), **kwargs)
wg_blaze_manager = WebGrid()  # noqa: E305


class Grid(BaseGrid):
    manager = wg_blaze_manager
