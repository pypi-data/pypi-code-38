import datetime
import os
import tarfile

from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import boundHandler, setResponseHeader
from girder.constants import AccessType, AssetstoreType, TokenScope
from girder.exceptions import AccessException, RestException
from girder.models.assetstore import Assetstore
from girder.models.file import File
from girder.models.folder import Folder
from girder.models.item import Item
from girder.utility.assetstore_utilities import getAssetstoreAdapter, setAssetstoreAdapter
from girder.utility.filesystem_assetstore_adapter import FilesystemAssetstoreAdapter, BUF_SIZE
from girder.utility.progress import ProgressContext
from girder.plugin import getPlugin, GirderPlugin

EPOCH = datetime.datetime(1970, 1, 1)


class TapeArchivePlugin(GirderPlugin):
    DISPLAY_NAME = 'Tape Archive'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        # TODO allow a file to be stored in multiple tape archive assetstores
        setAssetstoreAdapter(AssetstoreType.FILESYSTEM, TarSupportAdapter)

        info['apiRoot'].assetstore.route('POST', (':id', 'tar_export'), _exportTar)
        info['apiRoot'].assetstore.route('POST', (':id', 'tar_import'), _importTar)

class TarSupportAdapter(FilesystemAssetstoreAdapter):
    def downloadFile(self, file, offset=0, headers=True, endByte=None, contentDisposition=None,
                     **kwargs):
        if file.get('pathInTarfile'):
            return self._downloadFromTar(file, offset, endByte, headers, contentDisposition)

        return super(TarSupportAdapter, self).downloadFile(
            file, offset, headers, endByte, contentDisposition, **kwargs)

    def _downloadFromTar(self, file, offset, endByte, headers, contentDisposition):
        if endByte is None or endByte > file['size']:
            endByte = file['size']

        if headers:
            setResponseHeader('Accept-Ranges', 'bytes')
            self.setContentHeaders(file, offset, endByte, contentDisposition)

        def stream():
            # Support tarPath as either absolute or relative to assetstore root
            if os.path.isabs(file['tarPath']):
                path = file['tarPath']
            else:
                path = os.path.join(self.assetstore['root'], file['tarPath'])
            with tarfile.open(path, 'r') as tar:
                fh = tar.extractfile(file['pathInTarfile'])
                bytesRead = offset

                if offset > 0:
                    fh.seek(offset)

                while True:
                    readLen = min(BUF_SIZE, endByte - bytesRead)
                    if readLen <= 0:
                        break

                    data = fh.read(readLen)
                    bytesRead += readLen

                    if not data:
                        break
                    yield data
                fh.close()

        return stream

    def _exportTar(self, path, folder, progress, user, compression):
        if os.path.isabs(path):
            raise RestException('Tar path must be relative, not absolute (%s).' % path)

        abspath = os.path.join(self.assetstore['root'], path)

        if os.path.exists(abspath):
            raise RestException('File already exists at %s.' % path)

        if progress:
            progress.update(total=-1, message='Computing size...')
            progress.update(total=Folder().getSizeRecursive(folder), current=0)

        with tarfile.open(abspath, 'w:' + compression) as tar:
            for name, file in Folder().fileList(folder, user=user, data=False):
                if not file.get('imported') or not file.get('tarPath'):
                    progress.update(message=name)
                    ti = tarfile.TarInfo(name)
                    ti.size = file['size']
                    ti.mtime = int((file.get('updated', file['created']) - EPOCH).total_seconds())
                    with File().open(file) as fh:
                        tar.addfile(ti, fh)

                    if file['assetstoreId'] != self.assetstore['_id']:
                        file['preArchiveAssetstoreId'] = file['assetstoreId']
                        file['assetstoreId'] = self.assetstore['_id']
                    file['imported'] = True
                    file['tarPath'] = path  # Store as relative so assetstore can be moved
                    file['pathInTarfile'] = name
                    File().save(file)

                progress.update(increment=file['size'])

        # TODO re-iterate over file list and delete any files that still have path & tarPath
        # TODO split up tar files into nearly fixed-size chunks?

    def _importTar(self, path, folder, progress, user):
        if not os.path.isabs(path):
            path = os.path.join(self.assetstore['root'], path)

        folderCache = {}

        def _resolveFolder(name):
            if name in {'.', ''}:  # This file is at the top level
                return folder
            if name not in folderCache:
                tokens = name.split('/')
                sub = folder
                for token in tokens:
                    if token == '.':
                        continue
                    sub = Folder().createFolder(sub, token, creator=user, reuseExisting=True)
                folderCache[name] = sub

            return folderCache[name]

        with tarfile.open(path, 'r') as tar:
            for entry in tar:
                if entry.isreg():
                    dir, name = os.path.split(entry.name)
                    progress.update(message=entry.name)
                    parent = _resolveFolder(dir)
                    if not Folder().hasAccess(parent, user, AccessType.WRITE):
                        raise AccessException('Write access denied for folder: %s' % folder['_id'])
                    item = Item().createItem(
                        name=name, creator=user, folder=parent, reuseExisting=True)
                    file = File().createFile(
                        name=name, creator=user, item=item, reuseExisting=True,
                        assetstore=self.assetstore, size=entry.size, saveFile=False)
                    file['path'] = ''
                    file['tarPath'] = path
                    file['imported'] = True
                    file['pathInTarfile'] = entry.name
                    File().save(file)


@boundHandler
@access.admin(scope=TokenScope.DATA_WRITE)
@autoDescribeRoute(
    Description('Archive the contents of a Girder folder.')
    .notes('This will move and (optionally compress) files from their assetstore location '
           'to within a tape archive (tar) file. They can still be served from that file as '
           'usual, but there will be a latency associated with reading from the archive format. '
           '\n\nFiles under this folder that are already archived will be skipped and not '
           'added to the new archive.')
    .modelParam('id', model=Assetstore)
    .modelParam('folderId', 'The folder to archive.', model=Folder, level=AccessType.WRITE,
                paramType='formData')
    .param('path', 'Path where the tar file will be written, relative to assetstore root.')
    .param('compression', 'Compression method', required=False, default='gz',
           enum=('gz', 'bz2', ''))
    .param('progress', 'Whether to record progress on the import.',
           dataType='boolean', default=False, required=False)
    .errorResponse()
    .errorResponse('You are not an administrator.', 403))
def _exportTar(self, assetstore, folder, path, compression, progress):
    user = self.getCurrentUser()
    adapter = getAssetstoreAdapter(assetstore)

    with ProgressContext(progress, user=user, title='Archiving %s' % folder['name']) as ctx:
        adapter._exportTar(path, folder, ctx, user, compression)


@boundHandler
@access.admin(scope=TokenScope.DATA_WRITE)
@autoDescribeRoute(
    Description('Import a tape archive (tar) file into the system.')
    .notes('This does not move or copy the existing data, it just creates '
           'references to it in the Girder data hierarchy. Deleting '
           'those references will not delete the underlying data.')
    .modelParam('id', model=Assetstore)
    .modelParam('folderId', 'Import destination folder.', model=Folder, level=AccessType.WRITE,
                paramType='formData')
    .param('path', 'Path of the tar file to import.')
    .param('progress', 'Whether to record progress on the import.',
           dataType='boolean', default=False, required=False)
    .errorResponse()
    .errorResponse('You are not an administrator.', 403))
def _importTar(self, assetstore, folder, path, progress):
    user = self.getCurrentUser()
    adapter = getAssetstoreAdapter(assetstore)

    with ProgressContext(progress, user=user, title='Importing data') as ctx:
        adapter._importTar(path, folder, ctx, user)
