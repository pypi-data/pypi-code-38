import pytest
from unittest.mock import Mock, MagicMock
from piripherals.util import noop
from piripherals import MPD


_data = []
_rwfile = Mock()


def patch_mock(m):
    global _rwfile
    c = m._mpd
    connect = c._connect_tcp = Mock()
    sock = connect()
    _rwfile = sock.makefile()
    _send('OK MPD 1.2.3\n')


def _send(*x):
    'what shoud send to the client'
    _rwfile.readline.side_effect = x


def _receive(*a, **k):
    'what MPD should recieve from the client'
    _rwfile.write.assert_called_with(*a, **k)


def patch_record(m):
    global _send, _receive, _data
    _send = _receive = noop
    _data = []

    c = m._mpd

    r = c._rfile.readline

    def readline():
        line = r()
        _data.append('< ' + line)
        return line

    c._rfile.readline = readline

    w = c._wfile.write

    def write(x):
        _data.append('> ' + x)
        w(x)

    c._wfile.write = write


@pytest.fixture()
def mpd():
    try:
        m = MPD()
        m.connect('localhost', 6600)
        patch_record(m)
        yield m
        m.disconnect()
    except:  # if connection to a real MPD fails, use mocked protocol replies
        m = MPD()
        patch_mock(m)
        m.connect('localhost', 6600)
        yield m
    finally:
        print(_rwfile.mock_calls)
        for x in _data:
            print(repr(x))


OK = 'OK\n'


def test_mpd_connect(mpd):
    assert mpd.timeout < 10
    assert mpd.idletimeout is None
    _send(OK)
    mpd.status()
    mpd._mpd.disconnect()
    _send('OK MPD foo\n', OK)
    mpd.status()  # fails if it did not reconnect automatically
    _rwfile.write.side_effect = [ConnectionError] + [None] * 10
    _send('OK MPD foo\n',  OK)
    mpd.status()  # fails if it did not reconnect automatically
    _send(ConnectionError, 'OK MPD foo\n', OK)
    mpd.status()  # fails if it did not reconnect automatically


@pytest.mark.xfail(strict=1)
def test_mpd_disconnect(mpd):
    mpd.disconnect()
    mpd.status()  # must fail, because it's disconnected


def test_volume(mpd):
    _send('volume: 10\n', OK)
    v = mpd.volume()
    assert 0 <= v <= 100
    _receive('status\n')

    _send(OK)
    mpd.volume(42)
    _receive('setvol "42"\n')

    _send('volume: 42\n', OK)
    assert mpd.volume() == 42
    _receive('status\n')

    _send('volume: 42\n', OK, OK)
    mpd.volume('+3')
    _receive('setvol "45"\n')

    _send('volume: 45\n', OK)
    assert mpd.volume() == 42 + 3
    _receive('status\n')

    _send('volume: 45\n', OK, OK)
    mpd.volume('-7')
    _receive('setvol "38"\n')

    _send('volume: 38\n', OK)
    assert mpd.volume() == 42 + 3 - 7
    _receive('status\n')


def test_toggle_play(mpd):
    _send(OK)
    mpd.clear()
    _receive('clear\n')

    _send(OK)
    mpd.add('http://89.16.185.174:8003/stream')
    _receive('add "http://89.16.185.174:8003/stream"\n')

    _send('state: stop\n', OK)
    assert mpd.state() == 'stop'
    _receive('status\n')

    _send('state: stop\n', OK, OK)
    mpd.toggle_play()
    _receive('play\n')

    _send('state: play\n', OK)
    assert mpd.state() == 'play'
    _receive('status\n')

    _send('state: play\n', OK, OK)
    mpd.toggle_play()
    _receive('pause\n')

    _send('state: pause\n', OK)
    assert mpd.state() == 'pause'
    _receive('status\n')

    _send('state: pause\n', OK, OK)
    mpd.toggle_play()
    _receive('pause\n')

    _send('state: play\n', OK)
    assert mpd.state() == 'play'
    _receive('status\n')

    _send(OK)
    mpd.stop()
    _receive('stop\n')

    _send('state: stop\n', OK)
    assert mpd.state() == 'stop'
    _receive('status\n')


def test_save_playlist(mpd):
    pl = '#foo#'

    _send('ACK [50@0] {rm} No such playlist\n', OK)
    mpd.save_playlist(pl)
    _receive('save "' + pl + '"\n')

    _send(OK, OK)
    mpd.save_playlist(pl)
    _receive('save "' + pl + '"\n')

    _send('playlist: #foo#\n', OK)
    assert mpd.has_playlist(pl)
    _receive('listplaylists\n')

    _send(OK)
    mpd.del_playlist(pl)
    _receive('rm "' + pl + '"\n')

    _send(OK)
    assert not mpd.has_playlist(pl)
    _receive('listplaylists\n')


def test_load_playlist(mpd):
    pl = '#bar#'

    _send(OK)
    mpd.clear()
    _receive('clear\n')

    _send(OK)
    mpd.add('http://foo')
    _receive('add "http://foo"\n')

    _send(OK)
    mpd.add('http://bar')
    _receive('add "http://bar"\n')

    _send(OK, OK)
    mpd.save_playlist(pl)
    _receive('save "' + pl + '"\n')

    _send(OK)
    mpd.clear()
    _receive('clear\n')

    _send(OK)
    assert not mpd.playlist()
    _receive('playlist\n')

    _send('playlist: #bar#\n', OK, OK, OK)
    mpd.load_playlist(pl)
    _receive('load "' + pl + '"\n')

    _send('0:file: http://foo\n', '1:file: http://bar\n', OK)
    p = mpd.playlist()
    assert len(p) == 2
    _receive('playlist\n')

    _send(OK)
    mpd.del_playlist(pl)
    _receive('rm "' + pl + '"\n')


def test_playlist(mpd):
    _send(OK)
    mpd.clear()
    _receive('clear\n')

    pl = mpd.current_playlist()

    _send('playlistlength: 0\n', OK)
    assert len(pl) == 0
    _receive('status\n')

    urls = ['http://89.16.185.174:8003/stream',
            'http://89.16.185.174:8000/stream',
            'http://89.16.185.174:8004/stream']

    for u in urls:
        _send(OK)
        mpd.add(u)
        _receive('add "' + u + '"\n')

    _send('playlistlength: 3\n', OK)
    assert len(pl) == 3
    _receive('status\n')

    _send('playlistlength: 3\n', OK)
    pl_iter = iter(pl)
    _receive('status\n')

    # with title
    _send('file: ' + urls[0] + '\n', 'Pos: 0\n', 'Title: foo\n', OK)
    song = next(pl_iter)
    _receive('playlistinfo "0"\n')
    assert song['file'] == urls[0]
    assert song['pos'] == '0'
    assert 'title' in song

    # without title
    _send('file: ' + urls[1] + '\n', 'Pos: 1\n',  OK, 'state: stop\n', OK, OK,
          'file: ' + urls[1] + '\n', 'Pos: 1\n', 'Title: bar\n', OK, OK)
    song = next(pl_iter)
    _receive('stop\n')
    assert song['file'] == urls[1]
    assert song['pos'] == '1'
    assert 'title' in song

    # title on second try
    _send('file: ' + urls[2] + '\n', 'Pos: 2\n',  OK, 'state: play\n', 'song: 1\n', OK, OK,
          'file: ' + urls[2] + '\n', 'Pos: 2\n',  OK,
          'file: ' + urls[2] + '\n', 'Pos: 2\n', 'Title: lorem ipsum\n', OK, OK)
    song = next(pl_iter)
    _receive('play "1"\n')
    assert song['file'] == urls[2]
    assert song['pos'] == '2'
    assert 'title' in song

    _send('state: stop\n', OK)
    assert mpd.state() == 'stop'
    _receive('status\n')


def test_playlist_find_next_single_album(mpd):
    _send(OK)
    mpd.clear()
    _receive('clear\n')

    pl = mpd.current_playlist()

    _send('playlistlength: 0\n', OK)
    assert len(pl) == 0
    _receive('status\n')

    urls = ['http://89.16.185.174:8003/stream',
            'http://89.16.185.174:8000/stream',
            'http://89.16.185.174:8004/stream']

    _send(OK, OK, OK)
    for u in urls:
        mpd.add(u)

    _send('state: stop\n', OK,
          'playlistlength: 3\n', OK,
          'Pos: 0\n', 'Album: foo\n', OK,
          'Pos: 1\n', 'Album: foo\n', OK,
          'Pos: 2\n', 'Album: foo\n', OK,
          )
    next = mpd.find_next('album')
    assert next is None


def test_playlist_find_next_two_albums(mpd):
    _send(OK)
    mpd.clear()
    _receive('clear\n')

    pl = mpd.current_playlist()

    _send('playlistlength: 0\n', OK)
    assert len(pl) == 0
    _receive('status\n')

    urls = ['http://89.16.185.174:8003/stream',
            'http://89.16.185.174:8000/stream',
            'http://89.16.185.174:8004/stream']

    _send(OK, OK, OK)
    for u in urls:
        mpd.add(u)

    _send('state: play\n', 'song: 1\n', OK,
          'playlistlength: 3\n', OK,
          'Pos: 1\n', 'Album: foo\n', OK,
          'Pos: 2\n', 'Album: bar\n', OK,
          )
    next = mpd.find_next('album')
    assert next == 2


def test_playlist_find_prev_single_album(mpd):
    _send(OK)
    mpd.clear()
    _receive('clear\n')

    pl = mpd.current_playlist()

    _send('playlistlength: 0\n', OK)
    assert len(pl) == 0
    _receive('status\n')

    urls = ['http://89.16.185.174:8003/stream',
            'http://89.16.185.174:8000/stream',
            'http://89.16.185.174:8004/stream']

    _send(OK, OK, OK)
    for u in urls:
        mpd.add(u)

    _send('state: stop\n', OK,
          'playlistlength: 3\n', OK,
          'Pos: 0\n', 'Album: foo\n', OK,
          'Pos: 1\n', 'Album: foo\n', OK,
          'Pos: 2\n', 'Album: foo\n', OK,
          )
    prev = mpd.find_prev('album')
    assert prev is None


def test_playlist_find_prev_two_albums(mpd):
    _send(OK)
    mpd.clear()
    _receive('clear\n')

    pl = mpd.current_playlist()

    _send('playlistlength: 0\n', OK)
    assert len(pl) == 0
    _receive('status\n')

    urls = ['http://89.16.185.174:8003/stream',
            'http://89.16.185.174:8000/stream',
            'http://89.16.185.174:8004/stream']

    _send(OK, OK, OK)
    for u in urls:
        mpd.add(u)

    _send('state: play\n', 'song: 2\n', OK,
          'playlistlength: 3\n', OK,
          'Pos: 2\n', 'Album: bar\n', OK,
          'Pos: 1\n', 'Album: foo\n', OK,
          'Pos: 0\n', 'Album: foo\n', OK,
          )
    prev = mpd.find_prev('album')
    assert prev == 0


def test_playlist_find_prev_three_albums(mpd):
    _send(OK)
    mpd.clear()
    _receive('clear\n')

    pl = mpd.current_playlist()

    _send('playlistlength: 0\n', OK)
    assert len(pl) == 0
    _receive('status\n')

    urls = ['http://89.16.185.174:8003/stream',
            'http://89.16.185.174:8000/stream',
            'http://89.16.185.174:8004/stream']

    _send(OK, OK, OK)
    for u in urls:
        mpd.add(u)
    _send(OK, OK, OK)
    for u in urls:
        mpd.add(u)

    _send('state: play\n', 'song: 4\n', OK,
          'playlistlength: 3\n', OK,
          'Pos: 4\n', 'Album: bar\n', OK,
          'Pos: 3\n', 'Album: bar\n', OK,
          'Pos: 2\n', 'Album: foo\n', OK,
          'Pos: 1\n', 'Album: foo\n', OK,
          'Pos: 0\n', 'Album: lorem\n', OK,
          )
    prev = mpd.find_prev('album')
    assert prev == 1
