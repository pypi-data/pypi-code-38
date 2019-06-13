from bout_install.Installer import Installer


class InstallerUsingCMake(Installer):
    """
    An Installer class which installs configures using `cmake` rather than 
    `./configure`
    """

    @staticmethod
    def get_cmake_command(cmake_options=None):
        """
        Get the command to cmake the package

        Notes
        -----
        The `..` at the end of cmake is automatically appended

        Parameters
        ----------
        cmake_options : dict
            Configuration options to use with `cmake`.
            The configuration options will be converted to `--key=val` during
            runtime

        Returns
        -------
        cmake_str : str
            The configuration command
        """

        options = ''
        if cmake_options is not None:
            for key, val in cmake_options.items():
                options += f' -{key}={val}'

        cmake_str = f'cmake{options} ..'
        return cmake_str

    def run_cmake(self,
                  build_dir,
                  makefile_path,
                  extra_cmake_option,
                  overwrite_on_exist):
        """
        Configures the package by running CMake

        Parameters
        ----------
        build_dir : Path
            Directory to make the build
        makefile_path : Path
            Path to the Makefile
        extra_cmake_option:
            Configure option to include.
            -DCMAKE_INSTALL_PREFIX=self.local_dir is already added as an option
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        if not makefile_path.is_file() or overwrite_on_exist:
            # Get the CMake options
            cmake_options = dict(DCMAKE_INSTALL_PREFIX=str(self.local_dir))
            if extra_cmake_option is not None:
                cmake_options = {**cmake_options, **extra_cmake_option}

            cmake_str = self.get_cmake_command(cmake_options=cmake_options)

            # NOTE: We could get in trouble if the build_dir already exists,
            #       so we deliberately throw an error if the directory exists
            build_dir.mkdir(exist_ok=False)

            self.logger.info(f'Running cmake with: {cmake_str}')
            self.run_subprocess(cmake_str, build_dir)
        else:
            self.logger.info(f'{makefile_path} found, skipping running of '
                             f'CMake')

    def install_package(self,
                        url,
                        file_from_make,
                        path_config_log='',
                        overwrite_on_exist=False,
                        extra_cmake_option=None):
        """
        Installs a package if it's not installed

        Parameters
        ----------
        url : str
            Url to the tar file of the package
        file_from_make : Path or str
            File originating from the make processes (used to check if the
            package has been made)
        path_config_log : str or Path
            Only used in parent class
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        extra_cmake_option : dict
            Configure option to include.
            The installation prefix of self.local_dir is already added as an
            option
        """

        # Download the tar file
        tar_file_path = self.get_tar_file_path(url)
        self.run_download_tar(url, tar_file_path, overwrite_on_exist)

        # Untar
        tar_dir = self.get_tar_dir(tar_file_path)
        self.run_untar(tar_file_path, tar_dir, overwrite_on_exist)

        # Configure and make
        build_dir = tar_dir.joinpath('build')
        makefile_path = build_dir.joinpath('Makefile')
        self.run_cmake(build_dir,
                       makefile_path,
                       extra_cmake_option,
                       overwrite_on_exist)
        self.run_make(build_dir, file_from_make, overwrite_on_exist)
