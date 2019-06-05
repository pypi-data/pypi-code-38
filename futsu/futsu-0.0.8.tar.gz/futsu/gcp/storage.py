gcstorage = None
try:
    from google.cloud import storage as gcstorage
except ImportError:
    pass
import re

BUCKET_PATH_FORMAT = 'gs://([^/]+)/?'
BUCKET_PATH_FORMAT_RE = None
def init_BUCKET_PATH_FORMAT_RE():
    global BUCKET_PATH_FORMAT_RE
    if BUCKET_PATH_FORMAT_RE is None:
        BUCKET_PATH_FORMAT_RE = re.compile(BUCKET_PATH_FORMAT)

FILE_PATH_FORMAT = 'gs://([^/]+)/(.+)'
FILE_PATH_FORMAT_RE = None
def init_FILE_PATH_FORMAT_RE():
    global FILE_PATH_FORMAT_RE
    if FILE_PATH_FORMAT_RE is None:
        FILE_PATH_FORMAT_RE = re.compile(FILE_PATH_FORMAT)

def is_gs_bucket_path(path):
    init_BUCKET_PATH_FORMAT_RE()
    return BUCKET_PATH_FORMAT_RE.fullmatch(path) is not None

def is_gs_file_path(path):
    init_FILE_PATH_FORMAT_RE()
    return FILE_PATH_FORMAT_RE.fullmatch(path) is not None

def prase_bucket_path(path):
    init_BUCKET_PATH_FORMAT_RE()
    m = BUCKET_PATH_FORMAT_RE.fullmatch(path)
    if not m: raise ValueError()
    return m.group(1)

def prase_file_path(path):
    init_FILE_PATH_FORMAT_RE()
    m = FILE_PATH_FORMAT_RE.fullmatch(path)
    if not m: raise ValueError()
    return m.group(1), m.group(2)

def bucket(gs_path, client):
    bucket_name = prase_bucket_path(gs_path)
    return client.bucket(bucket_name)

def blob(gs_path, client):
    bucket_name, blob_name = prase_file_path(gs_path)
    return client.bucket(bucket_name).blob(blob_name)

def cp_local_to_gcp(src,dst,client):
    blob(dst, client).upload_from_filename(src)

def cp_gcp_to_local(src,dst,client):
    blob(src, client).download_to_filename(dst)

def set_string(dst,s,client):
    blob(dst, client).upload_from_string(s.encode('utf8'))

def get_string(src,client):
    return blob(src, client).download_as_string().decode('utf8')

def exist(path,client):
    return blob(path, client).exists()

def rm(path,client):
    b = blob(path, client)
    if b.exists():
        b.delete()
