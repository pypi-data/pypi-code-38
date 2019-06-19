# -*- coding:utf-8 -*-
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
import six
from .. utils.components import IComponent


@six.python_2_unicode_compatible
class TagType(object):
    def __init__(self, key, desc, name=None):
        self._key = key
        assert(key.isalpha())
        self._name = name
        self._desc = desc

    def __repr__(self):
        return repr(self._key)

    def __str__(self):
        return repr(self._key)

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name or self._key

    @property
    def desc(self):
        return self._desc

    @property
    def term(self):
        return True

    def to_dict(self):
        return ['T', self._key, self._desc, self._name]


class GroupTagType(TagType):
    def __init__(self, key, tags, desc=None, name=None):
        super(GroupTagType, self).__init__(key, desc, name)
        self._tags = tuple(tags)

    def __getitem__(self, key):
        for tag in self._tags:
            if tag.key == key:
                return tag

        raise KeyError(u'No tag: "{}" in tag group: {}'.format(key, self))

    @property
    def term(self):
        return False

    def __iter__(self):
        for tag in self._tags:
            yield tag

    def to_dict(self):
        return ['G', self._key, self._desc, self._name,
                [tag.to_dict() for tag in self._tags]]


def from_dict(data):
    def inner():
        pass

    if data is None:
        return None

    kind = data[0]
    if kind == 'T':
        key, desc, name = data[1:]
        return TagType(key, desc, name)
    elif kind == 'G':
        key, desc, name, tags = data[1:]
        return GroupTagType(key, tuple([from_dict(tag) for tag in tags]), desc,
                            name)


class LibraryTags(IComponent):
    def __init__(self):
        self._root = None

    def __getitem__(self, key):
        root = self._root
        parts = key.split('.')
        partiter = iter(parts)
        group = root[six.next(partiter)]

        for part in partiter:
            group = group[part]

        assert(group.term())
        return group

    def to_dict(self):
        return self._root.to_dict()

    @staticmethod
    def from_dict(data):
        tags = LibraryTags()
        tags._root = from_dict(data)
        return tags

    @staticmethod
    def merge(tagslist):

        def inner(tag1, tag2):
            term1 = tag1.term
            term2 = tag2.term

            if not term1 and not term2:
                tags = []
                mapping1 = {}
                mapping2 = {}
                keys = set()

                for tag in tag1:
                    mapping1[tag.key] = tag
                    keys.add(tag.key)

                for tag in tag2:
                    mapping2[tag.key] = tag
                    keys.add(tag.key)

                for key in keys:
                    if key in set(mapping1).intersection(mapping2):
                        tag1 = mapping1[key]
                        tag2 = mapping2[key]

                        tags.append(inner(tag1, tag2))

                for key in keys - set(mapping2):
                    tags.append(mapping1[key])

                for key in keys - set(mapping1):
                    tags.append(mapping2[key])

                return GroupTagType(tag1.key, tuple(tags), desc=tag1.desc,
                                    name=tag1.name)

            elif not term1 and term2:
                assert(False)
            elif term1 and not term2:
                assert(False)
            else:
                # Both define the same term key, use the first one.
                return tag1

        tagslist = [tags for tags in tagslist if tags.valid]

        if tagslist:
            tagsiter = iter(tagslist)
            root = six.next(tagsiter)._root

            for tags in tagsiter:
                root = inner(root, tags._root)

            result = LibraryTags()
            result._root = root
            assert(result.valid)
            return result

    @property
    def valid(self):
        def inner(level, tag):
            if level == 2:
                return tag.term

            if not tag.term:
                return all(inner(level + 1, tag_) for tag_ in tag)

            return False

        return inner(0, self._root)

    @property
    def root(self):
        return self._root


@six.python_2_unicode_compatible
class Tag(object):
    def __init__(self, key):
        self._key = key

    def __getattr__(self, key):
        # Workaround for ipython messing around.
        if key == '_ipython_display_':
            return self._key
        key_ = self._key
        self._key = '.'.join([key_, key])
        return self

    def to_dict(self):
        return self.key

    @property
    def key(self):
        return self._key

    def __str__(self):
        return self._key

    def __repr__(self):
        return repr(six.text_type(self))


class TagBuilder(object):
    def __getattribute__(self, key):
        return Tag(key)


class Tags(object):
    def __init__(self, *tags):
        self._tags = tuple(tags)

    def __iter__(self):
        for tag in self._tags:
            yield tag

    def to_dict(self):
        return [tag.to_dict() for tag in self._tags]


tag_builder = TagBuilder()
