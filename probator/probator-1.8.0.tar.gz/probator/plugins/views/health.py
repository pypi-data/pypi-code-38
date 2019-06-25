import pkg_resources
import probator
from flask import request, session
from more_itertools import first
from probator.constants import HTTP
from probator.database import db
from probator.plugins import BaseView
from probator.utils import has_access
from probator.wrappers import rollback
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError


class Health(BaseView):
    URLS = ['/health']

    @rollback
    def get(self):
        status = {}
        error = False
        try:
            db_time = first(db.query(func.now()).first())
            db.query('SELECT NOW()')
            status['database'] = {
                'ok': True,
                'data': db_time
            }
        except SQLAlchemyError as ex:
            error |= True
            status['database'] = {
                'ok': False,
                'data': str(ex)
            }

        status['status'] = 'OK' if not error else 'ERROR'

        return self.make_response(
            data=status,
            code=HTTP.OK if not error else HTTP.SERVER_ERROR
        )


class Version(BaseView):
    URLS = ['/version']

    def get(self):
        response = {
            'version': probator.__version__
        }

        if session['user'] and has_access(user=session['user'], required_roles=['Admin']) and 'packages' in request.args:
            response['packages'] = {pkg.project_name: pkg.version for pkg in pkg_resources.working_set}

        return self.make_response(response)
