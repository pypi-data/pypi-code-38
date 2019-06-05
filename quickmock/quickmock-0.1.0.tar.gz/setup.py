###############################################################################
#
#   Copyright 2018-2019 Telefónica
#
#   Quickmock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from setuptools import find_packages, setup
import quickmock


with open("requirements.txt") as iF:
    requirements = iF.read().splitlines()


setup(
    name='quickmock',
    version=quickmock.__version__,
    author='Félix Brezo (@febrezo)',
    description='Python 3.6+ implementation deploying quick mocks of HTTP server.',
    url='https://github.com/telefonica/quickmock',
    include_package_data=True,
    license='GNU GPLv3+',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'quickmock=quickmock.launcher:main',
        ],
    },
    install_requires=requirements
)
