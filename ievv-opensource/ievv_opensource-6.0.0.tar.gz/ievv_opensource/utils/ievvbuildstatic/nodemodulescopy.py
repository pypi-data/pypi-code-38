import os
import shutil

from ievv_opensource.utils.ievvbuildstatic import pluginbase


class Plugin(pluginbase.Plugin):
    # Copy specified files from staticsources/<packagename>/node_modules/foo/bar/<libfile>.js to static/<packagename>/<version>/node_modules/<libfile>.js

    def __init__(self,
                 sourcefiles,
                 destinationfolder=os.path.join('scripts', 'node_modules'),
                 sourcefolder='node_modules',
                 **kwargs):
        super(Plugin, self).__init__(**kwargs)
        self.sourcefiles = sourcefiles
        self.destinationfolder = destinationfolder
        self.sourcefolder = sourcefolder

    def get_sourcefolder_path(self):
        return self.app.get_source_path(self.sourcefolder)

    def get_destinationfolder_path(self):
        return self.app.get_destination_path(self.destinationfolder)

    def get_filepaths(self):
        files = []
        sourcefolder = self.get_sourcefolder_path()
        for file in self.sourcefiles:
            files.append(os.path.join(sourcefolder, file))
        # no idea why regexfilelist wont work..
        # regex_file_list = RegexFileList(include_patterns=files)
        # file_list = regex_file_list.get_files_as_list(sourcefolder, absolute_paths=True)
        # print(file_list)
        return files

    def run(self):
        filepaths = self.get_filepaths()
        destinationfolder = self.get_destinationfolder_path()
        if os.path.exists(destinationfolder):
            self.get_logger().debug('Removing {}'.format(destinationfolder))
            shutil.rmtree(destinationfolder)

        os.makedirs(destinationfolder)

        for sourcepath in filepaths:
            if os.path.exists(sourcepath) and os.path.isfile(sourcepath):
                filename = os.path.basename(sourcepath)
                destinationpath = os.path.join(destinationfolder, filename)
                shutil.copyfile(sourcepath, destinationpath)


    def __str__(self):
        return '{}({})'.format(super(Plugin, self).__str__(), self.sourcefolder)
