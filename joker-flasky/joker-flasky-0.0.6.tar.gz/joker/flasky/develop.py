#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import os
from os.path import split, splitext

import flask

from joker.flasky.context import Rumor


def _create_flaskapp(contextmap, **flask_params):
    """
    :param contextmap: a dict-like obj with .get() and .setdefault()
    :param flask_params: (dict)
    :return: (flask.Flask)
    """
    app = flask.Flask(**flask_params)
    _global = contextmap.setdefault('_global', {})
    _global['sver'] = Rumor(**contextmap.get('_sver', {}))

    @app.route('/<path:path>')
    def render(path):
        name, ext = splitext(path)
        if ext and ext != '.html':
            return flask.abort(404)
        context = contextmap.get('_global', {}).copy()
        context.update(contextmap.get(name, {}))
        template_path = context.get('_prot', name) + '.html'
        return flask.render_template(template_path, **context)

    app.route('/')(lambda: render('index'))
    return app


def create_flaskapp(package, contextmap, static_folder=None):
    flask_params = {
        'root_path': split(package.__file__)[0],
        'import_name': package.__name__,
        'static_url_path': '/static',
    }
    if static_folder:
        flask_params['static_folder'] = static_folder
    return _create_flaskapp(contextmap, **flask_params)


def create_flat_flaskapp(root_path, contextmap):
    if os.path.isfile(root_path):
        root_path = split(root_path)[0]

    flask_params = {
        'root_path': root_path,
        'import_name': __name__,
    }
    return _create_flaskapp(contextmap, **flask_params)
