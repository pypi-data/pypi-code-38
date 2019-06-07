"""
Common pytest workhorse code and fixtures
"""
from builtins import object

from klein import Klein

from crosscap import openAPIDoc, enter
from crosscap.openapi import textHTML, queryParameter


class TopApp(object):
    app = Klein()

    @app.route('/sub/', branch=True)
    @enter('crosscap.test.conftest.SubApp')
    def subTree(self, request, subKlein):
        request.setHeader('content-type', 'application/topapp')
        return subKlein


class SubApp(object):
    app = Klein()

    @openAPIDoc(parameters=[queryParameter('color', required=True)])
    @app.route('/hasqueryarg', methods=['GET'])
    def hasQueryArg(self, request): # pragma: nocover
        """
        This is an endpoint that can be filtered out

        It takes a query arg and returns it
        """
        return request.args.get('color')[0]

    @app.route('/end', methods=['POST', 'HEAD'])
    def end(self, request):
        """
        This is an endpoint

        It takes nothing and returns "ended"
        """
        return 'ended'

    @openAPIDoc(responses=textHTML({'x-page-class': 'crosscap.test.conftest.PageClass'}))
    @app.route('/end', methods=['GET'])
    def getEnd(self, request): # pragma: nocover
        """
        What is the end?

        This is the end.
        ---
        tags: [a, z]
        fish: [red, blue]
        """
        return 'status: unending'

    @openAPIDoc(responses={'default': {'content': {'text/html': {'x-page-class': 'crosscap.test.conftest.OtherPageClass'}}}})
    @app.route('/end', methods=['PUT'])
    def putEnd(self, request): # pragma: nocover
        # this has no docstring, for test coverage
        pass
