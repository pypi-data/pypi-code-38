"""Contains the Flask app for the REST API"""
import logging
import os
import sys
from abc import abstractproperty

from flask import Flask, request, session, abort
from flask_compress import Compress
from flask_restful import Api
from flask_script import Server
from pkg_resources import resource_filename
from probator import app_config, PROBATOR_PLUGINS
from probator.config import dbconfig, DBCChoice
from probator.constants import DEFAULT_CONFIG_OPTIONS, PLUGIN_NAMESPACES
from probator.database import db
from probator.json_utils import ProbatorJSONDecoder, ProbatorJSONEncoder
from probator.log import auditlog
from probator.plugins import BootstrappedBasePlugin
from probator.plugins.types.accounts import BaseAccount
from probator.plugins.views import BaseView, LoginRedirectView, LogoutRedirectView
from probator.schema import ResourceType, ConfigNamespace, ConfigItem, Role, Template, IssueTypeModel
from probator.utils import get_hash, diff, has_access
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError

logger = logging.getLogger(__name__.split('.')[0])

__initialized = False


# region Helper functions
def _get_config_namespace(prefix, name, sort_order=2):
    nsobj = db.ConfigNamespace.find_one(ConfigNamespace.namespace_prefix == prefix)
    if not nsobj:
        logger.info(f'Adding namespace {name}')
        nsobj = ConfigNamespace()
        nsobj.namespace_prefix = prefix
        nsobj.name = name
        nsobj.sort_order = sort_order
        db.session.add(nsobj)
    return nsobj


def _register_default_option(nsobj, opt):
    """Register default configuration objects

    Register default ConfigOption value if it doesn't exist. If does exist, update the description if needed

    Args:
        nsobj (`ConfigNamespace`): Namespace object
        opt (`ConfigOption`): Configuration object

    Returns:
        `None`
    """
    item = ConfigItem.get(nsobj.namespace_prefix, opt.name)
    if not item:
        logger.info(f'Adding {nsobj.namespace_prefix}.{opt.name} ({opt.type}) = {opt.default_value}')
        item = ConfigItem()
        item.namespace_prefix = nsobj.namespace_prefix
        item.key = opt.name
        item.value = opt.default_value
        item.type = opt.type
        item.description = opt.description
        nsobj.config_items.append(item)
    else:
        if item.description != opt.description:
            logger.info(f'Updating description description of {item.namespace_prefix} / {item.key}')
            item.description = opt.description
            db.session.add(item)


def _bootstrap_plugins():
    for ns, info in PROBATOR_PLUGINS.items():
        if info['name'] == 'commands':
            continue

        for entry_point in info['plugins']:
            cls = entry_point.load()
            if issubclass(cls, BootstrappedBasePlugin):
                cls.bootstrap()


def _add_default_roles():
    roles = {
        'Admin': '#BD0000',
        'NOC': '#5B5BFF',
        'User': '#008000'
    }

    for name, color in roles.items():
        if not Role.get(name):
            role = Role()
            role.name = name
            role.color = color
            db.session.add(role)
            logger.info(f'Added standard role {name} ({color})')


def _import_templates(force=False):
    """Import templates from disk into database

    Reads all templates from disk and adds them to the database. By default, any template that has been modified by
    the user will not be updated. This can however be changed by setting `force` to `True`, which causes all templates
    to be imported regardless of status

    Args:
        force (`bool`): Force overwrite any templates with local changes made. Default: `False`

    Returns:
        `None`
    """
    packages = {'probator'} | {ep.module_name for ns in PLUGIN_NAMESPACES.values() for ep in PROBATOR_PLUGINS[ns]['plugins']}
    disk_templates = {}

    for package in packages:
        tmplpath = os.path.join(resource_filename(package, 'data'), 'templates')
        disk_templates.update({f: os.path.join(root, f) for root, directory, files in os.walk(tmplpath) for f in files})
    db_templates = {tmpl.template_name: tmpl for tmpl in db.Template.find()}

    for name, template_file in disk_templates.items():
        with open(template_file, 'r') as f:
            body = f.read()
        disk_hash = get_hash(body)

        if name not in db_templates:
            template = Template()
            template.template_name = name
            template.template = body

            db.session.add(template)
            auditlog(
                event='template.import',
                actor='init',
                data={
                    'template_name': name,
                    'template': body
                }
            )
            logger.info(f'Imported template {name}')
        else:
            template = db_templates[name]
            db_hash = get_hash(template.template)

            if db_hash != disk_hash:
                if force or not db_templates[name].is_modified:
                    old_body = template.template
                    template.template = body

                    db.session.add(template)
                    auditlog(
                        event='template.update',
                        actor='init',
                        data={
                            'template_name': name,
                            'template_diff': diff(old_body, body, template.template_name)
                        }
                    )
                    logger.info(f'Updated template {name}')
                else:
                    logger.warning(
                        f'Updated template available for {name}. Will not import as it would '
                        f'overwrite user edited content and force is not enabled'
                    )
# endregion


def initialize():
    """Initialize the application configuration, adding any missing default configuration or roles

    Returns:
        `None`
    """
    global __initialized

    if __initialized:
        return

    # Setup all the default base settings
    try:
        for data in DEFAULT_CONFIG_OPTIONS:
            nsobj = _get_config_namespace(data['prefix'], data['name'], sort_order=data['sort_order'])
            for opt in data['options']:
                _register_default_option(nsobj, opt)
            db.session.add(nsobj)

        # Iterate over all of our plugins and setup their defaults
        for ns, info in PROBATOR_PLUGINS.items():
            if info['name'] == 'commands':
                continue

            for entry_point in info['plugins']:
                cls = entry_point.load()
                if hasattr(cls, 'ns'):
                    ns_name = f'{info.name.capitalize()}: {cls.name}'
                    if not isinstance(cls.options, abstractproperty):
                        if cls.options:
                            nsobj = _get_config_namespace(cls.ns, ns_name)

                            for opt in cls.options:
                                _register_default_option(nsobj, opt)

                            db.session.add(nsobj)

        # Create the default roles if they are missing and import any missing or updated templates,
        # if they havent been modified by the user
        _add_default_roles()
        _import_templates()

        db.session.commit()
        dbconfig.reload_data()

        _bootstrap_plugins()
        __initialized = True
    except ProgrammingError as ex:
        if str(ex).find('1146') != -1:
            logger.error('Missing required tables, please make sure you run `probator db upgrade`')


class ServerWrapper(Server):
    """Wrapper class for the built-in runserver functionality, which registers views before calling Flask's
    ServerWrapper
    """

    def run(self):
        super().run()

    def __call__(self, app, *args, **kwargs):
        app.register_plugins()
        super().__call__(app, *args, **kwargs)


class ProbatorFlask(Flask):
    """Wrapper class for the Flask application. Takes case of setting up all the settings require for flask to run
    """
    json_encoder = ProbatorJSONEncoder
    json_decoder = ProbatorJSONDecoder

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = None
        self.active_auth_system = None
        self.types = {}
        self.issue_types = {}
        self.available_auth_systems = {}

        self.config['DEBUG'] = app_config.log_level == 'DEBUG'
        self.config['SECRET_KEY'] = app_config.flask.secret_key

        initialize()
        self.api = ProbatorAPI(self)

        self.notifiers = self.__register_notifiers()

    def register_plugins(self):
        self.__register_types()
        self.__register_issues()
        self.api.register_views(self)

    def update_auth_system_settings(self):
        """Update the list of available auth systems

        Returns:
            `None`
        """
        auth_systems = []
        cfg_item = dbconfig.get('auth_system')

        for entry_point in PROBATOR_PLUGINS['probator.plugins.auth']['plugins']:
            cls = entry_point.load()
            auth_systems.append(cls.name)

        dbconfig.set(
            namespace='default',
            key='auth_system',
            value=DBCChoice({
                'enabled': cfg_item['enabled'],
                'available': auth_systems,
                'max_items': 1,
                'min_items': 1

            })
        )

    def register_auth_system(self, auth_system):
        """Register a given authentication system with the framework

        Returns `True` if the `auth_system` is registered as the active auth system, else `False`

        Args:
            auth_system (:obj:`BaseAuthPlugin`): A subclass of the `BaseAuthPlugin` class to register

        Returns:
            `bool`
        """
        auth_system_settings = dbconfig.get('auth_system')

        if auth_system.name == auth_system_settings['enabled'][0]:
            self.active_auth_system = auth_system
            auth_system().bootstrap()
            logger.debug(f'Registered {auth_system.name} as the active auth system')
            return True

        else:
            logger.debug(f'Not trying to load the {auth_system.name} auth system as it is disabled by config')
            return False

    # region Helper methods
    def __register_types(self):
        """Iterates all entry points for resource types and registers a `resource_type_id` to class mapping

        Returns:
            `None`
        """
        try:
            for entry_point in PROBATOR_PLUGINS['probator.plugins.types']['plugins']:
                cls = entry_point.load()
                self.types[ResourceType.get(cls.resource_type).resource_type_id] = cls
                logger.debug(f'Registered resource type {cls.__name__}')
        except SQLAlchemyError as ex:
            logger.warning(f'Failed loading type information: {ex}')

    def __register_issues(self):
        """Iterates all entry points for issue types and registers a `issue_type_id` to class mapping

        Returns:
            `None`
        """
        try:
            for entry_point in PROBATOR_PLUGINS['probator.plugins.types.issues']['plugins']:
                cls = entry_point.load()
                self.issue_types[IssueTypeModel.get(cls.issue_type).issue_type_id] = cls
                logger.debug(f'Registered issue type {cls.__name__}')
        except SQLAlchemyError as ex:
            logger.warning(f'Failed loading type information: {ex}')

    @staticmethod
    def __register_notifiers():
        """Lists all notifiers to be able to provide metadata for the frontend

        Returns:
            `list` of `dict`
        """
        notifiers = {}
        for entry_point in PROBATOR_PLUGINS['probator.plugins.notifiers']['plugins']:
            cls = entry_point.load()
            notifiers[cls.notifier_type] = cls.validation

        return notifiers
    # endregion


class ProbatorAPI(Api):
    """Wrapper around the flask_restful API class."""

    def register_views(self, app):
        """Iterates all entry points for views and auth systems and dynamically load and register the routes with Flask

        Args:
            app (`ProbatorFlask`): ProbatorFlask object to register views for

        Returns:
            `None`
        """
        self.add_resource(LoginRedirectView, '/auth/login')
        self.add_resource(LogoutRedirectView, '/auth/logout')

        app.update_auth_system_settings()

        for entry_point in PROBATOR_PLUGINS['probator.plugins.auth']['plugins']:
            cls = entry_point.load()
            app.available_auth_systems[cls.name] = cls

            if app.register_auth_system(cls):
                for vcls in cls.views:
                    self.add_resource(vcls, *vcls.URLS)
                    logger.debug(f'Registered auth system view {cls.__name__} for paths: {", ".join(vcls.URLS)}')

        if not app.active_auth_system:
            logger.error('No auth systems active, please enable an auth system and then start the system again')
            sys.exit(-1)

        for entry_point in PROBATOR_PLUGINS['probator.plugins.views']['plugins']:
            view = entry_point.load()
            self.add_resource(view, *view.URLS)

            logger.debug(f'Registered view {view.__name__} for paths: {", ".join(view.URLS)}')


def before_request():
    """Checks to ensure that the session is valid and validates the users CSRF token is present

    Returns:
        `None`
    """
    _, accounts = BaseAccount.search()

    if 'user' in session and session['user']:
        session['accounts'] = [acct.account_id for acct in accounts if has_access(session['user'], acct.required_roles)]

    if not request.path.startswith('/saml') and not request.path.startswith('/auth'):
        # Validate the session has the items we need
        if 'accounts' not in session:
            logger.debug('Missing "accounts" from session object, sending user to login page')
            return BaseView.make_unauth_response()

        # Require the CSRF token to be present if we are performing a change action (add, delete or modify objects)
        # but exclude the SAML endpoints from the CSRF check
        if request.method in ('POST', 'PUT', 'DELETE',):
            if session['csrf_token'] != request.headers.get('X-Csrf-Token'):
                logger.info('CSRF Token is missing or incorrect, sending user to login page')
                abort(403)


def after_request(response):
    """Modifies the response object prior to sending it to the client. Used to add CORS headers to the request

    Args:
        response (response): Flask response object

    Returns:
        `None`
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')

    return response


def create_app():
    app = ProbatorFlask(__name__)

    # Setup before/after request handlers
    app.before_request(before_request)
    app.after_request(after_request)

    Compress(app)

    return app
