# Copyright (c) 2019 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# StringIO moves in Python3.
# In Python2, two packages exist: cStringIO and StringIO. StringIO is pure
# Python and cStringIO is a fast replacement. These support ASCII, and StringIO
# also supports Unicode. In Python3, only one package exists: io.StringIO.
# io.StringIO only supports Unicode. To make the transition easy, this will be
# the only usage of cStringIO, and this usage will fall back to io.StringIO when
# we switch to Python3.
try:
    # pylint: disable=unused-import
    from cStringIO import StringIO
except ImportError:
    # pylint: disable=unused-import
    from io import StringIO
