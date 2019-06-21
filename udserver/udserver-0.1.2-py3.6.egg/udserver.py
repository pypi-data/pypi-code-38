# -*- coding: utf-8 -*-
"""Main module."""

from __future__ import print_function
import os
from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_dropzone import Dropzone
import glob
import sys
import socket
import logging
import pkg_resources
import argparse
import configparser

package_name = 'udserver'
# root = os.path.dirname(pkg_resources.resource_filename(package_name, __file__))
# sys.path.insert(0, root)
# print(sys.path)

app = Flask(__name__, static_folder='public', static_url_path='')
# app.config.from_object('config.ProductionConfig')
cfgfile = pkg_resources.resource_filename(package_name, 'config.cfg')
app.config.from_pyfile(cfgfile)

dropzone = Dropzone(app)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not os.path.isdir(app.config['STORAGE_FOLDER']):
    os.makedirs(app.config['STORAGE_FOLDER'])


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'public'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


@app.route('/storage/<path:filename>')
def custom_static(filename):
    return send_from_directory(
        #  app.config['STORAGE_FOLDER'], filename, attachment=True)
        app.config['STORAGE_FOLDER'],
        filename)


@app.route('/')
def root():
    print(app.config['STORAGE_FOLDER'])
    fpaths = glob.glob(app.config['STORAGE_FOLDER'] + '/*')
    fnames = map(os.path.basename, fpaths)

    return render_template('index.html', fnames=fnames)
    #  return app.send_static_file('index.html')


@app.route('/uploads', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('file')
        if files:
            for f in files:
                f.save(os.path.join(app.config['STORAGE_FOLDER'], f.filename))
        else:
            print('0 files', file=sys.stderr)

    return 'bad upload request'


@app.route('/clean_storage', methods=['POST'])
def clean_storage():
    rc = {}
    rc['success'] = False
    rc['error'] = ''

    operation = request.get_json()['operation']

    if operation == 'clean':
        fpaths = glob.glob(app.config['STORAGE_FOLDER'] + '/*')

        for file in fpaths:
            try:
                os.remove(file)
            except OSError:
                rc['success'] = False
                rc['error'] = 'OSError: %s is not being removed' % file

                break

        rc['success'] = True

    return jsonify(rc)


def show_localip():
    # msg = '===============Local ip=================\n'
    # msg = '\t' + socket.gethostbyname(socket.gethostname()) + '\n'
    msg = '\nlocal ip: ' + socket.gethostbyname(socket.gethostname()) + '\n'
    msg += '========================================\n\n'
    logger.warning(msg)


if __name__ == '__main__':
    show_localip()
    app.run(host='0.0.0.0', debug=True)

    #  handler = RotatingFileHandler(log_fpath, maxBytes=10000, backupCount=1)
    #  handler.setLevel(logging.INFO)
    #  app.logger.setLevel(logging.INFO)
    #  app.logger.addHandler(handler)
    #  app.run(host='0.0.0.0')
