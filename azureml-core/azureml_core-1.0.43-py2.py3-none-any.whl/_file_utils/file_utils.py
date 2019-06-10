# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import logging
import time

from requests import Session
from requests.exceptions import RequestException
from urllib3.exceptions import HTTPError

from azureml.exceptions import AzureMLException

module_logger = logging.getLogger(__name__)


def normalize_path_and_join(path, name):
    """
    Normalizes user provided paths by expanding the user paths such as ~ or ~user,
    converting it into an absolute path and joins the path with the provided file or directory name.
    :param path: Path to normalize.
    :type path: str
    :param name: Name of the file(with extension) or directory name.
    :type name: str
    :return: A normalized absolute path, including the file name or directory name.
    :rtype: str
    """
    # Expand the user path if the path starts with '~' or '~user'.
    normalized_path = normalize_path(path)
    if os.path.basename(normalized_path) != name:
        normalized_path = os.path.join(normalized_path, name)
    return normalized_path


def normalize_path(path):
    """
    Normalizes user provided paths by expanding the user paths such as ~ or ~user
    and converting it into an absolute path.
    :param path: Path to normalize.
    :type path: str
    :return: A normalized, absolute path.
    :rtype: str
    """
    return os.path.abspath(os.path.expanduser(path))


def directory_exists(path, directory_name):
    """
    Normalizes the path and checks if the directory exists.
    :param path: Path to check for the directory.
    :type path: str
    :param directory_name: Name of the directory to check.
    :type directory_name: str
    :return: True or False based on whether the directory exists.
    :rtype: bool
    """
    normalized_path = normalize_path_and_join(path, directory_name)
    return os.path.isdir(normalized_path)


def check_and_create_dir(path, directory_name=None):
    """
    Normalizes the provided path and creates the directory if it doesn't exist.
    :param path: Path to create the directory in.
    :type path: str
    :param directory_name: Name of the directory to create.
    :type directory_name: str
    """
    if directory_name is None:
        # directory_name hasn't been provided, so use the basename of the provided
        # path as the directory name.
        directory_name = os.path.basename(path)

    if not directory_exists(path, directory_name):
        # Directory doesn't exist, so create the directory
        normalized_path = normalize_path_and_join(path, directory_name)
        os.mkdir(normalized_path)


def makedirs_for_file_path(file_path):
    """
    :param file_path: relative or absolute path to a file
    """
    parent_path = os.path.join(file_path, os.path.pardir)
    parent_path = os.path.normpath(parent_path)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path, exist_ok=True)
    return True


def get_root_path():
    """
    Gets the root directory for the drive.
    NOTE: On Windows, it returns 'C:\' or the path to the root dir for the drive.
          On Linux, it returns '/'.
    :return: Path to the root directory for the drive.
    :rtype: str
    """
    return os.path.realpath(os.sep)


def traverse_up_path_and_find_file(path, file_name, directory_name=None, num_levels=None):
    """
    Traverses up the provided path until we find the file, reach a directory
    that the user does not have permissions to, or if we reach num_levels (if set by the user).
    NOTE: num_levels=2 would mean that we search the current directory and two levels above (inclusive).
    :param path: Path to traverse up from.
    :type path: str
    :param file_name: The name of the file to look for, including the file extension.
    :type file_name: str
    :param directory_name: (optional)The name of the directory that the file should be in. ie) /aml_config/config.json
    :type directory_name: str
    :param num_levels: Number of levels to traverse up the path for (inclusive).
    :type num_levels: int
    :return: Path to the file that we found, or an empty string if we couldn't find the file.
    :rtype: str
    """
    current_path = normalize_path(path)
    if directory_name is not None:
        file_name = os.path.join(directory_name, file_name)

    current_level = 0
    root_path = get_root_path()
    while True:
        path_to_check = os.path.join(current_path, file_name)
        if os.path.isfile(path_to_check):
            return path_to_check

        if current_path == root_path or (num_levels is not None and num_levels == current_level):
            break
        current_path = os.path.realpath(os.path.join(current_path, os.path.pardir))
        current_level = current_level + 1

    return ''


def normalize_file_ext(file_name, extension):
    """
    Normalizes the file extension by appending the provided extension to the file_name.
    If file_name contains the file extension, we make sure that it matches the extension provided (case-sensitive).

    :param file_name: The name of the file to normalize (may or may not contain the file extension).
    :type file_name: str
    :param extension: File extension to use for the file, with or without the leading period (i.e. '.json' or 'json').
    :type extension: str
    :return: File name and the extension for the file.
    :rtype: str
    """
    extension = extension if extension[0] == '.' else '.' + extension
    root, ext = os.path.splitext(file_name)
    if not ext:
        # Case when file_name doesn't contain the file extension and ext is an empty string.
        return file_name + extension
    return root + extension


def download_file(source_uri, path=None, max_retries=3, stream=True, protocol="https", session=None):
    """
    Downloads the file from source_uri. Saves the content to the path if set.
    Returns the response of the get request"
    :param source_uri: The name of the file to normalize (may or may not contain the file extension).
    :type source_uri: str
    :param path: if set the content of the file will be written to path
    :type path: str
    :param max_retries:
    :type max_retries: int
    :param stream: Whether to incrementally download the file
    :type stream: bool
    :param protocol: The http protocol for the get request, defaults to https
    :type protocol: str
    :return: The response for the get request to source_uri
    :rtype: requests.Response
    """
    module_logger.debug("downloading file to {path}, with max_retries: {max_retries}, "
                        "stream: {stream}, and protocol: {protocol}".format(path=path,
                                                                            max_retries=max_retries,
                                                                            stream=stream,
                                                                            protocol=protocol))
    is_new_session = session is None
    session = Session() if is_new_session else session
    wait_time = 2
    retries = 0
    while retries < max_retries:
        try:
            response = session.get(source_uri, stream=stream)
            if response.status_code != 200:
                response.raise_for_status()

            if path is not None:
                makedirs_for_file_path(path)
                with open(path, 'wb') as write_to_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            write_to_file.write(chunk)
            else:
                module_logger.debug("Output file path is {}, the file was not downloaded.".format(path))
            return response
        except (RequestException, HTTPError) as request_exception:
            retries += 1
            if retries < max_retries:
                module_logger.debug('RequestException or HTTPError raised in download_file with message: {}'
                                    .format(request_exception))
                time.sleep(wait_time)
                wait_time = wait_time ** 2
                continue
            else:
                module_logger.debug('Failed to download file with error: {}'.format(request_exception))
                raise AzureMLException('Download of file failed with error: {}'.format(request_exception))
        finally:
            if is_new_session:
                session.close()


def download_file_stream(source_uri, encoding="utf-8", download_to_bytes=False, **kwargs):
    """
    Downloads the file from source_uri. Saves the content to the path if set.
    Returns the response of the get request"
    :param source_uri: The name of the file to normalize (may or may not contain the file extension).
    :type source_uri: str
    :param encoding: encoding of the http body
    :type encoding: str
    :param max_retries:
    :type max_retries: str
    :param stream: Whether to incrementally download the file
    :type stream: bool
    :param protocol: The http protocol for the get request, defaults to https
    :type protocol: str
    :return: The response for the get request to source_uri
    :rtype: requests.Response
    """
    response = download_file(source_uri, **kwargs)
    bytes_str = bytes()
    if response.status_code != 200:
        response.raise_for_status()
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            bytes_str += chunk
    return bytes_str if download_to_bytes else bytes_str.decode(encoding)


def get_directory_size(path, size_limit=None, include_function=None, exclude_function=None):
    """
    Get the size of the directory. If size_limit is specified, stop after reaching this value.

    :type path: str
    :type include_function: Callable
    :type exclude_function: Callable

    :rtype: int
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            full_path = os.path.normpath(os.path.join(dirpath, name))

            if ((not exclude_function and not include_function) or
               (exclude_function and not exclude_function(full_path)) or
               (include_function and include_function(full_path))):
                    total_size += os.path.getsize(full_path)
                    if size_limit and total_size > size_limit:
                        return total_size

    return total_size


def get_path_size(file_or_folder_path, size_limit, exclude_function=None):
    """
    Calculate the size of the file or folder
    :param file_or_folder_path:
    :type file_or_folder_path: str
    :rtype: int the size of the file or folder
    """
    if os.path.isfile(file_or_folder_path):
        size = os.path.getsize(file_or_folder_path)
    else:
        size = get_directory_size(
            file_or_folder_path, size_limit=size_limit, exclude_function=exclude_function)
    return size
