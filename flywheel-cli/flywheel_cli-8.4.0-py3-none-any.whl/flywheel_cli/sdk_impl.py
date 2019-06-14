"""Provides flywheel-sdk implementations of common abstract classes"""
import copy
import flywheel
import json
import logging
import os
import requests
import sys

from .importers import Uploader, ContainerResolver

CONFIG_PATH = '~/.config/flywheel/user.json'
config = None

TICKETED_UPLOAD_PATH = '/{ContainerType}/{ContainerId}/files'

log = logging.getLogger(__name__)

def pluralize(container_type):
    """ Convert container_type to plural name

    Simplistic logic that supports:
    group,  project,  session, subject, acquisition, analysis, collection
    """
    if container_type == 'analysis':
        return 'analyses'
    if not container_type.endswith('s'):
        return container_type + 's'
    return container_type


def load_config():
    global config
    if config is None:
        path = os.path.expanduser(CONFIG_PATH)
        try:
            with open(path, 'r') as f:
                config = json.load(f)
        except:
            pass
    return config


def create_flywheel_client(require=True):
    config = load_config()
    if config is None or config.get('key') is None:
        if require:
            print('Not logged in, please login using `fw login` and your API key', file=sys.stderr)
            sys.exit(1)
        return None
    result = flywheel.Flywheel(config['key'])
    log.debug('SDK Version: %s', flywheel.flywheel.SDK_VERSION)
    log.debug('Flywheel Site URL: %s', result.api_client.configuration.host)
    return result


def save_api_key(api_key):
    """Save the given api key to the user's config file.

    If api_key is None, then remove it from the file.
    """
    config = load_config()
    if config is None:
        config = {}

    if api_key is None:
        config.pop('key', None)
    else:
        config['key'] = api_key

    path = os.path.expanduser(CONFIG_PATH)
    with open(path, 'w') as f:
        json.dump(config, f)


def parse_resolver_path(path):
    """Split out a string path, keeping analyses and files paths"""
    # TODO: Port this to SDK?
    if not path:
        return []

    if path.startswith('fw://'):
        path = path[5:]

    path = (path or '').strip('/')

    if '/files/' in path:
        path, file_path = path.split('/files/')
        file_path = ['files', file_path]
    else:
        file_path = []

    if '/analyses/' in path:
        path, analysis_path = path.split('/analyses/')
        analysis_path = ['analyses', analysis_path]
    else:
        analysis_path = []

    path = path.split('/') or []
    path = path + analysis_path + file_path

    return [path_el for path_el in path if path_el]

def get_login_id(fw):
    """Get a readable login id for the current api key"""
    status = fw.get_auth_status()

    if status.is_device:
        device = fw.get_device(status.origin.id)
        return '{} - {}'.format(device.get('type', 'device'), device.get('name', status.origin.id))

    user = fw.get_current_user()
    return '{} {}'.format(user.firstname, user.lastname)

"""
For now we skip subjects, replacing them (effectively) with the project layer,
and treating them as if they always exist.
"""
class SdkUploadWrapper(Uploader, ContainerResolver):
    def __init__(self, fw):
        self.fw = fw
        self.fw.api_client.set_default_header('X-Accept-Feature', 'Subject-Container')
        self._supports_signed_url = None
        # Session for signed-url uploads
        self._upload_session = requests.Session()

    def supports_signed_url(self):
        if self._supports_signed_url is None:
            config = self.fw.get_config()

            # Support the new and legacy method of feature advertisement, respectively
            # Ref: https://github.com/flywheel-io/core/pull/1503
            features = config.get('features')
            f1 = features.get('signed_url', False) if features else False
            f2 = config.get('signed_url', False)

            self._supports_signed_url = f1 or f2
        return self._supports_signed_url

    def resolve_path(self, container_type, path):
        parts = path.split('/')

        try:
            result = self.fw.resolve(parts)
            container = result.path[-1]
            log.debug('Resolve %s: %s - returned: %s', container_type, path, container.id)
            return container.id, container.get('uid')
        except flywheel.ApiException:
            log.debug('Resolve %s: %s - NOT FOUND', container_type, path)
            return None, None

    def create_container(self, parent, container):
        # Create container
        create_fn = getattr(self.fw, 'add_{}'.format(container.container_type), None)
        if not create_fn:
            raise ValueError('Unsupported container type: {}'.format(container.container_type))
        create_doc = copy.deepcopy(container.context[container.container_type])

        if container.container_type == 'session':
            # Add subject to session
            create_doc['project'] = parent.parent.id
            create_doc['subject'] = copy.deepcopy(container.context['subject'])
            create_doc['subject']['_id'] = parent.id
            # Copy subject label to code
            create_doc['subject'].setdefault('code', create_doc['subject'].get('label', None))
        elif parent:
            create_doc[parent.container_type] = parent.id

        new_id = create_fn(create_doc)
        log.debug('Created container: %s as %s', create_doc, new_id)
        return new_id

    def check_unique_uids(self, request):
        try:
            return self.fw.check_uids_exist(request)
        except flywheel.ApiException as e:
            if e.status == 404:
                raise NotImplementedError('Unique UID check is not supported by the server')
            raise

    def upload(self, container, name, fileobj, metadata=None):
        upload_fn = getattr(self.fw, 'upload_file_to_{}'.format(container.container_type), None)

        if not upload_fn:
            print('Skipping unsupported upload to container: {}'.format(container.container_type))
            return

        log.debug('Uploading file %s to %s=%s', name, container.container_type, container.id)
        if self.supports_signed_url():
            self.signed_url_upload(container, name, fileobj, metadata=metadata)
        else:
            upload_fn(container.id, flywheel.FileSpec(name, fileobj), metadata=json.dumps(metadata))

    def file_exists(self, container, name):
        cont = self.fw.get(container.id)
        if not cont:
            return False
        for file_entry in cont.get('files', []):
            if file_entry['name'] == name:
                return True
        return False

    def signed_url_upload(self, container, name, fileobj, metadata=None):
        """Upload fileobj to container as name, using signed-urls"""
        # Create ticketed upload
        path_params = {
            'ContainerType': pluralize(container.container_type),
            'ContainerId': container.id
        }
        ticket, upload_url = self.create_upload_ticket(path_params, name, metadata=metadata)

        log.debug('Upload url for %s on %s=%s: %s (ticket=%s)', name,
            container.container_type, container.id, ticket, upload_url)

        # Perform the upload
        resp = self._upload_session.put(upload_url, data=fileobj)
        resp.raise_for_status()
        resp.close()

        # Complete the upload
        self.complete_upload_ticket(path_params, ticket)

    def create_upload_ticket(self, path_params, name, metadata=None):
        body = {
            'metadata': metadata or {},
            'filenames': [ name ]
        }

        response = self.call_api(TICKETED_UPLOAD_PATH, 'POST',
            path_params=path_params,
            query_params=[('ticket', '')],
            body=body,
            response_type=object
        )

        return response['ticket'], response['urls'][name]

    def complete_upload_ticket(self, path_params, ticket):
        self.call_api(TICKETED_UPLOAD_PATH, 'POST',
            path_params=path_params,
            query_params=[('ticket', ticket)])

    def call_api(self, resource_path, method, **kwargs):
        kwargs.setdefault('auth_settings', ['ApiKey'])
        kwargs.setdefault('_return_http_data_only', True)
        kwargs.setdefault('_preload_content', True)

        return self.fw.api_client.call_api(resource_path, method, **kwargs)

