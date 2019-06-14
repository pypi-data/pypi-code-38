import requests
import json
import base64

from django.conf import settings

from ppmutils.ppm import PPM

import logging
logger = logging.getLogger(__name__)


class Fileservice(PPM.Service):

    # Set the service name
    service = 'Fileservice'

    @classmethod
    def default_url_for_env(cls, environment):
        """
        Give implementing classes an opportunity to list a default set of URLs based on the DBMI_ENV,
        if specified. Otherwise, return nothing
        :param environment: The DBMI_ENV string
        :return: A URL, if any
        """
        if 'local' in environment:
            return 'http://dbmi-fileservice:8012'
        elif 'dev' in environment:
            return 'https://fileservice.aws.dbmi-dev.hms.harvard.edu'
        elif 'prod' in environment:
            return 'https://files.dbmi.hms.harvard.edu'
        else:
            logger.error(f'Could not return a default URL for environment: {environment}')

        return None

    @classmethod
    def check_groups(cls, admins=None):

        # Get current groups.
        groups = cls.get(path='/filemaster/groups/')
        if groups is None:
            logger.error('Getting groups failed')
            return False

        # Check for the required group.
        for group in groups:
            if cls.group_name('uploaders') == group['name']:
                return True

        # Get admins
        if not admins and hasattr(settings, 'FILESERVICE_GROUP_ADMINS'):
            admins = settings.FILESERVICE_GROUP_ADMINS

        # Group was not found, create it.
        data = {
            'name': settings.FILESERVICE_GROUP,
        }

        # Add admins
        if admins:
            data['users'] = [{'email': email} for email in admins],
        else:
            logger.warning('No group admins passed or specified, '
                           'group "{}" has no users!'.format(settings.FILESERVICE_GROUP))

        # Make the request.
        response = cls.post(path='/filemaster/groups/', data=data)
        if response is None:
            logger.error('Failed to create groups: {}'.format(response.content))
            return False

        # Get the upload group ID.
        upload_group_id = [group['id'] for group in response if group['name'] == cls.group_name('UPLOADERS')][0]

        # Create the request to add the bucket to the upload group.
        bucket_data = {
            'buckets': [
                {'name': settings.FILESERVICE_AWS_BUCKET}
            ]
        }

        # Make the request.
        response = cls.put(path='/filemaster/groups/{}/'.format(upload_group_id), data=bucket_data)

        return response

    @classmethod
    def create_file_record(cls, filename=None, metadata=None, tags=None):

        # Build the request.
        data = {
            'permissions': [
                settings.FILESERVICE_GROUP
            ],
            'metadata': metadata,
            'filename': filename,
            'tags': tags,
        }

        # Add passed data
        if filename:
            data['filename'] = filename

        if metadata:
            data['metadata'] = metadata

        if tags:
            data['tags'] = tags

        # Make the request.
        file = cls.post(path='/filemaster/api/file/', data=data)

        return file

    @classmethod
    def create_file(cls, filename=None, metadata=None, tags=None, conditions=None):
        """
        Create a file and generate the presigned S3 POST for sending the file to S3. Allows for specification
        of additional parameters for the upload.
        :param filename: The filename of the file
        :param metadata: A dictionary of metadata
        :param tags: A list of tags
        :param conditions: A list of S3 conditions to pass along when creating the signature for the post
        :return:
        """

        # Ensure groups exist.
        if not cls.check_groups():
            logger.error('Groups do not exist or failed to create')
            return None

        # Build the request.
        data = {
            'permissions': [
                settings.FILESERVICE_GROUP
            ],
            'metadata': metadata,
            'filename': filename,
            'tags': tags,
        }

        # Add passed data
        if filename:
            data['filename'] = filename

        if metadata:
            data['metadata'] = metadata

        if tags:
            data['tags'] = tags

        # Make the request.
        file = cls.post(path='/filemaster/api/file/', data=data)

        # Get the UUID.
        uuid = file['uuid']

        # Form the request for the file link
        params = {
            'cloud': 'aws',
            'bucket': settings.FILESERVICE_AWS_BUCKET,
            'expires': 100
        }

        # Add conditions if passed
        if conditions:
            params['conditions'] = base64.b64encode(json.dumps(conditions).encode()).decode()

        # Make the request for an s3 presigned post.
        response = cls.get(path='/filemaster/api/file/{}/post/'.format(uuid), data=params)

        return uuid, response

    @classmethod
    def get_files(cls, uuids=None):

        # Build the request.
        if uuids:
            params = {
                'uuids': uuids.split(',')
            }
        else:
            params = {}

        # Make the request.
        response = cls.get(path='/filemaster/api/file/', data=params, raw=True)

        # No files will return a 403, handle this gracefully
        if response.status_code == 403:
            logger.debug('Fileservice returned 403, assuming empty file list: {}'.format(response.content))
            return []
        elif response.ok:
            return response.json()
        else:
            return None

    @classmethod
    def get_file(cls, uuid):

        # Build the request.
        params = {
            'uuids': uuid
        }

        # Make the request.
        response = cls.get(path='/filemaster/api/file/', data=params)

        return response

    @classmethod
    def update_file(cls, uuid, file):

        # Make the request.
        response = cls.patch(path=f'/filemaster/api/file/{uuid}/', data=file, raw=True)

        # Check response
        if response.ok:
            return response.json()
        else:
            return None

    @classmethod
    def copy_file(cls, uuid, bucket):
        """
        Copy the requested file to the new bucket
        :param uuid: The file's Fileservice UUID
        :param bucket: The destination S3 bucket
        :return: The result of the operation
        """
        # Build path
        path = f'/filemaster/api/file/{uuid}/copy/?to={bucket}'

        # Make the request.
        response = cls.post(path=path, raw=True)

        # Check response
        if response.ok:
            return response.json()
        else:
            return None

    @classmethod
    def move_file(cls, uuid, bucket):
        """
        Move the requested file to the new bucket
        :param uuid: The file's Fileservice UUID
        :param bucket: The destination S3 bucket
        :return: The result of the operation
        """
        # Build path
        path = f'/filemaster/api/file/{uuid}/move/?to={bucket}'

        # Make the request.
        response = cls.post(path=path, raw=True)

        # Check response
        if response.ok:
            return response.json()
        else:
            return None

    @classmethod
    def delete_file(cls, uuid, location=None):
        """
        Delete the requested file from the passed location
        :param uuid: The file's Fileservice UUID
        :param location: The file's location to delete (if in multiple locations)
        :return: The result of the operation
        """
        # Build the path
        if location:
            path = f'/filemaster/api/file/{uuid}/?location={location}'
        else:
            path = f'/filemaster/api/file/{uuid}/'

        # Make the request.
        response = cls.delete(path=path, raw=True)

        # Check response
        if response.ok:
            return response.json()
        else:
            return None

    @classmethod
    def uploaded_file(cls, uuid, location_id):

        # Build the request.
        params = {
            'location': location_id
        }

        # Make the request.
        response = cls.get(path='/filemaster/api/file/{}/uploadcomplete/'.format(uuid), data=params, raw=True)

        return response.ok

    @classmethod
    def download_url(cls, uuid):

        # Prepare the request.
        response = cls.get(path='/filemaster/api/file/{}/download/'.format(uuid))

        return response['url']

    @classmethod
    def download_file(cls, uuid):

        # Get the URL
        url = cls.download_url(uuid)

        # Request the file from S3 and get its contents.
        response = requests.get(url)

        # Add the content to the FHIR resource as a data element and remove the URL element.
        return response.content

    @classmethod
    def proxy_download_url(cls, uuid):

        # Prepare the request.
        response = cls.get(path='/filemaster/api/file/{}/proxy/'.format(uuid))

        return response['url']

    @classmethod
    def proxy_download_file(cls, uuid):

        # Request the file from S3 and get its contents.
        response = cls.get(path='/filemaster/api/file/{}/proxy/'.format(uuid))

        # Add the content to the FHIR resource as a data element and remove the URL element.
        return response.content

    @classmethod
    def download_archive(cls, uuids):

        # Request the file from S3 and get its contents.
        response = cls.get(path='/filemaster/api/file/archive/', data={'uuids': ','.join(uuids)})

        # Add the content to the FHIR resource as a data element and remove the URL element.
        return response.content


    @classmethod
    def group_name(cls, permission):

        # Check settings
        if hasattr(settings, 'FILESERVICE_GROUP'):
            return '{}__{}'.format(settings.FILESERVICE_GROUP, permission.upper())

        raise ValueError('FILESERVICE_GROUP not defined in settings')

    @classmethod
    def file_url(cls, uuid):
        return cls._build_url('/filemaster/api/file/{}/download/'.format(uuid))

    @classmethod
    def file_md5(cls, uuid):

        # Request the file from S3 and get its contents.
        response = cls.get(path='/filemaster/api/file/{}/filehash/'.format(uuid))

        # Add the content to the FHIR resource as a data element and remove the URL element.
        return response.content

