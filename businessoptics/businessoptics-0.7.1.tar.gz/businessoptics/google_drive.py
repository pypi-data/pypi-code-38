import argparse
import json
import logging
import os
from warnings import catch_warnings, filterwarnings

import boto3
import httplib2
from apiclient import discovery
from googleapiclient.http import MediaFileUpload
from littleutils import file_to_json
from oauth2client import tools
from oauth2client._helpers import _MISSING_FILE_MESSAGE
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

log = logging.getLogger(__name__)


def google_drive_service():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.google-credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'credentials.json')
    scope_out_of_date = (os.path.exists(credential_path) and
                         file_to_json(credential_path)['scopes'] ==
                         ['https://www.googleapis.com/auth/drive.readonly'])
    if scope_out_of_date:
        os.remove(credential_path)
        log.info('Previously saved credentials have been deleted as the scope has changed, '
                 'you will need to authorise once more')
    client_secret_path = os.path.join(credential_dir, 'client_secret.json')
    store = Storage(credential_path)
    with catch_warnings():
        filterwarnings('ignore', _MISSING_FILE_MESSAGE.format(credential_path))
        credentials = store.get()
    if not credentials or credentials.invalid:
        if not os.path.exists(client_secret_path):
            log.info('Client secret not found at %s. Downloading...', client_secret_path)
            try:
                boto3.client('s3').download_file('businessoptics-alex',
                                                 'cs.json',
                                                 client_secret_path)
            except Exception:
                log.error('Error downloading the client secret. Request it from Alex.')
                raise
        flow = flow_from_clientsecrets(
            client_secret_path, 'https://www.googleapis.com/auth/drive')
        flow.user_agent = 'businessoptics client'
        flags = argparse.ArgumentParser(parents=[tools.argparser]
                                        ).parse_args(['--noauth_local_webserver'])
        credentials = tools.run_flow(flow, store, flags)
        log.info('Storing credentials to ' + credential_path)
    http = credentials.authorize(httplib2.Http())
    autodetect_logger = logging.getLogger('googleapiclient.discovery_cache')
    old_level = autodetect_logger.level
    autodetect_logger.setLevel(logging.ERROR)
    try:
        return discovery.build('drive', 'v3', http=http)
    finally:
        autodetect_logger.level = old_level


def upload_to_google_drive(path, name=None, zipit=False):
    """
    Upload a local file to Google Drive under the folder 'BusinessOptics shared > Python Client Uploads'.

    :param path: path to the local file.
    :param name: name for the file on Google Drive. If left blank, the filename portion of `path`
                   will be used. Must be unique within the folder.
    :param zipit: if True, will upload a .zip containing the file.
    """
    folder_name = 'BusinessOptics shared > Python Client Uploads'
    folder_id = '1pdtVD2cEyaedGFpvBNHU-Wl25xzpYiWp'

    if zipit:
        path = zip_file(path)

    name = name or os.path.split(path)[1]

    if zipit and not name.endswith('.zip'):
        name += '.zip'

    service = google_drive_service()
    query = 'name = %r and %r in parents and not trashed' % (name, folder_id)
    existing_files = service.files().list(
        q=query, fields='files(mimeType, id, name, parents)').execute()['files']
    if existing_files:
        raise ValueError("A file '%s > %s' already exists: %s" % (
            folder_name, existing_files[0]['name'], json.dumps(existing_files[0], indent=4)))

    media = MediaFileUpload(path, resumable=True)
    request = service.files().create(media_body=media, body={'name': name, 'parents': [folder_id]})
    log.info("Uploading %s to 'Google Drive > %s > %s'", os.path.abspath(path), folder_name, name)
    _process_file_with_progress('Upload', request)


def _process_file_with_progress(label, request):
    done = False
    progress = 0
    while not done:
        status, done = request.next_chunk()
        if status:
            new_progress = int(status.progress() * 100)
            if new_progress > progress:
                progress = new_progress
                log.info('%sed %d%%', label, progress)
    log.info(label + ' complete!')


def zip_file(path):
    from zipfile import ZipFile, ZIP_DEFLATED

    zip_path = path + '.zip'
    assert os.path.isfile(path)
    assert not os.path.exists(zip_path), zip_path + " exists already"
    with ZipFile(zip_path, mode='w', compression=ZIP_DEFLATED) as z:
        z.write(path, arcname=os.path.split(path)[1])

    return zip_path
