class BaseStorage:  # pragma: no cover

    def __init__(self, bucket_name):
        """ Will create a bucket for file storage, if one already exists it will not be crated twice. """
        raise NotImplementedError()

    def get_files(self):
        """ Returns a list of all files in the bucket """
        raise NotImplementedError()

    def list_files(self):
        """ Prints a list of all the files in the bucket """
        raise NotImplementedError()

    def upload_file(self, file_path_on_disk, file_path_in_bucket):
        """ Uploads given file from the disk to the bucket """
        raise NotImplementedError()

    def download_file(self, file_path_in_bucket, file_path_on_disk):
        """ Downloads given file from the bucket to the disk """
        raise NotImplementedError()

    def delete_file(self, file_path_in_bucket):
        """ Removes a file from the bucket """
        raise NotImplementedError()
