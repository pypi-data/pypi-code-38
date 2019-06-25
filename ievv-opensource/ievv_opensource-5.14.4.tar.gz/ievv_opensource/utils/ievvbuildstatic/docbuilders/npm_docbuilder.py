import os

import shutil
from ievv_opensource.utils.shellcommandmixin import ShellCommandError

from . import base


class NpmDocBuilder(base.AbstractDocBuilder):
    """
    Doc builder that looks for a npm script named ``build-docs``
    and runs that if it is available.

    Assumes that the ``build-docs`` task outputs its docs in ``built_docs/``
    in the source directory (the same directory as package.json).
    """
    name = 'npmdocbuilder'

    def get_script_keys(self):
        scripts_dict = self.app.get_installer('npm').get_packagejson_dict().get('scripts', {})
        return scripts_dict.keys()

    def is_available(self):
        """
        Is this docbuilder available in the app?
        """
        return 'build-docs' in self.get_script_keys()

    def __run_build_docs_npm_script(self):
        try:
            self.app.get_installer('npm').run_packagejson_script(
                script='build-docs',
                args=['--silent'])
        except ShellCommandError:
            self.get_logger().command_error('documentation build FAILED!')
            raise SystemExit()

    def __get_staticsources_build_directory(self):
        return self.app.get_source_path('built_docs')

    def __verify_docs_built_in_correct_directory(self):
        if not os.path.exists(self.__get_staticsources_build_directory()):
            self.get_logger().error(
                '"npm run build-docs" was executed successfully, '
                'but it did not output the results in {expected_build_directory!r}.'.format(
                    expected_build_directory=self.__get_staticsources_build_directory()
                ))
            self.get_logger().command_error('documentation build FAILED!')
            raise SystemExit()

    def __move_docs_into_output_directory(self, output_directory):
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
        shutil.move(self.__get_staticsources_build_directory(), output_directory)

    def build_docs(self, output_directory):
        self.get_logger().command_start('Building docs for {appname}'.format(
            appname=self.app.appname))
        if os.path.exists(self.__get_staticsources_build_directory()):
            shutil.rmtree(self.__get_staticsources_build_directory())
        self.__run_build_docs_npm_script()
        self.__verify_docs_built_in_correct_directory()
        self.__move_docs_into_output_directory(output_directory=output_directory)
        self.get_logger().command_success('documentation build for {appname} succeeded :)'.format(
            appname=self.app.appname
        ))
