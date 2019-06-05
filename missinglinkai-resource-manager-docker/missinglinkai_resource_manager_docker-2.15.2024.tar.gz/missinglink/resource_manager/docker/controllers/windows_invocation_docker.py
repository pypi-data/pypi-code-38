# -*- coding: utf-8 -*-

import uuid

from .invocation_docker import InvocationDocker


class WindowsInvocationDocker(InvocationDocker):

    GIT_CLONE_DESTINATION = "C:/temp_code"
    COMMANDS_VOLUME = 'ml_commands'

    def _get_pull_code_command(self):
        # can't git clone directly to a mounted volume
        # see https://www.bountysource.com/issues/40368769-git-clone-does-not-work-in-windows-docker-container-in-mounted-host-volume-folder

        git_command = super(WindowsInvocationDocker, self)._get_pull_code_command()
        # This hack was the only way I got it to work - for some reason the git clone gets "C:temp_code" if we send c:\\temp_code
        copy_source = self.GIT_CLONE_DESTINATION.replace("/", "\\")
        return f'"{git_command} ; XCOPY /s /h /e {copy_source} c:\\code"'

    async def _do_pull_image(self, _, image, __):
        return await self.docker_wrapper.async_pull(image)

    def _get_b64_decoding_command(self, command_func, command_id=None):
        self._setup_commands_volume()

        command_data = command_func(**self.command_parts)
        command_id = command_id or uuid.uuid4()
        command_file_path = self._get_command_file_path(command_id)
        self._write_command_data(command_file_path, command_data)
        command_template = self._get_b64_decoding_command_template()
        return command_template.format(command_file_path)

    def _setup_commands_volume(self):
        if self.commands_volume is None:
            volume = self.get_or_create_volume(self.COMMANDS_VOLUME)
            self.commands_volume = self._bind_volume(volume.id, self.COMMANDS_VOLUME)
            self.persistent_paths[self.COMMANDS_VOLUME] = self.commands_volume[1]

    @staticmethod
    def _write_command_data(command_file_path, data):
        with open(command_file_path, 'w') as f:
            f.write(data)

    def _get_command_file_path(self, command_id):
        return "c:\\{}\\{}".format(self.COMMANDS_VOLUME, command_id)

    @staticmethod
    def _get_b64_decoding_command_template():
        return 'cmd /c "md c:\\ml_temp && CertUtil -decode {} c:\\ml_temp\\cmd.bat && c:\\ml_temp\\cmd.bat"'

    def _get_setup_root_mounts(self):
        mounts = super(WindowsInvocationDocker, self)._get_setup_root_mounts()
        mounts[self.COMMANDS_VOLUME] = self.volumes[self.COMMANDS_VOLUME]
        return mounts
