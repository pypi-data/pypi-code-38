from app import app
from torrent.client import delugeclient
import json
from flask import request, render_template

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/connect')
def test():
   delugeclient.connect() 
   return 'success'

@app.route('/api/session', methods=['GET'])
def session_status():
    keys = ['download_rate', 'upload_rate']
    return json.dumps(delugeclient.get_session_status(keys))

@app.route('/api/torrents', methods=['GET'])
def torrents():
    torrents = delugeclient.get_torrents()
    return json.dumps(torrents)

@app.route('/api/torrents', methods=['POST'])
def upload_torrent():
    body = request.get_json()
    options = body.get('options', {})
    if body.get('url'):
        url = body.get('url')
        delugeclient.add_torrent_url(url, options)
    elif body.get('filename') and body.get('file'):
        filename = body.get('filename')
        file = body.get('file')
        delugeclient.add_torrent_file(filename, file, options)
    return json.dumps({ 'success': True })



@app.route('/api/torrents/<string:torrent_id>', methods=['GET'])
def torrent_status(torrent_id):
    result = delugeclient.get_torrent_status(torrent_id)
    return json.dumps(result)

@app.route('/api/torrents/<string:torrent_id>', methods=['DELETE'])
def remove_torrent(torrent_id):
    remove_data = True if request.args.get('data').lower() == 'true' else False
    delugeclient.remove_torrent(torrent_id, remove_data)
    return json.dumps({ 'success': True })

@app.route('/api/torrents/<string:torrent_id>/<string:action>')
def control_torrent(torrent_id, action):
    if action == 'pause':
        result = delugeclient.pause_torrents([torrent_id])
    elif action == 'resume':
        result = delugeclient.resume_torrents([torrent_id])
    return json.dumps(result)
