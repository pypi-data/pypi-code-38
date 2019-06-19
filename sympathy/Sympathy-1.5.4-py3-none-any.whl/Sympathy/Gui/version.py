# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from sympathy import version

major = version.major
minor = version.minor
micro = version.micro
status = version.status

version_tuple = version.version_tuple
version = version.version
build = status


def application_name():
    return 'Sympathy for Data'


def application_url():
    """Return the URL to the developer website."""
    return 'https://www.sympathyfordata.com/'


def application_copyright():
    """Return the name of the copyright holder."""
    return 'Combine Control Systems AB'


def email_bugs():
    """Return the email address for bug reports."""
    return 'support@sympathyfordata.com'


def email_contribution():
    """Return the email address to use for those who want to contribute."""
    return 'support@sympathyfordata.com'
