# Copyright (c) 2013, Combine Control Systems AB
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
# Ports definition classes.
from .. utils.port import Port, Ports, PortType, TemplateTypes

from .. utils.tag import tag_builder as Tag
from .. utils.tag import TagType, GroupTagType, Tags, LibraryTags


# Node parameter API, for accessing fields and building the structure.
from .. utils.parameter_helper import ParameterRoot

from .. utils.context import (inherit_doc, join_doc, deprecated_node,
                              deprecated_warn)

# Helper for implementing standardized adjust parameters.
from sympathy.platform.gennode import adjust

# Function returning worker settings.
from sympathy.platform.settings import settings


__all__ = ['Port', 'Ports', 'PortType', 'TemplateTypes', 'Tag', 'TagType',
           'GroupTagType', 'Tags', 'LibraryTags', 'ParameterRoot',
           'inherit_doc', 'join_doc', 'deprecated_node', 'adjust', 'settings',
           'deprecated_warn']
