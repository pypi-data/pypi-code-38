from abc import ABCMeta, abstractmethod

class Interface(object):
    """Abstract class for filessytem objects"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, config=None, creds=None, **kwargs):
        """
        :param self: self reference
        :param config: Config Object with the required storage config for the type
        :param creds Creds: Creds object per the type
        """

    @abstractmethod
    def open(self, uuid, path_hint, mode, **kwargs):
        """
        Open a file like object

        :param self: self reference
        :param uid: internal id of file reference
        :param path_hint: local relative path for file location
        :param mode: Mode to open file
        :param kwargs: Options list to pass to underlying storage layer
        :type uid: string
        :type path_hint: string
        :type mode: string
        :type kwargs: dict
        :raises ResourceNotFound: If the file could not be found
        :returns: An object implemeting a file like interface
        :rtype: File

        """
    @abstractmethod
    def remove_file(self, uuid, path_hint):
        """
        Removes file from storage

        :param self: self reference
        :param uuid: internal id of file reference
        :param path_hint: local relative path for file location
        :type uuid: string
        :type path_hint: string
        :raises ResourceNotFound: If the file could not be found
        :returns: Boolean indicating success
        :rtype: boolean
        """

    @abstractmethod
    def is_signed_url(self):
        """
        Return boolean if signed url is possible for this file type

        :param self: self reference
        :returns boolean:
        """

    @abstractmethod
    def get_signed_url(self, uuid, path_hint, purpose, filename, attachment=True, response_type=None):
        """
        Returns the signed url location of the file reference

        :param self: self reference
        :param string uuid: internal file uuid reference
        :param string path_hint: internal reference to file object on storage, used when uuid is not available
        :param string purpose: stated reason for signed url: upload or download
        :param string filename: Name of the downloaded file, used in the content-disposition header
        :param boolean attachment: True/False, attachment or not
        :param string response_type: Content-Type header of the response
        :raises ResourceNotFound: If the file could not be found
        :return: string, the signed url string for accessing the referenced file
        :rtype: string

        """

    @abstractmethod
    def can_redirect_request(self, headers):
        """
        Tests whether or not the given request could be redirected to a signed url.

        :param dict headers: The request headers
        :return: Whether or not the request can be redirected to a signed url.
        :rtype: boolean
        """

    @abstractmethod
    def get_file_hash(self, uuid, path_hint):
        """
        Returns the calculated hash for the current contents of the referenced file

        :param self: self reference
        :param string uuid: internal file uuid reference
        :param string path_hint: internal reference to the file object on storage, used when uuid is not available
        :raises ResourceNotFound: If the file could not be found
        :returns: The hash value of the curreent file contents
        :rtype: string
        """

    @abstractmethod
    def get_file_info(self, uuid, path_hint):
        """
        Returns basic file info about the referenced file object, None if the file does not exist

        :param self: self reference
        :param string uuid: internal fild uuid reference
        :param path_hint string: internal reference to the file object on stroage, used when uuid is not available
        :returns: Dict of file information with the following data attributes
            {
                'filesize': int,
            }
        :rtype: Dict | None
        """

    def initialize_storage(self, cors_allowed_origins, reconfigure=False):
        """
        Initializes the storage location, for example configuring CORS.

        Default behavior is to do nothing.

        :param self: self reference
        :param cors_allowed_origins list(str): The list of origins allowed for CORS
        :param reconfigure bool: Whether or not to force reconfiguration
        """
