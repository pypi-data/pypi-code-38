# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Pre-processing operations based on NDVars"""
from collections import Sequence
from copy import deepcopy
import fnmatch
from os import makedirs, remove
from os.path import basename, dirname, exists, getmtime, join, splitext

import mne
from scipy import signal

from .. import load
from .._data_obj import NDVar
from .._exceptions import DefinitionError
from .._io.fiff import KIT_NEIGHBORS
from .._ndvar import filter_data
from .._text import enumeration
from .._utils import as_sequence, ask, user_activity
from ..mne_fixes import CaptureLog
from .definitions import compound, typed_arg
from .exceptions import FileMissing


def _visit(recording: str) -> str:
    # visit field from recording compound
    if ' ' in recording:
        _, visit = recording.split(' ')
        return visit
    else:
        return ''


class RawPipe:

    def _can_link(self, pipes):
        raise NotImplementedError

    def _link(self, name, pipes, root, raw_dir, cache_dir, log):
        raise NotImplementedError

    def _link_base(self, name, path, root, log):
        out = deepcopy(self)
        out.name = name
        out.path = path
        out.root = root
        out.log = log
        return out

    def as_dict(self):
        return {'type': self.__class__.__name__, 'name': self.name}

    def cache(self, subject, recording):
        "Make sure the file exists and is up to date"
        raise NotImplementedError

    def get_connectivity(self, data):
        raise NotImplementedError

    def get_sysname(self, info, subject, data):
        raise NotImplementedError

    def load(self, subject, recording, add_bads=True, preload=False, raw=None):
        # raw
        if raw is None:
            raw = self._load(subject, recording, preload)
        # bad channels
        if isinstance(add_bads, Sequence):
            raw.info['bads'] = list(add_bads)
        elif add_bads:
            raw.info['bads'] = self.load_bad_channels(subject, recording)
        else:
            raw.info['bads'] = []
        return raw

    def _load(self, subject, recording, preload):
        path = self.path.format(root=self.root, subject=subject, recording=recording)
        return mne.io.read_raw_fif(path, preload=preload)

    def load_bad_channels(self, subject, recording):
        raise NotImplementedError

    def make_bad_channels(self, subject, recording, bad_chs, redo):
        raise NotImplementedError

    def make_bad_channels_auto(self, subject, recording, flat):
        raise NotImplementedError

    def mtime(self, subject, recording, bad_chs=True):
        "Modification time of anything influencing the output of load"
        raise NotImplementedError


class RawSource(RawPipe):
    """Raw data source

    Parameters
    ----------
    filename : str
        Pattern for filenames. The pattern should contain the fields
        ``{subject}`` and ``{recording}`` (which internally is expanded to
        ``session`` and, if applicable, ``visit``;
        default ``'{subject}_{recording}-raw.fif'``).
    reader : callable
        Function for reading data (default is :func:`mne.io.read_raw_fif`).
    sysname : str
        Used to determine sensor positions (not needed for KIT files, or when a
        montage is specified).
    rename_channels : dict
        Rename channels before applying montage, ``{from: to}`` dictionary;
        useful to convert idiosyncratic naming conventions to standard montages.
    montage : str
        Name of a montage that is applied to raw data to set sensor positions.
    connectivity : str | list of (str, str)
        Connectivity between sensors. Can be specified as:

        - list of connections (e.g., ``[('OZ', 'O1'), ('OZ', 'O2'), ...]``)
        - :class:`numpy.ndarray` of int, shape (n_edges, 2), to specify
          connections in terms of indices. Each row should specify one
          connection [i, j] with i < j. If the array's dtype is uint32,
          property checks are disabled to improve efficiency.
        - ``"grid"`` to use adjacency in the sensor names

        If unspecified, it is inferred from ``sysname`` if possible.
    ...
        Additional parameters for the ``reader`` function.
    """
    _dig_sessions = None  # {subject: {for_recording: use_recording}}

    def __init__(self, filename='{subject}_{recording}-raw.fif', reader=mne.io.read_raw_fif, sysname=None, rename_channels=None, montage=None, connectivity=None, **kwargs):
        RawPipe.__init__(self)
        self.filename = typed_arg(filename, str)
        self.reader = reader
        self.sysname = sysname
        self.rename_channels = typed_arg(rename_channels, dict)
        self.montage = typed_arg(montage, str)
        self.connectivity = connectivity
        self._kwargs = kwargs
        if reader is mne.io.read_raw_cnt:
            self._read_raw_kwargs = {'montage': None, **kwargs}
        else:
            self._read_raw_kwargs = kwargs

    def _can_link(self, pipes):
        return True

    def _link(self, name, pipes, root, raw_dir, cache_dir, log):
        if name != 'raw':
            raise NotImplementedError("RawSource with name {name!r}: the raw source must be called 'raw'")
        path = join(raw_dir, self.filename)
        if self.filename.endswith('-raw.fif'):
            head = path[:-8]
        else:
            head = splitext(path)[0]
        out = RawPipe._link_base(self, name, path, root, log)
        out.bads_path = head + '-bad_channels.txt'
        return out

    def as_dict(self):
        out = RawPipe.as_dict(self)
        out.update(self._kwargs)
        if self.reader != mne.io.read_raw_fif:
            out['reader'] = self.reader.__name__
        if self.rename_channels:
            out['rename_channels'] = self.rename_channels
        if self.montage:
            out['montage'] = self.montage
        if self.connectivity is not None:
            out['connectivity'] = self.connectivity
        return out
    
    def _load(self, subject, recording, preload):
        path = self.path.format(root=self.root, subject=subject, recording=recording)
        raw = self.reader(path, preload=preload, **self._read_raw_kwargs)
        if self.rename_channels:
            raw.rename_channels(self.rename_channels)
        if self.montage:
            raw.set_montage(self.montage)
        if raw.info['dig'] is None and self._dig_sessions is not None:
            dig_session = self._dig_sessions[subject][recording]
            dig_raw = self._load(subject, dig_session, False)
            raw.info['dig'] = dig_raw.info['dig']
        return raw

    def cache(self, subject, recording):
        "Make sure the file exists and is up to date"
        path = self.path.format(root=self.root, subject=subject, recording=recording)
        if not exists(path):
            raise FileMissing(f"Raw input file for {subject}/{recording} does not exist at expected location {path}")
        return path

    def get_connectivity(self, data):
        if data == 'eog':
            return None
        else:
            return self.connectivity

    def get_sysname(self, info, subject, data):
        if data == 'eog':
            return None
        elif data == 'mag':
            kit_system_id = info.get('kit_system_id')
            if kit_system_id:
                try:
                    return KIT_NEIGHBORS[kit_system_id]
                except KeyError:
                    raise NotImplementedError(f"Unknown KIT system-ID: {kit_system_id}; please contact developers")
        if isinstance(self.sysname, str):
            return self.sysname
        elif isinstance(self.sysname, dict):
            for k, v in self.sysname.items():
                if fnmatch.fnmatch(subject, k):
                    return v
        elif self.connectivity is None:
            raise RuntimeError(f"Unknown sensor configuration for {subject}, data={data!r}. Consider setting connectivity or sysname explicitly.")

    def load_bad_channels(self, subject, recording):
        path = self.bads_path.format(root=self.root, subject=subject, recording=recording)
        if not exists(path):
            # need to create one to know mtime after user deletes the file
            self.log.info("Generating bad_channels file for %s %s", subject, recording)
            self.make_bad_channels_auto(subject, recording)
        with open(path) as fid:
            return [l for l in fid.read().splitlines() if l]

    def make_bad_channels(self, subject, recording, bad_chs, redo):
        path = self.bads_path.format(root=self.root, subject=subject, recording=recording)
        if exists(path):
            old_bads = self.load_bad_channels(subject, recording)
        else:
            old_bads = None
        # find new bad channels
        if isinstance(bad_chs, (str, int)):
            bad_chs = (bad_chs,)
        raw = self.load(subject, recording, add_bads=False)
        sensor = load.fiff.sensor_dim(raw)
        new_bads = sensor._normalize_sensor_names(bad_chs)
        # update with old bad channels
        if old_bads is not None and not redo:
            new_bads = sorted(set(old_bads).union(new_bads))
        # print change
        print(f"{old_bads} -> {new_bads}")
        if new_bads == old_bads:
            return
        # write new bad channels
        text = '\n'.join(new_bads)
        with open(path, 'w') as fid:
            fid.write(text)

    def make_bad_channels_auto(self, subject, recording, flat=1e-14, redo=False):
        if not flat:
            return
        raw = self.load(subject, recording, preload=True, add_bads=False)
        raw = load.fiff.raw_ndvar(raw)
        bad_chs = raw.sensor.names[raw.std('time') < flat]
        self.make_bad_channels(subject, recording, bad_chs, redo)

    def mtime(self, subject, recording, bad_chs=True):
        path = self.path.format(root=self.root, subject=subject, recording=recording)
        if exists(path):
            mtime = getmtime(path)
            if not bad_chs:
                return mtime
            path = self.bads_path.format(root=self.root, subject=subject, recording=recording)
            if exists(path):
                return max(mtime, getmtime(path))


class CachedRawPipe(RawPipe):

    _bad_chs_affect_cache = False

    def __init__(self, source, cache=True):
        RawPipe.__init__(self)
        self._source_name = source
        self._cache = cache

    def _can_link(self, pipes):
        return self._source_name in pipes

    def _link(self, name, pipes, root, raw_dir, cache_path, log):
        path = cache_path.format(root='{root}', raw=name, subject='{subject}', recording='{recording}')
        if self._source_name not in pipes:
            raise DefinitionError(f"{self.__class__.__name__} {name!r} source {self._source_name!r} does not exist")
        out = RawPipe._link_base(self, name, path, root, log)
        out.source = pipes[self._source_name]
        return out

    def as_dict(self):
        out = RawPipe.as_dict(self)
        out['source'] = self._source_name
        return out

    def cache(self, subject, recording):
        "Make sure the cache is up to date"
        path = self.path.format(root=self.root, subject=subject, recording=recording)
        if exists(path):
            mtime = self.mtime(subject, recording, self._bad_chs_affect_cache)
            if mtime and getmtime(path) >= mtime:
                return
        from .. import __version__
        # make sure the target directory exists
        makedirs(dirname(path), exist_ok=True)
        # generate new raw
        with CaptureLog(path[:-3] + 'log') as logger:
            logger.info(f"eelbrain {__version__}")
            logger.info(f"mne {mne.__version__}")
            logger.info(repr(self.as_dict()))
            raw = self._make(subject, recording)
        # save
        try:
            raw.save(path, overwrite=True)
        except:
            # clean up potentially corrupted file
            if exists(path):
                remove(path)
            raise
        return raw

    def get_connectivity(self, data):
        return self.source.get_connectivity(data)

    def get_sysname(self, info, subject, data):
        return self.source.get_sysname(info, subject, data)

    def load(self, subject, recording, add_bads=True, preload=False, raw=None):
        if raw is not None:
            pass
        elif self._cache:
            raw = self.cache(subject, recording)
        else:
            raw = self._make(subject, recording)
        if not isinstance(raw, mne.io.Raw):
            raw = None  # only propagate fiff raw for appending
        return RawPipe.load(self, subject, recording, add_bads, preload, raw)

    def load_bad_channels(self, subject, recording):
        return self.source.load_bad_channels(subject, recording)

    def _make(self, subject, recording):
        raise NotImplementedError

    def make_bad_channels(self, subject, recording, bad_chs, redo):
        self.source.make_bad_channels(subject, recording, bad_chs, redo)

    def make_bad_channels_auto(self, *args, **kwargs):
        self.source.make_bad_channels_auto(*args, **kwargs)

    def mtime(self, subject, recording, bad_chs=True):
        return self.source.mtime(subject, recording, bad_chs or self._bad_chs_affect_cache)


class RawFilter(CachedRawPipe):
    """Filter raw pipe

    Parameters
    ----------
    source : str
        Name of the raw pipe to use for input data.
    ...
        :meth:`mne.io.Raw.filter` parameters.
    """

    def __init__(self, source, l_freq=None, h_freq=None, **kwargs):
        CachedRawPipe.__init__(self, source)
        self.args = (l_freq, h_freq)
        self.kwargs = kwargs
        # mne backwards compatibility (fir_design default change 0.15 -> 0.16)
        if 'use_kwargs' in kwargs:
            self._use_kwargs = kwargs.pop('use_kwargs')
        else:
            self._use_kwargs = kwargs

    def as_dict(self):
        out = CachedRawPipe.as_dict(self)
        out['args'] = self.args
        out['kwargs'] = self.kwargs
        return out

    def filter_ndvar(self, ndvar):
        return filter_data(ndvar, *self.args, **self._use_kwargs)

    def _make(self, subject, recording):
        raw = self.source.load(subject, recording, preload=True)
        self.log.info("Raw %s: filtering for %s/%s...", self.name, subject, recording)
        raw.filter(*self.args, **self._use_kwargs)
        return raw


class RawFilterElliptic(CachedRawPipe):

    def __init__(self, source, low_stop, low_pass, high_pass, high_stop, gpass, gstop):
        CachedRawPipe.__init__(self, source)
        self.args = (low_stop, low_pass, high_pass, high_stop, gpass, gstop)

    def as_dict(self):
        out = CachedRawPipe.as_dict(self)
        out['args'] = self.args
        return out

    def _sos(self, sfreq):
        nyq = sfreq / 2.
        low_stop, low_pass, high_pass, high_stop, gpass, gstop = self.args
        if high_stop is None:
            assert low_stop is not None
            assert high_pass is None
        else:
            high_stop /= nyq
            high_pass /= nyq

        if low_stop is None:
            assert low_pass is None
        else:
            low_pass /= nyq
            low_stop /= nyq

        if low_stop is None:
            btype = 'lowpass'
            wp, ws = high_pass, high_stop
        elif high_stop is None:
            btype = 'highpass'
            wp, ws = low_pass, low_stop
        else:
            btype = 'bandpass'
            wp, ws = (low_pass, high_pass), (low_stop, high_stop)
        order, wn = signal.ellipord(wp, ws, gpass, gstop)
        return signal.ellip(order, gpass, gstop, wn, btype, output='sos')

    def filter_ndvar(self, ndvar):
        axis = ndvar.get_axis('time')
        sos = self._sos(1. / ndvar.time.tstep)
        x = signal.sosfilt(sos, ndvar.x, axis)
        return NDVar(x, ndvar.dims, ndvar.info.copy(), ndvar.name)

    def _make(self, subject, recording):
        raw = self.source.load(subject, recording, preload=True)
        self.log.info("Raw %s: filtering for %s/%s...", self.name, subject, recording)
        # filter data
        picks = mne.pick_types(raw.info, eeg=True, ref_meg=True)
        sos = self._sos(raw.info['sfreq'])
        for i in picks:
            raw._data[i] = signal.sosfilt(sos, raw._data[i])
        # update info
        low, high = self.args[1], self.args[2]
        if high and raw.info['lowpass'] > high:
            raw.info['lowpass'] = float(high)
        if low and raw.info['highpass'] < low:
            raw.info['highpass'] = float(low)
        return raw


class RawICA(CachedRawPipe):
    """ICA raw pipe

    Parameters
    ----------
    source : str
        Name of the raw pipe to use for input data.
    session : str | sequence of str
        Session(s) to use for estimating ICA components.
    method : str
        Method for ICA decomposition (default: ``'extended-infomax'``; see
        :class:`mne.preprocessing.ICA`).
    random_state : int
        Set the random state for ICA decomposition to make results reproducible
        (default 0, see :class:`mne.preprocessing.ICA`).
    cache : bool
        Cache the resulting raw files (default False).
    ...
        Additional parameters for :class:`mne.preprocessing.ICA`.

    Notes
    -----
    This preprocessing step estimates one set of ICA components per subject,
    using the data specified in the ``session`` parameter. The selected
    components are then removed from all data sessions during this preprocessing
    step, regardless of whether they were used to estimate the components or
    not.

    Use :meth:`~eelbrain.MneExperiment.make_ica_selection` for each subject to
    select ICA components that should be removed. The arguments to that function
    determine what data is used to visualize the component time courses.
    For example, to determine which components load strongly on empty room data,
    use ``e.make_ica_selection(session='emptyroom')`` (assuming an
    ``'emptyroom'`` session is present).

    This step merges bad channels from all sessions.
    """

    def __init__(self, source, session, method='extended-infomax', random_state=0, cache=False, **kwargs):
        CachedRawPipe.__init__(self, source, cache)
        if isinstance(session, str):
            session = (session,)
        else:
            if not isinstance(session, tuple):
                session = tuple(session)
            assert all(isinstance(s, str) for s in session)
        self.session = session
        self.kwargs = {'method': method, 'random_state': random_state, **kwargs}

    def _link(self, name, pipes, root, raw_dir, cache_path, log):
        out = CachedRawPipe._link(self, name, pipes, root, raw_dir, cache_path, log)
        out.ica_path = join(raw_dir, f'{{subject_visit}} {name}-ica.fif')
        return out

    def as_dict(self):
        out = CachedRawPipe.as_dict(self)
        out['session'] = self.session
        out['kwargs'] = self.kwargs
        return out

    def load_bad_channels(self, subject, recording):
        visit = _visit(recording)
        bad_chs = set()
        for session in self.session:
            recording = compound((session, visit))
            bad_chs.update(self.source.load_bad_channels(subject, recording))
        return sorted(bad_chs)

    def load_ica(self, subject, recording):
        visit = _visit(recording)
        path = self._ica_path(subject, visit)
        if not exists(path):
            raise RuntimeError(f"ICA file {basename(path)} does not exist for raw={self.name!r}. Run e.make_ica_selection() to create it.")
        return mne.preprocessing.read_ica(path)

    @staticmethod
    def _check_ica_channels(ica, raw):
        picks = mne.pick_types(raw.info, eeg=True, ref_meg=False)
        return ica.ch_names == [raw.ch_names[i] for i in picks]

    def load_concatenated_source_raw(self, subject, session, visit):
        sessions = as_sequence(session)
        recordings = [compound((session, visit)) for session in sessions]
        bad_channels = self.load_bad_channels(subject, recordings[0])
        raw = self.source.load(subject, recordings[0], False)
        raw.info['bads'] = bad_channels
        for recording in recordings[1:]:
            raw_ = self.source.load(subject, recording, False)
            raw_.info['bads'] = bad_channels
            raw.append(raw_)
        return raw

    def make_ica(self, subject, visit):
        path = self._ica_path(subject, visit)
        recordings = [compound((session, visit)) for session in self.session]
        raw = self.source.load(subject, recordings[0], False)
        bad_channels = self.load_bad_channels(subject, recordings[0])
        raw.info['bads'] = bad_channels
        if exists(path):
            ica = mne.preprocessing.read_ica(path)
            if not self._check_ica_channels(ica, raw):
                self.log.info("Raw %s: ICA outdated due to change in bad channels for %s", self.name, subject)
            else:
                mtimes = [self.source.mtime(subject, recording, self._bad_chs_affect_cache) for recording in recordings]
                if all(mtimes) and getmtime(path) > max(mtimes):
                    return path
                # ICA file is newer than raw
                command = ask(f"The input for the ICA of {subject} seems to have changed since the ICA was generated.", [('delete', 'delete and recompute the ICA'), ('ignore', 'Keep using the old ICA')], help="This message indicates that the modification date of the raw input data or of the bad channels file is more recent than that of the ICA file. If the data actually changed, ICA components might not be valid anymore and should be recomputed. If the change is spurious (e.g., the raw file was modified in a way that does not affect the ICA) load and resave the ICA file to stop seeing this message.")
                if command == 'ignore':
                    return path
                elif command == 'delete':
                    remove(path)
                else:
                    raise RuntimeError(f"command={command!r}")

        for session in self.session[1:]:
            recording = compound((session, visit))
            raw_ = self.source.load(subject, recording, False)
            raw_.info['bads'] = bad_channels
            raw.append(raw_)

        self.log.info("Raw %s: computing ICA decomposition for %s", self.name, subject)
        kwargs = self.kwargs if 'max_iter' in self.kwargs else {'max_iter': 256, **self.kwargs}
        ica = mne.preprocessing.ICA(**kwargs)
        # reject presets from meeg-preprocessing
        with user_activity:
            ica.fit(raw, reject={'mag': 5e-12, 'grad': 5000e-13, 'eeg': 300e-6})
        ica.save(path)
        return path

    def _make(self, subject, recording):
        raw = self.source.load(subject, recording, preload=True)
        raw.info['bads'] = self.load_bad_channels(subject, recording)
        ica = self.load_ica(subject, recording)
        if not self._check_ica_channels(ica, raw):
            raise RuntimeError(f"Raw {self.name}, ICA for {subject} outdated due to change in bad channels. Reset bad channels or re-run .make_ica().")
        self.log.debug("Raw %s: applying ICA for %s/%s...", self.name, subject, recording)
        ica.apply(raw)
        return raw

    def mtime(self, subject, recording, bad_chs=True):
        mtime = CachedRawPipe.mtime(self, subject, recording, bad_chs or self._bad_chs_affect_cache)
        if mtime:
            path = self._ica_path(subject, recording=recording)
            if exists(path):
                return max(mtime, getmtime(path))

    def _ica_path(self, subject, visit=None, recording=None):
        if recording:
            visit = _visit(recording)
        return self.ica_path.format(root=self.root, subject=subject, subject_visit=compound((subject, visit)))


class RawApplyICA(CachedRawPipe):
    """Apply ICA estimated in a :class:`RawICA` pipe

    Parameters
    ----------
    source : str
        Name of the raw pipe to use for input data.
    ica : str
        Name of the :class:`RawICA` pipe from which to load the ICA components.

    Notes
    -----
    This pipe inherits bad channels from the ICA.

    Examples
    --------
    Estimate ICA components with 1-40 Hz band-pass filter and apply the ICA
    to data that is high pass filtered at 0.1 Hz::

        class Experiment(MneExperiment):

            raw = {
                '1-40': RawFilter('raw', 1, 40),
                'ica': RawICA('1-40', 'session', 'extended-infomax', n_components=0.99),
                '0.1-40': RawFilter('raw', 0.1, 40),
                '0.1-40-ica': RawApplyICA('0.1-40', 'ica'),
            }

    """

    def __init__(self, source, ica, cache=False):
        CachedRawPipe.__init__(self, source, cache)
        self._ica_source = ica

    def _can_link(self, pipes):
        return CachedRawPipe._can_link(self, pipes) and self._ica_source in pipes

    def _link(self, name, pipes, root, raw_dir, cache_path, log):
        out = CachedRawPipe._link(self, name, pipes, root, raw_dir, cache_path, log)
        out.ica_source = pipes[self._ica_source]
        return out

    def as_dict(self):
        out = CachedRawPipe.as_dict(self)
        out['ica_source'] = self._ica_source
        return out

    def load_bad_channels(self, subject, recording):
        return self.ica_source.load_bad_channels(subject, recording)

    def _make(self, subject, recording):
        raw = self.source.load(subject, recording, preload=True)
        raw.info['bads'] = self.load_bad_channels(subject, recording)
        ica = self.ica_source.load_ica(subject, recording)
        if not self.ica_source._check_ica_channels(ica, raw):
            raise RuntimeError(f"Raw {self.name}, ICA for {subject} outdated due to change in bad channels. Reset bad channels or re-run .make_ica().")
        self.log.debug("Raw %s: applying ICA for %s/%s...", self.name, subject, recording)
        ica.apply(raw)
        return raw

    def mtime(self, subject, recording, bad_chs=True):
        mtime = CachedRawPipe.mtime(self, subject, recording, bad_chs)
        if mtime:
            ica_mtime = self.ica_source.mtime(subject, recording, bad_chs)
            if ica_mtime:
                return max(mtime, ica_mtime)


class RawMaxwell(CachedRawPipe):
    """Maxwell filter raw pipe

    Parameters
    ----------
    source : str
        Name of the raw pipe to use for input data.
    session : str | sequence of str
        Session(s) to use for estimating ICA components.
    ...
        :func:`mne.preprocessing.maxwell_filter` parameters.
    """

    _bad_chs_affect_cache = True

    def __init__(self, source, **kwargs):
        CachedRawPipe.__init__(self, source)
        self.kwargs = kwargs

    def as_dict(self):
        out = CachedRawPipe.as_dict(self)
        out['kwargs'] = self.kwargs
        return out

    def _make(self, subject, recording):
        raw = self.source.load(subject, recording)
        self.log.info("Raw %s: computing Maxwell filter for %s/%s", self.name, subject, recording)
        with user_activity:
            return mne.preprocessing.maxwell_filter(raw, **self.kwargs)


class RawReReference(CachedRawPipe):
    """Re-reference EEG data

    Parameters
    ----------
    source : str
        Name of the raw pipe to use for input data.
    reference : str | sequence of str
        New reference: ``'average'`` (default) or one or several electrode
        names.
    """

    def __init__(self, source, reference='average'):
        CachedRawPipe.__init__(self, source, False)
        if not isinstance(reference, str):
            reference = list(reference)
            if not all(isinstance(ch, str) for ch in reference):
                raise TypeError(f"reference={reference}: must be list of str")
        self.reference = reference

    def as_dict(self):
        out = CachedRawPipe.as_dict(self)
        out['reference'] = self.reference
        return out

    def _make(self, subject, recording):
        raw = self.source.load(subject, recording, preload=True)
        raw.set_eeg_reference(self.reference)
        return raw


def assemble_pipeline(raw_dict, raw_dir, cache_path, root, sessions, log):
    "Assemble preprocessing pipeline form a definition in a dict"
    # convert to Raw objects
    raw = {}
    for key, raw_def in raw_dict.items():
        if not isinstance(raw_def, RawPipe):
            params = {**raw_def}
            source = params.pop('source', None)
            if source is None:
                raw_def = RawSource(**params)
            else:
                pipe_type = params.pop('type')
                kwargs = params.pop('kwargs', {})
                if pipe_type == 'filter':
                    if 'fir_design' not in kwargs:
                        kwargs = {**kwargs, 'use_kwargs': {**kwargs, 'fir_design': 'firwin2'}}
                    raw_def = RawFilter(source, *params.pop('args', ()), **kwargs)
                elif pipe_type == 'ica':
                    raw_def = RawICA(source, params.pop('session'), **kwargs)
                elif pipe_type == 'maxwell_filter':
                    raw_def = RawMaxwell(source, **kwargs)
                else:
                    raise DefinitionError(f"Raw {key!r}: unknonw type {pipe_type!r}")
                if params:
                    raise DefinitionError(f"Unused parameters in raw definition {key!r}: {raw_def}")
        raw[key] = raw_def
    n_source = sum(isinstance(p, RawSource) for p in raw.values())
    if n_source == 0:
        raise DefinitionError("No RawSource pipe")
    elif n_source > 1:
        raise NotImplementedError("More than one RawSource pipes")
    # link sources
    linked_raw = {}
    while raw:
        n = len(raw)
        for key in list(raw):
            if raw[key]._can_link(linked_raw):
                pipe = raw.pop(key)._link(key, linked_raw, root, raw_dir, cache_path, log)
                if isinstance(pipe, RawICA):
                    missing = set(pipe.session).difference(sessions)
                    if missing:
                        raise DefinitionError(f"RawICA {key!r} lists one or more non-exising sessions: {', '.join(missing)}")
                linked_raw[key] = pipe
        if len(raw) == n:
            raise DefinitionError(f"Unable to resolve source for raw {enumeration(raw)}, circular dependency?")
    return linked_raw


###############################################################################
# Comparing pipelines
######################


def compare_pipelines(old, new, log):
    """Return a tuple of raw keys for which definitions changed

    Parameters
    ----------
    old : {str: dict}
        A {name: params} dict for the previous preprocessing pipeline.
    new : {str: dict}
        Current pipeline.
    log : logger
        Logger for logging changes.

    Returns
    -------
    bad_raw : {str: str}
        ``{pipe_name: status}`` dictionary. Status can be 'new', 'removed' or
        'changed'.
    bad_ica : {str: str}
        Same as ``bad_raw`` but only for RawICA pipes (for which ICA files
        might have to be removed).
    """
    # status:  good, changed, new, removed, secondary
    out = {k: 'new' for k in new if k not in old}
    out.update({k: 'removed' for k in old if k not in new})

    # parameter changes
    to_check = set(new) - set(out)
    for key in tuple(to_check):
        if new[key] != old[key]:
            log.debug("  raw changed: %s %s -> %s", key, old[key], new[key])
            out[key] = 'changed'
            to_check.remove(key)

    # does not need to be checked for source
    if 'raw' in to_check:
        to_check.remove('raw')
        out['raw'] = 'good'

    # secondary changes
    while to_check:
        n = len(to_check)
        for key in tuple(to_check):
            parents = [new[key][k] for k in ('source', 'ica_source') if k in new[key]]
            if any(p not in out for p in parents):
                continue
            elif all(out[p] == 'good' for p in parents):
                out[key] = 'good'
            else:
                out[key] = 'secondary'
            to_check.remove(key)
        if len(to_check) == n:
            raise RuntimeError("Queue not decreasing")

    bad_raw = {k: v for k, v in out.items() if v != 'good'}
    bad_ica = {k: v for k, v in bad_raw.items() if new.get(k, old.get(k))['type'] == 'RawICA'}
    return bad_raw, bad_ica


def ask_to_delete_ica_files(raw, status, filenames):
    "Ask whether outdated ICA files should be removed and act accordingly"
    if status == 'new':
        msg = ("The definition for raw=%r has been added, but ICA-files "
               "already exist. These files might not correspond to the new "
               "settings and should probably be deleted." % (raw,))
    elif status == 'removed':
        msg = ("The definition for raw=%r has been removed. The corresponsing "
               "ICA files should probably be deleted:" % (raw,))
    elif status == 'changed':
        msg = ("The definition for raw=%r has changed. The corresponding ICA "
               "files should probably be deleted." % (raw,))
    else:
        raise RuntimeError("status=%r" % (status,))
    command = ask(
        "%s Delete %i files?" % (msg, len(filenames)),
        (('abort', 'abort to fix the raw definition and try again'),
         ('delete', 'delete the invalid fils'),
         ('ignore', 'pretend that the files are valid; you will not be warned again')))

    if command == 'delete':
        for filename in filenames:
            remove(filename)
    elif command == 'abort':
        raise RuntimeError("User abort")
    elif command != 'ignore':
        raise RuntimeError("command=%r" % (command,))
