from time import sleep
try:
    from mpd import MPDClient
    from mpd import ConnectionError as MPDConnectionError
    from mpd import CommandError as MPDCommandError
except:
    pass

__all__ = ['MPD', 'MPDPlaylist']


class MPD(object):
    """Wrapper for `MPDClient`_ that adds

    - automatic reconnect on connection loss, see `issue64`_.
    - custom methods
    - volume limit

    It supports all methods of ``MPDClient``.

    Args:
        maxvol (int): volume limit
        *args: args for ``MPDClient``
        **kwargs: kwargs for ``MPDClient``

    .. _MPDClient: https://github.com/Mic92/python-mpd2
    .. _issue64: https://github.com/Mic92/python-mpd2/issues/64
    """

    _mpd = None
    _connect_args = None

    def __init__(self, maxvol=100, *args, **kwargs):
        self._mpd = MPDClient(*args, **kwargs)
        self.maxvol = maxvol
        self.timeout = 5

    def __getattr__(self, name):
        a = getattr(self._mpd, name)
        if not callable(a):
            return a

        def with_reconnect(*args, **kwargs):
            try:
                return a(*args, **kwargs)
            except (MPDConnectionError, ConnectionError, OSError) as e:
                cargs = self._connect_args
                if not cargs:
                    raise
                cargs, ckwargs = cargs
                self.connect(*cargs, **ckwargs)
                return a(*args, **kwargs)

        return with_reconnect

    def __setattr__(self, name, value):
        if hasattr(self._mpd, name):
            setattr(self._mpd, name, value)
        else:
            self.__dict__[name] = value

    def connect(self, *args, **kwargs):
        """establish connection

        disconnects if already connected, host and port are stored,
        will reconnect automatically if connection is lost

        All parameters are passed to ``MPDClient.connect()``.

        Args:
                host (str): hostname/ip/socket
                port (int): port, usually 6600
        """
        self.disconnect()
        self._connect_args = args, kwargs
        self._mpd.connect(*args, **kwargs)

    def disconnect(self):
        """disconnect, disables auto reconnect"""
        try:
            self._connect_args = None
            self._mpd.close()
            self._mpd.disconnect()
        except (MPDConnectionError, ConnectionError) as e:
            pass
        finally:
            self._mpd._reset()

    def volume(self, v=None):
        """adjust volume

        Args:
            v: int = absolute volume 0-100,
                str = absolute volume or relative volume change if prefixed
                with ``+`` or ``-``

        Return:
            int: volume if v was omitted
        """
        if v is not None:
            try:
                if v.startswith('+') or v.startswith('-'):
                    v = self.volume() + int(v)
            except:
                pass
            self.setvol(max(0, min(self.maxvol, v)))
        else:
            return int(self.status()['volume'])

    def state(self):
        """current playback state

        Return:
            str: ``stop``, ``play``, ``pause``
        """
        return self.status()['state']

    def toggle_play(self):
        """play or pause

        - start playing if stopped or paused
        - pause if playing
        """
        if self.state() == 'stop':
            self.play()
        else:
            self.pause()

    def save_playlist(self, name):
        """save current playlist

        if playlist exists, it will be overwritten

        Args:
            name (str): name of the playlist
        """
        self.del_playlist(name)
        self.save(name)

    def del_playlist(self, name):
        """delete playlist

        if playlist exists, this does nothing

        Args:
            name (str): name of the playlist to delete
        """
        try:
            self.rm(name)
        except MPDCommandError:
            pass

    def has_playlist(self, name):
        """check for playlist

        Args:
            name (str): name of the playlist to look for

        Return:
            bool: true if playlist exists
        """
        for i in self.listplaylists():
            if name == i['playlist']:
                return True
        return False

    def load_playlist(self, name):
        """load a playlist

        - replaces current playlist with the named playlist
        - if the given playlist does not exists, this does nothing

        Args:
            name (str): name of the playlist to load
        """
        if self.has_playlist(name):
            self.clear()
            self.load(name)

    def current_playlist(self):
        return MPDPlaylist(self)

    def find_next(self, *a):
        return self.current_playlist().find_next(*a)

    def find_prev(self, *a):
        return self.current_playlist().find_prev(*a)


class MPDPlaylist:
    """the current playlist

    Args:
        mpd (MPD): MPD instance to get the playlist from
        field (str): metadata field to look for when getting metadata for an
            playlist entry. If this field is not present, play the track to
            retrieve the metadata, then switch back to previous state
    """

    def __init__(self, mpd, field='title'):
        self.mpd = mpd
        self.field = field

    def __len__(self):
        """# of songs in the playlist

        Return:
            int: length of playlist
        """
        n = int(self.mpd.status()['playlistlength'])
        #assert n == len(self.mpd.playlist())
        return n

    def __getitem__(self, i):
        return self.get(i, self.field)

    def __iter__(self):
        return (self[i] for i in range(len(self)))

    def get(self, i, field=None):
        """get metadata of playlist entry

        Args:
            i (int): # of playlist entry
            field (str): metadata field to look for, if omitted,
                self.field is used
        """
        info = self.mpd.playlistinfo(i)[0]
        assert int(info['pos']) == i
        info0 = info
        if (field or self.field) not in info:
            status = self.mpd.status()
            k = int(status['song']) if status['state'] != 'stop' else None
            self.mpd.play(i)
            for _ in range(30):
                sleep(0.1)
                info = self.mpd.playlistinfo(i)[0]
                if info != info0:
                    break
            self.mpd.play(k) if k is not None else self.mpd.stop()
        return info

    def find_next(self, field='album'):
        """find next song with different field

        Find the next song, where ``field`` has a different value than the
        currently playing song. With ``field='album'``, this gets the beginning
        of the next album.

        If there is only a single album in the playlist or the currently
        playing song is of the last album, ``None`` is returned.

        Return:
            int: # of playlist entry or None
        """
        status = self.mpd.status()
        i = int(status['song']) if 'song' in status else 0
        n = len(self)
        if n:
            v0 = self.get(i, field).get(field)
            for i in range(i + 1, n):
                v = self.get(i, field).get(field)
                if v != v0:
                    return i

    def find_prev(self, field='album'):
        """find previous song with different field

        Find the previous song, where ``field`` has a different value than the
        currently playing song. With ``field='album'``, this gets the beginning
        of the previous album.

        If there is only a single album in the playlist or the currently
        playing song is of the first album, ``None`` is returned.

        Return:
            int: # of playlist entry or None
        """
        status = self.mpd.status()
        i = int(status['song']) if 'song' in status else 0
        if len(self):
            v0 = self.get(i, field).get(field)
            v1 = None
            for i in range(i - 1, -1, -1):
                v = self.get(i, field).get(field)
                if v1 is None and v != v0:
                    v1 = v
                if v1 and v != v1:
                    return i + 1
            if v1:
                return i
