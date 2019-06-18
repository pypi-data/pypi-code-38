#!/usr/bin/env python

# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import app
from flask import render_template, url_for, redirect, flash, request
import fastr
import fastr.exceptions
import requests

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>title</title>
        <link rel="stylesheet" href="style.css">
      </head>
      <body>
        Server shutting down...
      </body>
    </html>
    """

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/websocketclient')
def websocket_client():
    return render_template('websocket_client.html')


@app.route('/networks')
def networks():
    # http://stackoverflow.com/questions/26868372/calling-rest-api-from-the-same-server
    # http://stackoverflow.com/questions/20169326/calling-flask-restful-api-resource-methods
    # import api

    # print requests.get("http://localhost:9000/api/networks/")
    # test = api.api.resource("/networks/")
    # print(request.args.get("/api/networks/"))
    networks = list(fastr.networklist.values())

    return render_template('networks.html')


@app.route('/network/<name>')
def network(name=None):
    return render_template('network.html', name=name)


@app.route('/doc', endpoint='docs')
def doc():
    return render_template('docs.html', url=url_for('static', filename='doc/index.html'))


@app.route('/prov')
def prov():
    return render_template('prov.html')


@app.route('/tool')
@app.route('/tool/<toolname>')
@app.route('/tool/<toolname>/<version>')
def tool(toolname=None, version=None):
    if toolname is None and version is None:
        unique_toolnames = {'{}.{}'.format(key[0], key[1]) for key in fastr.tools.keys()}
        print('Unique tool names: {}'.format(unique_toolnames))
        tools = sorted([(tool, sorted([str(v) for v in fastr.tools.toolversions(tool)], reverse=True)) for tool in unique_toolnames])
        return render_template('tool_overview.html', tools=tools)

    # If either a toolname or both version and toolname is set:
    if toolname in fastr.tools:
        versions = sorted([str(v) for v in fastr.tools.toolversions(toolname)], reverse=True)
        tools = [(v, fastr.tools[toolname, v]) for v in versions]
    else:
        flash("Tool ({}) is not known.".format(toolname), 'danger')
        tools = []
    # When there is no explicit version set, appoint the first version in the list as selected.
    if version is None and tools != []:
        version = tools[0][0]
    return render_template('tool.html', toolname=toolname, selected_version=version, tools=tools)
