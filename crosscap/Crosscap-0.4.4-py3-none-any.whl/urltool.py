"""
URLtool - tool for documenting http API and building API clients

This assumes using crosscap.tree.enter() decorator
"""
from __future__ import print_function

import re

from builtins import object

import click

import yaml

import attr

from twisted.python.reflect import namedAny

from crosscap import openapi
from crosscap.doc import Documentation


def _iterClass(cls, prefix=''):
    """
    Descend a Klein()'s url_map, and generate ConvertedRule() for each one
    """
    iterableRules = [(prefix, cls, cls.app.url_map.iter_rules())]
    for prefix, currentClass, i in iter(iterableRules):
        for rule in i:
            converted = dumpRule(currentClass, rule, prefix)
            if converted.branch:
                continue

            if converted.subKlein:
                clsDown = namedAny(converted.subKlein)
                iterableRules.append((converted.rulePath, clsDown, clsDown.app.url_map.iter_rules()))

            yield converted


@click.command()
@click.argument('classQname')
@click.argument('filt', required=False)
@click.option("--reverse", "-v", is_flag=True, help='Invert the filter: select URLs which do not match', default=False)
def urltool(classqname, filt, reverse):
    """
    Dump all urls branching from a class as OpenAPI 3 documentation

    The class must be given as a FQPN which points to a Klein() instance.

    Apply optional [FILT] as a regular expression searching within urls. For
    example, to match all urls beginning with api, you might use '^/api'
    """
    filt = re.compile(filt or '.*')

    rootCls = namedAny(classqname)
    rules = list(_iterClass(rootCls))
    arr = []
    for item in sorted(rules):
        if item.subKlein:
            continue

        matched = filt.search(item.rulePath)
        matched = not matched if reverse else matched
        if matched:
            arr.append(tuple(item.toOpenAPIPath()))

    openapi3 = openapi.OpenAPI()
    for pathPath, pathItem in arr:
        if pathPath in openapi3.paths:
            openapi3.paths[pathPath].merge(pathItem)
        else:
            openapi3.paths[pathPath] = pathItem
    print(yaml.dump(openapi3, default_flow_style=False))


@attr.s
class ConvertedRule(object):
    """
    An atom of structured information about one route
    """
    rulePath = attr.ib()
    operationId = attr.ib()
    doco = attr.ib(default=None)
    branch = attr.ib(default=False)
    methods = attr.ib(default=attr.Factory(list))
    subKlein = attr.ib(default=None)

    def toOpenAPIPath(self):
        """
        Produce a data structure compatible with OpenAPI

        @returns tuple of (path, pathItem)
        """
        pathItem = openapi.OpenAPIPathItem()
        methods = self.methods[:] or ['x-any-method']
        for meth in methods:
            if meth.lower() in ['head']:
                continue
            operation = openapi.OpenAPIOperation()
            operation.operationId = self.operationId
            self._parseRawDoc(operation)
            pathItem.addOperation(meth.lower(), operation)

        return self.rulePath, pathItem

    def _parseRawDoc(self, operation):
        """
        Set doc fields of this operation by using the Documentation object

        - If the Documentation object has a .yamlData property, we update values
          of the operation properties from them. Unrecognized properties will
          be added with the 'x-' prefix.
        - Documentation.full is the description
        - Documentation.first is the summary
        """
        operation.summary = self.doco.first
        operation.description = self.doco.full
        if self.doco.yamlData:
            fieldNames = [f.name for f in attr.fields(operation.__class__)]
            for k in self.doco.yamlData:
                if k in fieldNames:
                    setattr(operation, k, self.doco.yamlData[k])
                else:
                    operation._extended['x-' + k] = self.doco.yamlData[k]


@attr.s
class OpenAPIExtendedDocumentation(Documentation):
    """
    A `Documentation` that recognizes and parses yaml inclusions

    If the string contains '---', anything below it is treated as yaml properties

    If the docstring contains multiple `---`-separated documents, they will be merged
    into one another, starting from the top.
    """
    yamlData = attr.ib(default=None)

    @classmethod
    def fromObject(cls, obj, decode=None):
        orig = Documentation.fromObject(obj, decode)
        self = cls(orig.raw)
        lines = self.raw.splitlines()
        if '---' in lines:
            n = lines.index('---')
            this, that = '\n'.join(lines[:n]), '\n'.join(lines[n:])
            self.yamlData = {}
            for ydoc in yaml.load_all(that):
                assert isinstance(ydoc, dict), "only dict-like structures allowed in yaml docstrings not %r" % type(ydoc)
                self.yamlData.update(ydoc)
        else:
            this = '\n'.join(lines)
        self.raw = this
        return self


def dumpRule(serviceCls, rule, prefix):
    """
    Create an in-between representation of the rule, so we can eventually convert it to OpenAPIPathItem with OpenAPIOperation(s)
    """
    rulePath = prefix + rule.rule
    rulePath = re.sub('/{2,}', '/', rulePath)

    cor = ConvertedRule(
            rulePath=rulePath,
            operationId=rule.endpoint
            )

    # look for methods
    for meth in sorted(rule.methods or []):
        cor.methods.append(meth)

    # edit _branch operationId to provide the true method name
    origEP = cor.operationId
    if origEP.endswith('_branch'):
        origEP = origEP[:-7]
        cor.branch = True
    cor.operationId = '%s.%s' % (serviceCls.__name__, origEP)
    # get the actual method so we can inspect it for extension attributes
    meth = getattr(serviceCls, origEP)

    if hasattr(meth, '_subKleinQname'):
        cor.subKlein = meth._subKleinQname

    cor.doco = OpenAPIExtendedDocumentation.fromObject(meth, decode=True)
    return cor


def literal_unicode_representer(dumper, data):
    """
    Use |- literal syntax for long strings
    """
    if '\n' in data:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
    else:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data)
