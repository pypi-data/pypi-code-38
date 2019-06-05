#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, make_response, request
from flask_restful import Resource, Api, reqparse
import os
import sys
from gherkan.flask_api import resources
from gherkan.flask_api import API_FSA
import argparse


def main(cmd_line_args=None):
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Runs RESTful API for the Gherkan NL Instruction Processing system.')

    host_group = parser.add_mutually_exclusive_group()
    host_group.add_argument('host', nargs="?", help="The hostname to listen on. Set this to '0.0.0.0' to have the server available externally as well. Defaults to '127.0.0.1'", default="127.0.0.1")
    host_group.add_argument('-x', '--external', help="Sets the host to '0.0.0.0' (see the 'host' parameter). Can only be used if host is not specified", action='store_true')

    port_group = parser.add_mutually_exclusive_group()
    port_group.add_argument('port', nargs="?", help='The port of the webserver. Defaults to 5000.', default=5000, type=int)
    port_group.add_argument('-p', help='The port of the webserver. Defaults to 5000.', default=0, type=int)

    parser.add_argument('-d', '--debug', help='Enables debug mode. An interactive debugger will be shown for unhandled exceptions, and the server will be reloaded when code changes.', action='store_true')
    parser.add_argument('-s', '--set', nargs=2, help='Sets a value to the fsa_config.yaml. Anything else is ignored, i.e. the system is not run and the script will exit after setting the variable. Multiple variables can be set at once.', action='append')
    parser.add_argument('-f', '--flush', help='Will flush previous error.', action='store_true')
    parser.add_argument('-rf', '--regenerate_flush', help='Regenerate fsa_config and flush errors.', action='store_true')

    args = parser.parse_args(cmd_line_args)

    API_FSA.setup(debugMode=args.debug)
    print(args)

    api_host = args.host
    if args.set is not None:
        # Iterate of the parameters, set them and exit
        for (key, value) in args.set:
            if value.isdecimal():
                value = int(value)
            elif value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            API_FSA.setConfig(key, value)
        sys.exit(0)
    else:
        if args.regenerate_flush:
            API_FSA.regenerateConfig()
            API_FSA.setState(API_FSA.S_OFF)
            API_FSA.setConfig("flush", True)
        elif args.flush:
            API_FSA.setConfig("flush", True)  # set flush to true so that previous errors are ignored
        if args.p > 0:
            api_port = args.p
        else:
            api_port = args.port
        api_debug = args.debug
        if args.external:
            api_host = '0.0.0.0'

    # Initialize the FSA
    API_FSA.init_fsa(api_host, api_port)

    app = Flask(__name__)
    api = Api(app)

    # Append resources
    api.add_resource(resources.Actions, '/actions', endpoint='actions')
    api.add_resource(resources.Actions, '/actions/<language>', endpoint='actions_language')
    api.add_resource(resources.Audio, '/audio')
    api.add_resource(resources.NLScenario, '/nlscenario')
    api.add_resource(resources.NLText, '/nltext')
    api.add_resource(resources.SignalMap, '/signal_map')
    api.add_resource(resources.SignalMap, '/signal_map/<language>', endpoint='signal_map_language')
    api.add_resource(resources.Signals, '/signals')
    api.add_resource(resources.NegatedSignals, '/signals_negated')
    api.add_resource(resources.Handler, '/<string:action>', endpoint='handler')
    api.add_resource(resources.Handler, '/<string:action>/<string:param>', endpoint='handler_param')

    # Run the API App
    app.run(host=api_host, port=api_port, debug=api_debug)


if __name__ == '__main__':
    print("setting up Gherkan API via script")
    main()
