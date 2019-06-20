# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Filip Valder <fvalder@redhat.com>

"""Generic resolver functions."""


import six
from abc import ABCMeta, abstractmethod

import module_build_service.config as cfg
from module_build_service import conf


class GenericResolver(six.with_metaclass(ABCMeta)):
    """
    External Api for resolvers
    """

    _resolvers = cfg.SUPPORTED_RESOLVERS

    # Resolver name. Each subclass of GenericResolver must set its own name.
    backend = "generic"

    # Supported resolver backends registry. Generally, resolver backend is
    # registered by calling :meth:`GenericResolver.register_backend_class`.
    # This is a mapping from resolver name to backend class object
    # For example, {'mbs': MBSResolver}
    backends = {}

    @classmethod
    def register_backend_class(cls, backend_class):
        GenericResolver.backends[backend_class.backend] = backend_class

    @classmethod
    def create(cls, config, backend=None, **extra):
        """Factory method to create a resolver object

        :param config: MBS config object.
        :type config: :class:`Config`
        :kwarg str backend: resolver backend name, e.g. 'db'. If omitted,
            system configuration ``resolver`` is used.
        :kwarg extra: any additional arguments are optional extras which can
            be passed along and are implementation-dependent.
        :return: resolver backend object.
        :rtype: corresponding registered resolver class.
        :raises ValueError: if specified resolver backend name is not
            registered.
        """
        # get the appropriate resolver backend via configuration
        if not backend:
            backend = conf.resolver

        if backend in GenericResolver.backends:
            return GenericResolver.backends[backend](config, **extra)
        else:
            raise ValueError("Resolver backend='%s' not recognized" % backend)

    @classmethod
    def supported_builders(cls):
        if cls is GenericResolver:
            return {k: v["builders"] for k, v in cls._resolvers.items()}
        else:
            try:
                return cls._resolvers[cls.backend]["builders"]
            except KeyError:
                raise RuntimeError(
                    "No configuration of builder backends found for resolver {}".format(cls))

    @classmethod
    def is_builder_compatible(cls, builder):
        """
        :param backend: a string representing builder e.g. 'koji'

        Get supported builder backend(s) via configuration
        """
        if cls is not GenericResolver:
            return builder in cls.supported_builders()

        return False

    @abstractmethod
    def get_module_count(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_latest_with_virtual_stream(self, name, virtual_stream):
        raise NotImplementedError()

    @abstractmethod
    def get_module_modulemds(
        self,
        name,
        stream,
        version=None,
        context=None,
        strict=False,
        stream_version_lte=None,
        virtual_streams=None,
    ):
        raise NotImplementedError()

    @abstractmethod
    def get_buildrequired_modulemds(self, name, stream, base_module_nsvc, strict=False):
        raise NotImplementedError()

    @abstractmethod
    def resolve_profiles(self, mmd, keys):
        raise NotImplementedError()

    @abstractmethod
    def get_module_build_dependencies(
        self, name=None, stream=None, version=None, mmd=None, context=None, strict=False
    ):
        raise NotImplementedError()

    @abstractmethod
    def resolve_requires(self, requires):
        raise NotImplementedError()

    @abstractmethod
    def get_modulemd_by_koji_tag(self, tag):
        """Get module metadata by module's koji_tag

        :param str tag: name of module's koji_tag.
        :return: module metadata
        :rtype: Modulemd.Module
        """
        raise NotImplementedError()
