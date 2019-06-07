"""
Tests of the urltool command-line program
"""
from inspect import cleandoc

from click.testing import CliRunner

from pytest import fixture

import yaml

from werkzeug.routing import Rule

from crosscap import urltool
from crosscap.test.conftest import TopApp, SubApp


def test_dumpRule():
    """
    Do I produce the correct data structure for a rule?
    """
    rule = Rule('/end/', endpoint='end')
    cor = urltool.dumpRule(SubApp, rule, '/sub')
    expect = urltool.ConvertedRule(
            operationId='SubApp.end',
            rulePath='/sub/end/',
            doco=urltool.OpenAPIExtendedDocumentation('This is an endpoint\n\nIt takes nothing and returns "ended"')
            )
    assert cor == expect

    rule2 = Rule('/sub/', endpoint='subTree_branch')
    utr2 = urltool.dumpRule(TopApp, rule2, '')
    expect2 = urltool.ConvertedRule(
            operationId='TopApp.subTree',
            rulePath='/sub/',
            doco=urltool.OpenAPIExtendedDocumentation(''),
            branch=True,
            subKlein='crosscap.test.conftest.SubApp',
            )
    assert utr2 == expect2


@fixture
def runner():
    return CliRunner()


def test_filter(runner):
    """
    Do I filter correctly? Forwards and reverse?
    """
    res = runner.invoke(urltool.urltool, ['crosscap.test.conftest.TopApp', 'hasqueryarg'])
    assert res.output.strip() == cleandoc("""
        openapi: 3.0.0
        info:
          title: TODO
          version: TODO
        paths:
          /sub/hasqueryarg:
            get:
              summary: This is an endpoint that can be filtered out
              description: |-
                This is an endpoint that can be filtered out

                It takes a query arg and returns it
              operationId: SubApp.hasQueryArg
              parameters:
              - name: color
                in: query
                required: true
    """)

    res = runner.invoke(urltool.urltool, ['crosscap.test.conftest.TopApp', 'hasqueryarg', '--reverse'])
    assert res.output.strip() == cleandoc("""
        openapi: 3.0.0
        info:
          title: TODO
          version: TODO
        paths:
          /sub/end:
            get:
              tags:
              - a
              - z
              summary: What is the end?
              description: |-
                What is the end?

                This is the end.
              operationId: SubApp.getEnd
              responses:
                default:
                  content:
                    text/html:
                      x-page-class: crosscap.test.conftest.PageClass
              x-fish:
              - red
              - blue
            post:
              summary: This is an endpoint
              description: |-
                This is an endpoint

                It takes nothing and returns "ended"
              operationId: SubApp.end
            put:
              operationId: SubApp.putEnd
              responses:
                default:
                  content:
                    text/html:
                      x-page-class: crosscap.test.conftest.OtherPageClass

        """)


def test_postOptions(runner):
    """
    Do I produce some nicely-formatted output
    """
    res = runner.invoke(urltool.urltool, ['crosscap.test.conftest.TopApp'])
    assert res.output.strip() == cleandoc("""
        openapi: 3.0.0
        info:
          title: TODO
          version: TODO
        paths:
          /sub/end:
            get:
              tags:
              - a
              - z
              summary: What is the end?
              description: |-
                What is the end?

                This is the end.
              operationId: SubApp.getEnd
              responses:
                default:
                  content:
                    text/html:
                      x-page-class: crosscap.test.conftest.PageClass
              x-fish:
              - red
              - blue
            post:
              summary: This is an endpoint
              description: |-
                This is an endpoint

                It takes nothing and returns "ended"
              operationId: SubApp.end
            put:
              operationId: SubApp.putEnd
              responses:
                default:
                  content:
                    text/html:
                      x-page-class: crosscap.test.conftest.OtherPageClass
          /sub/hasqueryarg:
            get:
              summary: This is an endpoint that can be filtered out
              description: |-
                This is an endpoint that can be filtered out

                It takes a query arg and returns it
              operationId: SubApp.hasQueryArg
              parameters:
              - name: color
                in: query
                required: true

        """)


def test_yamlMultilineString():
    """
    Do I properly represent strings using multiline syntax
    """
    obj = {'thing': 'a\nb'}
    assert yaml.dump(obj, default_flow_style=False) == 'thing: |-\n  a\n  b\n'
