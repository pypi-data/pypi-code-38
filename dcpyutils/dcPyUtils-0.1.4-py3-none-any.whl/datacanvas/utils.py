from pandas.io import s3
import s3fs

_original_pd_s3_get_filepath_or_buffer = s3.get_filepath_or_buffer


def get_s3_fs(endpoint_url, access_key, secret_key):
    return s3fs.S3FileSystem(anon=False, key=access_key, secret=secret_key, use_ssl=False,
                             client_kwargs={'endpoint_url': endpoint_url, 'aws_secret_access_key': secret_key,
                                            'aws_access_key_id': access_key}
                             )


def mix_pd_s3(endpoint_url, access_key, secret_key):
    def my_get_filepath_or_buffer(filepath_or_buffer, encoding=None, compression=None, mode=None):
        try:
            fs = get_s3_fs(endpoint_url, access_key, secret_key)
            if mode is None:
                mode = 'rb'
            filepath_or_buffer = fs.open(s3._strip_schema(filepath_or_buffer), mode)
            return filepath_or_buffer, None, compression, True
        except Exception:
            return _original_pd_s3_get_filepath_or_buffer(filepath_or_buffer, encoding, compression, mode)

    s3.get_filepath_or_buffer = my_get_filepath_or_buffer
