# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.

class BaseOutputError(Exception):
    def __init__(self, *args: object, **kwargs: object) -> None:
        if len(args) > 1:
            message = args[0] % tuple(args[1:])
        else:
            message = args[0]
        super().__init__(message, **kwargs)

class ParameterNotFoundError(BaseOutputError):
    '''
    Should be raised when an expected parameter is not found.
    '''
    pass

class RuleNotFound(BaseOutputError):
    '''
    Thrown if an outbound rule can not be located to process an outbound
    message.
    '''
    pass

class ExpectedContextVariableError(BaseOutputError):
    '''
    Thrown if the Rule Context does not contain an expected context variable.
    '''
    pass

class ProtocolNotSupportedError(BaseOutputError):
    '''
    Thrown if the Rule Context does not contain an expected context variable.
    '''
    pass
