# coding=utf-8
from __future__ import absolute_import, print_function

import functools
import itertools

from suanpan.dw import dw
from suanpan.interfaces import HasArguments
from suanpan.log import logger
from suanpan.mq import mq
from suanpan.mstorage import mstorage
from suanpan.storage import storage


class HasBaseServices(HasArguments):
    ENABLED_BASE_SERVICES = {"mq", "mstorage", "dw", "storage"}

    def setBackendIfHasArgs(*keys):  # pylint: disable=no-method-argument
        def _wrap(func):
            @functools.wraps(func)
            def _dec(cls, sargs, *args, **kwargs):
                return (
                    func(cls, sargs, *args, **kwargs)
                    if all(getattr(sargs, key, None) is not None for key in keys)
                    else None
                )

            return _dec

        return _wrap

    @classmethod
    def setBaseServices(cls, args):
        mapping = {
            "mq": cls.setMQ,
            "mstorage": cls.setMStorage,
            "dw": cls.setDataWarehouse,
            "storage": cls.setStorage,
        }
        setters = {
            service: mapping.get(service) for service in cls.ENABLED_BASE_SERVICES
        }
        if not all(setters.values()):
            raise Exception(
                "Unknown base serivces: {}".format(
                    set(cls.ENABLED_BASE_SERVICES) - set(mapping.keys())
                )
            )
        backends = ((service, setter(args)) for service, setter in setters.items())
        baseServices = {service: backend for service, backend in backends if backend}
        logger.info("Base services init: {}".format(", ".join(baseServices.keys())))
        return baseServices

    def getGlobalArguments(self, *args, **kwargs):
        arguments = super(HasBaseServices, self).getGlobalArguments(*args, **kwargs)
        return arguments + self.getBaseServicesArguments()

    @classmethod
    def getBaseServicesArguments(cls):
        mapping = {
            "mq": mq.ARGUMENTS,
            "mstorage": mstorage.ARGUMENTS,
            "dw": dw.ARGUMENTS,
            "storage": storage.ARGUMENTS,
        }
        arguments = {
            service: mapping.get(service) for service in cls.ENABLED_BASE_SERVICES
        }
        if not all(arguments.values()):
            raise Exception(
                "Unknown base serivces: {}".format(
                    set(cls.ENABLED_BASE_SERVICES) - set(mapping.keys())
                )
            )
        return list(itertools.chain(*arguments.values()))

    @classmethod
    @setBackendIfHasArgs("mq_type")
    def setMQ(cls, args):
        return mq.setBackend(**cls.defaultArgumentsFormat(args, mq.ARGUMENTS))

    @classmethod
    @setBackendIfHasArgs("mstorage_type")
    def setMStorage(cls, args):
        return mstorage.setBackend(
            **cls.defaultArgumentsFormat(args, mstorage.ARGUMENTS)
        )

    @classmethod
    @setBackendIfHasArgs("dw_type")
    def setDataWarehouse(cls, args):
        return dw.setBackend(**cls.defaultArgumentsFormat(args, dw.ARGUMENTS))

    @classmethod
    @setBackendIfHasArgs("storage_type")
    def setStorage(cls, args):
        return storage.setBackend(**cls.defaultArgumentsFormat(args, storage.ARGUMENTS))
