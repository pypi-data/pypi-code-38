from deluge.ui.client import client
from deluge.log import setup_logger
from twisted.internet import reactor
import time
import threading
from crochet import setup as crochet_setup, wait_for, run_in_reactor
setup_logger(level='info')
crochet_setup()

class DelugeClient(object):
    def __init__(self):
        self.__daemon = None
        self.connected = False

    @run_in_reactor
    def connect(self, host='localhost', port=58846, username=None, password=None):
        def on_connect(version):
            print('Successfully connected. Daemon version:', version)
            self.connected = True
        def on_failure(result):
            print('Failed to connect to daemon:', result)
            pass
        self.__daemon = client.connect(host=host, port=port, username=username, password=password)

    @wait_for(timeout=5.0)
    def get_torrents(self):
        return client.core.get_torrents_status({}, [])

    @wait_for(timeout=5.0)
    def get_torrent_status(self, torrent_id):
        return client.core.get_torrent_status(torrent_id, {})

    @wait_for(timeout=5.0)
    def add_torrent_url(self, url, options):
        if url.startswith('magnet:'):
            return client.core.add_torrent_magnet(url, options)
        else:
            return client.core.add_torrent_url(url, options)

    @wait_for(timeout=5.0)
    def add_torrent_file(self, filename, file, options):
        return client.core.add_torrent_file(filename, file, options)

    @wait_for(timeout=5.0)
    def pause_torrents(self, torrents):
        return client.core.pause_torrent(torrents)

    @wait_for(timeout=5.0)
    def resume_torrents(self, torrents):
        return client.core.resume_torrent(torrents)

    @wait_for(timeout=5.0)
    def remove_torrent(self, torrent, remove_data):
        return client.core.remove_torrent(torrent, remove_data)

    @wait_for(timeout=5.0)
    def get_session_status(self, keys):
        return client.core.get_session_status(keys)

delugeclient = DelugeClient()
delugeclient.connect()
