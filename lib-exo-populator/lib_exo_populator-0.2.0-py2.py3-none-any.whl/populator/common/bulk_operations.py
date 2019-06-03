import importlib
import os
import glob
import stringcase
from uuid import UUID

from django.conf import settings


class BulkOperations:
    def __init__(self, entity, cmd):
        self.entity = entity
        self.model = '{0}Manager'.format(
            stringcase.titlecase(entity).replace(" ", ""))
        self.root_path = settings.BASE_DIR
        self.cmd = cmd

    def populate(self):
        allowed = settings.POPULATE_ALLOWED_POPULATE_ENTITIES
        if self.entity in allowed:
            result = []
            for item in self.get_item_list():
                module = importlib.import_module(
                    'populator.{0}.{0}_manager'.format(self.entity))
                class_ = getattr(module, self.model)
                result.append(class_(stdout=self.cmd.stdout, stderr=self.cmd.stderr).get_object(item).id)
        else:
            result = 'Skipped'
        return result

    def is_uuid(self, uuid_string):
        try:
            UUID(uuid_string, version=4)
        except ValueError:
            return False
        return True

    def get_item_list(self):
        list = []
        folder = '{0}/populator/{1}/files/'.format(self.root_path, self.entity)
        files = glob.glob(folder + '**/*.yml', recursive=True)
        for file in files:
            filename, _ = os.path.splitext(os.path.basename(file))
            if self.is_uuid(filename.replace('_', '-')):
                list.append(filename)
            else:
                list.append(stringcase.titlecase(filename))
        return list
