#!flask/bin/python
from flask import Flask, request, jsonify, send_from_directory, abort, make_response
import os
import json
import datetime
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app = Flask(__name__)

now_time = (datetime.datetime.now() - datetime.timedelta(hours=13)).strftime('%Y%m%d')

editors_path = os.path.abspath('..')+"/storage/data/"+now_time+"/"
headlines_path = os.path.abspath('..')+"/storage/data/"+now_time+"/"
image_path = os.path.abspath('..')+"/storage/data/"+now_time+"/"
menu_path = os.path.abspath('..')+"/storage/data/"+now_time+"/"
menu_name = "meta_data.json"
default_image_path = os.path.abspath('..')+"/storage/default/"

editors = []

headlines = []

users = [
    {'username': 'tom', 'password': '111111'},
    {'username': 'michael', 'password': '123456'}
]


@auth.get_password
def get_password(username):
    for user in users:
        if user['username'] == username:
            return user['password']


@app.route('/api/getplaylist/v1/editors', methods=['GET'])
@auth.login_required
def get_editors():
    if os.path.isfile(os.path.join(menu_path, menu_name)):
        with open(os.path.join(menu_path, menu_name), encoding='utf-8') as f:
            try:
                line = f.read()
                temp = json.loads(line)
                global editors
                # editors = temp['editors']
                editors = temp
            finally:
                f.close()
    return jsonify({'playlist': editors})

@app.route('/api/getplaylist/v1/headlines', methods=['GET'])
@auth.login_required
def get_headlines():
    if os.path.isfile(os.path.join(menu_path, menu_name)):
        with open(os.path.join(menu_path, menu_name), encoding='utf-8') as f:
            try:
                line = f.read()
                temp = json.loads(line)
                global headlines
                # headlines = temp['headlines']
                headlines = temp
            finally:
                f.close()
    return jsonify({'playlist': headlines})


@app.route('/api/getaudio/v1/<string:file_name>', methods=['GET'])
@auth.login_required
def get_task(file_name):
    task = filter(lambda t: t['filename'] == file_name, editors)
    newlist = list(task)
    if len(newlist) == 0:
        abort(404)
    return jsonify({'task': newlist[0]})


@app.route('/api/downloadaudio/v1/editors/<string:file_name>', methods=['GET'])
@auth.login_required
def download_editors(file_name):
    if request.method == "GET":
        task = filter(lambda t: t['filename']+".mp3" == file_name, editors)
        newlist = list(task)
        if len(newlist) == 0:
            abort(404)
        filename = newlist[0]['filename']
        if os.path.isfile(os.path.join(editors_path, filename+".mp3")):
            return send_from_directory(editors_path, filename+".mp3", as_attachment=True)
        abort(404)

@app.route('/api/downloadaudio/v1/headlines/<string:file_name>', methods=['GET'])
@auth.login_required
def download_headlines(file_name):
    if request.method == "GET":
        task = filter(lambda t: t['filename']+".mp3" == file_name, headlines)
        newlist = list(task)
        if len(newlist) == 0:
            abort(404)
        filename = newlist[0]['filename']
        if os.path.isfile(os.path.join(headlines_path, filename+".mp3")):
            return send_from_directory(headlines_path, filename+".mp3", as_attachment=True)
        abort(404)

# show photo
@app.route('/api/show/image/<string:filename>', methods=['GET'])
@auth.login_required
def show_photo(filename):
    if request.method == 'GET':
        if filename is None:
            abort(404)
        else:
            image_data = open(os.path.join(image_path, filename+".jpg"), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        abort(404)

@app.route('/api/download/image/v1/<string:file_name>', methods=['GET'])
@auth.login_required
def download_image(file_name):
    if request.method == "GET":
        task = filter(lambda t: t['filename'] == file_name, headlines)
        newlist = list(task)
        if len(newlist) == 0:
            abort(404)
        filename = newlist[0]['filename']
        temp_str = filename + ".jpg"
        if os.path.isfile(os.path.join(image_path, temp_str)):
            return send_from_directory(image_path, temp_str, as_attachment=True)
        abort(404)

@app.route('/api/download/default/image/v1/<string:file_name>', methods=['GET'])
@auth.login_required
def download_default_image(file_name):
    if request.method == "GET":
        temp_str = file_name
        if os.path.isfile(os.path.join(default_image_path, temp_str)):
            return send_from_directory(default_image_path, temp_str, as_attachment=True)
        abort(404)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

if __name__ == '__main__':
    app.run(debug=True)


