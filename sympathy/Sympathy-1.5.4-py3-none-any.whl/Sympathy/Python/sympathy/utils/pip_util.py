# -*- coding: utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
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
"""
Module/script for extracting license information from pip and updating
third party licenses for Sympathy/Package/Windows/License.txt.in.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import sys
import os
import re
import io
import subprocess
import argparse
_fs_encoding = sys.getfilesystemencoding()

license_info = {
    'alabaster': 'BSD',
    'backports.functools-lru-cache': 'MIT',
    'h5py': 'BSD',
    'lxml': 'BSD',
    'mock': 'BSD',
    'pbr': 'APACHE',
    'prompt-toolkit': 'BSD',
    'svgutils': 'MIT',
    'kiwisolver': 'BSD',
    'backports-abc': 'PSF'}


def freeze():
    output = subprocess.check_output(
        [sys.executable, '-m', 'pip', 'freeze']).decode(_fs_encoding)
    return _freeze_str(output)


def _freeze_str(output):
    return dict(
        (k.strip(), v.strip())
        for k, v in re.findall('^([^=<>]*)[ \t]*[=<>]*[ \t]*(.*)$', output,
                               re.MULTILINE))


def show(pkg):
    output = subprocess.check_output(
        [sys.executable, '-m', 'pip', 'show', pkg]).decode(_fs_encoding)
    return _show_str(output)


def requirements(filename):
    if os.path.exists(filename):
        with io.open(filename) as f:
            data = f.read()
            return _freeze_str(data)
    else:
        try:
            return dict.fromkeys(re.findall('[ \t]*([^ \t,]+),?',
                                            show('Sympathy')['Requires']))
        except Exception:
            return {}


def _show_str(output, ignore_missing=False):
    res = dict(
        (k.strip(), v.strip())
        for k, v in re.findall('^([^:]*): *(.*)$', output, re.MULTILINE))
    lice = res.get('License')
    if lice is None or lice == 'UNKNOWN':
        name = res['Name']
        try:
            res['License'] = license_info[name]
        except KeyError:
            if ignore_missing:
                pass
            else:
                raise KeyError(
                    'Missing license for included package: "{name}" '
                    'please add that information to license_info'.format(
                        name=name))
    return res


def showall(names=None, ignore_missing=False):
    if not names:
        names = list(freeze().keys())

    output = subprocess.check_output(
        [sys.executable, '-m', 'pip', 'show'] + names).decode(_fs_encoding)
    pkgs = re.split('^---.*$[\r\n]+', output, flags=re.MULTILINE)
    return sorted([_show_str(pkg, ignore_missing) for pkg in pkgs],
                  key=lambda x: x['Name'])


def format_third_party(pkg):
    return '{name} ({home}) {lice}'.format(
        name=pkg['Name'],
        home=pkg['Home-page'],
        lice=pkg['License'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-I', '--input', action='store', default=None,
                        help='Input file used as template for expansion')
    parser.add_argument('-O', '--output', action='store', default=None,
                        help='Output file used for storing result')
    parsed = parser.parse_args()
    pkgs = showall()
    template = '{PYTHON_LICENSES}\n'
    indent = ''

    if parsed.input:
        with io.open(parsed.input) as f:
            template = f.read()

    match = re.search('^(.*){PYTHON_LICENSES}.*$', template, re.MULTILINE)
    if match:
        indent = match.group(1)
    text = ('\n' + indent).join(format_third_party(pkg) for pkg in pkgs)
    res = template.format(PYTHON_LICENSES=text)

    if parsed.output:
        with io.open(parsed.output, 'w') as f:
            f.write(res)
    else:
        print(res)
