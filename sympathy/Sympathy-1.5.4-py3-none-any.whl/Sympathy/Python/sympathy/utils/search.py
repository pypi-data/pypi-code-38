# Copyright (c) 2018 Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import re
import six

_regex_escape = '()[].*\\+${}^-,*?|'


def highlight_patterns(pattern, flags=re.IGNORECASE):
    res = []

    if pattern:
        words = pattern

        if isinstance(pattern, six.string_types):
            words = pattern.split(' ')
        for word in [w for w in words if w]:
            sub_patterns = []

            for c in word:
                if c in _regex_escape:
                    sub_patterns.append('\\{}\S*?'.format(c))
                else:
                    sub_patterns.append('{}\S*?'.format(c))

            res.append(re.compile(''.join(sub_patterns), flags))
    return res


def fuzzy_pattern(pattern, flags=re.IGNORECASE):
    patterns = ['^.*']
    res = None

    if pattern:
        words = pattern

        if isinstance(pattern, six.string_types):
            words = pattern.split(' ')
        for word in [w for w in words if w]:
            sub_patterns = []

            for c in word:
                if c in _regex_escape:
                    sub_patterns.append('\\{}.*'.format(c))
                else:
                    sub_patterns.append(c)

            patterns.append('.*{}'.format(''.join(sub_patterns)))
        patterns.append('.*$')
        res = re.compile(''.join(patterns), flags)
    return res


def matches(compiled_pattern, text):
    res = True
    if compiled_pattern:
        res = False
        if compiled_pattern.match(text):
            res = True
    return res
