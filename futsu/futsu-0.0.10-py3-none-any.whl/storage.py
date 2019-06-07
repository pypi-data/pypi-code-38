import lazy_import
fgcpstorage = lazy_import.lazy_module('futsu.gcp.storage')
gcstorage = lazy_import.lazy_module('google.cloud.storage')
ffs = lazy_import.lazy_module('futsu.fs')

def local_to_path(dst, src):
    if fgcpstorage.is_blob_path(dst):
        gcs_client = gcstorage.client.Client()
        fgcpstorage.file_to_blob(dst, src, gcs_client)
        return
    ffs.cp(dst,src)

def path_to_local(dst, src):
    if fgcpstorage.is_blob_path(src):
        gcs_client = gcstorage.client.Client()
        fgcpstorage.blob_to_file(dst, src, gcs_client)
        return
    ffs.cp(dst,src)
