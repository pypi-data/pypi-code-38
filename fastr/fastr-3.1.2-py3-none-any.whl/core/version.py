# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module containing the class that represent versions
"""

import re
from .. import exceptions


class Version(tuple):
    """
    Class representing a software version definition. Allows for sorting and
    extraction of parts.
    """
    # Regular expression to split a version into 7 fields: major, minor, extras, seperator, status, build, and suffix
    version_matcher = re.compile(r'(\d+)\.(\d+)((?:\.\d+)+)?([_\-\.])?'
                                 r'(a(?=\d)|b(?=\d)|alpha(?=\d)|beta(?=\d)'
                                 r'|rc(?=\d)|r(?=\d))?(\d+)?([a-zA-Z0-9\-_\.]*)')
    date_version_matcher = re.compile(r'(\d+)-(\d+)-(\d+)([_\-\.])?(.*)')

    def __new__(cls, *version):
        """Class containing a version

        Can be constructed by:

        .. code-block:: python

          Version( 'major.$minor.$extra[0].$extra[1]$seperator$status$build$suffix' )
          Version( major, minor, extra, status, build, suffix, seperator )
          Version( (major, minor, extra, status, build, suffix, seperator) )
          Version( [major, minor, extra, status, build, suffix, seperator] )

        :param int major: interger giving major version
        :param int minor: is an integer (required)
        :param extra: is a list of integers
        :type extra: list of int
        :param str status: can be "a", "alpha", "b", "beta", "rc", or "r"
        :param int build: is an integer
        :param str suffix: can contain any combination of alpha-numeric character and "._-"
        :param str seperator: is any of ".", "-", or "_", which is located between $extra and $build

        .. note::

           The method based on strings is the recommended method. For strings
           the major and minor version are required, where for tuple and list
           constructors all seven elements are optional.

        Examples:

        .. code-block:: python

           >>> a = Version('0.1')
           >>> print(tuple(a))
           (0, 1, None, None, None, '', None)
           >>> b = Version('2.5.3-rc2')
           >>> print(tuple(b))
           (2, 5, [3], 'rc', 2, '', '-')
           >>> c = Version('1.2.3.4.5.6.7-beta8_with_suffix')
           >>> print(tuple(c))
           (1, 2, [3, 4, 5, 6, 7], 'beta', 8, '_with_suffix', '-')


        """
        # Check if arguments are a list of arguments or a single argument containing a list, tuple or str
        if len(version) == 1:
            if isinstance(version[0], (list, tuple, str)):
                version = version[0]
            else:
                raise exceptions.FastrVersionInvalidError('"{}" is not a valid version input!'.format(version))

        orig_version = repr(version)
        if isinstance(version, str):
            version = str(version)

        if isinstance(version, str):
            version_match = cls.version_matcher.match(version)

            if version_match is not None:
                version = version_match.groups()
            else:
                version_match = cls.date_version_matcher.match(version)
                if version_match is not None:
                    version = version_match.groups()
                    version = (version[0], version[1], version[2], version[3], None, None, version[4])
                else:
                    raise exceptions.FastrVersionInvalidError('"{}" is not a valid version input!'.format(orig_version))

            # Move separator (element at index 3) to the end
            version = list(version)
            version.append(version[3])
            version.pop(3)

        if isinstance(version, tuple):
            version = list(version)

        if not isinstance(version, list) or len(version) > 7:
            raise exceptions.FastrVersionInvalidError('"{}" is not a valid version input!'.format(orig_version))

        default = [0, 0, None, None, None, None, None]

        if len(version) < 7:
            version += default[len(version):]

        # Parse the fields
        version[0] = int(version[0])
        version[1] = int(version[1])
        if isinstance(version[2], str):
            version[2] = re.split(r'\.', version[2].strip('.'))
            version[2] = tuple(int(x) for x in version[2])
        if isinstance(version[2], list):
            version[2] = tuple(version[2])
        # Small hack to make sure r > rc
        if version[3] == 'r':
            version[3] = 're'
        if version[4] is not None:
            version[4] = int(version[4])

        return super(Version, cls).__new__(Version, version)

    def __str__(self):
        """
        Return a string representation of the version
        """
        string = '{v.major}.{v.minor}{v.extra_string}'.format(v=self)

        if self[6] is not None:
            string += str(self[6])

        if self.status is not None:
            string += str(self.status)

        if self.build is not None:
            string += str(self.build)

        if self.suffix is not None:
            string += str(self.suffix)

        return string

    def __repr__(self):
        """
        Return a in-editor representation of the version
        """
        return '<Version: ' + str(self) + '>'

    @property
    def major(self):
        """
        major version
        """
        return self[0]

    @property
    def minor(self):
        """
        minor version
        """
        return self[1]

    @property
    def extra(self):
        """
        extra version extension as a list
        """
        return self[2]

    @property
    def extra_string(self):
        """
        extra version extension as a string
        """
        if self[2] is None:
            return ''
        else:
            return ''.join(['.{}'.format(x) for x in self[2]])

    @property
    def status(self):
        """
        the status of the version (a, alpha, b, beta, rc or r)
        """
        if self[3] == 're':
            return 'r'
        else:
            return self[3]

    @property
    def build(self):
        """
        the build number, this is following the status (e.g. for
        3.2-beta4, this would be 4)
        """
        return self[4]

    @property
    def suffix(self):
        """
        the remainder of the version which was not formatted in a known way
        """
        return self[5]
