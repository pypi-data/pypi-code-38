"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on May 20, 2018

@author: jrm
"""
import sys
from flask import Flask
from atom.api import Instance
from web.apps.web_app import WebApplication


class FlaskApplication(WebApplication):
    """ An application based on MagicStack's uvloop
    
    """
    #: Flask app
    app = Instance(Flask, ())

    def start(self, **kwargs):
        """ Start the application's main event loop.

        """
        self.app.run(host=kwargs.pop('host', self.interface),
                     port=kwargs.pop('port', self.port),
                     debug=kwargs.pop('debug', self.debug),
                     **kwargs)

    def stop(self):
        """ Stop the application's main event loop.

        """
        sys.exit(0)

    # -------------------------------------------------------------------------
    # HTTP API
    # -------------------------------------------------------------------------
    def handle_request(self, handler, request, response):
        """ Handle the request and response.
        
        Parameters
        ----------
        handler: web.core.http.Handler
            A user provided handler that will handle the request and response
            parameters by the user. Once the request method is parsed it
            should lookup the method on this handler and call that with the
            populated request and response if present.
        request: web.core.http.Request
            The request object
        response: web.core.http.Response
            The response object. This implementation should convert this
            to the proper type needed by this application.
        
        Returns
        -------
        result: Object
            A proper response expected by this web server.
        
        """
        raise NotImplementedError
    
    def add_route(self, route, handler, **kwargs):
        """ Create a route for the given handler
        
        Parameters
        ----------
        route: String
            The route used
        handler: Object
            The application specific handler for this route
        kwargs: Dict
            Any extra kwargs for this route
        
        """
        self.app.route(route, handler, **kwargs)
    
    def add_static(self, route, path, **kwargs):
        """ Create a route for serving static files at the given path.
        
        Parameters
        ----------
        route: String
            The route used
        path: String
            The file path
        kwargs: Dict
            Any extra kwargs for this route
        
        """
        raise NotImplementedError
