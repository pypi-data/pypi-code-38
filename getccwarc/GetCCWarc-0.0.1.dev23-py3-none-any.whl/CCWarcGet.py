import zlib

import boto3
from botocore import UNSIGNED
from botocore.client import Config


def get_warc_file(filename, length, offset, gzip=True):
    # Boto3 anonymous login to common crawl
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    # Count the range
    offset_end = offset + length - 1
    byte_range = 'bytes={offset}-{end}'.format(offset=offset, end=offset_end)
    gzipped_text = s3.get_object(Bucket='commoncrawl', Key=filename, Range=byte_range)['Body'].read()

    if gzip:
        return gzipped_text
    else:
        return zlib.decompress(gzipped_text, 16 + zlib.MAX_WBITS)


if __name__ == '__main__':
    off, len, file = 437157916, 884, \
                               "crawl-data/CC-MAIN-2019-22/segments/1558232256040.41/warc/" \
                               "CC-MAIN-20190520142005-20190520164005-00160.warc.gz"

    text = get_warc_file(file, len, off, gzip=False)
    print(text)

