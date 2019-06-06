import json
import errno
import shutil

from restiro.generators import BaseGenerator
from os.path import join, dirname


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

class SPAGenerator(BaseGenerator):

    def generate_index(self):
        this_dir = dirname(__file__)
        assets_dir = join(this_dir, 'dist')
        copy(assets_dir, self.destination_dir)

        f = self._ensure_file('docs.js')
        f.write(
            'window.restiro_docs = %s' % json.dumps(self.docs_root.to_dict())
        )
        f.close()

    def generate_documents(self):
        pass

    def generate_resources(self):
        pass

    def write_resource(self, file_stream, resource):  # pragma: nocover
        pass

    def write_document(self, file_stream, document):  # pragma: nocover
        pass

    def write_index(self, file_stream):
        pass
