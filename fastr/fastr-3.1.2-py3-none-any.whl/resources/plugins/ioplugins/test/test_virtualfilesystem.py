import os
import random
import shutil
import string
import tempfile

import fastr


class TestVFS:

    def setup(self):
        self.vfs_plugin = fastr.plugin_manager['VirtualFileSystem']

        fastr.log.info('Setup')
        """ Setup the test environment for the vfs tests. """
        # We assume there is a tmp mount. (It should be tested).
        # Generate a file in the tmp mount.
        self.dir = os.path.join(fastr.config.mounts['tmp'], '_test')
        if os.path.exists(self.dir):
            fastr.log.warning('Cleaning up existing temporary test directory {}'.format(self.dir))
            shutil.rmtree(self.dir)
        os.makedirs(self.dir)
        fastr.log.info('Using temporary directory {}'.format(self.dir))
        if not os.path.isdir(self.dir):
            fastr.log.critical('Temporary directory not available!')

        self.source_dir = os.path.join(self.dir, 'source')
        os.mkdir(self.source_dir)
        self.destination_dir = os.path.join(self.dir, 'destination')
        os.mkdir(self.destination_dir)

        self.handle, self.absfilename = tempfile.mkstemp(dir=self.source_dir)
        self.filename = os.path.basename(self.absfilename)
        self.niigz_handle, self.niigz_absfilename = tempfile.mkstemp(dir=self.source_dir, suffix='.nii.gz')
        self.niigz_filename = os.path.basename(self.niigz_absfilename)

        fastr.log.info('Created {} and {}'.format(self.absfilename, self.niigz_absfilename))
        if not os.path.exists(self.absfilename):
            fastr.log.critical('Source file {} does not exist!'.format(self.absfilename))
        if not os.path.exists(self.niigz_absfilename):
            fastr.log.critical('Source file {} does not exist!'.format(self.niigz_absfilename))

    def random_unique_string(self, length=8, existing=None):
        """ Return a random alpha-numeric string with a certain length. """
        s = ''.join([random.choice(string.ascii_letters + string.digits) for ch in range(length)])
        if existing is not None and s in existing:
            s = self.random_unique_string(length, existing)
        return s

    def test_ioplugins_pull_source_data_no_extension(self):
        output_file = os.path.join(self.destination_dir, self.filename)
        self.vfs_plugin.pull_source_data('vfs://tmp/_test/source/{}'.format(self.filename),
                                   self.destination_dir,
                                   'id_0',
                                   datatype=fastr.types['NiftiImageFile'])
        assert os.path.isfile(output_file)
        if os.path.isfile(output_file):
            os.remove(output_file)

    def test_ioplugins_pull_source_data_niigz(self):
        self.vfs_plugin.pull_source_data('vfs://tmp/_test/source/{}'.format(self.filename),
                                   self.destination_dir,
                                   'id_nii_0',
                                   datatype=fastr.types['NiftiImageFileCompressed'])
        output_file = os.path.join(self.destination_dir, self.filename)
        assert os.path.isfile(output_file)
        if os.path.isfile(output_file):
            os.remove(output_file)

    def test_ioplugins_pull_source_data_mhd(self):
        absfilename_mhd = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.mhd')
        absfilename_raw = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.raw')
        filename_mhd = os.path.basename(absfilename_mhd)
        filename_raw = os.path.basename(absfilename_raw)

        destination_path = self.destination_dir
        destination_path_mhd = os.path.join(self.destination_dir, filename_mhd)
        destination_path_raw = os.path.join(self.destination_dir, filename_raw)

        if os.path.exists(destination_path_mhd):
            os.remove(destination_path_mhd)
        if os.path.exists(destination_path_raw):
            os.remove(destination_path_raw)

        self.vfs_plugin.pull_source_data(self.vfs_plugin.path_to_url(absfilename_mhd),
                                         destination_path,
                                        'id_mhd_0',
                                        datatype=fastr.types['ITKImageFile'])

        assert os.path.isfile(destination_path_mhd)
        assert os.path.isfile(destination_path_raw)

    def test_ioplugins_push_sink_data_niigz(self):
        random_filename = self.random_unique_string()
        output_file = os.path.join(self.destination_dir, random_filename) + '.nii.gz'
        output_url = self.vfs_plugin.path_to_url(output_file)
        self.vfs_plugin.push_sink_data(self.niigz_absfilename, output_url)
        assert os.path.isfile(output_file)

        if os.path.isfile(output_file):
            os.remove(output_file)

    def test_ioplugins_push_sink_data_mhd(self):
        absfilename_mhd = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.mhd')
        absfilename_raw = os.path.join(fastr.config.mounts['example_data'], 'images', 'mrwhite.raw')
        filename_mhd = os.path.basename(absfilename_mhd)
        filename_raw = os.path.basename(absfilename_raw)

        push_target = os.path.join(self.destination_dir, 'sink')
        os.mkdir(push_target)
        destination_path_mhd = os.path.join(push_target, filename_mhd)
        destination_path_raw = os.path.join(push_target, filename_raw)
        destination_url_mhd = self.vfs_plugin.path_to_url(destination_path_mhd)

        if os.path.exists(destination_path_mhd):
            os.remove(destination_path_mhd)
        if os.path.exists(destination_path_raw):
            os.remove(destination_path_raw)

        self.vfs_plugin.push_sink_data(absfilename_mhd, destination_url_mhd)
        assert os.path.isfile(destination_path_mhd)
        assert os.path.isfile(destination_path_raw)
