import os
import fs.path
import fs.osfs
from .util import sanitize_string_to_filename
from .importers import Uploader, ContainerResolver

class FSWrapper(Uploader, ContainerResolver):
    verb = 'Copying'

    def __init__(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)

        self.dst_fs = fs.osfs.OSFS(path)

    def upload(self, container, name, fileobj, metadata=None):
        # Save to disk
        path = fs.path.join(container.id, name)
        if hasattr(fileobj, 'read'):
            self.dst_fs.writefile(path, fileobj)
        else:
            self.dst_fs.writebytes(path, fileobj)

    def file_exists(self, container, name):
        path = fs.path.join(container.id, name)
        return self.dst_fs.exists(path)

    def path_el(self, container):
        if container.container_type == 'group':
            return sanitize_string_to_filename(container.id)
        return sanitize_string_to_filename(container.label)

    def resolve_path(self, container_type, path):
        # Resolve folder
        if self.dst_fs.exists(path):
            return path, None
        return None, None

    def create_container(self, parent, container):
        # Create folder, if it doesn't exist
        if parent:
            parent_path = parent.id
            path = fs.path.join(parent_path, sanitize_string_to_filename(container.label))
        else:
            path = sanitize_string_to_filename(container.id) # Group id

        if not self.dst_fs.exists(path):
            self.dst_fs.makedir(path)

        return path

    def check_unique_uids(self, request):
        raise NotImplementedError('Unique UID check is not supported for output-folder')
