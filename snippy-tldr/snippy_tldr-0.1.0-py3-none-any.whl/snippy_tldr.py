#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  SPDX-License-Identifier: Apache-2.0
#
#  Copyright 2019 Heikki J. Laaksonen  <laaksonen.heikki.j@gmail.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Snippy-tldr is a plugin to import tldr man pages to snippy."""

class SnippyTldr(object):  # pylint: disable=too-few-public-methods
    """Plugin to import tldr man pages to snippy."""

    def __init__(self):
        print("hello from snippy-tldr")

    @staticmethod
    def run():
        """Dummy run."""

        print("hello from run")
