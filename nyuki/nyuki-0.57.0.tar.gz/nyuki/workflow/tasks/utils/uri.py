import re
from collections import namedtuple

from . import runtime


class InvalidWorkflowUri(Exception):
    pass


WorkflowUri = namedtuple(
    'WorkflowURI',
    ['template_id', 'holder', 'instance_id']
)


class URI:

    REGEX = re.compile(
        r"^nyuki://(?P<template_id>[\w-]+)"
        r"@(?P<holder>[\w-]+)"
        r"(/(?P<instance_id>[\w-]+))?$"
    )

    @staticmethod
    def instance(obj):
        tid = obj.template.uid
        try:
            iid = obj.instance.uid
        except AttributeError:
            iid = obj.uid
        return 'nyuki://{template_id}@{holder}/{instance_id}'.format(
            template_id=tid, holder=runtime.bus.name, instance_id=iid
        )

    @staticmethod
    def template(template_id):
        return 'nyuki://{template_id}@{holder}'.format(
            template_id=template_id, holder=runtime.bus.name
        )

    @classmethod
    def parse(cls, uri):
        result = re.match(cls.REGEX, uri)
        if not result:
            raise InvalidWorkflowUri(uri)
        return WorkflowUri(
            result.group('template_id'),
            result.group('holder'),
            result.group('instance_id'),
        )
