"""Abstract base class for handling device firmware update."""
#   Copyright 2019 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from abc import ABC, abstractmethod


class FirmwareHandler(ABC):
    """Handle firmware installation and abort commands, and report version.

    Once an object of this class is passed to a Wolk object,
    it will set callback methods `on_install_success` and
    `on_install_fail` used for reporting the result of
    the firmware update process. Use these callbacks in `install_firmware`
    and `abort_installation` methods.

    :ivar on_install_fail: Installation failure callback method
    :vartype on_install_fail: Callable[[str, FirmwareUpdateStatus], None]
    :ivar on_install_success: Installation successful callback method
    :vartype on_install_success: Callable[[str], None]
    """

    on_install_success = None
    on_install_fail = None

    @abstractmethod
    def install_firmware(
        self, device_key: str, firmware_file_path: str
    ) -> None:
        """
        Handle the installation of the firmware file.

        Call ``self.on_install_success(device_key)`` to report success.
        Reporting success will also get new firmware version.

        If installation fails, call ``self.on_install_fail(device_key, status)``
        where:

        .. code-block:: python

                status = FirmwareUpdateStatus(
                    FirmwareUpdateState.ERROR,
                    FirmwareUpdateErrorCode.INSTALLATION_FAILED
                )

        or use other values from ``FirmwareUpdateErrorCode`` if they fit better.

        :param device_key: Device for which the firmware command is intended
        :type device_key: str
        :param firmware_file_path: Path where the firmware file is located
        :type firmware_file_path: str
        """
        pass

    @abstractmethod
    def abort_installation(self, device_key: str) -> None:
        """
        Attempt to abort the firmware installation process for device.

        Call ``self.on_install_fail(device_key, status)`` to report if
        the installation process was able to be aborted with
        ``status = FirmwareUpdateStatus(FirmwareUpdateState.ABORTED)``.
        If unable to stop the installation process, no action is required.

        :param device_key: Device for which to abort installation
        :type device_key: str
        """
        pass

    @abstractmethod
    def get_firmware_version(self, device_key: str) -> str:
        """
        Return device's current firmware version.

        :param device_key: Device identifier
        :type device_key: str
        :returns: version
        :rtype: str
        """
        pass
