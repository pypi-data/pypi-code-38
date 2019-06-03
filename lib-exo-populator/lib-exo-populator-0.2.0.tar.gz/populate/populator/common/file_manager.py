import os
import shutil

from django.core.management.base import BaseCommand
from django.conf import settings


class FileManager:

    def __init__(self, stdout, stderr):
        self.target_path = '{}/populator'.format(settings.BASE_DIR)
        self.regression_path = '{0}/populator/data/'.format(settings.BASE_DIR)
        self.cmd = BaseCommand(stdout=stdout, stderr=stderr)

    def clear_files(self):
        for f in settings.POPULATE_ALLOWED_DATA_FOLDERS:
            f = '{0}/{1}/files'.format(self.target_path, f)
            self.delete(f)

    def delete(self, src):
        for file in os.listdir(src):
            src_file = os.path.join(src, file)
            if self.is_yml(src_file):
                self.cmd.stdout.write(
                    self.cmd.style.ERROR('Removed file: {0}'.format(src_file)))
                os.unlink(src_file)
            elif self.is_dir(src_file):
                self.delete(src_file)
                os.rmdir(src_file)

    def prepare_regression_files(self):
        for folder in os.listdir(self.regression_path):
            src_path = '{0}/{1}'.format(self.regression_path, folder)
            dst_path = '{0}/{1}/files'.format(self.target_path, folder)
            self.copytree(src_path, dst_path)

    def copytree(self, src, dst):
        for file in os.listdir(src):
            src_file = os.path.join(src, file)
            dst_file = os.path.join(dst, file)
            if self.is_yml(src_file):
                shutil.copy2(src_file, dst_file)
                self.cmd.stdout.write(
                    self.cmd.style.SUCCESS('{0}'.format(dst_file)))
            elif self.is_dir(src_file):
                os.makedirs(dst_file)
                self.copytree(src_file, dst_file)

    def is_yml(self, file):
        _, extension = os.path.splitext(file)
        return extension == '.yml'

    def is_dir(self, file):
        return os.path.isdir(file)
