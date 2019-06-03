from abc import ABC

from django.core.management.base import BaseCommand

import yaml
from populator import BASE_DIR


class Manager(ABC):
    builder = None
    model = None
    attribute = None
    files_path = None

    def __init__(self, stdout, stderr):
        self.cmd = BaseCommand(stdout=stdout, stderr=stderr)
        super().__init__()

    def get_object(self, value):
        attr_value = value
        if isinstance(value, dict):
            attr_value = value.get(self.attribute)
        try:
            return self.model.objects.get(
                **self.build_expression(attr_value))
        except self.model.DoesNotExist:
            data = self.load_file(attr_value)
            if isinstance(data, dict):
                self.cmd.stdout.write('Parsing {0} {1}...'.format(
                    self.model.__name__, attr_value))
                try:
                    object = self.model.objects.get(
                        **self.build_expression(attr_value))
                    self.output_warn(object, 'already exists!')
                    return object
                except self.model.DoesNotExist:
                    if isinstance(value, dict):
                        data.update(value)
                    object = self.builder(data).create_object()
                    self.output_success(object, 'created!')
                    return object
            else:
                return data

    def build_expression(self, attr_value):
        if self.attribute == 'uuid':
            return {'{}'.format(self.attribute): attr_value.replace('_', '-')}
        return {'{}__iexact'.format(self.attribute): attr_value}

    def load_file(self, value):
        path = '{base_dir}{file_path}'.format(
            base_dir=BASE_DIR, file_path=self.files_path)
        file_obj = open('{}{}.yml'.format(path, self.normalize(value)))
        data = yaml.load(file_obj, Loader=yaml.Loader)
        file_obj.close()
        return data

    def normalize(self, value):
        return value.lower().replace('-', '_').replace(' ', '_')

    def delete_all(self):
        self.model.objects.all().delete()

    def output_success(self, object, msg):
        self.cmd.stdout.write(
            self.cmd.style.SUCCESS(
                self.model.__name__ + ' ' + getattr(
                    object, self.attribute).__str__() + ' ' + msg))

    def output_warn(self, object, msg):
        self.cmd.stdout.write(
            self.cmd.style.WARNING(
                self.model.__name__ + ' ' + getattr(
                    object, self.attribute) + ' ' + msg))
