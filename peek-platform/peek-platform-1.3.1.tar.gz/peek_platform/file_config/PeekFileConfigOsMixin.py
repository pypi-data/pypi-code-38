from abc import ABCMeta


from jsoncfg.value_mappers import require_string, require_integer
from peek_platform.WindowsPatch import isWindows


class PeekFileConfigOsMixin(metaclass=ABCMeta):

    _bashDefault = "C:\\Program Files\\Git\\bin\\bash.exe" if isWindows else "/bin/bash"

    ### SERVER SECTION ###
    @property
    def bashLocation(self):
        """ Bash Location

        :return: The location of the bash interpreter

        :windows: "C:\Program Files\Git\bin\bash.exe"
        :Linux: /bin/bash

        """
        with self._cfg as c:
            return c.os.bashLocation(self._bashDefault, require_string)


