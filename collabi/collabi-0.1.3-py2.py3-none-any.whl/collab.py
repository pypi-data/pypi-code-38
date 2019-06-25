"""Provides functional access to the UnityCloud Collaboration service.
"""
import os
import errno
import hashlib
import httplib
import dateutil.parser

from logging import getLogger
from urllib import urlencode
from requests import HTTPError
from datetime import datetime
from send2trash import send2trash
from tqdm import tqdm

from collabi.lazy_file import LazyFile
from collabi.open_struct import OpenStruct
from collabi.rest import Rest

# TODO: desperately need to report progress when uploading/downloading many files

class Collab(object):
    CHUNK_BYTES = 32768

    class Revision(OpenStruct):
        def __init__(self, obj):
            super(Revision, self).__init__(obj)
            if hasattr(self, 'committed_date'):
                self.committed_date = dateutil.parser.parse(self.committed_date)
            else:
                self.committed_date = datetime.utcfromtimestamp(0)

    class FileEntry(OpenStruct):
        pass

    class DirectoryEntry(OpenStruct):
        pass

    class LocalEntry(object):
        def __init__(self, path, expected_md5=None):
            self._logger = getLogger('unity.collab.local_entry')
            self._md5 = None
            self.expected_md5 = expected_md5
            self.path = path
            self.transfer_seconds = 0
            self.transfer_bytes = 0

        def exists(self):
            return os.path.exists(self.path)

        def open(self, *args):
            return open(self.path, *args)

        def size(self):
            return os.path.getsize(self.path)

        def mtime(self):
            return os.path.getmtime(self.path)

        def md5(self):
            if not self._md5:
                hash_md5 = hashlib.md5()
                with self.open('rb') as f:
                    for chunk in iter(lambda: f.read(Collab.CHUNK_BYTES), b''):
                        hash_md5.update(chunk)
                self._md5 = hash_md5.hexdigest()
            return self._md5

        def isdiff(self, cloud_entry):
            return (
                (isinstance(cloud_entry, Collab.FileEntry) and
                 not os.path.isfile(self.path)) or
                (isinstance(cloud_entry, Collab.DirectoryEntry) and
                 not os.path.isdir(self.path)) or
                (cloud_entry.size != self.size()) or
                (cloud_entry.hash != self.md5())
            )

        def delete(self, overwrite=False):
            if overwrite:
                os.remove(self.path)
            else:
                self._logger.info('Sending to trash: '+self.path)
                send2trash(self.path)

        def __repr__(self):
            return str({
                'path': self.path,
                'md5': self.md5(),
                'mtime': self.mtime(),
                'size': self.size(),
            })

    class Download(object):
        def __init__(self, path_md5s, recursive=False):
            self._logger = getLogger('unity.collab.download')
            self.pathmap = {}
            self.filemap = {}
            for path, md5 in path_md5s.iteritems():
                fl = Collab.LocalEntry(path, expected_md5=md5)
                self.pathmap[path] = fl

    class Upload(object):
        def __init__(self, paths, recursive=False):
            self._logger = getLogger('unity.collab.upload')
            self.transaction_id = None
            self.md5map = {}
            self.pathmap = {}
            self.filemap = {}
            if recursive:
                progress_paths = tqdm(paths, desc='Collecting upload paths: ', unit=' paths')
            else:
                progress_paths = paths
            for path in progress_paths:
                if isinstance(path, Collab.LocalEntry):
                    fl = path
                else:
                    if os.path.isdir(path):
                        if recursive:
                            paths.extend(os.path.join(path, e) for e in os.listdir(path))
                        else:
                            self._logger.warning('Skipping directory (recursive not enabled): ' +
                                                 path)
                        continue
                    fl = Collab.LocalEntry(path)
                self.md5map[fl.md5()] = fl # doesn't matter which one if multiple (same md5)
                self.pathmap[path] = fl

    ########################################

    def __init__(self, config, rest, project_id, branch_id, revision_id):
        self._logger = getLogger('unity.collab')
        self._config = config
        self._rest = rest
        self._branch_id = branch_id
        self._project_id = project_id
        self._project_path = 'projects/'+self._project_id+'/'
        self._branches_path = self._project_path+'branches/'
        self._branch_path = self._branches_path+branch_id
        self._revisions_path = self._branch_path+'/revisions/'
        self._revisions_etag = None
        self.set_revision_id(revision_id)

    def set_revision_id(self, revision_id):
        self._revision_id = revision_id
        self._revision_path = self._revisions_path+revision_id+'/'

    def list(self, paths, recursive=False):
        options = '?recurse' if recursive else ''
        entries = []
        for path in paths:
            if path[0] != '/': path = '/'+path
            rpath = self._revision_path+'entries'+path+options
            resp = self._rest.request('get', rpath)
            json = resp.json()
            if 'name' in json:
                dirpath = path.replace(json['name'],'',1)
                self._process(dirpath, json, entries)
        return entries

    def branches(self):
        resp = self._rest.request('get', self._branches_path)
        return resp.json()['branches']

    def create_branch(self, attrs):
        resp = self._rest.request('post', self._branches_path, json=attrs)
        return resp.json()

    def update_branch(self, attrs):
        resp = self._rest.request('put', self._branch_path, json=attrs)
        return resp.json()

    def has_new_revisions(self):
        hdrs = {}
        if self._revisions_etag:
            hdrs['If-None-Match'] = self._revisions_etag
        rpath = self._revisions_path+'?limit=1'
        resp = self._rest.request('get', rpath, headers=hdrs)
        self._revisions_etag = resp.headers.get('ETag')
        return resp.status_code != httplib.NOT_MODIFIED and len(resp.json()['revisions']) > 0

    def revisions(self, **kwargs):
        if 'limit' in kwargs and kwargs['limit'] == None:
            del(kwargs['limit'])
        if 'start_revision' not in kwargs:
            kwargs['start_revision'] = self._revision_id
        rpath = self._revisions_path+'?'+urlencode(kwargs)
        resp = self._rest.request('get', rpath)
        self._revisions_etag = resp.headers.get('ETag')
        return resp.json()['revisions']

    def diff(self, **kwargs):
        rpath = self._revision_path+'diff'
        if len(kwargs) > 0:
            rpath += '?'+urlencode(kwargs)
        resp = self._rest.request('get', rpath)
        if resp.status_code == httplib.OK and int(resp.headers.get('Content-Length', 0)) > 0:
            return resp.json()['diff']
        return []

    def history(self, paths, limit=None):
        if paths == ['/']:
            return {'/': self.revisions(limit=limit)}
        bpath = self._revision_path+'/history'
        history = {}
        for path in paths:
            sep = '' if path[0] == '/' else '/'
            hpath = bpath+sep+path
            uri = hpath+'?limit='+limit if limit else hpath
            resp = self._rest.request('get', uri)
            history[path] = resp.json()['history']
        return history

    def download(self, paths_or_entries, dst, recursive=False, overwrite=False, concurrency=4):
        path_md5s = self._get_path_md5s(paths_or_entries, recursive)
        if len(path_md5s) > 1:
            self._logger.info('Starting to download '+str(len(path_md5s))+' files')

        download = Collab.Download(path_md5s, recursive=recursive)

        for fl in download.pathmap.values():
            if fl.path[0] != '/': path = '/'+fl.path
            if fl.expected_md5:
                rpath = self._project_path+'cache/source/'+fl.expected_md5
            else:
                rpath = self._revision_path+'download'+fl.path
            areq = self._rest.async_request('get', rpath)
            req_id = areq.kwargs['headers'][Rest.REQ_ID_HDR]
            del(areq.kwargs['headers']['Content-Type']) # otherwise will fail when downloading from gcp
            download.filemap[req_id] = fl

        resps = self._rest.async_request_flush(concurrency)

        dst = os.path.normpath(dst)
        for resp in resps:
            resp.raise_for_status()
            req = resp.request
            req_id = req.headers[Rest.REQ_ID_HDR]
            fl = download.filemap[req_id]
            fldst = os.path.abspath(self._local_path_join(dst, fl.path))
            self._save_file(resp, fldst, overwrite)
            fl.transfer_seconds = resp.elapsed.total_seconds()
            fl.transfer_bytes = int(resp.headers.get('Content-Length', 0))

        return download

    # FIXME: split this up into the two stages: prepare_upload() and upload()
    #        (makes for better testing and ability for alternate callers of the api eg. latency)
    def upload(self, paths, upload=None, upload_transaction_id=None,
               recursive=False, concurrency=4):
        if not upload:
            upload = Collab.Upload(paths, recursive=recursive)
            upload.transaction_id = upload_transaction_id

        resp = self._try_reusing_upload(upload)
        if not resp:
            rpath = self._project_path+'uploads'
            resp = self._rest.request('post', rpath, json={'files': upload.md5map.keys()})

        json = resp.json()
        upload.transaction_id = json['transaction_id']
        self._logger.info('Using upload transaction: '+upload.transaction_id)
        self._config.save(upload_transaction_id=upload.transaction_id)
        urls = json['signed_urls']
        if len(urls) > 1:
            self._logger.info('Starting to upload '+str(len(urls))+' files')

        for md5, url in urls.iteritems():
            fl = upload.md5map[md5]
            if fl.size() < 1:
                areq = self._rest.async_request_raw('put', url, data=b'')
            else:
                areq = self._rest.async_request_raw('put', url, data=LazyFile(fl.path, 'rb'))
            req_id = areq.kwargs['headers'][Rest.REQ_ID_HDR]
            del(areq.kwargs['headers']['Content-Type'])  # otherwise will fail when uploading to gcp
            upload.filemap[req_id] = fl

        resps = self._rest.async_request_flush(concurrency)
        for resp in resps:
            resp.close()
            resp.raise_for_status()
            req = resp.request
            if req.body: req.body.close()
            req_id = req.headers[Rest.REQ_ID_HDR]
            fl = upload.filemap[req_id]
            fl.transfer_seconds = resp.elapsed.total_seconds()
            fl.transfer_bytes = int(req.headers.get('Content-Length', 0))
            server = resp.headers.get('Server', '')
            if server == 'AmazonS3' or server == 'UploadServer':
                etag = resp.headers['ETag']
                etag = etag.replace('"', '').strip()
                if fl.md5() != etag:
                    raise ValueError(fl.path + ' md5 mismatch: expected='+fl.md5()+ ' got='+etag)
            else:
                self._logger.warning('Not validating ETag for response from '+server)

        self._config.save(delete=['upload_transaction_id'])
        return upload

    def commit(self, message, upload=None, moves=[], deletes=[], strip_components=0):
        hr = 'NOT_IMPLEMENTED' if self._revision_id == 'HEAD' else self._revision_id
        aou = []
        action_info = {
            'action': 'commit',
            'transaction_id': (upload.transaction_id if upload else None),
            'data': {
                'head_revision': hr,
                'comment': message,
                'add_or_update': aou,
                'move': moves,
                'delete': deletes
            }
        }
        if upload:
            for fl in upload.pathmap.values():
                aou.append({
                    'path': self._collab_path(fl.path, strip_components),
                    'hash': fl.md5(),
                    'revision': self._revision_id
                })
        resp = self._rest.request('post', self._revisions_path, json={'action_info': action_info})
        return resp.json()

    def upload_sync(self, local_root, message, strip_components=0, concurrency=4):
        local_root = os.path.normpath(local_root)
        cloud_root = self._collab_path(local_root, strip_components)

        cloud_entries = self._get_cloud_entries(cloud_root)
        local_entries = self._get_local_entries(local_root)

        upload_entries = []
        for local_entry in local_entries.values():
            cloud_path = self._collab_path(local_entry.path, strip_components)
            cloud_entry = cloud_entries.pop(cloud_path, None)
            if not cloud_entry or local_entry.isdiff(cloud_entry):
                upload_entries.append(local_entry)

        if len(upload_entries) > 0:
            upload = self.upload(upload_entries, concurrency=concurrency)
        else:
            upload = None

        deletes = []
        for cloud_entry in cloud_entries.values():
            self._logger.info('Deleting: '+cloud_entry.name)
            deletes.append({'path': cloud_entry.name, 'revision': self._revision_id})

        if upload or len(deletes) > 0:
            return self.commit(message, upload, deletes=deletes, strip_components=strip_components)

        return None

    def download_sync(self, local_root, strip_components=0, overwrite=False, concurrency=4):
        local_root = os.path.normpath(local_root)
        cloud_root = self._collab_path(local_root, strip_components)

        cloud_entries = self._get_cloud_entries(cloud_root)
        local_entries = self._get_local_entries(local_root)

        download_entries = []
        for cloud_entry in cloud_entries.values():
            local_path = self._local_path_join(local_root, cloud_entry.name)
            local_entry = local_entries.pop(local_path, None)
            if not local_entry or local_entry.isdiff(cloud_entry):
                download_entries.append(cloud_entry)

        for local_entry in local_entries.values():
            local_entry.delete(overwrite)

        if len(download_entries) > 0:
            return self.download(download_entries, local_root,
                                 overwrite=overwrite, concurrency=concurrency)

        return None

    ######################################################################
    # private

    def _process(self, path, json, entries):
        if not path.endswith('/'): path += '/'
        if 'recursive' in json:
            del(json['recursive'])
            if 'entries' in json :
                dirpath = path + json['name']
                for entry_json in json['entries']:
                    self._process(dirpath, entry_json, entries)
                return
            else:
                entry = Collab.DirectoryEntry(json)
        else:
            entry = Collab.FileEntry(json)
        entry.name = path + entry.name
        entries.append(entry)

    def _try_reusing_upload(self, upload):
        if not upload.transaction_id:
            return None
        try:
            rpath = self._project_path+'uploads/'+upload.transaction_id
            resp = self._rest.request('put', rpath, json={'files': upload.md5map.keys()})
            self._logger.info('Reusing previous transaction: '+upload.transaction_id)
            return resp
        except HTTPError as exc:
            prev_id = upload.transaction_id
            upload.transaction_id = None
            if exc.response.status_code == httplib.NOT_FOUND:
                self._logger.info('Previous transaction is no longer valid: '+prev_id)
                return None
            raise

    def _get_path_md5s(self, paths_or_entries, recursive):
        if isinstance(paths_or_entries[0], str):
            entries = self.list(paths_or_entries, recursive)
        else:
            entries = paths_or_entries
        path_md5s = {}
        for entry in entries:
            if isinstance(entry, Collab.FileEntry):
                path_md5s[entry.name] = entry.hash
        return path_md5s

    def _save_file(self, resp, dst, overwrite):
        if dst.startswith("/dev/null/"):
            self._logger.info('Discarding '+dst);
            for chunk in resp.iter_content(Collab.CHUNK_BYTES):
                pass
            return
        self._logger.info('Saving '+dst);
        self._mkpath_parent(dst)
        if (not overwrite and os.path.exists(dst)): send2trash(dst)
        with open(dst, 'wb') as fd:
            for chunk in resp.iter_content(Collab.CHUNK_BYTES):
                fd.write(chunk)

    def _get_cloud_entries(self, path):
        try:
            raw_entries = self.list([path], recursive=True)
        except HTTPError as ex:
            if ex.response.status_code == httplib.NOT_FOUND:
                raw_entries = []
            else:
                raise
        entries = {}
        for entry in raw_entries:
            if not isinstance(entry, Collab.FileEntry): continue
            entries[entry.name] = entry
        return entries

    @staticmethod
    def _get_local_entries(path):
        entries = {}
        for root, dirnames, filenames in os.walk(path):
            for fn in filenames:
                entry = Collab.LocalEntry(os.path.join(root, fn))
                entries[entry.path] = entry
        return entries

    @staticmethod
    def _local_path_join(local_path, collab_path):
        return Collab._overlap_join(local_path, os.sep.join(collab_path.split('/')))

    @staticmethod
    def _collab_path(local_path, strip_components=0):
        components = local_path.split(os.sep)
        return '/'+'/'.join(components[strip_components:])

    @staticmethod
    def _overlap_join(head_path, tail_path):
        if head_path[-1] == os.sep:
            head_path = head_path[:-1]
        if tail_path[0] == os.sep:
            tail_path = tail_path[1:]
        head_comps = head_path.split(os.sep)
        tail_comps = tail_path.split(os.sep)
        for comp in reversed(head_comps):
            if len(tail_comps) < 1 or comp != tail_comps[0]:
                break
            del(tail_comps[0])
        return os.sep.join(head_comps + tail_comps)

    @staticmethod
    def _mkpath_parent(path):
        Collab._mkpath(os.path.dirname(path))

    @staticmethod
    def _mkpath(path):
        try:
            os.makedirs(path)
        except OSError as ex:  # Python >2.5
            if ex.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
