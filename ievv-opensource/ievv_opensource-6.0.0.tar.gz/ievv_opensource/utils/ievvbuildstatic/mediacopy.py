import os
import shutil

from ievv_opensource.utils.ievvbuildstatic import filepath
from ievv_opensource.utils.ievvbuildstatic import pluginbase


class Plugin(pluginbase.Plugin):
    """
    Media copy plugin --- copies media files from staticsources into
    the static directory, and supports watching for file changes.

    Examples:

        Copy all files in ``demoapp/staticsources/demoapp/media/`` into
        ``demoapp/static/1.0.0/media/``::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.mediacopy.Plugin(),
                    ]
                )
            )

        Using a different source folder. This will copy
        all files in ``demoapp/staticsources/demoapp/assets/`` into
        ``demoapp/static/1.0.0/assets/``::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.mediacopy.Plugin(sourcefolder="assets"),
                    ]
                )
            )
    """
    name = 'mediacopy'

    def __init__(self, sourcefolder='media', destinationfolder=None, **kwargs):
        """
        Parameters:
            sourcefolder: The folder where media files is located relative to
                the source folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
                You can specify a folder in another app using
                a :class:`ievv_opensource.utils.ievvbuildstatic.filepath.SourcePath` object.
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin`.
        """
        super(Plugin, self).__init__(**kwargs)
        self.sourcefolder = sourcefolder
        if isinstance(sourcefolder, filepath.FilePathInterface) and destinationfolder is None:
            raise ValueError('destinationfolder must be specifed when sourcefolder is not a string.')
        self.destinationfolder = destinationfolder or sourcefolder

    def get_sourcefolder_path(self):
        return self.app.get_source_path(self.sourcefolder)

    def get_destinationfolder_path(self):
        return self.app.get_destination_path(self.destinationfolder)

    def run(self):
        sourcefolder = self.get_sourcefolder_path()
        self.get_logger().command_start('Copying media')
        if not os.path.exists(sourcefolder):
            self.get_logger().warning('Media source folder, {}, does not exist.'.format(
                sourcefolder))
            return

        destinationfolder = self.get_destinationfolder_path()
        if os.path.abspath(destinationfolder) == os.path.abspath(sourcefolder):
            raise ValueError('mediacopy: Sourcefolder {} is the same as destinationfolder {}'.format(
                sourcefolder, destinationfolder))

        if os.path.exists(destinationfolder):
            self.get_logger().debug('Removing {}'.format(destinationfolder))
            shutil.rmtree(destinationfolder)

        self.get_logger().debug('Copying {} -> {}'.format(sourcefolder, destinationfolder))
        shutil.copytree(sourcefolder, destinationfolder)
        self.get_logger().command_success('Copied media successfully :)')

    def get_watch_folders(self):
        """
        We only watch the folder where the less sources are located,
        so this returns the absolute path of the ``sourcefolder``.
        """
        return [self.app.get_source_path(self.sourcefolder)]

    def __str__(self):
        return '{}({})'.format(super(Plugin, self).__str__(), self.sourcefolder)
