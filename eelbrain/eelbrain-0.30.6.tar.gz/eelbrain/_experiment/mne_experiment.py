# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""MneExperiment class to manage data from a experiment

For testing purposed, set up an experiment class without checking for data:

MneExperiment.auto_delete_cache = 'disable'
MneExperiment.sessions = ('session',)
e = MneExperiment('.', find_subjects=False)

"""
from collections import defaultdict, Sequence
from datetime import datetime
from glob import glob
import inspect
from itertools import chain, product
import logging
import os
from os.path import basename, exists, getmtime, isdir, join, relpath
from pathlib import Path
import re
import shutil
import time
import warnings

import numpy as np

import mne
from mne.baseline import rescale
from mne.minimum_norm import make_inverse_operator, apply_inverse, apply_inverse_epochs

from .. import _report
from .. import fmtxt
from .. import gui
from .. import load
from .. import plot
from .. import save
from .. import table
from .. import testnd
from .._data_obj import (
    Datalist, Dataset, Factor, Var, SourceSpace, VolumeSourceSpace,
    align1, all_equal, assert_is_legal_dataset_key, combine)
from .._exceptions import DefinitionError, DimensionMismatchError, OldVersionError
from .._info import BAD_CHANNELS
from .._io.pickle import update_subjects_dir
from .._names import INTERPOLATE_CHANNELS
from .._meeg import new_rejection_ds
from .._mne import (
    dissolve_label, labels_from_mni_coords, rename_label, combination_label,
    morph_source_space, shift_mne_epoch_trigger, find_source_subject,
    label_from_annot,
)
from ..mne_fixes import (
    write_labels_to_annot, _interpolate_bads_eeg, _interpolate_bads_meg)
from ..mne_fixes._trans import hsp_equal, mrk_equal
from ..mne_fixes._source_space import merge_volume_source_space, prune_volume_source_space
from .._ndvar import concatenate, cwt_morlet, neighbor_correlation
from ..fmtxt import List, Report, Image, read_meta
from .._stats.stats import ttest_t
from .._stats.testnd import _MergedTemporalClusterDist
from .._text import enumeration, plural
from .._utils import IS_WINDOWS, ask, subp, keydefaultdict, log_level, ScreenHandler
from .._utils.mne_utils import fix_annot_names, is_fake_mri
from .definitions import find_dependent_epochs, find_epochs_vars, log_dict_change, log_list_change
from .epochs import PrimaryEpoch, SecondaryEpoch, SuperEpoch, EpochCollection, assemble_epochs, decim_param
from .exceptions import FileDeficient, FileMissing
from .experiment import FileTree
from .groups import assemble_groups
from .parc import (
    assemble_parcs,
    FS_PARC, FSA_PARC, SEEDED_PARC_RE,
    CombinationParc, EelbrainParc, FreeSurferParc, FSAverageParc, SeededParc,
    IndividualSeededParc, LabelParc
)
from .preprocessing import (
    assemble_pipeline, RawSource, RawFilter, RawICA,
    compare_pipelines, ask_to_delete_ica_files)
from .test_def import (
    Test, EvokedTest,
    ROITestResult, TestDims, TwoStageTest,
    assemble_tests, find_test_vars,
)
from .variable_def import Variables


# current cache state version
CACHE_STATE_VERSION = 12
# History:
#  10:  input_state: share forward-solutions between sessions
#  11:  add samplingrate to epochs
#  12:  store test-vars as Variables object

# paths
LOG_FILE = join('{root}', 'eelbrain {name}.log')
LOG_FILE_OLD = join('{root}', '.eelbrain.log')

# Allowable parameters
COV_PARAMS = {'epoch', 'session', 'method', 'reg', 'keep_sample_mean', 'reg_eval_win_pad'}
INV_METHODS = ('MNE', 'dSPM', 'sLORETA', 'eLORETA')
SRC_RE = re.compile(r'^(ico|vol)-(\d+)(?:-(brainstem))?$')
inv_re = re.compile(r"^"
                    r"(free|fixed|loose\.\d+|vec)-"  # orientation constraint
                    r"(\d*\.?\d+)-"  # SNR
                    rf"({'|'.join(INV_METHODS)})"  # method
                    r"(?:-((?:0\.)?\d+))?"  # depth weighting
                    r"(?:-(pick_normal))?"
                    r"$")  # pick normal

# Eelbrain 0.24 raw/preprocessing pipeline
LEGACY_RAW = {
    '0-40': RawFilter('raw', None, 40, method='iir'),
    '0.1-40': RawFilter('raw', 0.1, 40, l_trans_bandwidth=0.08, filter_length='60s'),
    '0.2-40': RawFilter('raw', 0.2, 40, l_trans_bandwidth=0.08, filter_length='60s'),
    '1-40': RawFilter('raw', 1, 40, method='iir'),
}


CACHE_HELP = "A change in the {experiment} class definition (or the input files) means that some {filetype} files no longer reflect the current definition. In order to keep local results consistent with the definition, these files should be deleted. If you want to keep a copy of the results, be sure to move them to a different location before proceding. If you think the change in the definition was a mistake, you can select 'abort', revert the change and try again."

################################################################################


def _mask_ndvar(ds, name):
    y = ds[name]
    if y.source.parc is None:
        raise RuntimeError('%r has no parcellation' % (y,))
    mask = y.source.parc.startswith('unknown')
    if mask.any():
        ds[name] = y.sub(source=np.invert(mask))


def _time_str(t):
    "String for representing a time value"
    if t is None:
        return ''
    else:
        return '%i' % round(t * 1000)


def _time_window_str(window, delim='-'):
    "String for representing a time window"
    return delim.join(map(_time_str, window))


def guess_y(ds, default=None):
    "Given a dataset, guess the dependent variable"
    for y in ('srcm', 'src', 'meg', 'eeg'):
        if y in ds:
            return y
    if default is not None:
        return default
    raise RuntimeError(r"Could not find data in {ds}")


class DictSet:
    """Helper class for list of dicts without duplicates"""
    def __init__(self):
        self._list = []

    def __repr__(self):
        return "DictSet(%s)" % self._list

    def __iter__(self):
        return self._list.__iter__()

    def add(self, item):
        if item not in self._list:
            self._list.append(item)

    def update(self, items):
        for item in items:
            self.add(item)


class CacheDict(dict):

    def __init__(self, func, key_vars, *args):
        super(CacheDict, self).__init__()
        self._func = func
        self._key_vars = key_vars
        self._args = args

    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)

        if isinstance(key, str):
            out = self._func(*self._args, **{self._key_vars: key})
        else:
            out = self._func(*self._args, **dict(zip(self._key_vars, key)))

        self[key] = out
        return out


def cache_valid(mtime, *source_mtimes):
    "Determine whether mtime is up-to-date"
    return (
        mtime is not None
        and all(t is not None for t in source_mtimes)
        and mtime > max(source_mtimes))


temp = {
    # MEG
    'equalize_evoked_count': ('', 'eq'),
    # locations
    'raw-sdir': join('{root}', 'meg'),
    'raw-dir': join('{raw-sdir}', '{subject}'),

    # raw input files
    'trans-file': join('{raw-dir}', '{mrisubject_visit}-trans.fif'),
    # log-files (eye-tracker etc.)
    'log-dir': join('{raw-dir}', 'logs'),
    'edf-file': join('{log-dir}', '*.edf'),

    # created input files
    'ica-file': join('{raw-dir}', '{subject_visit} {raw}-ica.fif'),  # hard-coded in RawICA
    'rej-dir': join('{raw-dir}', 'epoch selection'),
    'rej-file': join('{rej-dir}', '{session}_{sns_kind}_{epoch_visit}-{rej}.pickled'),

    # cache
    'cache-dir': join('{root}', 'eelbrain-cache'),
    # raw
    'raw-cache-dir': join('{cache-dir}', 'raw', '{subject}'),
    'raw-cache-base': join('{raw-cache-dir}', '{recording} {raw}'),
    'cached-raw-file': '{raw-cache-base}-raw.fif',
    'event-file': '{raw-cache-base}-evts.pickled',
    'interp-file': '{raw-cache-base}-interp.pickled',
    'cached-raw-log-file': '{raw-cache-base}-raw.log',

    # forward modeling:
    'fwd-file': join('{raw-cache-dir}', '{recording}-{mrisubject}-{src}-fwd.fif'),
    # sensor covariance
    'cov-dir': join('{cache-dir}', 'cov'),
    'cov-base': join('{cov-dir}', '{subject_visit}', '{sns_kind} {cov}-{rej}'),
    'cov-file': '{cov-base}-cov.fif',
    'cov-info-file': '{cov-base}-info.txt',
    # evoked
    'evoked-dir': join('{cache-dir}', 'evoked'),
    'evoked-file': join('{evoked-dir}', '{subject}', '{sns_kind} {epoch_visit} {model} {evoked_kind}-ave.fif'),
    # test files
    'test-dir': join('{cache-dir}', 'test'),
    'test-file': join('{test-dir}', '{analysis} {group}', '{test_desc} {test_dims}.pickled'),

    # MRIs
    'common_brain': 'fsaverage',
    # MRI base files
    'mri-sdir': join('{root}', 'mri'),
    'mri-dir': join('{mri-sdir}', '{mrisubject}'),
    'bem-dir': join('{mri-dir}', 'bem'),
    'mri-cfg-file': join('{mri-dir}', 'MRI scaling parameters.cfg'),
    'mri-file': join('{mri-dir}', 'mri', 'orig.mgz'),
    'bem-file': join('{bem-dir}', '{mrisubject}-inner_skull-bem.fif'),
    'bem-sol-file': join('{bem-dir}', '{mrisubject}-*-bem-sol.fif'),  # removed for 0.24
    'head-bem-file': join('{bem-dir}', '{mrisubject}-head.fif'),
    'src-file': join('{bem-dir}', '{mrisubject}-{src}-src.fif'),
    'fiducials-file': join('{bem-dir}', '{mrisubject}-fiducials.fif'),
    # Labels
    'hemi': ('lh', 'rh'),
    'label-dir': join('{mri-dir}', 'label'),
    'annot-file': join('{label-dir}', '{hemi}.{parc}.annot'),

    # (method) plots
    'methods-dir': join('{root}', 'methods'),

    # result output files
    # data processing parameters
    #    > group
    #        > kind of test
    #    > single-subject
    #        > kind of test
    #            > subject
    'res-dir': join('{root}', 'results'),
    'res-file': join('{res-dir}', '{analysis}', '{resname}.{ext}'),
    'res-deep-file': join('{res-dir}', '{analysis}', '{folder}', '{resname}.{ext}'),
    'report-file': join('{res-dir}', '{analysis} {group}', '{folder}', '{test_desc}.html'),
    'group-mov-file': join('{res-dir}', '{analysis} {group}', '{epoch_visit} {test_options} {resname}.mov'),
    'subject-res-dir': join('{res-dir}', '{analysis} subjects'),
    'subject-spm-report': join('{subject-res-dir}', '{test} {epoch_visit} {test_options}', '{subject}.html'),
    'subject-mov-file': join('{subject-res-dir}', '{epoch_visit} {test_options} {resname}', '{subject}.mov'),

    # plots
    # plot corresponding to a report (and using same folder structure)
    'res-plot-root': join('{root}', 'result plots'),
    'res-plot-dir': join('{res-plot-root}', '{analysis} {group}', '{folder}', '{test_desc}'),

    # besa
    'besa-root': join('{root}', 'besa'),
    'besa-trig': join('{besa-root}', '{subject}', '{subject}_{recording}_{epoch_visit}_triggers.txt'),
    'besa-evt': join('{besa-root}', '{subject}', '{subject}_{recording}_{epoch_visit}[{rej}].evt'),

    # MRAT
    'mrat_condition': '',
    'mrat-root': join('{root}', 'mrat'),
    'mrat-sns-root': join('{mrat-root}', '{sns_kind}', '{epoch_visit} {model} {evoked_kind}'),
    'mrat-src-root': join('{mrat-root}', '{src_kind}', '{epoch_visit} {model} {evoked_kind}'),
    'mrat-sns-file': join('{mrat-sns-root}', '{mrat_condition}', '{mrat_condition}_{subject}-ave.fif'),
    'mrat_info-file': join('{mrat-root}', '{subject} info.txt'),
    'mrat-src-file': join('{mrat-src-root}', '{mrat_condition}', '{mrat_condition}_{subject}'),
}


class MneExperiment(FileTree):
    """Analyze an MEG experiment (gradiometer only) with MNE

    Parameters
    ----------
    root : str | None
        the root directory for the experiment (usually the directory
        containing the 'meg' and 'mri' directories). The experiment can be
        initialized without the root for testing purposes.
    find_subjects : bool
        Automatically look for subjects in the MEG-directory (default
        True). Set ``find_subjects=False`` to initialize the experiment
        without any files.
    ...
        Initial state parameters.

    Notes
    -----
    .. seealso::
        Guide on using :ref:`experiment-class-guide`.
    """
    path_version = 2
    screen_log_level = logging.INFO
    auto_delete_results = False
    auto_delete_cache = True
    # what to do when the experiment class definition changed:
    #   True: delete outdated files
    #   False: raise an error
    #   'disable': ignore it
    #   'debug': prompt with debug options

    # tuple (if the experiment has multiple sessions)
    sessions = None
    visits = ('',)

    # Raw preprocessing pipeline
    raw = {}

    # add this value to all trigger times
    trigger_shift = 0

    # variables for automatic labeling {name: {trigger: label, triggers: label}}
    variables = {}

    # Default values for epoch definitions
    epoch_default = {'decim': 5}

    # named epochs
    epochs = {}

    # Rejection
    # =========
    # eog_sns: The sensors to plot separately in the rejection GUI. The default
    # is the two MEG sensors closest to the eyes.
    _eog_sns = {None: (),
                'KIT-157': ('MEG 143', 'MEG 151'),
                'KIT-208': ('MEG 087', 'MEG 130'),
                'KIT-UMD-1': ('MEG 042', 'MEG 025'),
                'KIT-UMD-2': ('MEG 042', 'MEG 025'),
                'KIT-UMD-3': ('MEG 042', 'MEG 025'),
                'KIT-BRAINVISION': ('HEOGL', 'HEOGR', 'VEOGb'),
                'neuromag306mag': ('MEG 0121', 'MEG 1411')}
    #
    # artifact_rejection dict:
    #
    # kind : 'manual' | 'make'
    #     How the rejection is derived:
    #     'manual': manually create a rejection file (use the selection GUI
    #     through .make_epoch_selection())
    #     'make' a rejection file is created by the user
    # interpolation : bool
    #     enable by-epoch channel interpolation
    #
    # For manual rejection
    # ^^^^^^^^^^^^^^^^^^^^
    _artifact_rejection = {
        '': {'kind': None},
        'man': {'kind': 'manual', 'interpolation': True},
    }
    artifact_rejection = {}

    exclude = {}  # field_values to exclude (e.g. subjects)

    # groups can be defined as subject lists: {'group': ('member1', 'member2', ...)}
    # or by exclusion: {'group': {'base': 'all', 'exclude': ('member1', 'member2')}}
    groups = {}

    # whether to look for and load eye tracker data when loading raw files
    has_edf = defaultdict(lambda: False)

    # Pattern for subject names. The first group is used to determine what
    # MEG-system the data was recorded from
    subject_re = r'(R|S|A|Y|AD|QP)(\d{3,})$'
    # MEG-system (legacy variable).
    meg_system = None

    # kwargs for regularization of the covariance matrix (see .make_cov())
    _covs = {'auto': {'epoch': 'cov', 'method': 'auto'},
             'bestreg': {'epoch': 'cov', 'reg': 'best'},
             'reg': {'epoch': 'cov', 'reg': True},
             'noreg': {'epoch': 'cov', 'reg': None},
             'emptyroom': {'session': 'emptyroom', 'reg': None}}

    # MRI subject names: {subject: mrisubject} mappings
    # selected with e.set(mri=dict_name)
    # default is identity (mrisubject = subject)
    _mri_subjects = {'': keydefaultdict(lambda s: s)}

    # Where to search for subjects (defined as a template name). If the
    # experiment searches for subjects automatically, it scans this directory
    # for subfolders matching subject_re.
    _subject_loc = 'raw-sdir'

    # Parcellations
    __parcs = {
        'aparc.a2005s': FS_PARC,
        'aparc.a2009s': FS_PARC,
        'aparc': FS_PARC,
        'aparc.DKTatlas': FS_PARC,
        'cortex': LabelParc(('cortex',), ('lateral', 'medial')),
        'PALS_B12_Brodmann': FSA_PARC,
        'PALS_B12_Lobes': FSA_PARC,
        'PALS_B12_OrbitoFrontal': FSA_PARC,
        'PALS_B12_Visuotopic': FSA_PARC,
        'lobes': EelbrainParc(True, ('lateral', 'medial')),
        'lobes-op': CombinationParc('lobes', {'occipitoparietal': "occipital + parietal"}, ('lateral', 'medial')),
        'lobes-ot': CombinationParc('lobes', {'occipitotemporal': "occipital + temporal"}, ('lateral', 'medial')),
    }
    parcs = {}

    # Frequencies:  lowbound, highbound, step
    _freqs = {'gamma': {'frequencies': np.arange(25, 50, 2),
                        'n_cycles': 5}}
    freqs = {}

    # basic templates to use. Can be a string referring to a templates
    # dictionary in the module level _temp dictionary, or a templates
    # dictionary
    _templates = temp
    # specify additional templates
    _values = {}
    # specify defaults for specific fields (e.g. specify the initial subject
    # name)
    defaults = {}

    # model order: list of factors in the order in which models should be built
    # (default for factors not in this list is alphabetic)
    _model_order = []

    # Backup
    # ------
    # basic state for a backup
    _backup_state = {'subject': '*', 'mrisubject': '*', 'session': '*', 'raw': 'raw'}
    # files to back up, together with state modifications on the basic state
    _backup_files = (('rej-file', {'raw': '*', 'epoch': '*', 'rej': '*'}),
                     ('trans-file', {}),
                     ('mri-cfg-file', {}),
                     ('log-dir', {}),)

    # Tests
    # -----
    # specify tests as (test_type, model, test_parameter) tuple. For example,
    # ("anova", "condition", "condition*subject")
    # ("t_contrast_rel", "ref%loc", "+min(ref|left>nref|*, ref|right>nref|*)")
    # Make sure dictionary keys (test names) are appropriate for filenames.
    # tests imply a model which is set automatically
    tests = {}
    _empty_test = False  # for TRFExperiment
    _cluster_criteria = {
        '': {'time': 0.025, 'sensor': 4, 'source': 10},
        'all': {},
        '10ms': {'time': 0.01, 'sensor': 4, 'source': 10},
        'large': {'time': 0.025, 'sensor': 8, 'source': 20},
    }

    # plotting
    # --------
    _brain_plot_defaults = {'surf': 'inflated'}
    brain_plot_defaults = {}

    def __init__(self, root=None, find_subjects=True, **state):
        # checks
        if hasattr(self, 'cluster_criteria'):
            raise AttributeError("MneExperiment subclasses can not have a .cluster_criteria attribute anymore. Please remove the attribute, delete the eelbrain-cache folder and use the select_clusters analysis parameter.")

        # create attributes (overwrite class attributes)
        self._mri_subjects = self._mri_subjects.copy()
        self._templates = self._templates.copy()
        # templates version
        if self.path_version == 0:
            self._templates['raw-dir'] = join('{raw-sdir}', 'meg', 'raw')
            raw_def = {**LEGACY_RAW, 'raw': RawSource('{subject}_{recording}_clm-raw.fif'), **self.raw}
        elif self.path_version == 1:
            raw_def = {**LEGACY_RAW, 'raw': RawSource(), **self.raw}
        elif self.path_version == 2:
            raw_def = {'raw': RawSource(), **self.raw}
        else:
            raise ValueError(f"MneExperiment.path_version={self.path_version}; needs to be 0, 1 or 2")
        # update templates with _values
        for cls in reversed(inspect.getmro(self.__class__)):
            if hasattr(cls, '_values'):
                self._templates.update(cls._values)

        FileTree.__init__(self)
        self._log = log = logging.Logger(self.__class__.__name__, logging.DEBUG)

        ########################################################################
        # sessions
        if self.sessions is None:
            raise TypeError("The MneExperiment.sessions parameter needs to be specified. The session name is contained in your raw data files. For example if your file is named `R0026_mysession-raw.fif` your session name is 'mysession' and you should set MneExperiment.sessions to 'mysession'.")
        elif isinstance(self.sessions, str):
            self._sessions = (self.sessions,)
        elif isinstance(self.sessions, Sequence):
            self._sessions = tuple(self.sessions)
        else:
            raise TypeError(f"MneExperiment.sessions={self.sessions!r}; needs to be a string or a tuple")
        self._visits = (self._visits,) if isinstance(self.visits, str) else tuple(self.visits)

        ########################################################################
        # subjects
        if root is None:
            find_subjects = False
        else:
            root = self.get('root', root=root)

        if find_subjects:
            subject_re = re.compile(self.subject_re)
            sub_dir = self.get(self._subject_loc)
            if not exists(sub_dir):
                raise IOError(f"Subjects directory {sub_dir}: does notexist. To initialize {self.__class__.__name__} without data, initialize with root=None or find_subjects=False")
            subjects = [s for s in os.listdir(sub_dir) if subject_re.match(s) and isdir(join(sub_dir, s))]
            if len(subjects) == 0:
                log.warning(f"No subjects found in {sub_dir}")
            subjects.sort()
            subjects = tuple(subjects)
        else:
            subjects = ()

        ########################################################################
        # groups
        self._groups = assemble_groups(self.groups, set(subjects))

        ########################################################################
        # Preprocessing
        skip = {'root', 'subject', 'recording', 'raw'}
        raw_dir = self._partial('raw-dir', skip)
        cache_path = self._partial('cached-raw-file', skip)
        self._raw = assemble_pipeline(raw_def, raw_dir, cache_path, root, self._sessions, log)

        raw_pipe = self._raw['raw']
        # legacy connectivity determination
        if raw_pipe.sysname is None:
            if self.meg_system is not None:
                raw_pipe.sysname = self.meg_system
        # update templates
        self._register_constant('raw-file', raw_pipe.path)

        ########################################################################
        # variables
        self._variables = Variables(self.variables)
        self._variables._check_trigger_vars()

        ########################################################################
        # epochs
        epoch_default = {'session': self._sessions[0], **self.epoch_default}
        self._epochs = assemble_epochs(self.epochs, epoch_default)

        ########################################################################
        # store epoch rejection settings
        artifact_rejection = {}
        for name, params in chain(self._artifact_rejection.items(), self.artifact_rejection.items()):
            if params['kind'] in ('manual', 'make', None):
                artifact_rejection[name] = params.copy()
            elif params['kind'] == 'ica':
                raise ValueError(f"kind={params['kind']!r} in artifact_rejection {name!r}; The ICA option has been removed, use the RawICA raw pipe instead.")
            else:
                raise ValueError(f"kind={params['kind']!r} in artifact_rejection {name!r}")
        self._artifact_rejection = artifact_rejection

        ########################################################################
        # Cov
        #####
        for k, params in self._covs.items():
            params = set(params)
            n_datasource = ('epoch' in params) + ('session' in params)
            if n_datasource != 1:
                if n_datasource == 0:
                    raise ValueError("Cov %s has neither epoch nor session "
                                     "entry" % k)
                raise ValueError("Cov %s has both epoch and session entry" % k)
            if params.difference(COV_PARAMS):
                raise ValueError("Cov %s has unused entries: %s" %
                                 (k, ', '.join(params.difference(COV_PARAMS))))

        ########################################################################
        # parcellations
        ###############
        # make : can be made if non-existent
        # morph_from_fraverage : can be morphed from fsaverage to other subjects
        self._parcs = assemble_parcs(chain(self.__parcs.items(), self.parcs.items()))
        parc_values = list(self._parcs.keys())
        parc_values.append('')

        ########################################################################
        # frequency
        freqs = {}
        for name, f in chain(self._freqs.items(), self.freqs.items()):
            if name in freqs:
                raise ValueError("Frequency %s defined twice" % name)
            elif 'frequencies' not in f:
                raise KeyError("Frequency values missing for %s" % name)
            elif 'n_cycles' not in f:
                raise KeyError("Number of cycles not defined for %s" % name)
            freqs[name] = f

        self._freqs = freqs

        ########################################################################
        # tests
        self._tests = assemble_tests(self.tests)
        test_values = sorted(self._tests)
        if self._empty_test:
            test_values.insert(0, '')

        ########################################################################
        # Experiment class setup
        ########################
        self._register_field('mri', sorted(self._mri_subjects), allow_empty=True)
        self._register_field('subject', subjects or None, repr=True)
        self._register_field('group', self._groups.keys(), 'all', post_set_handler=self._post_set_group)

        raw_default = sorted(self.raw)[0] if self.raw else None
        self._register_field('raw', sorted(self._raw), default=raw_default, repr=True)
        self._register_field('rej', self._artifact_rejection.keys(), 'man', allow_empty=True)

        # epoch
        epoch_keys = sorted(self._epochs)
        for default_epoch in epoch_keys:
            if isinstance(self._epochs[default_epoch], PrimaryEpoch):
                break
        else:
            default_epoch = None
        self._register_field('epoch', epoch_keys, default_epoch, repr=True)
        self._register_field('session', self._sessions, depends_on=('epoch',), slave_handler=self._update_session, repr=True)
        self._register_field('visit', self._visits, allow_empty=True, repr=True)

        # cov
        if 'bestreg' in self._covs:
            default_cov = 'bestreg'
        else:
            default_cov = None
        self._register_field('cov', sorted(self._covs), default_cov)
        self._register_field('inv', default='free-3-dSPM', eval_handler=self._eval_inv, post_set_handler=self._post_set_inv)
        self._register_field('model', eval_handler=self._eval_model)
        self._register_field('test', test_values, post_set_handler=self._post_set_test, allow_empty=self._empty_test, repr=False)
        self._register_field('parc', parc_values, 'aparc', eval_handler=self._eval_parc, allow_empty=True)
        self._register_field('freq', self._freqs.keys())
        self._register_field('src', default='ico-4', eval_handler=self._eval_src)
        self._register_field('connectivity', ('', 'link-midline'), allow_empty=True)
        self._register_field('select_clusters', self._cluster_criteria.keys(), allow_empty=True)

        # slave fields
        self._register_field('mrisubject', depends_on=('mri', 'subject'), slave_handler=self._update_mrisubject, repr=False)
        self._register_field('src-name', depends_on=('src',), slave_handler=self._update_src_name, repr=False)

        # fields used internally
        self._register_field('analysis', repr=False)
        self._register_field('test_options', repr=False)
        self._register_field('name', repr=False)
        self._register_field('folder', repr=False)
        self._register_field('resname', repr=False)
        self._register_field('ext', repr=False)
        self._register_field('test_dims', repr=False)

        # compounds
        self._register_compound('sns_kind', ('raw',))
        self._register_compound('src_kind', ('sns_kind', 'cov', 'mri', 'src-name', 'inv'))
        self._register_compound('recording', ('session', 'visit'))
        self._register_compound('subject_visit', ('subject', 'visit'))
        self._register_compound('mrisubject_visit', ('mrisubject', 'visit'))
        self._register_compound('epoch_visit', ('epoch', 'visit'))
        self._register_compound('evoked_kind', ('rej', 'equalize_evoked_count'))
        self._register_compound('test_desc', ('epoch', 'visit', 'test', 'test_options'))

        # Define make handlers
        self._bind_cache('cov-file', self.make_cov)
        self._bind_cache('src-file', self.make_src)
        self._bind_cache('fwd-file', self.make_fwd)

        # currently only used for .rm()
        self._secondary_cache['cached-raw-file'] = ('event-file', 'interp-file', 'cached-raw-log-file')

        ########################################################################
        # logger
        ########
        # log-file
        if root:
            log_file = LOG_FILE.format(root=root, name=self.__class__.__name__)
            log_file_old = LOG_FILE_OLD.format(root=root)
            if exists(log_file_old):
                os.rename(log_file_old, log_file)
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter("%(levelname)-8s %(asctime)s %(message)s",
                                          "%m-%d %H:%M")  # %(name)-12s
            handler.setFormatter(formatter)
            handler.setLevel(logging.DEBUG)
            log.addHandler(handler)
        # Terminal log
        handler = ScreenHandler()
        self._screen_log_level = log_level(self.screen_log_level)
        handler.setLevel(self._screen_log_level)
        log.addHandler(handler)
        self._screen_log_handler = handler

        # log package versions
        from .. import __version__
        log.info("*** %s initialized with root %s on %s ***", self.__class__.__name__, 
                 root, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        msg = "Using eelbrain %s, mne %s." % (__version__, mne.__version__)
        if any('dev' in v for v in (__version__, mne.__version__)):
            log.warning(f"{msg} Development versions are more likely to contain errors.")
        else:
            log.info(msg)

        if self.auto_delete_cache == 'disable':
            log.warning("Cache-management disabled")
            return

        ########################################################################
        # Finalize
        ##########
        # register experimental features
        self._subclass_init()

        # Check that the template model is complete
        self._find_missing_fields()

        # set initial values
        self.set(**state)
        self._store_state()

        ########################################################################
        # Cache
        #######
        if not root:
            return

        # loading events will create cache-dir
        cache_dir = self.get('cache-dir')
        cache_dir_existed = exists(cache_dir)

        # collect input file information
        # ==============================
        raw_missing = []  # [(subject, recording), ...]
        subjects_with_raw_changes = set()  # {subject, ...}
        events = {}  # {(subject, recording): event_dataset}

        # saved mtimes
        input_state_file = join(cache_dir, 'input-state.pickle')
        if exists(input_state_file):
            input_state = load.unpickle(input_state_file)
            if input_state['version'] < 10:
                input_state = None
            elif input_state['version'] > CACHE_STATE_VERSION:
                raise RuntimeError(
                    "You are trying to initialize an experiment with an older "
                    "version of Eelbrain than that which wrote the cache. If "
                    "you really need this, delete the eelbrain-cache folder "
                    "and try again.")
        else:
            input_state = None

        if input_state is None:
            input_state = {
                'version': CACHE_STATE_VERSION,
                'raw-mtimes': {},
                'fwd-sessions': {s: {} for s in subjects},
            }

        # collect current events and mtime
        raw_mtimes = input_state['raw-mtimes']
        pipe = self._raw['raw']
        with self._temporary_state:
            for subject, visit, recording in self.iter(('subject', 'visit', 'recording'), group='all', raw='raw'):
                key = subject, recording
                mtime = pipe.mtime(subject, recording, bad_chs=False)
                if mtime is None:
                    raw_missing.append(key)
                    continue
                # events
                events[key] = self.load_events(add_bads=False, data_raw=False)
                if key not in raw_mtimes or mtime != raw_mtimes[key]:
                    subjects_with_raw_changes.add((subject, visit))
                    raw_mtimes[key] = mtime
            # log missing raw files
            if raw_missing:
                log.debug("Raw files missing:")
                missing = defaultdict(list)
                for subject, recording in raw_missing:
                    missing[subject].append(recording)
                for subject, recordings in missing.items():
                    log.debug(f"  {subject}: {', '.join(recordings)}")

        # check for digitizer data differences
        # ====================================
        # Coordinate frames:
        # MEG (markers)  ==raw-file==>  head shape  ==trans-file==>  MRI
        #
        #  - raw files with identical head shapes can share trans-file (head-mri)
        #  - raw files with identical MEG markers (and head shape) can share
        #    forward solutions
        #  - SuperEpochs currently need to have a single forward solution,
        #    hence marker positions need to be the same between sub-epochs
            if subjects_with_raw_changes:
                log.info("Raw input files changed, checking digitizer data")
                super_epochs = [epoch for epoch in self._epochs.values() if isinstance(epoch, SuperEpoch)]
            for subject, visit in subjects_with_raw_changes:
                # find unique digitizer datasets
                head_shape = None
                markers = []  # unique MEG marker measurements
                marker_ids = {}  # {recording: index in markers}
                dig_missing = []  # raw files without dig
                for recording in self.iter('recording', subject=subject, visit=visit):
                    if (subject, recording) in raw_missing:
                        continue
                    raw = self.load_raw(False)
                    dig = raw.info['dig']
                    if dig is None:
                        dig_missing.append(recording)
                        continue
                    elif head_shape is None:
                        head_shape = dig
                    elif not hsp_equal(dig, head_shape):
                        raise FileDeficient(f"Raw file {recording} for {subject} has head shape that is different from {enumeration(marker_ids)}; consider defining different visits.")

                    # find if marker pos already exists
                    for i, dig_i in enumerate(markers):
                        if mrk_equal(dig, dig_i):
                            marker_ids[recording] = i
                            break
                    else:
                        marker_ids[recording] = len(markers)
                        markers.append(dig)

                # checks for missing digitizer data
                if len(markers) > 1:
                    if dig_missing:
                        n = len(dig_missing)
                        raise FileDeficient(f"The raw {plural('file', n)} for {subject}, {plural('recording', n)} {enumeration(dig_missing)} {plural('is', n)} missing digitizer information")
                    for epoch in super_epochs:
                        if len(set(marker_ids[s] for s in epoch.sessions)) > 1:
                            groups = defaultdict(list)
                            for s in epoch.sessions:
                                groups[marker_ids[s]].append(s)
                            group_desc = ' vs '.join('/'.join(group) for group in groups.values())
                            raise NotImplementedError(f"SuperEpoch {epoch.name} has sessions with incompatible marker positions ({group_desc}); SuperEpochs with different forward solutions are not implemented.")

                # determine which sessions to use for forward solutions
                # -> {for_session: use_session}
                use_for_session = input_state['fwd-sessions'].setdefault(subject, {})
                # -> {marker_id: use_session}, initialize with previously used sessions
                use_for_id = {marker_ids[s]: s for s in use_for_session.values() if s in marker_ids}
                for recording in sorted(marker_ids):
                    mrk_id = marker_ids[recording]
                    if recording in use_for_session:
                        assert mrk_id == marker_ids[use_for_session[recording]]
                        continue
                    elif mrk_id not in use_for_id:
                        use_for_id[mrk_id] = recording
                    use_for_session[recording] = use_for_id[mrk_id]
                # for files missing digitizer, use singe available fwd-recording
                for recording in dig_missing:
                    if use_for_id:
                        assert len(use_for_id) == 1
                        use_for_session[recording] = use_for_id[0]

        # save input-state
        if not cache_dir_existed:
            os.makedirs(cache_dir, exist_ok=True)
        save.pickle(input_state, input_state_file)
        self._dig_sessions = pipe._dig_sessions = input_state['fwd-sessions']  # {subject: {for_recording: use_recording}}

        # Check the cache, delete invalid files
        # =====================================
        cache_state_path = join(cache_dir, 'cache-state.pickle')
        raw_state = {k: v.as_dict() for k, v in self._raw.items()}
        epoch_state = {k: v.as_dict() for k, v in self._epochs.items()}
        parcs_state = {k: v.as_dict() for k, v in self._parcs.items()}
        tests_state = {k: v.as_dict() for k, v in self._tests.items()}
        if exists(cache_state_path):
            # check time stamp
            state_mtime = getmtime(cache_state_path)
            now = time.time() + IS_WINDOWS  # Windows seems to have rounding issue
            if state_mtime > now:
                raise RuntimeError(f"The cache's time stamp is in the future ({time.ctime(state_mtime)}). If the system time ({time.ctime(now)}) is wrong, adjust the system clock; if not, delete the eelbrain-cache folder.")
            cache_state = load.unpickle(cache_state_path)
            cache_state_v = cache_state.get('version', 0)
            if cache_state_v < CACHE_STATE_VERSION:
                log.debug("Updating cache-state %i -> %i", cache_state_v, CACHE_STATE_VERSION)
            elif cache_state_v > CACHE_STATE_VERSION:
                raise RuntimeError(f"The cache is from a newer version of Eelbrain than you are currently using. Either upgrade Eelbrain or delete the cache folder.")

            # Backwards compatibility
            # =======================
            # epochs
            if cache_state_v >= 11:
                epoch_state_v = epoch_state
            elif cache_state_v >= 3:
                # remove samplingrate parameter
                epoch_state_v = {k: {ki: vi for ki, vi in v.items() if ki != 'samplingrate'} for k, v in epoch_state.items()}
            else:
                # Epochs represented as dict up to Eelbrain 0.24
                epoch_state_v = {k: v.as_dict_24() for k, v in self._epochs.items()}
                for e in cache_state['epochs'].values():
                    e.pop('base', None)
                    if 'sel_epoch' in e:
                        e.pop('n_cases', None)

            # events did not include session
            if cache_state_v < 4:
                if not events:
                    raise DefinitionError("No raw files or events found. Did you set the MneExperiment.session parameter correctly?")
                session = self._sessions[0]
                cache_events = {(subject, session): v for subject, v in
                                cache_state['events'].items()}
            else:
                cache_events = cache_state['events']

            # raw pipeline
            if cache_state_v < 5:
                legacy_raw = assemble_pipeline(LEGACY_RAW, '', '', '', '', self._sessions, log)
                cache_raw = {k: v.as_dict() for k, v in legacy_raw.items()}
            else:
                cache_raw = cache_state['raw']

            # parcellations represented as dicts
            cache_parcs = cache_state['parcs']
            if cache_state_v < 6:
                for params in cache_parcs.values():
                    for key in ('morph_from_fsaverage', 'make'):
                        if key in params:
                            del params[key]

            # tests represented as dicts
            cache_tests = cache_state['tests']
            if cache_state_v < 7:
                for params in cache_tests.values():
                    if 'desc' in params:
                        del params['desc']
                cache_tests = {k: v.as_dict() for k, v in assemble_tests(cache_tests).items()}
            elif cache_state_v == 7:  # 'kind' key missing
                for name, params in cache_tests.items():
                    if name in tests_state:
                        params['kind'] = tests_state[name]['kind']
            if cache_state_v < 12:  # 'vars' entry added to all
                for test, params in cache_tests.items():
                    if 'vars' in params:
                        try:
                            params['vars'] = Variables(params['vars'])
                        except Exception as error:
                            log.warning("  Test %s: Defective vardef %r", test, params['vars'])
                            params['vars'] = None
                    else:
                        params['vars'] = None

            # Find modified definitions
            # =========================
            invalid_cache = defaultdict(set)
            # events (subject, recording):  overall change in events
            # variables:  event change restricted to certain variables
            # raw: preprocessing definition changed
            # groups:  change in group members
            # epochs:  change in epoch parameters
            # parcs: parc def change
            # tests: test def change

            # check events
            # 'events' -> number or timing of triggers (includes trigger_shift)
            # 'variables' -> only variable change
            for key, old_events in cache_events.items():
                new_events = events.get(key)
                if new_events is None:
                    invalid_cache['events'].add(key)
                    log.warning("  raw file removed: %s", '/'.join(key))
                elif new_events.n_cases != old_events.n_cases:
                    invalid_cache['events'].add(key)
                    log.warning("  event length: %s %i->%i", '/'.join(key), old_events.n_cases, new_events.n_cases)
                elif not np.all(new_events['i_start'] == old_events['i_start']):
                    invalid_cache['events'].add(key)
                    log.warning("  trigger times changed: %s", '/'.join(key))
                else:
                    for var in old_events:
                        if var == 'i_start':
                            continue
                        elif var not in new_events:
                            invalid_cache['variables'].add(var)
                            log.warning("  var removed: %s (%s)", var, '/'.join(key))
                            continue
                        old = old_events[var]
                        new = new_events[var]
                        if old.name != new.name:
                            invalid_cache['variables'].add(var)
                            log.warning("  var name changed: %s (%s) %s->%s", var, '/'.join(key), old.name, new.name)
                        elif new.__class__ is not old.__class__:
                            invalid_cache['variables'].add(var)
                            log.warning("  var type changed: %s (%s) %s->%s", var, '/'.join(key), old.__class__, new.__class)
                        elif not all_equal(old, new, True):
                            invalid_cache['variables'].add(var)
                            log.warning("  var changed: %s (%s) %i values", var, '/'.join(key), np.sum(new != old))

            # groups
            for group, members in cache_state['groups'].items():
                if group not in self._groups:
                    invalid_cache['groups'].add(group)
                    log.warning("  Group removed: %s", group)
                elif members != self._groups[group]:
                    invalid_cache['groups'].add(group)
                    log_list_change(log, "Group", group, members, self._groups[group])

            # raw
            changed, changed_ica = compare_pipelines(cache_raw, raw_state, log)
            if changed:
                invalid_cache['raw'].update(changed)
            for raw, status in changed_ica.items():
                filenames = self.glob('ica-file', raw=raw, subject='*', visit='*', match=False)
                if filenames:
                    rel_paths = '\n'.join(relpath(path, root) for path in filenames)
                    print(f"Outdated ICA files:\n{rel_paths}")
                    ask_to_delete_ica_files(raw, status, filenames)

            # epochs
            for epoch, old_params in cache_state['epochs'].items():
                new_params = epoch_state_v.get(epoch, None)
                if old_params != new_params:
                    invalid_cache['epochs'].add(epoch)
                    if new_params is None:
                        log.warning("  Epoch removed: %s", epoch)
                    else:
                        log_dict_change(log, 'Epoch', epoch, old_params, new_params)

            # parcs
            for parc, params in cache_parcs.items():
                if parc not in parcs_state:
                    invalid_cache['parcs'].add(parc)
                    log.warning("  Parc %s removed", parc)
                elif params != parcs_state[parc]:
                    # FS_PARC:  Parcellations that are provided by the user
                    # should not be automatically removed.
                    # FSA_PARC:  for other mrisubjects, the parcellation
                    # should automatically update if the user changes the
                    # fsaverage file.
                    if not isinstance(self._parcs[parc],
                                      (FreeSurferParc, FSAverageParc)):
                        invalid_cache['parcs'].add(parc)
                        log_dict_change(log, "Parc", parc, params, parcs_state[parc])

            # tests
            for test, params in cache_tests.items():
                if test not in tests_state or params != tests_state[test]:
                    invalid_cache['tests'].add(test)
                    if test in tests_state:
                        log_dict_change(log, "Test", test, params, tests_state[test])
                    else:
                        log.warning("  Test %s removed", test)

            # create message here, before secondary invalidations are added
            msg = []
            if cache_state_v < 2:
                msg.append("Check for invalid ANOVA tests (cache version %i)." %
                           cache_state_v)
            if invalid_cache:
                msg.append("Experiment definition changed:")
                for kind, values in invalid_cache.items():
                    msg.append("  %s: %s" % (kind, ', '.join(map(str, values))))

            # Secondary  invalidations
            # ========================
            # changed events -> group result involving those subjects is also bad
            if 'events' in invalid_cache:
                subjects = {subject for subject, _ in invalid_cache['events']}
                for group, members in cache_state['groups'].items():
                    if subjects.intersection(members):
                        invalid_cache['groups'].add(group)

            # tests/epochs based on variables
            if 'variables' in invalid_cache:
                bad_vars = invalid_cache['variables']
                # tests using bad variable
                for test in cache_tests:
                    if test in invalid_cache['tests']:
                        continue
                    params = tests_state[test]
                    bad = bad_vars.intersection(find_test_vars(params))
                    if bad:
                        invalid_cache['tests'].add(test)
                        log.debug("  Test %s depends on changed variables %s", test, ', '.join(bad))
                # epochs using bad variable
                epochs_vars = find_epochs_vars(cache_state['epochs'])
                for epoch, evars in epochs_vars.items():
                    bad = bad_vars.intersection(evars)
                    if bad:
                        invalid_cache['epochs'].add(epoch)
                        log.debug("  Epoch %s depends on changed variables %s", epoch, ', '.join(bad))

            # secondary epochs
            if 'epochs' in invalid_cache:
                for e in tuple(invalid_cache['epochs']):
                    invalid_cache['epochs'].update(find_dependent_epochs(e, cache_state['epochs']))

            # Collect invalid files
            # =====================
            if invalid_cache or cache_state_v < 2:
                rm = defaultdict(DictSet)

                # version
                if cache_state_v < 2:
                    bad_parcs = []
                    for parc, params in self._parcs.items():
                        if params['kind'] == 'seeded':
                            bad_parcs.append(parc + '-?')
                            bad_parcs.append(parc + '-??')
                            bad_parcs.append(parc + '-???')
                        else:
                            bad_parcs.append(parc)
                    bad_tests = []
                    for test, params in tests_state.items():
                        if params['kind'] == 'anova' and params['x'].count('*') > 1:
                            bad_tests.append(test)
                    if bad_tests and bad_parcs:
                        log.warning("  Invalid ANOVA tests: %s for %s", bad_tests, bad_parcs)
                    for test, parc in product(bad_tests, bad_parcs):
                        rm['test-file'].add({'test': test, 'test_dims': parc})
                        rm['report-file'].add({'test': test, 'folder': parc})

                # evoked files are based on old events
                for subject, recording in invalid_cache['events']:
                    for epoch, params in self._epochs.items():
                        if recording not in params.sessions:
                            continue
                        rm['evoked-file'].add({'subject': subject, 'epoch': epoch})

                # variables
                for var in invalid_cache['variables']:
                    rm['evoked-file'].add({'model': '*%s*' % var})

                # groups
                for group in invalid_cache['groups']:
                    rm['test-file'].add({'group': group})
                    rm['group-mov-file'].add({'group': group})
                    rm['report-file'].add({'group': group})

                # raw
                for raw in invalid_cache['raw']:
                    rm['cached-raw-file'].add({'raw': raw})
                    rm['evoked-file'].add({'raw': raw})
                    analysis = {'analysis': '* %s *' % raw}
                    rm['test-file'].add(analysis)
                    rm['report-file'].add(analysis)
                    rm['group-mov-file'].add(analysis)
                    rm['subject-mov-file'].add(analysis)

                # epochs
                for epoch in invalid_cache['epochs']:
                    rm['evoked-file'].add({'epoch': epoch})
                    for cov, cov_params in self._covs.items():
                        if cov_params.get('epoch') != epoch:
                            continue
                        analysis = '* %s *' % cov
                        rm['test-file'].add({'analysis': analysis})
                        rm['report-file'].add({'analysis': analysis})
                        rm['group-mov-file'].add({'analysis': analysis})
                        rm['subject-mov-file'].add({'analysis': analysis})
                    rm['test-file'].add({'epoch': epoch})
                    rm['report-file'].add({'epoch': epoch})
                    rm['group-mov-file'].add({'epoch': epoch})
                    rm['subject-mov-file'].add({'epoch': epoch})

                # parcs
                bad_parcs = []
                for parc in invalid_cache['parcs']:
                    if cache_state['parcs'][parc]['kind'].endswith('seeded'):
                        bad_parcs.append(parc + '-?')
                        bad_parcs.append(parc + '-??')
                        bad_parcs.append(parc + '-???')
                    else:
                        bad_parcs.append(parc)
                for parc in bad_parcs:
                    rm['annot-file'].add({'parc': parc})
                    rm['test-file'].add({'test_dims': parc})
                    rm['test-file'].add({'test_dims': parc + '.*'})
                    rm['report-file'].add({'folder': parc})
                    rm['report-file'].add({'folder': '%s *' % parc})
                    rm['report-file'].add({'folder': '%s *' % parc.capitalize()})  # pre 0.26
                    rm['res-file'].add({'analysis': 'Source Annot',
                                        'resname': parc + ' * *', 'ext': 'p*'})

                # tests
                for test in invalid_cache['tests']:
                    rm['test-file'].add({'test': test})
                    rm['report-file'].add({'test': test})

                # secondary cache files
                for temp in tuple(rm):
                    for stemp in self._secondary_cache[temp]:
                        rm[stemp].update(rm[temp])

                # find actual files to delete
                log.debug("Outdated cache files:")
                files = set()
                result_files = []
                for temp, arg_dicts in rm.items():
                    for args in arg_dicts:
                        pattern = self._glob_pattern(temp, True, vmatch=False, **args)
                        filenames = glob(pattern)
                        files.update(filenames)
                        # log
                        rel_pattern = relpath(pattern, root)
                        rel_filenames = sorted('  ' + relpath(f, root) for f in filenames)
                        log.debug(' >%s', rel_pattern)
                        for filename in rel_filenames:
                            log.debug(filename)
                        # message to the screen unless log is already displayed
                        if rel_pattern.startswith('results'):
                            result_files.extend(rel_filenames)

                # handle invalid files
                n_result_files = len(result_files)
                if n_result_files and self.auto_delete_cache is True and not self.auto_delete_results:
                    if self._screen_log_level > logging.DEBUG:
                        msg = result_files[:]
                        msg.insert(0, "Outdated result files detected:")
                    else:
                        msg = []
                    msg.append("Delete %i outdated results?" % (n_result_files,))
                    command = ask(
                        '\n'.join(msg),
                        options=(
                            ('delete', 'delete invalid result files'),
                            ('abort', 'raise an error')),
                        help=CACHE_HELP.format(
                            experiment=self.__class__.__name__,
                            filetype='result'),
                    )
                    if command == 'abort':
                        raise RuntimeError("User aborted invalid result deletion")
                    elif command != 'delete':
                        raise RuntimeError("command=%r" % (command,))

                if files:
                    if self.auto_delete_cache is False:
                        raise RuntimeError(
                            "Automatic cache management disabled. Either "
                            "revert changes, or set e.auto_delete_cache=True")
                    elif isinstance(self.auto_delete_cache, str):
                        if self.auto_delete_cache != 'debug':
                            raise ValueError(f"MneExperiment.auto_delete_cache={self.auto_delete_cache!r}")
                        command = ask(
                            "Outdated cache files. Choose 'delete' to proceed. "
                            "WARNING: only choose 'ignore' or 'revalidate' if "
                            "you know what you are doing.",
                            options=(
                                ('delete', 'delete invalid files'),
                                ('abort', 'raise an error'),
                                ('ignore', 'proceed without doing anything'),
                                ('revalidate', "don't delete any cache files but write a new cache-state file")),
                            help=CACHE_HELP.format(
                                experiment=self.__class__.__name__,
                                filetype='cache and/or result'),
                        )
                        if command == 'delete':
                            pass
                        elif command == 'abort':
                            raise RuntimeError("User aborted invalid cache deletion")
                        elif command == 'ignore':
                            log.warning("Ignoring invalid cache")
                            return
                        elif command == 'revalidate':
                            log.warning("Revalidating invalid cache")
                            files.clear()
                        else:
                            raise RuntimeError("command=%s" % repr(command))
                    elif self.auto_delete_cache is not True:
                        raise TypeError(f"MneExperiment.auto_delete_cache={self.auto_delete_cache!r}")

                    # delete invalid files
                    n_cache_files = len(files) - n_result_files
                    descs = []
                    if n_result_files:
                        descs.append("%i invalid result files" % n_result_files)
                    if n_cache_files:
                        descs.append("%i invalid cache files" % n_cache_files)
                    log.info("Deleting " + (' and '.join(descs)) + '...')
                    for path in files:
                        os.remove(path)
                else:
                    log.debug("No existing cache files affected.")
            else:
                log.debug("Cache up to date.")
        elif cache_dir_existed:  # cache-dir but no history
            if self.auto_delete_cache is True:
                log.info("Deleting cache-dir without history")
                shutil.rmtree(cache_dir)
                os.mkdir(cache_dir)
            elif self.auto_delete_cache == 'disable':
                log.warning("Ignoring cache-dir without history")
            elif self.auto_delete_cache == 'debug':
                command = ask("Cache directory without history",
                              (('validate', 'write a history file treating cache as valid'),
                               ('abort', 'raise an error')))
                if command == 'abort':
                    raise RuntimeError("User aborted")
                elif command == 'validate':
                    log.warning("Validating cache-dir without history")
                else:
                    raise RuntimeError("command=%r" % (command,))
            else:
                raise IOError("Cache directory without history, but auto_delete_cache is not True")
        elif not exists(cache_dir):
            os.mkdir(cache_dir)

        new_state = {'version': CACHE_STATE_VERSION,
                     'raw': raw_state,
                     'groups': self._groups,
                     'epochs': epoch_state,
                     'tests': tests_state,
                     'parcs': parcs_state,
                     'events': events}
        save.pickle(new_state, cache_state_path)

    def _subclass_init(self):
        "Allow subclass to register experimental features"

    def __iter__(self):
        "Iterate state through subjects and yield each subject name."
        for subject in self.iter():
            yield subject

    # mtime methods
    # -------------
    # _mtime() functions return the time at which any input files affecting the
    # given file changed, and None if inputs are missing. They don't check
    # whether the file actually exists (usually there is no need to recompute an
    # intermediate file if it is not needed).
    # _file_mtime() functions directly return the file's mtime, or None if it
    # does not exists or is outdated
    def _annot_file_mtime(self, make_for=None):
        """Return max mtime of annot files or None if they do not exist.

        Can be user input, so we need to check the actual file.
        """
        if make_for:
            with self._temporary_state:
                self.make_annot(mrisubject=make_for)
                return self._annot_file_mtime()

        mtime = 0
        for _ in self.iter('hemi'):
            fpath = self.get('annot-file')
            if exists(fpath):
                mtime = max(mtime, getmtime(fpath))
            else:
                return
        return mtime

    def _cov_mtime(self):
        params = self._covs[self.get('cov')]
        with self._temporary_state:
            if 'epoch' in params:
                self.set(epoch=params['epoch'])
                return self._epochs_mtime()
            else:
                self.set(session=params['session'])
                return self._raw_mtime()

    def _epochs_mtime(self):
        raw_mtime = self._raw_mtime()
        if raw_mtime:
            epoch = self._epochs[self.get('epoch')]
            rej_mtime = self._rej_mtime(epoch)
            if rej_mtime:
                return max(raw_mtime, rej_mtime)

    def _epochs_stc_mtime(self):
        "Mtime affecting source estimates; does not check annot"
        epochs_mtime = self._epochs_mtime()
        if epochs_mtime:
            inv_mtime = self._inv_mtime()
            if inv_mtime:
                return max(epochs_mtime, inv_mtime)

    def _evoked_mtime(self):
        return self._epochs_mtime()

    def _evoked_stc_mtime(self):
        "Mtime if up-to-date, else None; do not check annot"
        evoked_mtime = self._evoked_mtime()
        if evoked_mtime:
            inv_mtime = self._inv_mtime()
            if inv_mtime:
                return max(evoked_mtime, inv_mtime)

    def _fwd_mtime(self, subject=None, recording=None, fwd_recording=None):
        "The last time at which input files affecting fwd-file changed"
        trans = self.get('trans-file')
        if exists(trans):
            src = self.get('src-file')
            if exists(src):
                if fwd_recording is None:
                    fwd_recording = self._get_fwd_recording(subject, recording)
                raw_mtime = self._raw_mtime('raw', False, subject, fwd_recording)
                if raw_mtime:
                    trans_mtime = getmtime(trans)
                    src_mtime = getmtime(src)
                    return max(raw_mtime, trans_mtime, src_mtime)

    def _inv_mtime(self):
        fwd_mtime = self._fwd_mtime()
        if fwd_mtime:
            cov_mtime = self._cov_mtime()
            if cov_mtime:
                return max(cov_mtime, fwd_mtime)

    def _raw_mtime(self, raw=None, bad_chs=True, subject=None, recording=None):
        if raw is None:
            raw = self.get('raw')
        elif raw not in self._raw:
            raise RuntimeError(f"raw-mtime with raw={raw!r}")
        pipe = self._raw[raw]
        if subject is None:
            subject = self.get('subject')
        if recording is None:
            recording = self.get('recording')
        return pipe.mtime(subject, recording, bad_chs)

    def _rej_mtime(self, epoch):
        """rej-file mtime for secondary epoch definition

        Parameters
        ----------
        epoch : dict
            Epoch definition.
        """
        rej = self._artifact_rejection[self.get('rej')]
        if rej['kind'] is None:
            return 1  # no rejection
        with self._temporary_state:
            paths = [self.get('rej-file', epoch=e) for e in epoch.rej_file_epochs]
        if all(exists(path) for path in paths):
            mtime = max(getmtime(path) for path in paths)
            return mtime

    def _result_file_mtime(self, dst, data, single_subject=False):
        """MTime if up-to-date, else None (for reports and movies)

        Parameters
        ----------
        dst : str
            Filename.
        data : TestDims
            Data type.
        single_subject : bool
            Whether the corresponding test is performed for a single subject
            (as opposed to the current group).
        """
        if exists(dst):
            mtime = self._result_mtime(data, single_subject)
            if mtime:
                dst_mtime = getmtime(dst)
                if dst_mtime > mtime:
                    return dst_mtime

    def _result_mtime(self, data, single_subject):
        "See ._result_file_mtime() above"
        if data.source:
            if data.parc_level:
                if single_subject:
                    out = self._annot_file_mtime(self.get('mrisubject'))
                elif data.parc_level == 'common':
                    out = self._annot_file_mtime(self.get('common_brain'))
                elif data.parc_level == 'individual':
                    out = 0
                    for _ in self:
                        mtime = self._annot_file_mtime()
                        if mtime is None:
                            return
                        else:
                            out = max(out, mtime)
                else:
                    raise RuntimeError(f"data={data.string!r}, parc_level={data.parc_level!r}")
            else:
                out = 1

            if not out:
                return
            mtime_func = self._epochs_stc_mtime
        else:
            out = 1
            mtime_func = self._epochs_mtime

        if single_subject:
            mtime_iterator = (mtime_func(),)
        else:
            mtime_iterator = (mtime_func() for _ in self)

        for mtime in mtime_iterator:
            if not mtime:
                return
            out = max(out, mtime)
        return out

    def _process_subject_arg(self, subjects, kwargs):
        """Process subject arg for methods that work on groups and subjects

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        kwargs : dict
            Additional state parameters to set.

        Returns
        -------
        subject : None | str
            Subject name if the value specifies a subject, None otherwise.
        group : None | str
            Group name if the value specifies a group, None otherwise.
        """
        if subjects is None:  # default:
            subjects = -1 if 'group' in kwargs else 1
        elif subjects is True:  # legacy value:
            subjects = -1

        if isinstance(subjects, int):
            if subjects == 1:
                return self.get('subject', **kwargs), None
            elif subjects == -1:
                return None, self.get('group', **kwargs)
            else:
                raise ValueError(f"subjects={subjects}")
        elif isinstance(subjects, str):
            if subjects in self.get_field_values('group'):
                if 'group' in kwargs:
                    if kwargs['group'] != subjects:
                        raise ValueError(f"group={kwargs['group']!r} inconsistent with subject={subjects!r}")
                    self.set(**kwargs)
                else:
                    self.set(group=subjects, **kwargs)
                return None, subjects
            else:
                return self.get('subject', subject=subjects, **kwargs), None
        else:
            raise TypeError(f"subjects={subjects!r}")

    def _cluster_criteria_kwargs(self, data):
        criteria = self._cluster_criteria[self.get('select_clusters')]
        return {'min' + dim: criteria[dim] for dim in data.dims if dim in criteria}

    def _add_vars(self, ds, vardef):
        """Add vars to the dataset

        Parameters
        ----------
        ds : Dataset
            Event dataset.
        vardef : dict | tuple
            Variable definition.
        """
        if isinstance(vardef, str):
            try:
                vardef = self._tests[vardef].vars
            except KeyError:
                raise ValueError(f"vardef={vardef!r}")
        elif not isinstance(vardef, Variables):
            vardef = Variables(vardef)
        vardef.apply(ds, self)

    def _backup(self, dst_root, v=False):
        """Backup all essential files to ``dst_root``.

        .. warning::
            Method is out of data and probably does not work as expected.

        Parameters
        ----------
        dst_root : str
            Directory to use as root for the backup.
        v : bool
            Verbose mode:  list all files that will be copied and ask for
            confirmation.

        Notes
        -----
        For repeated backups ``dst_root`` can be the same. If a file has been
        previously backed up, it is only copied if the local copy has been
        modified more recently than the previous backup. If the backup has been
        modified more recently than the local copy, a warning is displayed.

        Currently, the following files are included in the backup::

         * All rejection files
         * The trans-file
         * All files in the ``meg/{subject}/logs`` directory
         * For scaled MRIs, the file specifying the scale parameters

        MRIs are currently not backed up.
        """
        self._log.debug("Initiating backup to %s" % dst_root)
        root = self.get('root')
        root_len = len(root) + 1

        dirs = []  # directories to create
        pairs = []  # (src, dst) pairs to copy
        for temp, state_mod in self._backup_files:
            # determine state
            if state_mod:
                state = self._backup_state.copy()
                state.update(state_mod)
            else:
                state = self._backup_state

            # find files to back up
            if temp.endswith('dir'):
                paths = []
                for dirpath in self.glob(temp, **state):
                    for root_, _, filenames in os.walk(dirpath):
                        paths.extend(join(root_, fn) for fn in filenames)
            else:
                paths = self.glob(temp, **state)

            # convert to (src, dst) pairs
            for src in paths:
                if not src.startswith(root):
                    raise ValueError("Can only backup files in root directory")
                tail = src[root_len:]
                dst = join(dst_root, tail)
                if exists(dst):
                    src_m = getmtime(src)
                    dst_m = getmtime(dst)
                    if dst_m == src_m:
                        continue
                    elif dst_m > src_m:
                        self._log.warning("Backup more recent than original: %s", tail)
                        continue
                else:
                    i = 0
                    while True:
                        i = tail.find(os.sep, i + 1)
                        if i == -1:
                            break
                        path = tail[:i]
                        if path not in dirs:
                            dirs.append(path)

                pairs.append((src, dst))

        if len(pairs) == 0:
            if v:
                print("All files backed up.")
            else:
                self._log.info("All files backed up.")
            return

        # verbose file list
        if v:
            paths = [relpath(src, root) for src, _ in pairs]
            print('\n'.join(paths))
            cmd = 'x'
            while cmd not in 'yn':
                cmd = input("Proceed ([y]/n)? ")
            if cmd == 'n':
                print("Abort.")
                return
            else:
                print("Backing up %i files ..." % len(pairs))

        self._log.info("Backing up %i files ..." % len(pairs))
        # create directories
        for dirname in dirs:
            dirpath = join(dst_root, dirname)
            if not exists(dirpath):
                os.mkdir(dirpath)
        # copy files
        for src, dst in pairs:
            shutil.copy2(src, dst)

    def clear_cache(self, level=1):
        """Remove cached files.

        Parameters
        ----------
        level : int
            Level up to which to clear the cache (see notes below). The default
            is 1, which deletes all cached files.

        Notes
        -----
        Each lower level subsumes the higher levels:

        ``1``
            Delete all cached files.
        ``2``
            Epoched files - these need to be cleared when anything about the
            epoch definition changes (tmin, tmax, event inclusion, ...). Note
            that you might also have to manually update epoch rejection files
            with the :meth:`MneExperiment.make_epoch_selection` method.
        ``5``
            tests - these need to be cleared when the members of the relevant
            subject groups change.

        Examples
        --------
        To delete only test files, after adding raw data for a new subject to
        the experiment::

            >>> e.clear_cache(5)

        To delete cached data files after changing the selection criteria for
        a secondary epoch::

            >>> e.clear_cache(2)

        If criteria on a primary epoch are changed, the trial rejection has to
        be re-done in addition to clearing the cache.

        To delete all cached files and clear up hard drive space::

            >>> e.clear_cache(1)
        """
        if level <= 1:
            self.rm('cache-dir', confirm=True)
            print("All cached data cleared.")
        else:
            if level <= 2:
                self.rm('evoked-dir', confirm=True)
                self.rm('cov-dir', confirm=True)
                print("Cached epoch data cleared")
            if level <= 5:
                self.rm('test-dir', confirm=True)
                print("Cached tests cleared.")

    def get_field_values(self, field, exclude=(), **state):
        """Find values for a field taking into account exclusion

        Parameters
        ----------
        field : str
            Field for which to find values.
        exclude : list of str
            Exclude these values.
        ...
            State parameters.
        """
        if state:
            self.set(**state)
        if isinstance(exclude, str):
            exclude = (exclude,)

        if field == 'mrisubject':
            subjects = FileTree.get_field_values(self, 'subject')
            mri_subjects = self._mri_subjects[self.get('mri')]
            mrisubjects = sorted(mri_subjects[s] for s in subjects)
            if exclude:
                mrisubjects = [s for s in mrisubjects if s not in exclude]
            common_brain = self.get('common_brain')
            if common_brain and (not exclude or common_brain not in exclude):
                mrisubjects.insert(0, common_brain)
            return mrisubjects
        else:
            return FileTree.get_field_values(self, field, exclude)

    def _get_fwd_recording(self, subject: str = None, recording: str = None) -> str:
        if subject is None:
            subject = self.get('subject')
        if recording is None:
            recording = self.get('recording')
        try:
            return self._dig_sessions[subject][recording]
        except KeyError:
            raise FileMissing(f"Raw data missing for {subject}, session {recording}")

    def iter(self, fields='subject', exclude=None, values=None, group=None, progress_bar=None, **kwargs):
        """
        Cycle the experiment's state through all values on the given fields

        Parameters
        ----------
        fields : sequence | str
            Field(s) over which should be iterated.
        exclude : dict  {str: iterator over str}
            Exclude values from iteration (``{field: values_to_exclude}``).
        values : dict  {str: iterator over str}
            Fields with custom values to iterate over (instead of the
            corresponding field values) with {name: (sequence of values)}
            entries.
        group : None | str
            If iterating over subjects, use this group ('all' for all except
            excluded subjects, 'all!' for all including excluded subjects, or
            a name defined in experiment.groups).
        progress_bar : str
            Message to show in the progress bar.
        ...
            Fields with constant values throughout the iteration.
        """
        if group is not None:
            kwargs['group'] = group
        return FileTree.iter(self, fields, exclude, values, progress_bar, **kwargs)

    def iter_range(self, start=None, stop=None, field='subject'):
        """Iterate through a range on a field with ordered values.

        Parameters
        ----------
        start : None | str
            Start value (inclusive). With ``None``, begin at the first value.
        stop : None | str
            Stop value (inclusive). With ``None``, end with the last value.
        field : str
            Name of the field.

        Returns
        -------
        iterator over value : str
            Current field value.
        """
        values = self.get_field_values(field)
        if start is not None:
            start = values.index(start)
        if stop is not None:
            stop = values.index(stop) + 1
        values = values[start:stop]

        with self._temporary_state:
            for value in values:
                self._restore_state(discard_tip=False)
                self.set(**{field: value})
                yield value

    def _label_events(self, ds):
        # add standard variables
        ds['T'] = ds['i_start'] / ds.info['sfreq']
        ds['SOA'] = ds['T'].diff(0)
        ds['subject'] = Factor([ds.info['subject']], repeat=ds.n_cases, random=True)
        if len(self._sessions) > 1:
            ds[:, 'session'] = ds.info['session']
        if len(self._visits) > 1:
            ds[:, 'visit'] = ds.info['visit']
        self._variables.apply(ds, self)

        # subclass label_events
        info = ds.info
        ds = self.label_events(ds)
        if not isinstance(ds, Dataset):
            raise DefinitionError(f"{self.__class__.__name__}.label_events() needs to return the events Dataset. Got {ds!r}.")
        elif 'i_start' not in ds:
            raise DefinitionError(f"The Dataset returned by {self.__class__.__name__}.label_events() does not contain a variable called `i_start`. This variable is required to ascribe events to data samples.")
        elif 'trigger' not in ds:
            raise DefinitionError(f"The Dataset returned by {self.__class__.__name__}.label_events() does not contain a variable called `trigger`. This variable is required to check rejection files.")
        elif ds.info is not info:
            ds.info.update(info)
        return ds

    def label_events(self, ds):
        """Add event labels to events loaded from raw files

        Parameters
        ----------
        ds : Dataset
            A Dataset containing events (with variables as returned by
            :func:`load.fiff.events`).

        Notes
        -----
        Override this method in MneExperiment subclasses to add event labels.
        The session that the events are from can be determined with
        ``ds.info['session']``.
        Calling the original (super-class) method is not necessary.
        """
        return ds

    def label_subjects(self, ds):
        """Label the subjects in ds

        Creates a boolean :class:`Var` in ``ds`` for each group marking group
        membership.

        Parameters
        ----------
        ds : Dataset
            A Dataset with 'subject' entry.
        """
        subject = ds['subject']
        for name, subjects in self._groups.items():
            ds[name] = Var(subject.isin(subjects))

    def label_groups(self, subject, groups):
        """Generate Factor for group membership

        Parameters
        ----------
        subject : Factor
            A Factor with subjects.
        groups : list of str | {str: str} dict
            Groups which to label (raises an error if group membership is not
            unique). To use labels other than the group names themselves, use
            a ``{group: label}`` dict.

        Returns
        -------
        group : Factor
            A :class:`Factor` that labels the group for each subject.
        """
        if not isinstance(groups, dict):
            groups = {g: g for g in groups}
        labels = {s: [l for g, l in groups.items() if s in self._groups[g]] for s in subject.cells}
        problems = [s for s, g in labels.items() if len(g) != 1]
        if problems:
            desc = (', '.join(labels[s]) if labels[s] else 'no group' for s in problems)
            msg = ', '.join('%s (%s)' % pair for pair in zip(problems, desc))
            raise ValueError(f"Groups {groups} are not unique for subjects: {msg}")
        labels = {s: g[0] for s, g in labels.items()}
        return Factor(subject, labels=labels)

    def load_annot(self, **state):
        """Load a parcellation (from an annot file)

        Returns
        -------
        labels : list of Label
            Labels in the parcellation (output of
            :func:`mne.read_labels_from_annot`).
        ...
            State parameters.
        """
        self.make_annot(**state)
        return mne.read_labels_from_annot(self.get('mrisubject'),
                                          self.get('parc'), 'both',
                                          subjects_dir=self.get('mri-sdir'))

    def load_bad_channels(self, **kwargs):
        """Load bad channels
        
        Parameters
        ----------
        ...
            State parameters.

        Returns
        -------
        bad_chs : list of str
            Bad chnnels.
        """
        pipe = self._raw[self.get('raw', **kwargs)]
        return pipe.load_bad_channels(self.get('subject'), self.get('recording'))

    def _load_bem(self):
        subject = self.get('mrisubject')
        if subject == 'fsaverage' or is_fake_mri(self.get('mri-dir')):
            return mne.read_bem_surfaces(self.get('bem-file'))
        else:
            bem_dir = self.get('bem-dir')
            surfs = ('inner_skull', 'outer_skull', 'outer_skin')
            paths = {s: join(bem_dir, s + '.surf') for s in surfs}
            missing = [s for s in surfs if not exists(paths[s])]
            if missing:
                bem_dir = self.get('bem-dir')
                temp = join(".*", "bem", "(.*)")
                for surf in missing[:]:
                    path = paths[surf]
                    if os.path.islink(path):
                        # try to fix broken symlinks
                        old_target = os.readlink(path)
                        m = re.match(temp, old_target)
                        if m:
                            new_target = m.group(1)
                            if exists(join(bem_dir, new_target)):
                                self._log.info("Fixing broken symlink for %s "
                                               "%s surface file", subject, surf)
                                os.unlink(path)
                                os.symlink(new_target, path)
                                missing.remove(surf)
                        #         continue
                        # self._log.info("Deleting broken symlink " + path)
                        # os.unlink(path)
                if missing:
                    self._log.info("%s %s missing for %s. Running "
                                   "mne.make_watershed_bem()...",
                                   enumeration(missing).capitalize(),
                                   plural('surface', len(missing)), subject)
                    # re-run watershed_bem
                    # mne-python expects the environment variable
                    os.environ['FREESURFER_HOME'] = subp.get_fs_home()
                    mne.bem.make_watershed_bem(subject, self.get('mri-sdir'),
                                               overwrite=True)

            return mne.make_bem_model(subject, conductivity=(0.3,),
                                      subjects_dir=self.get('mri-sdir'))

    def load_cov(self, **kwargs):
        """Load the covariance matrix

        Parameters
        ----------
        ...
            State parameters.
        """
        return mne.read_cov(self.get('cov-file', make=True, **kwargs))

    def load_edf(self, **kwargs):
        """Load the edf file ("edf-file" template)
        
        Parameters
        ----------
        ...
            State parameters.
        """
        path = self.get('edf-file', fmatch=False, **kwargs)
        return load.eyelink.Edf(path)

    def load_epochs(self, subjects=None, baseline=False, ndvar=True,
                    add_bads=True, reject=True, cat=None,
                    decim=None, pad=0, data_raw=False, vardef=None, data='sensor',
                    trigger_shift=True, tmin=None,
                    tmax=None, tstop=None, interpolate_bads=False, **kwargs):
        """
        Load a Dataset with epochs for a given epoch definition

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        baseline : bool | tuple
            Apply baseline correction using this period. True to use the
            epoch's baseline specification. The default is to not apply baseline
            correction.
        ndvar : bool | 'both'
            Convert epochs to an NDVar (named 'meg' for MEG data and 'eeg' for
            EEG data). Use 'both' to include NDVar and MNE Epochs.
        add_bads : bool | list
            Add bad channel information to the Raw. If True, bad channel
            information is retrieved from the bad channels file. Alternatively,
            a list of bad channels can be specified.
        reject : bool | 'keep'
            Reject bad trials. If ``True`` (default), bad trials are removed
            from the Dataset. Set to ``False`` to ignore the trial rejection.
            Set ``reject='keep'`` to load the rejection (added it to the events
            as ``'accept'`` variable), but keep bad trails.
        cat : sequence of cell-names
            Only load data for these cells (cells of model).
        decim : int
            Data decimation factor (the default is the factor specified in the
            epoch definition).
        pad : scalar
            Pad the epochs with this much time (in seconds; e.g. for spectral
            analysis).
        data_raw : bool
            Keep the :class:`mne.io.Raw` instance in ``ds.info['raw']``
            (default False).
        vardef : str
            Name of a 2-stage test defining additional variables.
        data : str
            Data to load; 'sensor' to load all sensor data (default);
            'sensor.rms' to return RMS over sensors. Only applies to NDVar
            output.
        trigger_shift : bool
            Apply post-baseline trigger-shift if it applies to the epoch
            (default True).
        tmin : scalar
            Override the epoch's ``tmin`` parameter.
        tmax : scalar
            Override the epoch's ``tmax`` parameter.
        tstop : scalar
            Override the epoch's ``tmax`` parameter as exclusive ``tstop``.
        interpolate_bads : bool
            Interpolate channels marked as bad for the whole recording (useful
            when comparing topographies across subjects; default False).
        ...
            Applicable :ref:`state-parameters`:

             - :ref:`state-raw`: preprocessing pipeline
             - :ref:`state-epoch`: which events to use and time window
             - :ref:`state-rej`: which trials to use

        """
        data = TestDims.coerce(data)
        if not data.sensor:
            raise ValueError(f"data={data.string!r}; load_evoked is for loading sensor data")
        elif data.sensor is not True:
            if not ndvar:
                raise ValueError(f"data={data.string!r} with ndvar=False")
            elif interpolate_bads:
                raise ValueError(f"interpolate_bads={interpolate_bads!r} with data={data.string}")
        if ndvar:
            if isinstance(ndvar, str):
                if ndvar != 'both':
                    raise ValueError("ndvar=%s" % repr(ndvar))
        subject, group = self._process_subject_arg(subjects, kwargs)

        if group is not None:
            dss = []
            for _ in self.iter(group=group):
                ds = self.load_epochs(None, baseline, ndvar, add_bads, reject, cat, decim, pad, data_raw, vardef, data, True, tmin, tmax, tstop, interpolate_bads)
                dss.append(ds)

            return combine(dss)

        # single subject
        epoch = self._epochs[self.get('epoch')]
        if isinstance(epoch, EpochCollection):
            dss = []
            with self._temporary_state:
                for sub_epoch in epoch.collect:
                    ds = self.load_epochs(subject, baseline, ndvar, add_bads, reject, cat, decim, pad, data_raw, vardef, data, trigger_shift, tmin, tmax, tstop, interpolate_bads, epoch=sub_epoch)
                    ds[:, 'epoch'] = sub_epoch
                    dss.append(ds)
            return combine(dss)

        if isinstance(add_bads, str):
            if add_bads == 'info':
                add_bads_to_info = True
                add_bads = True
            else:
                raise ValueError(f"add_bads={add_bads!r}")
        else:
            add_bads_to_info = False

        with self._temporary_state:
            ds = self.load_selected_events(add_bads=add_bads, reject=reject, data_raw=True, vardef=vardef, cat=cat)
            if ds.n_cases == 0:
                err = f"No events left for epoch={epoch.name!r}, subject={subject!r}"
                if cat:
                    err += f", cat={cat!r}"
                raise RuntimeError(err)

        # load sensor space data
        if tmin is None:
            tmin = epoch.tmin
        if tmax is None and tstop is None:
            tmax = epoch.tmax
        if baseline is True:
            baseline = epoch.baseline
        if pad:
            tmin -= pad
            tmax += pad
        decim = decim_param(epoch, decim, ds.info['raw'].info)

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', 'The events passed to the Epochs constructor', RuntimeWarning)
            ds = load.fiff.add_mne_epochs(ds, tmin, tmax, baseline, decim=decim, drop_bad_chs=False, tstop=tstop)

        # post baseline-correction trigger shift
        if trigger_shift and epoch.post_baseline_trigger_shift:
            ds['epochs'] = shift_mne_epoch_trigger(ds['epochs'],
                                                   ds[epoch.post_baseline_trigger_shift],
                                                   epoch.post_baseline_trigger_shift_min,
                                                   epoch.post_baseline_trigger_shift_max)
        info = ds['epochs'].info
        data_to_ndvar = data.data_to_ndvar(info)

        # determine channels to interpolate
        bads_all = None
        bads_individual = None
        if interpolate_bads:
            bads_all = info['bads']
            if ds.info[INTERPOLATE_CHANNELS] and any(ds[INTERPOLATE_CHANNELS]):
                bads_individual = ds[INTERPOLATE_CHANNELS]
                if bads_all:
                    bads_all = set(bads_all)
                    bads_individual = [sorted(bads_all.union(bads)) for bads in bads_individual]

        # interpolate bad channels
        if bads_all:
            if isinstance(interpolate_bads, str):
                if interpolate_bads == 'keep':
                    reset_bads = False
                else:
                    raise ValueError(f"interpolate_bads={interpolate_bads}")
            else:
                reset_bads = True
            ds['epochs'].interpolate_bads(reset_bads=reset_bads)

        # interpolate channels
        if reject and bads_individual:
            if 'mag' in data_to_ndvar:
                interp_path = self.get('interp-file')
                if exists(interp_path):
                    interp_cache = load.unpickle(interp_path)
                else:
                    interp_cache = {}
                n_in_cache = len(interp_cache)
                _interpolate_bads_meg(ds['epochs'], bads_individual, interp_cache)
                if len(interp_cache) > n_in_cache:
                    save.pickle(interp_cache, interp_path)
            if 'eeg' in data_to_ndvar:
                _interpolate_bads_eeg(ds['epochs'], bads_individual)

        if ndvar:
            pipe = self._raw[self.get('raw')]
            exclude = () if add_bads_to_info else 'bads'
            for data_kind in data_to_ndvar:
                sysname = pipe.get_sysname(info, ds.info['subject'], data_kind)
                connectivity = pipe.get_connectivity(data_kind)
                name = 'meg' if data_kind == 'mag' else data_kind
                ds[name] = load.fiff.epochs_ndvar(ds['epochs'], data=data_kind, sysname=sysname, connectivity=connectivity, exclude=exclude)
                if add_bads_to_info:
                    ds[name].info[BAD_CHANNELS] = ds['epochs'].info['bads']
                if isinstance(data.sensor, str):
                    ds[name] = getattr(ds[name], data.sensor)('sensor')

            if ndvar != 'both':
                del ds['epochs']

        if not data_raw:
            del ds.info['raw']

        return ds

    def load_epochs_stc(self, subjects=None, baseline=True, src_baseline=False, cat=None, keep_epochs=False, morph=False, mask=False, data_raw=False, vardef=None, decim=None, ndvar=True, reject=True, **state):
        """Load a Dataset with stcs for single epochs

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
            Warning: loading single trial data for multiple subjects at once
            uses a lot of memory, which can lead to a periodically unresponsive
            terminal).
        baseline : bool | tuple
            Apply baseline correction using this period in sensor space.
            True to use the epoch's baseline specification (default).
        src_baseline : bool | tuple
            Apply baseline correction using this period in source space.
            True to use the epoch's baseline specification. The default is to
            not apply baseline correction.
        cat : sequence of cell-names
            Only load data for these cells (cells of model).
        keep_epochs : bool | 'ndvar' | 'both'
            Keep the sensor space data in the Dataset that is returned (default
            False; True to keep :class:`mne.Epochs` object; ``'ndvar'`` to keep
            :class:`NDVar`; ``'both'`` to keep both).
        morph : bool
            Morph the source estimates to the common_brain (default False).
        mask : bool | str
            Discard data that is labelled 'unknown' by the parcellation (only
            applies to NDVars, default False).
        data_raw : bool
            Keep the :class:`mne.io.Raw` instance in ``ds.info['raw']``
            (default False).
        vardef : str
            Name of a 2-stage test defining additional variables.
        decim : int
            Override the epoch decim factor.
        ndvar : bool
            Add the source estimates as :class:`NDVar` named "src" instead of a list of
            :class:`mne.SourceEstimate` objects named "stc" (default True).
        reject : bool | 'keep'
            Reject bad trials. If ``True`` (default), bad trials are removed
            from the Dataset. Set to ``False`` to ignore the trial rejection.
            Set ``reject='keep'`` to load the rejection (added it to the events
            as ``'accept'`` variable), but keep bad trails.
        ...
            Applicable :ref:`state-parameters`:

             - :ref:`state-raw`: preprocessing pipeline
             - :ref:`state-epoch`: which events to use and time window
             - :ref:`state-rej`: which trials to use
             - :ref:`state-cov`: covariance matrix for inverse solution
             - :ref:`state-src`: source space
             - :ref:`state-inv`: inverse solution

        Returns
        -------
        epochs_dataset : Dataset
            Dataset containing single trial data (epochs).
        """
        if 'sns_baseline' in state:
            baseline = state.pop('sns_baseline')
            warnings.warn("The sns_baseline parameter is deprecated, use baseline instead", DeprecationWarning)
        epoch = self._epochs[self.get('epoch')]
        if not baseline and src_baseline and epoch.post_baseline_trigger_shift:
            raise NotImplementedError("src_baseline with post_baseline_trigger_shift")
        subject, group = self._process_subject_arg(subjects, state)
        if group is not None:
            if data_raw:
                raise ValueError(f"data_raw={data_raw!r} with group: Can not combine raw data from multiple subjects.")
            elif keep_epochs:
                raise ValueError(f"keep_epochs={keep_epochs!r} with group: Can not combine Epochs objects for different subjects. Set keep_epochs=False (default).")
            elif not morph:
                raise ValueError(f"morph={morph!r} with group: Source estimates can only be combined after morphing data to common brain model. Set morph=True.")
            dss = []
            for _ in self.iter(group=group):
                ds = self.load_epochs_stc(None, baseline, src_baseline, cat, keep_epochs, morph, mask, False, vardef, decim, ndvar, reject)
                dss.append(ds)
            return combine(dss)

        if keep_epochs is True:
            sns_ndvar = False
            del_epochs = False
        elif keep_epochs is False:
            sns_ndvar = False
            del_epochs = True
        elif keep_epochs == 'ndvar':
            sns_ndvar = 'both'
            del_epochs = True
        elif keep_epochs == 'both':
            sns_ndvar = 'both'
            del_epochs = False
        else:
            raise ValueError(f'keep_epochs={keep_epochs!r}')

        ds = self.load_epochs(subject, baseline, sns_ndvar, reject=reject, cat=cat, decim=decim, data_raw=data_raw, vardef=vardef)

        # load inv
        if src_baseline is True:
            src_baseline = epoch.baseline
        parc = self.get('parc') or None
        if isinstance(mask, str) and parc != mask:
            parc = mask
            self.set(parc=mask)
        # make sure annotation exists
        if parc:
            self.make_annot()
        epochs = ds['epochs']
        inv = self.load_inv(epochs)

        # determine whether initial source-space can be restricted
        mri_sdir = self.get('mri-sdir')
        mrisubject = self.get('mrisubject')
        is_scaled = find_source_subject(mrisubject, mri_sdir)
        if mask and (is_scaled or not morph):
            label = label_from_annot(inv['src'], mrisubject, mri_sdir, parc)
        else:
            label = None
        stc = apply_inverse_epochs(epochs, inv, label=label, **self._params['apply_inv_kw'])

        if ndvar:
            src = self.get('src')
            src = load.fiff.stc_ndvar(
                stc, mrisubject, src, mri_sdir, self._params['apply_inv_kw']['method'],
                self._params['make_inv_kw'].get('fixed', False), parc=parc,
                connectivity=self.get('connectivity'))
            if src_baseline:
                src -= src.summary(time=src_baseline)

            if morph:
                common_brain = self.get('common_brain')
                with self._temporary_state:
                    self.make_annot(mrisubject=common_brain)
                ds['srcm'] = morph_source_space(src, common_brain)
                if mask and not is_scaled:
                    _mask_ndvar(ds, 'srcm')
            else:
                ds['src'] = src
        else:
            if src_baseline:
                raise NotImplementedError("Baseline for SourceEstimate")
            if morph:
                raise NotImplementedError("Morphing for SourceEstimate")
            ds['stc'] = stc

        if del_epochs:
            del ds['epochs']
        return ds

    def load_events(self, subject=None, add_bads=True, data_raw=True, **kwargs):
        """
        Load events from a raw file.

        Loads events from the corresponding raw file, adds the raw to the info
        dict.

        Parameters
        ----------
        subject : str
            Subject for which to load events (default is the current subject
            in the experiment's state).
        add_bads : False | True | list
            Add bad channel information to the Raw. If True, bad channel
            information is retrieved from the bad channels file. Alternatively,
            a list of bad channels can be specified.
        data_raw : bool
            Keep the :class:`mne.io.Raw` instance in ``ds.info['raw']``
            (default False).
        ...
            Applicable :ref:`state-parameters`:

             - :ref:`state-raw`: preprocessing pipeline
             - :ref:`state-epoch`: which events to use and time window

        """
        evt_file = self.get('event-file', mkdir=True, subject=subject, **kwargs)
        subject = self.get('subject')

        # search for and check cached version
        raw_mtime = self._raw_mtime(bad_chs=False, subject=subject)
        if exists(evt_file):
            ds = load.unpickle(evt_file)
            if ds.info['raw-mtime'] != raw_mtime:
                ds = None
        else:
            ds = None

        # refresh cache
        if ds is None:
            self._log.debug("Extracting events for %s %s %s", self.get('raw'), subject, self.get('recording'))
            raw = self.load_raw(add_bads)
            ds = load.fiff.events(raw)
            del ds.info['raw']
            ds.info['sfreq'] = raw.info['sfreq']
            ds.info['raw-mtime'] = raw_mtime

            # add edf
            if self.has_edf[subject]:
                edf = self.load_edf()
                edf.add_t_to(ds)
                ds.info['edf'] = edf

            save.pickle(ds, evt_file)
            if data_raw:
                ds.info['raw'] = raw
        elif data_raw:
            ds.info['raw'] = self.load_raw(add_bads)

        ds.info['subject'] = subject
        ds.info['session'] = self.get('session')
        if len(self._visits) > 1:
            ds.info['visit'] = self.get('visit')

        if self.trigger_shift:
            if isinstance(self.trigger_shift, dict):
                trigger_shift = self.trigger_shift[subject]
            else:
                trigger_shift = self.trigger_shift

            if trigger_shift:
                ds['i_start'] += int(round(trigger_shift * ds.info['sfreq']))

        return self._label_events(ds)

    def load_evoked(self, subjects=None, baseline=False, ndvar=True, cat=None,
                    decim=None, data_raw=False, vardef=None, data='sensor',
                    **kwargs):
        """
        Load a Dataset with the evoked responses for each subject.

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        baseline : bool | tuple
            Apply baseline correction using this period. True to use the
            epoch's baseline specification. The default is to not apply baseline
            correction.
        ndvar : bool
            Convert the mne Evoked objects to an NDVar (the name in the
            Dataset is 'meg' or 'eeg').
        cat : sequence of cell-names
            Only load data for these cells (cells of model).
        decim : int
            Data decimation factor (the default is the factor specified in the
            epoch definition).
        data_raw : bool
            Keep the :class:`mne.io.Raw` instance in ``ds.info['raw']``
            (default False).
        vardef : str
            Name of a 2-stage test defining additional variables.
        data : str
            Data to load; 'sensor' to load all sensor data (default);
            'sensor.rms' to return RMS over sensors. Only applies to NDVar
            output.
        ...
            Applicable :ref:`state-parameters`:

             - :ref:`state-raw`: preprocessing pipeline
             - :ref:`state-epoch`: which events to use and time window
             - :ref:`state-rej`: which trials to use
             - :ref:`state-model`: how to group trials into conditions
             - :ref:`state-equalize_evoked_count`: control number of trials per cell

        """
        subject, group = self._process_subject_arg(subjects, kwargs)
        epoch = self._epochs[self.get('epoch')]
        data = TestDims.coerce(data)
        if not data.sensor:
            raise ValueError(f"data={data.string!r}; load_evoked is for loading sensor data")
        elif data.sensor is not True and not ndvar:
            raise ValueError(f"data={data.string!r} with ndvar=False")
        if baseline is True:
            baseline = epoch.baseline

        if group is not None:
            # when aggregating across sensors, do it before combining subjects
            # to avoid losing sensors that are not shared
            individual_ndvar = isinstance(data.sensor, str)
            dss = [self.load_evoked(None, baseline, individual_ndvar, cat, decim, data_raw, vardef, data)
                   for _ in self.iter(group=group)]
            if individual_ndvar:
                ndvar = False
            elif ndvar:
                # set interpolated channels to good
                for ds in dss:
                    for e in ds['evoked']:
                        if e.info['description'] is None:
                            continue
                        m = re.match(r"Eelbrain (\d+)", e.info['description'])
                        if not m:
                            continue
                        v = int(m.group(1))
                        if v >= 11:
                            e.info['bads'] = []
            ds = combine(dss, incomplete='drop')

            # check consistency in MNE objects' number of time points
            lens = [len(e.times) for e in ds['evoked']]
            ulens = set(lens)
            if len(ulens) > 1:
                err = ["Unequal time axis sampling (len):"]
                alens = np.array(lens)
                for l in ulens:
                    err.append('%i: %r' % (l, ds['subject', alens == l].cells))
                raise DimensionMismatchError('\n'.join(err))
        else:  # single subject
            ds = self._make_evoked(decim, data_raw)

            if cat:
                model = self.get('model')
                if not model:
                    raise TypeError(f"cat={cat!r}: Can't set cat when model is ''")
                model = ds.eval(model)
                idx = model.isin(cat)
                ds = ds.sub(idx)
                if ds.n_cases == 0:
                    raise RuntimeError(f"Selection with cat={cat!r} resulted in empty Dataset")

            self._add_vars(ds, vardef)

            # baseline correction
            if isinstance(baseline, str):
                raise NotImplementedError
            elif baseline and not epoch.post_baseline_trigger_shift:
                for e in ds['evoked']:
                    rescale(e.data, e.times, baseline, 'mean', copy=False)

        # convert to NDVar
        if ndvar:
            pipe = self._raw[self.get('raw')]
            info = ds[0, 'evoked'].info
            for data_kind in data.data_to_ndvar(info):
                sysname = pipe.get_sysname(info, subject, data_kind)
                connectivity = pipe.get_connectivity(data_kind)
                name = 'meg' if data_kind == 'mag' else data_kind
                ds[name] = load.fiff.evoked_ndvar(ds['evoked'], data=data_kind, sysname=sysname, connectivity=connectivity)
                if data_kind != 'eog' and isinstance(data.sensor, str):
                    ds[name] = getattr(ds[name], data.sensor)('sensor')
            # if ndvar != 'both':
            #     del ds['evoked']

        return ds

    def load_epochs_stf(self, subjects=None, baseline=True, mask=True, morph=False, keep_stc=False, **state):
        """Load frequency space single trial data

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        baseline : bool | tuple
            Apply baseline correction using this period in sensor space.
            True to use the epoch's baseline specification. The default is True.
        mask : bool | str
            Discard data that is labelled 'unknown' by the parcellation (only
            applies to NDVars, default True).
        morph : bool
            Morph the source estimates to the common_brain (default False).
        keep_stc : bool
            Keep the source timecourse data in the Dataset that is returned
            (default False).
        ...
            State parameters.
        """
        if 'sns_baseline' in state:
            baseline = state.pop('sns_baseline')
            warnings.warn("The sns_baseline parameter is deprecated, use baseline instead", DeprecationWarning)
        ds = self.load_epochs_stc(subjects, baseline, ndvar=True, morph=morph, mask=mask, **state)
        name = 'srcm' if morph else 'src'

        # apply morlet transformation
        freq_params = self.freqs[self.get('freq')]
        freq_range = freq_params['frequencies']
        ds['stf'] = cwt_morlet(ds[name], freq_range, use_fft=True,
                               n_cycles=freq_params['n_cycles'],
                               zero_mean=False, out='magnitude')

        if not keep_stc:
            del ds[name]

        return ds

    def load_evoked_stf(self, subjects=None, baseline=True, mask=True, morph=False, keep_stc=False, **state):
        """Load frequency space evoked data

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        baseline : bool | tuple
            Apply baseline correction using this period in sensor space.
            True to use the epoch's baseline specification. The default is True.
        mask : bool | str
            Whether to just load the sources from the parcellation that are not
            defined as "unknown". Default is True.
        morph : bool
            Morph the source estimates to the common_brain (default False).
        keep_stc : bool
            Keep the source timecourse data in the Dataset that is returned
            (default False).
        ...
            State parameters.
        """
        if 'sns_baseline' in state:
            baseline = state.pop('sns_baseline')
            warnings.warn("The sns_baseline parameter is deprecated, use baseline instead", DeprecationWarning)
        ds = self.load_evoked_stc(subjects, baseline, morph=morph, mask=mask, **state)
        name = 'srcm' if morph else 'src'

        # apply morlet transformation
        freq_params = self.freqs[self.get('freq')]
        freq_range = freq_params['frequencies']
        ds['stf'] = cwt_morlet(ds[name], freq_range, use_fft=True,
                               n_cycles=freq_params['n_cycles'],
                               zero_mean=False, out='magnitude')

        if not keep_stc:
            del ds[name]

        return ds

    def load_evoked_stc(self, subjects=None, baseline=True, src_baseline=False,
                        cat=None, keep_evoked=False, morph=False, mask=False,
                        data_raw=False, vardef=None, decim=None, ndvar=True,
                        **state):
        """Load evoked source estimates.

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        baseline : bool | tuple
            Apply baseline correction using this period in sensor space.
            True to use the epoch's baseline specification. The default is True.
        src_baseline : bool | tuple
            Apply baseline correction using this period in source space.
            True to use the epoch's baseline specification. The default is to
            not apply baseline correction.
        cat : sequence of cell-names
            Only load data for these cells (cells of model).
        keep_evoked : bool
            Keep the sensor space data in the Dataset that is returned (default
            False).
        morph : bool
            Morph the source estimates to the common_brain (default False).
        mask : bool | str
            Discard data that is labelled 'unknown' by the parcellation (only
            applies to NDVars, default False). Can be set to a parcellation
            name or ``True`` to use the current parcellation.
        data_raw : bool
            Keep the :class:`mne.io.Raw` instance in ``ds.info['raw']``
            (default False).
        vardef : str
            Name of a 2-stage test defining additional variables.
        decim : int
            Override the epoch decim factor.
        ndvar : bool
            Add the source estimates as NDVar named "src" instead of a list of
            :class:`mne.SourceEstimate` objects named "stc" (default True).
        ...
            Applicable :ref:`state-parameters`:

             - :ref:`state-raw`: preprocessing pipeline
             - :ref:`state-epoch`: which events to use and time window
             - :ref:`state-rej`: which trials to use
             - :ref:`state-model`: how to group trials into conditions
             - :ref:`state-equalize_evoked_count`: control number of trials per cell
             - :ref:`state-cov`: covariance matrix for inverse solution
             - :ref:`state-src`: source space
             - :ref:`state-inv`: inverse solution

        """
        if 'sns_baseline' in state:
            baseline = state.pop('sns_baseline')
            warnings.warn("The sns_baseline parameter is deprecated, use baseline instead", DeprecationWarning)

        if state:
            self.set(**state)

        # check baseline
        epoch = self._epochs[self.get('epoch')]
        if src_baseline and epoch.post_baseline_trigger_shift:
            raise NotImplementedError(f"src_baseline={src_baseline!r}: post_baseline_trigger_shift is not implemented for baseline correction in source space")
        elif src_baseline is True:
            src_baseline = epoch.baseline

        # load sensor data
        sns_ndvar = keep_evoked and ndvar
        ds = self.load_evoked(subjects, baseline, sns_ndvar, cat, decim, data_raw, vardef)

        # from-subject for the purpose of morphing
        common_brain = self.get('common_brain')
        meg_subjects = ds['subject'].cells
        from_subjects = {}
        for subject in meg_subjects:
            if is_fake_mri(self.get('mri-dir', subject=subject)):
                subject_from = common_brain
            else:
                subject_from = self.get('mrisubject', subject=subject)
            from_subjects[subject] = subject_from

        # make sure annot files are available (needed only for NDVar)
        if ndvar:
            if morph:
                self.make_annot(mrisubject=common_brain)
            elif len(meg_subjects) > 1:
                raise ValueError(f"ndvar=True, morph=False with multiple subjects: Can't create ndvars with data from different brains")
            else:
                self.make_annot(subject=meg_subjects[0])

        # convert evoked objects
        stcs = []
        invs = {}
        mm_cache = CacheDict(self.load_morph_matrix, 'mrisubject')
        for subject, evoked in ds.zip('subject', 'evoked'):
            subject_from = from_subjects[subject]

            # get inv
            if subject in invs:
                inv = invs[subject]
            else:
                inv = invs[subject] = self.load_inv(evoked, subject=subject)

            # apply inv
            stc = apply_inverse(evoked, inv, **self._params['apply_inv_kw'])

            # baseline correction
            if src_baseline:
                rescale(stc._data, stc.times, src_baseline, 'mean', copy=False)

            if morph:
                if subject_from == common_brain:
                    stc.subject = common_brain
                else:
                    mm, v_to = mm_cache[subject_from]
                    stc = mne.morph_data_precomputed(subject_from, common_brain, stc, v_to, mm)
            stcs.append(stc)

        # add to Dataset
        src = self.get('src')
        parc = mask if isinstance(mask, str) else self.get('parc') or None
        mri_sdir = self.get('mri-sdir')
        if ndvar:
            if morph:
                key, subject = 'srcm', common_brain
            else:
                key, subject = 'src', meg_subjects[0]
            method = self._params['apply_inv_kw']['method']
            fixed = self._params['make_inv_kw'].get('fixed', False)
            ds[key] = load.fiff.stc_ndvar(stcs, subject, src, mri_sdir, method, fixed, parc=parc, connectivity=self.get('connectivity'))
            if mask:
                _mask_ndvar(ds, key)
        else:
            key = 'stcm' if morph else 'stc'
            ds[key] = stcs

        if not keep_evoked:
            del ds['evoked']

        return ds

    def load_fwd(self, surf_ori=True, ndvar=False, mask=None, **state):
        """Load the forward solution

        Parameters
        ----------
        surf_ori : bool
            Force surface orientation (default True; only applies if
            ``ndvar=False``, :class:`NDVar` forward operators are alsways
            surface based).
        ndvar : bool
            Return forward solution as :class:`NDVar` (default is
            :class:`mne.forward.Forward`).
        mask : str | bool
            Remove source labelled "unknown". Can be parcellation name or True,
            in which case the current parcellation is used.
        ...
            State parameters.

        Returns
        -------
        forward_operator : mne.forward.Forward | NDVar
            Forward operator.
        """
        if mask and not ndvar:
            raise NotImplementedError("mask is only implemented for ndvar=True")
        elif isinstance(mask, str):
            state['parc'] = mask
            mask = True
        fwd_file = self.get('fwd-file', make=True, **state)
        src = self.get('src')
        if ndvar:
            if src.startswith('vol'):
                parc = None
                assert mask is None
            else:
                self.make_annot()
                parc = self.get('parc')
            fwd = load.fiff.forward_operator(fwd_file, src, self.get('mri-sdir'), parc)
            if mask:
                fwd = fwd.sub(source=np.invert(
                    fwd.source.parc.startswith('unknown')))
            return fwd
        else:
            fwd = mne.read_forward_solution(fwd_file)
            if surf_ori:
                mne.convert_forward_solution(fwd, surf_ori, copy=False)
            return fwd

    def load_ica(self, **state):
        """Load the mne-python ICA object

        Returns
        -------
        ica : mne.preprocessing.ICA
            ICA object for the current raw/rej setting.
        ...
            State parameters.
        """
        path = self.make_ica(**state)
        return mne.preprocessing.read_ica(path)

    def load_inv(self, fiff=None, ndvar=False, mask=None, **state):
        """Load the inverse operator

        Parameters
        ----------
        fiff : Raw | Epochs | Evoked | ...
            Object which provides the mne info dictionary (default: load the
            raw file).
        ndvar : bool
            Return the inverse operator as NDVar (default is 
            :class:`mne.minimum_norm.InverseOperator`). The NDVar representation 
            does not take into account any direction selectivity (loose/free 
            orientation) or noise normalization properties.
        mask : str | bool
            Remove source labelled "unknown". Can be parcellation name or True,
            in which case the current parcellation is used.
        ...
            Applicable :ref:`state-parameters`:

             - :ref:`state-raw`: preprocessing pipeline
             - :ref:`state-rej`: which trials to use
             - :ref:`state-cov`: covariance matrix for inverse solution
             - :ref:`state-src`: source space
             - :ref:`state-inv`: inverse solution

        """
        if state:
            self.set(**state)
        if mask and not ndvar:
            raise NotImplementedError("mask is only implemented for ndvar=True")
        elif isinstance(mask, str):
            self.set(parc=mask)
            mask = True

        src = self.get('src')
        if src[:3] == 'vol':
            inv = self.get('inv')
            if not (inv.startswith('vec') or inv.startswith('free')):
                raise ValueError(f'inv={inv!r} with src={src!r}: volume source space requires free or vector inverse')

        if fiff is None:
            fiff = self.load_raw()

        inv = make_inverse_operator(fiff.info, self.load_fwd(), self.load_cov(),
                                    use_cps=True, **self._params['make_inv_kw'])

        if ndvar:
            inv = load.fiff.inverse_operator(
                inv, self.get('src'), self.get('mri-sdir'), self.get('parc'))
            if mask:
                inv = inv.sub(source=~inv.source.parc.startswith('unknown'))
        return inv

    def load_label(self, label, **kwargs):
        """Retrieve a label as mne Label object

        Parameters
        ----------
        label : str
            Name of the label. If the label name does not end in '-bh' or '-rh'
            the combination of the labels ``label + '-lh'`` and
            ``label + '-rh'`` is returned.
        ...
            State parameters.
        """
        labels = self._load_labels(label, **kwargs)
        if label in labels:
            return labels[label]
        elif not label.endswith(('-lh', '-rh')):
            return labels[label + '-lh'] + labels[label + '-rh']
        else:
            raise ValueError("Label %r could not be found in parc %r."
                             % (label, self.get('parc')))

    def _load_labels(self, regexp=None, **kwargs):
        """Load labels from an annotation file."""
        self.make_annot(**kwargs)
        mri_sdir = self.get('mri-sdir')
        labels = mne.read_labels_from_annot(self.get('mrisubject'),
                                            self.get('parc'), regexp=regexp,
                                            subjects_dir=mri_sdir)
        return {l.name: l for l in labels}

    def load_morph_matrix(self, **state):
        """Load the morph matrix from mrisubject to common_brain

        Parameters
        ----------
        ...
            State parameters.

        Returns
        -------
        mm : sparse matrix
            Morph matrix.
        vertices_to : list of 2 array
            Vertices of the morphed data.
        """
        subjects_dir = self.get('mri-sdir', **state)
        subject_to = self.get('common_brain')
        subject_from = self.get('mrisubject')

        src_to = self.load_src(mrisubject=subject_to, match=False)
        src_from = self.load_src(mrisubject=subject_from, match=False)

        vertices_to = [src_to[0]['vertno'], src_to[1]['vertno']]
        vertices_from = [src_from[0]['vertno'], src_from[1]['vertno']]

        mm = mne.compute_morph_matrix(subject_from, subject_to, vertices_from,
                                      vertices_to, None, subjects_dir)
        return mm, vertices_to

    def load_neighbor_correlation(self, subjects=None, epoch=None, **state):
        """Load sensor neighbor correlation

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        epoch : str
            Epoch to use for computing neighbor-correlation (by default, the
            whole session is used).

        Returns
        -------
        nc : NDVar | Dataset
            Sensor neighbor-correlation as :class:`NDVar` for a single subject
            or as :class:`Dataset` for multiple subjects.
        """
        subject, group = self._process_subject_arg(subjects, state)
        if group is not None:
            if state:
                self.set(**state)
            lines = [(subject, self.load_neighbor_correlation(1, epoch)) for subject in self]
            return Dataset.from_caselist(['subject', 'nc'], lines)
        if epoch:
            if epoch is True:
                epoch = self.get('epoch')
            epoch_params = self._epochs[epoch]
            if len(epoch_params.sessions) != 1:
                raise ValueError(f"epoch={epoch!r}: epoch has multiple session")
            ds = self.load_epochs(epoch=epoch, reject=False, decim=1, **state)
            data = concatenate(ds['meg'])
        else:
            data = self.load_raw(ndvar=True, **state)
        return neighbor_correlation(data)

    def load_raw(self, add_bads=True, preload=False, ndvar=False, decim=1, **kwargs):
        """
        Load a raw file as mne Raw object.

        Parameters
        ----------
        add_bads : bool | list
            Add bad channel information to the bad channels text file (default
            True).
        preload : bool
            Load raw data into memory (default False; see
            :func:`mne.io.read_raw_fif` parameter).
        ndvar : bool
            Load as NDVar instead of mne Raw object (default False).
        decim : int
            Decimate data (default 1, i.e. no decimation; value other than 1
            implies ``preload=True``)
        ...
            Applicable :ref:`state-parameters`:

             - :ref:`state-session`: from which session to load raw data
             - :ref:`state-raw`: preprocessing pipeline

        Notes
        -----
        Bad channels defined in the raw file itself are ignored in favor of the
        bad channels in the bad channels file.
        """
        pipe = self._raw[self.get('raw', **kwargs)]
        if decim > 1:
            preload = True
        raw = pipe.load(self.get('subject'), self.get('recording'), add_bads, preload)
        if decim > 1:
            if ndvar:
                # avoid warning for downsampling event channel
                stim_picks = np.empty(0)
                events = np.empty((0, 3))
            else:
                stim_picks = events = None
            sfreq = int(round(raw.info['sfreq'] / decim))
            raw.resample(sfreq, stim_picks=stim_picks, events=events)

        if ndvar:
            data = TestDims('sensor')
            data_kind = data.data_to_ndvar(raw.info)[0]
            sysname = pipe.get_sysname(raw.info, self.get('subject'), data_kind)
            connectivity = pipe.get_connectivity(data_kind)
            raw = load.fiff.raw_ndvar(raw, sysname=sysname, connectivity=connectivity)

        return raw

    def _load_result_plotter(self, test, tstart, tstop, pmin, parc=None,
                             mask=None, samples=10000, data='source',
                             baseline=True, src_baseline=None,
                             colors=None, labels=None, h=1.2, rc=None,
                             dst=None, vec_fmt='svg', pix_fmt='png', **kwargs):
        """Load cluster-based test result plotter

        Parameters
        ----------
        test : str
            Name of the test.
        tstart, tstop, pmin, parc, mask, samples, data, baseline, src_baseline
            Test parameters.
        colors : dict
            Colors for data cells as ``{cell: matplotlib_color}`` dictionary.
        labels : dict
            Labels for data in a ``{cell: label}`` dictionary (the default is to
            use cell names).
        h : scalar
            Plot height in inches (default 1.1).
        rc : dict
            Matplotlib rc-parameters dictionary (the default is optimized for
            the default plot size ``h=1.1``).
        dst : str
            Directory in which to place results (default is the ``result plots``
            directory).
        vec_fmt : str
            Format for vector graphics (default 'pdf').
        pix_fmt : str
            Format for pixel graphics (default 'png').
        ...
            State parameters.
        """
        if not isinstance(self._tests[test], EvokedTest):
            raise NotImplementedError("Result-plots for %s" %
                                      self._tests[test].__class__.__name__)
        elif data != 'source':
            raise NotImplementedError("data=%s" % repr(data))
        elif not isinstance(pmin, float):
            raise NotImplementedError("Threshold-free tests")

        from .._result_plots import ClusterPlotter

        # calls _set_analysis_options():
        ds, res = self.load_test(test, tstart, tstop, pmin, parc, mask, samples,
                                 data, baseline, src_baseline, True,
                                 **kwargs)
        if dst is None:
            dst = self.get('res-plot-dir', mkdir=True)

        return ClusterPlotter(ds, res, colors, dst, vec_fmt, pix_fmt, labels, h,
                              rc)

    def load_selected_events(self, subjects=None, reject=True, add_bads=True,
                             index=True, data_raw=False, vardef=None, cat=None,
                             **kwargs):
        """
        Load events and return a subset based on epoch and rejection

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        reject : bool | 'keep'
            Reject bad trials. If ``True`` (default), bad trials are removed
            from the Dataset. Set to ``False`` to ignore the trial rejection.
            Set ``reject='keep'`` to load the rejection (added it to the events
            as ``'accept'`` variable), but keep bad trails.
        add_bads : False | True | list
            Add bad channel information to the Raw. If True, bad channel
            information is retrieved from the bad channels file. Alternatively,
            a list of bad channels can be specified.
        index : bool | str
            Index the Dataset before rejection (provide index name as str).
        data_raw : bool
            Keep the :class:`mne.io.Raw` instance in ``ds.info['raw']``
            (default False).
        vardef : str
            Name of a 2-stage test defining additional variables.
        cat : sequence of cell-names
            Only load data for these cells (cells of model).
        ...
            State parameters.

        Notes
        -----
        When trial rejection is set to automatic, not rejection is performed
        because no epochs are loaded.
        """
        # process arguments
        if reject not in (True, False, 'keep'):
            raise ValueError(f"reject={reject!r}")

        if index is True:
            index = 'index'
        elif index and not isinstance(index, str):
            raise TypeError(f"index={index!r}")

        # case of loading events for a group
        subject, group = self._process_subject_arg(subjects, kwargs)
        if group is not None:
            if data_raw:
                raise ValueError(f"data_var={data_raw!r}: can't keep raw when combining subjects")
            dss = [self.load_selected_events(reject=reject, add_bads=add_bads, index=index, vardef=vardef) for _ in self.iter(group=group)]
            ds = combine(dss)
            return ds

        epoch = self._epochs[self.get('epoch')]
        if isinstance(epoch, EpochCollection):
            raise ValueError(f"epoch={self.get('epoch')!r}; can't load events for collection epoch")

        # rejection comes from somewhere else
        if isinstance(epoch, SuperEpoch):
            with self._temporary_state:
                dss = []
                raw = None
                # find bad channels
                if isinstance(add_bads, Sequence):
                    bad_channels = list(add_bads)
                elif add_bads:
                    bad_channels = sorted(set.union(*(
                        set(self.load_bad_channels(session=session)) for
                        session in epoch.sessions)))
                else:
                    bad_channels = []
                # load events
                for session in epoch.sessions:
                    self.set(session=session)
                    # load events for this session
                    session_dss = []
                    for sub_epoch in epoch.sub_epochs:
                        if self._epochs[sub_epoch].session != session:
                            continue
                        ds = self.load_selected_events(subject, reject, add_bads, index, True, epoch=sub_epoch)
                        ds[:, 'epoch'] = sub_epoch
                        session_dss.append(ds)
                    ds = combine(session_dss)
                    dss.append(ds)
                    # combine raw
                    raw_ = session_dss[0].info['raw']
                    raw_.info['bads'] = bad_channels
                    if raw is None:
                        raw = raw_
                    else:
                        ds['i_start'] += raw.last_samp + 1 - raw_.first_samp
                        raw.append(raw_)

            # combine bad channels
            ds = combine(dss)
            if data_raw:
                ds.info['raw'] = raw
            ds.info[BAD_CHANNELS] = bad_channels
        elif isinstance(epoch, SecondaryEpoch):
            with self._temporary_state:
                ds = self.load_selected_events(None, 'keep' if reject else False, add_bads, index, data_raw, epoch=epoch.sel_epoch)

            if epoch.sel:
                ds = ds.sub(epoch.sel)
            if index:
                ds.index(index)

            if reject is True:
                if self._artifact_rejection[self.get('rej')]['kind'] is not None:
                    ds = ds.sub('accept')
        else:
            rej_params = self._artifact_rejection[self.get('rej')]
            # load files
            with self._temporary_state:
                ds = self.load_events(add_bads=add_bads, data_raw=data_raw, session=epoch.session)
                if reject and rej_params['kind'] is not None:
                    rej_file = self.get('rej-file')
                    if exists(rej_file):
                        ds_sel = load.unpickle(rej_file)
                    else:
                        rej_file = self._get_rel('rej-file', 'root')
                        raise FileMissing(f"The rejection file at {rej_file} does not exist. Run .make_epoch_selection() first.")
                else:
                    ds_sel = None

            # primary event selection
            if epoch.sel:
                ds = ds.sub(epoch.sel)
            if index:
                ds.index(index)
            if epoch.n_cases is not None and ds.n_cases != epoch.n_cases:
                raise RuntimeError(f"Number of epochs {ds.n_cases}, expected {epoch.n_cases}")

            # rejection
            if ds_sel is not None:
                # check file
                if not np.all(ds['trigger'] == ds_sel['trigger']):
                    #  TODO:  this warning should be given in make_epoch_selection already
                    if np.all(ds[:-1, 'trigger'] == ds_sel['trigger']):
                        ds = ds[:-1]
                        self._log.warning(self.format("Last epoch for {subject} is missing"))
                    elif np.all(ds[1:, 'trigger'] == ds_sel['trigger']):
                        ds = ds[1:]
                        self._log.warning(self.format("First epoch for {subject} is missing"))
                    else:
                        raise RuntimeError(f"The epoch selection file contains different events (trigger IDs) from the epoch data loaded from the raw file. If the events included in the epoch were changed intentionally, delete the corresponding epoch rejection file and redo epoch rejection: {rej_file}")

                if rej_params['interpolation']:
                    ds.info[INTERPOLATE_CHANNELS] = True
                    if INTERPOLATE_CHANNELS in ds_sel:
                        ds[INTERPOLATE_CHANNELS] = ds_sel[INTERPOLATE_CHANNELS]
                    else:
                        ds[INTERPOLATE_CHANNELS] = Datalist([[]] * ds.n_cases,
                                                            INTERPOLATE_CHANNELS,
                                                            'strlist')
                else:
                    ds.info[INTERPOLATE_CHANNELS] = False

                # subset events
                if reject == 'keep':
                    ds['accept'] = ds_sel['accept']
                elif reject is True:
                    ds = ds.sub(ds_sel['accept'])
                else:
                    raise RuntimeError("reject=%s" % repr(reject))

                # bad channels
                if add_bads:
                    if BAD_CHANNELS in ds_sel.info:
                        ds.info[BAD_CHANNELS] = ds_sel.info[BAD_CHANNELS]
                    else:
                        ds.info[BAD_CHANNELS] = []
            else:  # no artifact rejection
                ds.info[INTERPOLATE_CHANNELS] = False
                ds.info[BAD_CHANNELS] = []

        # apply trigger-shift
        if epoch.trigger_shift:
            shift = epoch.trigger_shift
            if isinstance(shift, str):
                shift = ds.eval(shift)
            if isinstance(shift, Var):
                shift = shift.x

            if np.isscalar(shift):
                ds['i_start'] += int(round(shift * ds.info['sfreq']))
            else:
                ds['i_start'] += np.round(shift * ds.info['sfreq']).astype(int)

        # Additional variables
        self._add_vars(ds, epoch.vars)
        self._add_vars(ds, vardef)

        # apply cat subset
        if cat:
            model = ds.eval(self.get('model'))
            idx = model.isin(cat)
            ds = ds.sub(idx)

        return ds

    def _load_spm(self, baseline=True, src_baseline=False):
        "Load LM"
        subject = self.get('subject')
        test = self.get('test')
        test_obj = self._tests[test]
        if not isinstance(test_obj, TwoStageTest):
            raise NotImplementedError("Test kind %r" % test_obj.__class__.__name__)
        ds = self.load_epochs_stc(subject, baseline, src_baseline, mask=True, vardef=test_obj.vars)
        return testnd.LM('src', test_obj.stage_1, ds, subject=subject)

    def load_src(self, add_geom=False, ndvar=False, **state):
        """Load the current source space
        
        Parameters
        ----------
        add_geom : bool
            Parameter for :func:`mne.read_source_spaces`.
        ndvar : bool
            Return as NDVar Dimension object (default False).
        ...
            State parameters.
        """
        fpath = self.get('src-file', make=True, **state)
        if ndvar:
            src = self.get('src')
            if src.startswith('vol'):
                return VolumeSourceSpace.from_file(
                    self.get('mri-sdir'), self.get('mrisubject'), src)
            return SourceSpace.from_file(
                self.get('mri-sdir'), self.get('mrisubject'), src, self.get('parc'))
        return mne.read_source_spaces(fpath, add_geom)

    def load_test(self, test, tstart=None, tstop=None, pmin=None, parc=None,
                  mask=None, samples=10000, data='source', baseline=True,
                  src_baseline=None, return_data=False, make=False, **state):
        """Create and load spatio-temporal cluster test results

        Parameters
        ----------
        test : None | str
            Test for which to create a report (entry in MneExperiment.tests;
            None to use the test that was specified most recently).
        tstart : scalar
            Beginning of the time window for the test in seconds
            (default is the beginning of the epoch).
        tstop : scalar
            End of the time window for the test in seconds
            (default is the end of the epoch).
        pmin : float | 'tfce' | None
            Kind of test.
        parc : None | str
            Parcellation for which to collect distribution.
        mask : None | str
            Mask whole brain.
        samples : int
            Number of random permutations of the data used to determine cluster
            p values (default 10'000).
        data : str
            Data to test, for example:

            - ``'sensor'`` spatio-temporal test in sensor space.
            - ``'source'`` spatio-temporal test in source space.
            - ``'source.mean'`` ROI mean time course.
            - ``'sensor.rms'`` RMS across sensors.

        baseline : bool | tuple
            Apply baseline correction using this period in sensor space.
            True to use the epoch's baseline specification (default).
        src_baseline : bool | tuple
            Apply baseline correction using this period in source space.
            True to use the epoch's baseline specification. The default is to
            not apply baseline correction.
        return_data : bool
            Return the data along with the test result (see below).
        make : bool
            If the target file does not exist, create it (could take a long
            time depending on the test; if False, raise an IOError).
        ...
            State parameters (Use the ``group`` state parameter to select the 
            subject group for which to perform the test).

        Returns
        -------
        ds : Dataset (if return_data==True)
            Data that forms the basis of the test.
        res : NDTest | ROITestResult
            Test result for the specified test (when performing tests in ROIs,
            an :class:`~_experiment.ROITestResult` object is returned).
        """
        if 'sns_baseline' in state:
            baseline = state.pop('sns_baseline')
            warnings.warn("The sns_baseline parameter is deprecated, use baseline instead", DeprecationWarning)

        self.set(test=test, **state)
        data = TestDims.coerce(data, morph=True)
        self._set_analysis_options(data, baseline, src_baseline, pmin, tstart, tstop, parc, mask)
        return self._load_test(test, tstart, tstop, pmin, parc, mask, samples, data, baseline, src_baseline, return_data, make)

    def _load_test(self, test, tstart, tstop, pmin, parc, mask, samples, data,
                   baseline, src_baseline, return_data, make):
        "Load a cached test after _set_analysis_options() has been called"
        test_obj = self._tests[test]

        dst = self.get('test-file', mkdir=True)

        # try to load cached test
        res = None
        desc = self._get_rel('test-file', 'test-dir')
        if self._result_file_mtime(dst, data):
            try:
                res = load.unpickle(dst)
                if data.source is True:
                    update_subjects_dir(res, self.get('mri-sdir'), 2)
            except OldVersionError:
                res = None
            else:
                if res.samples >= samples or res.samples == -1:
                    self._log.info("Load cached test: %s", desc)
                    if not return_data:
                        return res
                elif not make:
                    raise IOError("The requested test %s is cached with "
                                  "samples=%i, but you request samples=%i; Set "
                                  "make=True to perform the test." %
                                  (desc, res.samples, samples))
                else:
                    res = None
        elif not make and exists(dst):
            raise IOError("The requested test is outdated: %s. Set make=True "
                          "to perform the test." % desc)

        if res is None and not make:
            raise IOError("The requested test is not cached: %s. Set make=True "
                          "to perform the test." % desc)

        #  parc/mask
        parc_dim = None
        if data.source is True:
            if parc:
                mask = True
                parc_dim = 'source'
            elif mask:
                if pmin is None:  # can as well collect dist for parc
                    parc_dim = 'source'
        elif isinstance(data.source, str):
            if not isinstance(parc, str):
                raise TypeError("parc needs to be set for ROI test (data=%r)" % (data.string,))
            elif mask is not None:
                raise TypeError("Mask=%r invalid with data=%r" % (mask, data.string))
        elif parc is not None:
            raise TypeError("parc=%r invalid for sensor space test (data=%r)" % (parc, data.string))
        elif mask is not None:
            raise TypeError("mask=%r invalid for sensor space test (data=%r)" % (mask, data.string))

        do_test = res is None
        if do_test:
            test_kwargs = self._test_kwargs(samples, pmin, tstart, tstop, data, parc_dim)
        else:
            test_kwargs = None

        if isinstance(test_obj, TwoStageTest):
            if data.source is not True:
                raise NotImplementedError(f"Two-stage test with data={data.string!r}")

            if test_obj.model is not None:
                self.set(model=test_obj._within_model)

            # stage 1
            lms = []
            dss = []
            for subject in self.iter(progress_bar="Loading stage 1 models"):
                if test_obj.model is None:
                    ds = self.load_epochs_stc(subject, baseline, src_baseline, morph=True, mask=mask, vardef=test_obj.vars)
                else:
                    ds = self.load_evoked_stc(subject, baseline, src_baseline, morph=True, mask=mask, vardef=test_obj.vars)

                if do_test:
                    lms.append(test_obj.make_stage_1(data.y_name, ds, subject))
                if return_data:
                    dss.append(ds)

            if do_test:
                res = test_obj.make_stage_2(lms, test_kwargs)

            res_data = combine(dss) if return_data else None
        elif isinstance(data.source, str):
            res_data, res = self._make_test_rois(baseline, src_baseline, test_obj, samples, pmin, test_kwargs, res, data)
        else:
            if data.sensor:
                res_data = self.load_evoked(True, baseline, True, test_obj._within_cat, data=data, vardef=test_obj.vars)
            elif data.source:
                res_data = self.load_evoked_stc(True, baseline, src_baseline, morph=True, cat=test_obj._within_cat, mask=mask, vardef=test_obj.vars)
            else:
                raise ValueError(f"data={data.string!r}")

            if do_test:
                self._log.info("Make test: %s", desc)
                res = self._make_test(data.y_name, res_data, test_obj, test_kwargs)

        if do_test:
            save.pickle(res, dst)

        if return_data:
            return res_data, res
        else:
            return res

    def _make_test_rois(self, baseline, src_baseline, test_obj, samples, pmin,
                        test_kwargs, res, data):
        # load data
        dss = defaultdict(list)
        n_trials_dss = []
        subjects = self.get_field_values('subject')
        for _ in self.iter(progress_bar="Loading data"):
            ds = self.load_evoked_stc(None, baseline, src_baseline, vardef=test_obj.vars)
            src = ds.pop('src')
            n_trials_dss.append(ds.copy())
            for label in src.source.parc.cells:
                if label.startswith('unknown-'):
                    continue
                label_ds = ds.copy()
                label_ds['label_tc'] = getattr(src, data.source)(source=label)
                dss[label].append(label_ds)
            del src

        label_data = {label: combine(data, incomplete='drop') for
                      label, data in dss.items()}
        if res is not None:
            return label_data, res

        n_trials_ds = combine(n_trials_dss, incomplete='drop')

        # n subjects per label
        n_per_label = {label: len(dss[label]) for label in dss}

        # compute results
        do_mcc = (
            len(dss) > 1 and  # more than one ROI
            pmin not in (None, 'tfce') and  # not implemented
            len(set(n_per_label.values())) == 1  # equal n permutations
        )
        label_results = {
            label: self._make_test('label_tc', ds, test_obj, test_kwargs, do_mcc)
            for label, ds in label_data.items()
        }

        if do_mcc:
            cdists = [res._cdist for res in label_results.values()]
            merged_dist = _MergedTemporalClusterDist(cdists)
        else:
            merged_dist = None

        res = ROITestResult(subjects, samples, n_trials_ds, merged_dist, label_results)
        return label_data, res

    def make_annot(self, redo=False, **state):
        """Make sure the annot files for both hemispheres exist

        Parameters
        ----------
        redo : bool
            Even if the file exists, recreate it (default False).
        ...
            State parameters.

        Returns
        -------
        mtime : float | None
            Modification time of the existing files, or None if they were newly
            created.
        """
        self.set(**state)

        # variables
        parc, p = self._get_parc()
        if p is None:
            return

        mrisubject = self.get('mrisubject')
        common_brain = self.get('common_brain')
        mtime = self._annot_file_mtime()
        if mrisubject != common_brain:
            is_fake = is_fake_mri(self.get('mri-dir'))
            if p.morph_from_fsaverage or is_fake:
                # make sure annot exists for common brain
                self.set(mrisubject=common_brain, match=False)
                common_brain_mtime = self.make_annot()
                self.set(mrisubject=mrisubject, match=False)
                if not redo and cache_valid(mtime, common_brain_mtime):
                    return mtime
                elif is_fake:
                    for _ in self.iter('hemi'):
                        self.make_copy('annot-file', 'mrisubject', common_brain,
                                       mrisubject)
                else:
                    self.get('label-dir', make=True)
                    subjects_dir = self.get('mri-sdir')
                    for hemi in ('lh', 'rh'):
                        cmd = ["mri_surf2surf", "--srcsubject", common_brain,
                               "--trgsubject", mrisubject, "--sval-annot", parc,
                               "--tval", parc, "--hemi", hemi]
                        subp.run_freesurfer_command(cmd, subjects_dir)
                    fix_annot_names(mrisubject, parc, common_brain,
                                    subjects_dir=subjects_dir)
                return

        if not redo and mtime:
            return mtime
        elif not p.make:
            if redo and mtime:
                raise RuntimeError(
                    f"The {parc} parcellation cannot be created automatically "
                    f"for {mrisubject}. Please update the corresponding "
                    f"*.annot files manually.")
            else:
                raise RuntimeError(
                    f"The {parc} parcellation cannot be created automatically "
                    f"and is missing for {mrisubject}. Please add the "
                    f"corresponding *.annot files to the subject's label "
                    f"directory.")

        # make parcs:  common_brain | non-morphed
        labels = self._make_annot(parc, p, mrisubject)
        write_labels_to_annot(labels, mrisubject, parc, True,
                              self.get('mri-sdir'))

    def _make_annot(self, parc, p, subject):
        """Return labels

        Notes
        -----
        Only called to make custom annotation files for the common_brain
        """
        subjects_dir = self.get('mri-sdir')
        if isinstance(p, CombinationParc):
            with self._temporary_state:
                base = {l.name: l for l in self.load_annot(parc=p.base)}
            labels = []
            for name, exp in p.labels.items():
                labels += combination_label(name, exp, base, subjects_dir)
        elif isinstance(p, SeededParc):
            if p.mask:
                with self._temporary_state:
                    self.make_annot(parc=p.mask)
            name, extent = SEEDED_PARC_RE.match(parc).groups()
            labels = labels_from_mni_coords(
                p.seeds_for_subject(subject), float(extent), subject, p.surface,
                p.mask, subjects_dir, parc)
        elif isinstance(p, EelbrainParc) and p.name == 'lobes':
            if subject != 'fsaverage':
                raise RuntimeError("lobes parcellation can only be created for "
                                   "fsaverage, not for %s" % subject)

            # load source annot
            with self._temporary_state:
                labels = self.load_annot(parc='PALS_B12_Lobes')

            # sort labels
            labels = [l for l in labels if l.name[:-3] != 'MEDIAL.WALL']

            # rename good labels
            rename_label(labels, 'LOBE.FRONTAL', 'frontal')
            rename_label(labels, 'LOBE.OCCIPITAL', 'occipital')
            rename_label(labels, 'LOBE.PARIETAL', 'parietal')
            rename_label(labels, 'LOBE.TEMPORAL', 'temporal')

            # reassign unwanted labels
            targets = ('frontal', 'occipital', 'parietal', 'temporal')
            dissolve_label(labels, 'LOBE.LIMBIC', targets, subjects_dir)
            dissolve_label(labels, 'GYRUS', targets, subjects_dir, 'rh')
            dissolve_label(labels, '???', targets, subjects_dir)
            dissolve_label(labels, '????', targets, subjects_dir, 'rh')
            dissolve_label(labels, '???????', targets, subjects_dir, 'rh')
        elif isinstance(p, LabelParc):
            labels = []
            hemis = ('lh.', 'rh.')
            path = join(subjects_dir, subject, 'label', '%s.label')
            for label in p.labels:
                if label.startswith(hemis):
                    labels.append(mne.read_label(path % label))
                else:
                    labels.extend(mne.read_label(path % (hemi + label)) for hemi in hemis)
        else:
            raise NotImplementedError(
                "At least one of the annot files for the custom parcellation "
                "%r is missing for %r, and a make function is not "
                "implemented." % (parc, subject))
        return labels

    def make_bad_channels(self, bad_chs=(), redo=False, **kwargs):
        """Write the bad channel definition file for a raw file

        If the file already exists, new bad channels are added to the old ones.
        In order to replace the old file with only the new values, set
        ``redo=True``.

        Parameters
        ----------
        bad_chs : iterator of str
            Names of the channels to set as bad. Numerical entries are
            interpreted as "MEG XXX". If bad_chs contains entries not present
            in the raw data, a ValueError is raised.
        redo : bool
            If the file already exists, replace it (instead of adding).
        ...
            State parameters.

        See Also
        --------
        make_bad_channels_auto : find bad channels automatically
        load_bad_channels : load the current bad_channels file
        merge_bad_channels : merge bad channel definitions for all sessions
        """
        pipe = self._raw[self.get('raw', **kwargs)]
        pipe.make_bad_channels(self.get('subject'), self.get('recording'), bad_chs, redo)

    def make_bad_channels_auto(self, flat=1e-14, redo=False, **state):
        """Automatically detect bad channels

        Works on ``raw='raw'``

        Parameters
        ----------
        flat : scalar
            Threshold for detecting flat channels: channels with ``std < flat``
            are considered bad (default 1e-14).
        redo : bool
            If the file already exists, replace it (instead of adding).
        ...
            State parameters.
        """
        if state:
            self.set(**state)
        pipe = self._raw['raw']
        pipe.make_bad_channels_auto(self.get('subject'), self.get('recording'), flat, redo)

    def make_bad_channels_neighbor_correlation(self, r, epoch=None, **state):
        """Exclude bad channels based on low average neighbor-correlation

        Parameters
        ----------
        r : scalar
            Minimum admissible neighbor correlation. Any channel whose average
            correlation with its neighbors is below this value is added to the
            list of bad channels (e.g., 0.3).
        epoch : str
            Epoch to use for computing neighbor-correlation (by default, the
            whole session is used).
        ...
            State parameters.

        Notes
        -----
        Data is loaded for the currently specified ``raw`` setting, but bad
        channels apply to all ``raw`` settings equally. Hence, when using this
        method with multiple subjects, it is important to set ``raw`` to the
        same value.
        """
        nc = self.load_neighbor_correlation(1, epoch, **state)
        bad_chs = nc.sensor.names[nc < r]
        if bad_chs:
            self.make_bad_channels(bad_chs)

    def make_besa_evt(self, redo=False, **state):
        """Make the trigger and event files needed for besa

        Parameters
        ----------
        redo : bool
            If besa files already exist, overwrite them.
        ...
            State parameters.

        Notes
        -----
        Ignores the *decim* epoch parameter.

        Target files are saved relative to the *besa-root* location.
        """
        self.set(**state)
        rej = self.get('rej')
        trig_dest = self.get('besa-trig', rej='', mkdir=True)
        evt_dest = self.get('besa-evt', rej=rej, mkdir=True)
        if not redo and exists(evt_dest) and exists(trig_dest):
            return

        # load events
        ds = self.load_selected_events(reject='keep')

        # save triggers
        if redo or not exists(trig_dest):
            save.meg160_triggers(ds, trig_dest, pad=1)
            if not redo and exists(evt_dest):
                return
        else:
            ds.index('besa_index', 1)

        # reject bad trials
        ds = ds.sub('accept')

        # save evt
        epoch = self._epochs[self.get('epoch')]
        save.besa_evt(ds, tstart=epoch.tmin, tstop=epoch.tmax, dest=evt_dest)

    def make_copy(self, temp, field, src, dst, redo=False):
        """Make a copy of a file

        Parameters
        ----------
        temp : str
            Template of the file which to copy.
        field : str
            Field in which the source and target of the link are distinguished.
        src : str
            Value for field on the source file.
        dst : str
            Value for field on the destination filename.
        redo : bool
            If the target file already exists, overwrite it.
        """
        dst_path = self.get(temp, mkdir=True, **{field: dst})
        if not redo and exists(dst_path):
            return

        src_path = self.get(temp, **{field: src})
        if isdir(src_path):
            raise ValueError("Can only copy files, not directories.")
        shutil.copyfile(src_path, dst_path)

    def make_cov(self):
        "Make a noise covariance (cov) file"
        dest = self.get('cov-file', mkdir=True)
        if exists(dest):
            mtime = self._cov_mtime()
            if mtime and getmtime(dest) > mtime:
                return

        params = self._covs[self.get('cov')]
        method = params.get('method', 'empirical')
        keep_sample_mean = params.get('keep_sample_mean', True)
        reg = params.get('reg', None)

        if 'epoch' in params:
            with self._temporary_state:
                ds = self.load_epochs(None, True, False, decim=1, epoch=params['epoch'])
            epochs = ds['epochs']
            cov = mne.compute_covariance(epochs, keep_sample_mean, method=method)
            info = epochs.info
        else:
            with self._temporary_state:
                raw = self.load_raw(session=params['session'])
            cov = mne.compute_raw_covariance(raw, method=method)
            info = raw.info
            epochs = None

        if reg is True:
            cov = mne.cov.regularize(cov, info, rank=None)
        elif isinstance(reg, dict):
            cov = mne.cov.regularize(cov, info, **reg)
        elif reg == 'best':
            if mne.pick_types(epochs.info, meg='grad', eeg=True, ref_meg=False).size:
                raise NotImplementedError("EEG or gradiometer sensors")
            elif epochs is None:
                raise NotImplementedError("reg='best' for raw covariance")
            reg_vs = np.arange(0, 0.21, 0.01)
            covs = [mne.cov.regularize(cov, epochs.info, mag=v, rank=None) for v in reg_vs]

            # compute whitened global field power
            evoked = epochs.average()
            picks = mne.pick_types(evoked.info, meg='mag', ref_meg=False)
            gfps = [mne.whiten_evoked(evoked, cov, picks).data.std(0)
                    for cov in covs]

            # apply padding
            t_pad = params.get('reg_eval_win_pad', 0)
            if t_pad:
                n_pad = int(t_pad * epochs.info['sfreq'])
                if len(gfps[0]) <= 2 * n_pad:
                    msg = "Covariance padding (%s) is bigger than epoch" % t_pad
                    raise ValueError(msg)
                padding = slice(n_pad, -n_pad)
                gfps = [gfp[padding] for gfp in gfps]

            vs = [gfp.mean() for gfp in gfps]
            i = np.argmin(np.abs(1 - np.array(vs)))
            cov = covs[i]

            # save cov value
            with open(self.get('cov-info-file', mkdir=True), 'w') as fid:
                fid.write('%s\n' % reg_vs[i])
        elif reg is not None:
            raise RuntimeError(f"reg={reg!r} in {params}")

        cov.save(dest)

    def _make_evoked(self, decim, data_raw):
        """Make files with evoked sensor data.

        Parameters
        ----------
        decim : int
            Data decimation factor (the default is the factor specified in the
            epoch definition).
        """
        dst = self.get('evoked-file', mkdir=True)
        epoch = self._epochs[self.get('epoch')]
        # determine whether using default decimation
        if decim:
            if epoch.decim:
                default_decim = decim == epoch.decim
            else:
                raw = self.load_raw(False)
                default_decim = decim == raw.info['sfreq'] / epoch.samplingrate
        else:
            default_decim = True
        use_cache = default_decim
        model = self.get('model')
        equal_count = self.get('equalize_evoked_count') == 'eq'
        if use_cache and exists(dst) and cache_valid(getmtime(dst), self._evoked_mtime()):
            ds = self.load_selected_events(data_raw=data_raw)
            ds = ds.aggregate(model, drop_bad=True, equal_count=equal_count,
                              drop=('i_start', 't_edf', 'T', 'index', 'trigger'))
            ds['evoked'] = mne.read_evokeds(dst, proj=False)
            return ds

        # load the epochs (post baseline-correction trigger shift requires
        # baseline corrected evoked
        if epoch.post_baseline_trigger_shift:
            ds = self.load_epochs(ndvar=False, baseline=True, decim=decim, data_raw=data_raw, interpolate_bads='keep')
        else:
            ds = self.load_epochs(ndvar=False, decim=decim, data_raw=data_raw, interpolate_bads='keep')

        # aggregate
        ds_agg = ds.aggregate(model, drop_bad=True, equal_count=equal_count,
                              drop=('i_start', 't_edf', 'T', 'index', 'trigger'),
                              never_drop=('epochs',))
        ds_agg.rename('epochs', 'evoked')

        # save
        for e in ds_agg['evoked']:
            e.info['description'] = f"Eelbrain {CACHE_STATE_VERSION}"
        if use_cache:
            mne.write_evokeds(dst, ds_agg['evoked'])

        return ds_agg

    def make_fwd(self):
        """Make the forward model"""
        subject = self.get('subject')
        fwd_recording = self._get_fwd_recording(subject)
        with self._temporary_state:
            dst = self.get('fwd-file', recording=fwd_recording)
            if exists(dst):
                if cache_valid(getmtime(dst), self._fwd_mtime(subject, fwd_recording=fwd_recording)):
                    return dst
            # get trans for correct visit for fwd_session
            trans = self.get('trans-file')

        src = self.get('src-file', make=True)
        pipe = self._raw[self.get('raw')]
        raw = pipe.load(subject, fwd_recording)
        bem = self._load_bem()
        src = mne.read_source_spaces(src)

        self._log.debug(f"make_fwd {basename(dst)}...")
        bemsol = mne.make_bem_solution(bem)
        fwd = mne.make_forward_solution(raw.info, trans, src, bemsol, ignore_ref=True)
        for s, s0 in zip(fwd['src'], src):
            if s['nuse'] != s0['nuse']:
                raise RuntimeError(f"The forward solution {basename(dst)} contains fewer sources than the source space. This could be due to a corrupted bem file with sources outside of the inner skull surface.")
        mne.write_forward_solution(dst, fwd, True)
        return dst

    def make_ica_selection(self, epoch=None, decim=None, session=None, **state):
        """Select ICA components to remove through a GUI

        Parameters
        ----------
        epoch : str
            Epoch to use for visualization in the GUI (default is to use the
            raw data).
        decim : int
            Downsample data for visualization (to improve GUI performance;
            for raw data, the default is ~100 Hz, for epochs the default is the
            epoch setting).
        session : str | list of str
            One or more sessions for which to plot the raw data (this parameter
            can not be used together with ``epoch``; default is the session in
            the current state).
        ...
            State parameters.

        Notes
        -----
        Computing ICA decomposition can take a while. In order to precompute
        the decomposition for all subjects before doing the selection use
        :meth:`.make_ica()` in a loop as in::

            >>> for subject in e:
            ...     e.make_ica()
            ...
        """
        # ICA
        path = self.make_ica(**state)
        # display data
        subject = self.get('subject')
        pipe = self._raw[self.get('raw')]
        bads = pipe.load_bad_channels(subject, self.get('recording'))
        with self._temporary_state, warnings.catch_warnings():
            warnings.filterwarnings('ignore', 'The measurement information indicates a low-pass', RuntimeWarning)
            if epoch is None:
                if session is None:
                    session = self.get('session')
                raw = pipe.load_concatenated_source_raw(subject, session, self.get('visit'))
                events = mne.make_fixed_length_events(raw)
                ds = Dataset()
                decim = int(raw.info['sfreq'] // 100) if decim is None else decim
                ds['epochs'] = mne.Epochs(raw, events, 1, 0, 1, baseline=None, proj=False, decim=decim, preload=True)
            elif session is not None:
                raise TypeError(f"session={session!r} with epoch={epoch!r}")
            else:
                ds = self.load_epochs(ndvar=False, epoch=epoch, reject=False, raw=pipe.source.name, decim=decim, add_bads=bads)
        info = ds['epochs'].info
        data = TestDims('sensor')
        data_kind = data.data_to_ndvar(info)[0]
        sysname = pipe.get_sysname(info, subject, data_kind)
        connectivity = pipe.get_connectivity(data_kind)
        gui.select_components(path, ds, sysname, connectivity)

    def make_ica(self, **state):
        """Compute ICA decomposition for a :class:`pipeline.RawICA` preprocessing step

        If a corresponding file exists, a basic check is done as to whether the
        bad channels have changed, and if so the ICA is recomputed.

        Parameters
        ----------
        ...
            State parameters.

        Returns
        -------
        path : str
            Path to the ICA file.

        Notes
        -----
        ICA decomposition can take some time. This function can be used to
        precompute ICA decompositions for all subjects after trial pre-rejection
        has been completed::

            >>> for subject in e:
            ...     e.make_ica()

        """
        if state:
            self.set(**state)
        pipe = self._raw[self.get('raw')]
        if not isinstance(pipe, RawICA):
            ica_raws = [key for key, pipe in self._raw.items() if isinstance(pipe, RawICA)]
            if len(ica_raws) > 1:
                raise ValueError(f"raw={pipe.name!r} does not involve ICA; set raw to an ICA processing step ({enumeration(ica_raws)})")
            elif len(ica_raws) == 1:
                print(f"raw: {pipe.name} -> {ica_raws[0]}")
                return self.make_ica(raw=ica_raws[0])
            else:
                raise RuntimeError("Experiment has no RawICA processing step")
        return pipe.make_ica(self.get('subject'), self.get('visit'))

    def make_link(self, temp, field, src, dst, redo=False):
        """Make a hard link

        Make a hard link at the file with the ``dst`` value on ``field``,
        linking to the file with the ``src`` value of ``field``.

        Parameters
        ----------
        temp : str
            Template of the file for which to make a link.
        field : str
            Field in which the source and target of the link are distinguished.
        src : str
            Value for field on the source file.
        dst : str
            Value for field on the destination filename.
        redo : bool
            If the target file already exists, overwrite it.
        """
        dst_path = self.get(temp, **{field: dst})
        if not redo and exists(dst_path):
            return

        src_path = self.get(temp, **{field: src})
        os.link(src_path, dst_path)

    def make_mov_ga_dspm(self, subjects=None, baseline=True, src_baseline=False,
                         fmin=2, surf=None, views=None, hemi=None, time_dilation=4.,
                         foreground=None, background=None, smoothing_steps=None,
                         dst=None, redo=False, **state):
        """Make a grand average movie from dSPM values (requires PySurfer 0.6)

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        baseline : bool | tuple
            Apply baseline correction using this period in sensor space.
            True to use the epoch's baseline specification (default).
        src_baseline : bool | tuple
            Apply baseline correction using this period in source space.
            True to use the epoch's baseline specification. The default is to
            not apply baseline correction.
        fmin : scalar
            Minimum dSPM value to draw (default 2). fmax is 3 * fmin.
        surf : str
            Surface on which to plot data.
        views : str | tuple of str
            View(s) of the brain to include in the movie.
        hemi : 'lh' | 'rh' | 'both' | 'split'
            Which hemispheres to plot.
        time_dilation : scalar
            Factor by which to slow the passage of time. For example, with
            ``time_dilation=4`` (the default) a segment of data for 500 ms will
            last 2 s.
        foreground : mayavi color
            Figure foreground color (i.e., the text color).
        background : mayavi color
            Figure background color.
        smoothing_steps : None | int
            Number of smoothing steps if data is spatially undersampled (pysurfer
            ``Brain.add_data()`` argument).
        dst : str (optional)
            Path to save the movie. The default is a file in the results
            folder with a name determined based on the input data. Plotting
            parameters (``view`` and all subsequent parameters) are not
            included in the filename. "~" is expanded to the user's home
            folder.
        redo : bool
            Make the movie even if the target file exists already.
        ...
            State parameters.
        """
        if 'sns_baseline' in state:
            baseline = state.pop('sns_baseline')
            warnings.warn("The sns_baseline parameter is deprecated, use baseline instead", DeprecationWarning)

        state['model'] = ''
        subject, group = self._process_subject_arg(subjects, state)
        data = TestDims("source", morph=bool(group))
        brain_kwargs = self._surfer_plot_kwargs(surf, views, foreground, background,
                                                smoothing_steps, hemi)
        self._set_analysis_options(data, baseline, src_baseline, None, None, None)
        self.set(equalize_evoked_count='',
                 resname="GA dSPM %s %s" % (brain_kwargs['surf'], fmin))

        if dst is None:
            if group is None:
                dst = self.get('subject-mov-file', mkdir=True)
            else:
                dst = self.get('group-mov-file', mkdir=True)
        else:
            dst = os.path.expanduser(dst)

        if not redo and self._result_file_mtime(dst, data, group is None):
            return

        plot._brain.assert_can_save_movies()
        if group is None:
            ds = self.load_evoked_stc(subject, baseline, src_baseline)
            y = ds['src']
        else:
            ds = self.load_evoked_stc(group, baseline, src_baseline, morph=True)
            y = ds['srcm']

        brain = plot.brain.dspm(y, fmin, fmin * 3, colorbar=False, **brain_kwargs)
        brain.save_movie(dst, time_dilation)
        brain.close()

    def make_mov_ttest(self, subjects=None, model='', c1=None, c0=None, p=0.05,
                       baseline=True, src_baseline=False,
                       surf=None, views=None, hemi=None, time_dilation=4.,
                       foreground=None, background=None, smoothing_steps=None,
                       dst=None, redo=False, **state):
        """Make a t-test movie (requires PySurfer 0.6)

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        model : None | str
            Model on which the conditions c1 and c0 are defined. The default
            (``''``) is the grand average.
        c1 : None | str | tuple
            Test condition (cell in model). If None, the grand average is
            used and c0 has to be a scalar.
        c0 : str | scalar
            Control condition (cell on model) or scalar against which to
            compare c1.
        p : 0.1 | 0.05 | 0.01 | .001
            Maximum p value to draw.
        baseline : bool | tuple
            Apply baseline correction using this period in sensor space.
            True to use the epoch's baseline specification (default).
        src_baseline : bool | tuple
            Apply baseline correction using this period in source space.
            True to use the epoch's baseline specification. The default is to
            not apply baseline correction.
        surf : str
            Surface on which to plot data.
        views : str | tuple of str
            View(s) of the brain to include in the movie.
        hemi : 'lh' | 'rh' | 'both' | 'split'
            Which hemispheres to plot.
        time_dilation : scalar
            Factor by which to slow the passage of time. For example, with
            ``time_dilation=4`` (the default) a segment of data for 500 ms will
            last 2 s.
        foreground : mayavi color
            Figure foreground color (i.e., the text color).
        background : mayavi color
            Figure background color.
        smoothing_steps : None | int
            Number of smoothing steps if data is spatially undersampled (pysurfer
            ``Brain.add_data()`` argument).
        dst : str (optional)
            Path to save the movie. The default is a file in the results
            folder with a name determined based on the input data. Plotting
            parameters (``view`` and all subsequent parameters) are not
            included in the filename. "~" is expanded to the user's home
            folder.
        redo : bool
            Make the movie even if the target file exists already.
        ...
            State parameters.
        """
        if 'sns_baseline' in state:
            baseline = state.pop('sns_baseline')
            warnings.warn("The sns_baseline parameter is deprecated, use baseline instead", DeprecationWarning)

        if p == 0.1:
            pmid = 0.05
            pmin = 0.01
        elif p == 0.05:
            pmid = 0.01
            pmin = 0.001
        elif p == 0.01:
            pmid = 0.001
            pmin = 0.001
        elif p == 0.001:
            pmid = 0.0001
            pmin = 0.00001
        else:
            raise ValueError("p=%s" % p)

        data = TestDims("source", morph=True)
        brain_kwargs = self._surfer_plot_kwargs(surf, views, foreground, background,
                                                smoothing_steps, hemi)
        surf = brain_kwargs['surf']
        if model:
            if not c1:
                raise ValueError("If x is specified, c1 needs to be specified; "
                                 "got c1=%s" % repr(c1))
            elif c0:
                resname = "t-test %s-%s {test_options} %s" % (c1, c0, surf)
                cat = (c1, c0)
            else:
                resname = "t-test %s {test_options} %s" % (c1, surf)
                cat = (c1,)
        elif c1 or c0:
            raise ValueError("If x is not specified, c1 and c0 should not be "
                             "specified either; got c1=%s, c0=%s"
                             % (repr(c1), repr(c0)))
        else:
            resname = "t-test GA {test_options} %s" % surf
            cat = None

        state.update(resname=resname, model=model)
        with self._temporary_state:
            subject, group = self._process_subject_arg(subjects, state)
            self._set_analysis_options(data, baseline, src_baseline, p, None, None)

            if dst is None:
                if group is None:
                    dst = self.get('subject-mov-file', mkdir=True)
                else:
                    dst = self.get('group-mov-file', mkdir=True)
            else:
                dst = os.path.expanduser(dst)

            if not redo and self._result_file_mtime(dst, data, group is None):
                return

            plot._brain.assert_can_save_movies()
            if group is None:
                ds = self.load_epochs_stc(subject, baseline, src_baseline, cat=cat)
                y = 'src'
            else:
                ds = self.load_evoked_stc(group, baseline, src_baseline, morph=True, cat=cat)
                y = 'srcm'

            # find/apply cluster criteria
            state = self._cluster_criteria_kwargs(data)
            if state:
                state.update(samples=0, pmin=p)

        # compute t-maps
        if c0:
            if group:
                res = testnd.ttest_rel(y, model, c1, c0, match='subject', ds=ds, **state)
            else:
                res = testnd.ttest_ind(y, model, c1, c0, ds=ds, **state)
        else:
            res = testnd.ttest_1samp(y, ds=ds, **state)

        # select cluster-corrected t-map
        if state:
            tmap = res.masked_parameter_map(None)
        else:
            tmap = res.t

        # make movie
        brain = plot.brain.dspm(tmap, ttest_t(p, res.df), ttest_t(pmin, res.df),
                                ttest_t(pmid, res.df), surf=surf)
        brain.save_movie(dst, time_dilation)
        brain.close()

    def make_mrat_evoked(self, **kwargs):
        """Produce the sensor data fiff files needed for MRAT sensor analysis

        Parameters
        ----------
        ...
            State parameters.

        Examples
        --------
        To produce evoked files for all subjects in the experiment:

        >>> experiment.set(model='factor1%factor2')
        >>> for _ in experiment:
        >>>     experiment.make_mrat_evoked()
        ...
        """
        ds = self.load_evoked(ndvar=False, **kwargs)

        # create fiffs
        model = self.get('model')
        factors = [f.strip() for f in model.split('%')]
        for case in ds.itercases():
            condition = '_'.join(case[f] for f in factors)
            path = self.get('mrat-sns-file', mkdir=True,
                            mrat_condition=condition)
            evoked = case['evoked']
            evoked.save(path)

    def make_mrat_stcs(self, **kwargs):
        """Produce the STC files needed for the MRAT analysis tool

        Parameters
        ----------
        ...
            State parameters.

        Examples
        --------
        To produce stc files for all subjects in the experiment:

        >>> experiment.set_inv('free')
        >>> experiment.set(model='factor1%factor2')
        >>> for _ in experiment:
        >>>     experiment.make_mrat_stcs()
        ...
        """
        ds = self.load_evoked_stc(morph=True, ndvar=False, **kwargs)

        # save condition info
        info_file = self.get('mrat_info-file', mkdir=True)
        ds.save_txt(info_file)

        # create stcs
        model = self.get('model')
        factors = [f.strip() for f in model.split('%')]
        for case in ds.itercases():
            condition = '_'.join(case[f] for f in factors)
            path = self.get('mrat-src-file', mkdir=True,
                            mrat_condition=condition)
            stc = case['stcm']
            stc.save(path)

    def make_plot_annot(self, surf='inflated', redo=False, **state):
        """Create a figure for the contents of an annotation file

        Parameters
        ----------
        surf : str
            FreeSurfer surface on which to plot the annotation.
        redo : bool
            If the target file already exists, overwrite it.
        ...
            State parameters.
        """
        if is_fake_mri(self.get('mri-dir', **state)):
            mrisubject = self.get('common_brain')
            self.set(mrisubject=mrisubject, match=False)

        dst = self.get('res-file', mkdir=True, ext='png',
                       analysis='Source Annot',
                       resname="{parc} {mrisubject} %s" % surf)
        if not redo and exists(dst):
            return

        brain = self.plot_annot(surf=surf, axw=600)
        brain.save_image(dst, 'rgba', True)
        legend = brain.plot_legend(show=False)
        legend.save(dst[:-3] + 'pdf', transparent=True)
        brain.close()
        legend.close()

    def make_plot_label(self, label, surf='inflated', redo=False, **state):
        if is_fake_mri(self.get('mri-dir', **state)):
            mrisubject = self.get('common_brain')
            self.set(mrisubject=mrisubject, match=False)

        dst = self._make_plot_label_dst(surf, label)
        if not redo and exists(dst):
            return

        brain = self.plot_label(label, surf=surf)
        brain.save_image(dst, 'rgba', True)

    def make_plots_labels(self, surf='inflated', redo=False, **state):
        self.set(**state)
        with self._temporary_state:
            if is_fake_mri(self.get('mri-dir')):
                self.set(mrisubject=self.get('common_brain'), match=False)

            labels = tuple(self._load_labels().values())
            dsts = [self._make_plot_label_dst(surf, label.name) for label in labels]
        if not redo and all(exists(dst) for dst in dsts):
            return

        brain = self.plot_brain(surf, None, 'split', ['lat', 'med'], w=1200)
        for label, dst in zip(labels, dsts):
            brain.add_label(label)
            brain.save_image(dst, 'rgba', True)
            brain.remove_labels(hemi='lh')

    def _make_plot_label_dst(self, surf, label):
        return self.get('res-deep-file', mkdir=True, analysis='Source Labels',
                        folder="{parc} {mrisubject} %s" % surf, resname=label,
                        ext='png')

    def make_raw(self, **kwargs):
        """Make a raw file
        
        Parameters
        ----------
        ...
            State parameters.

        Notes
        -----
        Due to the electronics of the KIT system sensors, signal lower than
        0.16 Hz is not recorded even when recording at DC.
        """
        if kwargs:
            self.set(**kwargs)
        pipe = self._raw[self.get('raw')]
        pipe.cache(self.get('subject'), self.get('recording'))

    def make_epoch_selection(self, decim=None, auto=None, overwrite=None, **state):
        """Open :func:`gui.select_epochs` for manual epoch selection

        The GUI is opened with the correct file name; if the corresponding
        file exists, it is loaded, and upon saving the correct path is
        the default.

        Parameters
        ----------
        decim : int
            Decimate epochs for the purpose of faster display. Decimation is
            applied relative to the raw data file (i.e., if the raw data is
            sampled at a 1000 Hz, ``decim=10`` results in a sampling rate of
            100 Hz for display purposes. The default is to use the decim
            parameter specified in the epoch definition.
        auto : scalar (optional)
            Perform automatic rejection instead of showing the GUI by supplying
            a an absolute threshold (for example, ``1e-12`` to reject any epoch
            in which the absolute of at least one channel exceeds 1 picotesla).
            If a rejection file already exists also set ``overwrite=True``.
        overwrite : bool
            If ``auto`` is specified and a rejection file already exists,
            overwrite the old file. The default is to raise an error if the
            file exists (``None``). Set to ``False`` to quietly keep the exising
            file.
        ...
            State parameters.
        """
        rej = self.get('rej', **state)
        rej_args = self._artifact_rejection[rej]
        if rej_args['kind'] != 'manual':
            raise ValueError(f"rej={rej!r}; Epoch rejection is not manual")

        epoch = self._epochs[self.get('epoch')]
        if not isinstance(epoch, PrimaryEpoch):
            if isinstance(epoch, SecondaryEpoch):
                raise ValueError(f"The current epoch {epoch.name!r} inherits selections from {epoch.sel_epoch!r}. To access a rejection file for this epoch, call `e.set(epoch={epoch.sel_epoch!r})` and then call `e.make_epoch_selection()` again.")
            elif isinstance(epoch, SuperEpoch):
                raise ValueError(f"The current epoch {epoch.name!r} inherits selections from these other epochs: {epoch.sub_epochs!r}. To access selections for these epochs, call `e.make_epoch_selection(epoch=epoch)` for each.")
            else:
                raise ValueError(f"The current epoch {epoch.name!r} is not a primary epoch and inherits selections from other epochs. Generate trial rejection for these epochs.")

        path = self.get('rej-file', mkdir=True, session=epoch.session)

        if auto is not None and overwrite is not True and exists(path):
            if overwrite is False:
                return
            elif overwrite is None:
                raise IOError(self.format("A rejection file already exists for {subject}, epoch {epoch}, rej {rej}. Set the overwrite parameter to specify how to handle existing files."))
            else:
                raise TypeError(f"overwrite={overwrite!r}")

        ds = self.load_epochs(reject=False, trigger_shift=False, decim=decim)
        has_meg = 'meg' in ds
        has_grad = 'grad' in ds
        has_eeg = 'eeg' in ds
        has_eog = 'eog' in ds
        if sum((has_meg, has_grad, has_eeg)) > 1:
            raise NotImplementedError("Rejection GUI for multiple channel types")
        elif has_meg:
            y_name = 'meg'
            vlim = 2e-12
        elif has_grad:
            raise NotImplementedError("Rejection GUI for gradiometer data")
        elif has_eeg:
            y_name = 'eeg'
            vlim = 1.5e-4
        else:
            raise RuntimeError("No data found")

        if has_eog:
            eog_sns = []  # TODO:  use EOG
        else:
            eog_sns = self._eog_sns.get(ds[y_name].sensor.sysname)

        if auto is not None:
            # create rejection
            rej_ds = new_rejection_ds(ds)
            rej_ds[:, 'accept'] = ds[y_name].abs().max(('sensor', 'time')) <= auto
            # create description for info
            args = [f"auto={auto!r}"]
            if overwrite is True:
                args.append("overwrite=True")
            if decim is not None:
                args.append(f"decim={decim!r}")
            rej_ds.info['desc'] = f"Created with {self.__class__.__name__}.make_epoch_selection({', '.join(args)})"
            # save
            save.pickle(rej_ds, path)
            # print info
            n_rej = rej_ds.eval("sum(accept == False)")
            print(self.format(f"{n_rej} of {rej_ds.n_cases} epochs rejected with threshold {auto} for {{subject}}, epoch {{epoch}}"))
            return

        # don't mark eog sns if it is bad
        bad_channels = self.load_bad_channels()
        eog_sns = [c for c in eog_sns if c not in bad_channels]

        gui.select_epochs(ds, y_name, path=path, vlim=vlim, mark=eog_sns)

    def _need_not_recompute_report(self, dst, samples, data, redo):
        "Check (and log) whether the report needs to be redone"
        desc = self._get_rel('report-file', 'res-dir')
        if not exists(dst):
            self._log.debug("New report: %s", desc)
        elif redo:
            self._log.debug("Redoing report: %s", desc)
        elif not self._result_file_mtime(dst, data):
            self._log.debug("Report outdated: %s", desc)
        else:
            meta = read_meta(dst)
            if 'samples' in meta:
                if int(meta['samples']) >= samples:
                    self._log.debug("Report up to date: %s", desc)
                    return True
                else:
                    self._log.debug("Report file used %s samples, recomputing "
                                    "with %i: %s", meta['samples'], samples,
                                    desc)
            else:
                self._log.debug("Report created prior to Eelbrain 0.25, can "
                                "not check number of samples. Delete manually "
                                "to recompute: %s", desc)
                return True

    def make_report(self, test, parc=None, mask=None, pmin=None, tstart=None,
                    tstop=None, samples=10000, baseline=True,
                    src_baseline=None, include=0.2, redo=False, **state):
        """Create an HTML report on spatio-temporal clusters

        Parameters
        ----------
        test : str
            Test for which to create a report (entry in MneExperiment.tests).
        parc : None | str
            Find clusters in each label of parc (as opposed to the whole
            brain).
        mask : None | str
            Parcellation to apply as mask. Can only be specified if parc==None.
        pmin : None | scalar, 1 > pmin > 0 | 'tfce'
            Equivalent p-value for cluster threshold, or 'tfce' for
            threshold-free cluster enhancement.
        tstart : scalar
            Beginning of the time window for the test in seconds
            (default is the beginning of the epoch).
        tstop : scalar
            End of the time window for the test in seconds
            (default is the end of the epoch).
        samples : int > 0
            Number of samples used to determine cluster p values for spatio-
            temporal clusters (default 10,000).
        baseline : bool | tuple
            Apply baseline correction using this period in sensor space.
            True to use the epoch's baseline specification (default).
        src_baseline : bool | tuple
            Apply baseline correction using this period in source space.
            True to use the epoch's baseline specification. The default is to
            not apply baseline correction.
        include : 0 < scalar <= 1
            Create plots for all clusters with p-values smaller or equal this value.
        redo : bool
            If the target file already exists, delete and recreate it. This
            only applies to the HTML result file, not to the test.
        ...
            State parameters.

        See Also
        --------
        load_test : load corresponding data and tests
        """
        if samples < 1:
            raise ValueError("samples needs to be > 0")
        elif include <= 0 or include > 1:
            raise ValueError("include needs to be 0 < include <= 1, got %s"
                             % repr(include))

        self.set(**state)
        data = TestDims('source', morph=True)
        self._set_analysis_options(data, baseline, src_baseline, pmin, tstart, tstop, parc, mask)
        dst = self.get('report-file', mkdir=True, test=test)
        if self._need_not_recompute_report(dst, samples, data, redo):
            return

        # start report
        title = self.format('{recording} {test_desc}')
        report = Report(title)
        report.add_paragraph(self._report_methods_brief(dst))

        if isinstance(self._tests[test], TwoStageTest):
            self._two_stage_report(report, data, test, baseline, src_baseline, pmin, samples, tstart, tstop, parc, mask, include)
        else:
            self._evoked_report(report, data, test, baseline, src_baseline, pmin, samples, tstart, tstop, parc, mask, include)

        # report signature
        report.sign(('eelbrain', 'mne', 'surfer', 'scipy', 'numpy'))
        report.save_html(dst, meta={'samples': samples})

    def _evoked_report(self, report, data, test, baseline, src_baseline, pmin, samples, tstart, tstop, parc, mask, include):
        # load data
        ds, res = self._load_test(test, tstart, tstop, pmin, parc, mask, samples, data, baseline, src_baseline, True, True)

        # info
        surfer_kwargs = self._surfer_plot_kwargs()
        self._report_test_info(report.add_section("Test Info"), ds, test, res, data, include)
        if parc:
            section = report.add_section(parc)
            caption = "Labels in the %s parcellation." % parc
            self._report_parc_image(section, caption)
        elif mask:
            title = "Whole Brain Masked by %s" % mask
            section = report.add_section(title)
            caption = "Mask: %s" % mask.capitalize()
            self._report_parc_image(section, caption)

        colors = plot.colors_for_categorial(ds.eval(res._plot_model()))
        report.append(_report.source_time_results(res, ds, colors, include,
                                                  surfer_kwargs, parc=parc))

    def _two_stage_report(self, report, data, test, baseline, src_baseline, pmin, samples, tstart, tstop, parc, mask, include):
        test_obj = self._tests[test]
        return_data = test_obj._within_model is not None
        rlm = self._load_test(test, tstart, tstop, pmin, parc, mask, samples, data, baseline, src_baseline, return_data, True)
        if return_data:
            group_ds, rlm = rlm
        else:
            group_ds = None

        # start report
        surfer_kwargs = self._surfer_plot_kwargs()
        info_section = report.add_section("Test Info")
        if parc:
            section = report.add_section(parc)
            caption = "Labels in the %s parcellation." % parc
            self._report_parc_image(section, caption)
        elif mask:
            title = "Whole Brain Masked by %s" % mask
            section = report.add_section(title)
            caption = "Mask: %s" % mask.capitalize()
            self._report_parc_image(section, caption)

        # Design matrix
        section = report.add_section("Design Matrix")
        section.append(rlm.design())

        # add results to report
        for term in rlm.column_names:
            res = rlm.tests[term]
            ds = rlm.coefficients_dataset(term)
            report.append(
                _report.source_time_results(
                    res, ds, None, include, surfer_kwargs, term, y='coeff'))

        self._report_test_info(info_section, group_ds or ds, test_obj, res, data)

    def make_report_rois(self, test, parc=None, pmin=None, tstart=None, tstop=None,
                         samples=10000, baseline=True, src_baseline=False,
                         redo=False, **state):
        """Create an HTML report on ROI time courses

        Parameters
        ----------
        test : str
            Test for which to create a report (entry in MneExperiment.tests).
        parc : str
            Parcellation that defines ROIs.
        pmin : None | scalar, 1 > pmin > 0 | 'tfce'
            Equivalent p-value for cluster threshold, or 'tfce' for
            threshold-free cluster enhancement.
        tstart : scalar
            Beginning of the time window for the test in seconds
            (default is the beginning of the epoch).
        tstop : scalar
            End of the time window for the test in seconds
            (default is the end of the epoch).
        samples : int > 0
            Number of samples used to determine cluster p values for spatio-
            temporal clusters (default 1000).
        baseline : bool | tuple
            Apply baseline correction using this period in sensor space.
            True to use the epoch's baseline specification (default).
        src_baseline : bool | tuple
            Apply baseline correction using this period in source space.
            True to use the epoch's baseline specification. The default is to
            not apply baseline correction.
        redo : bool
            If the target file already exists, delete and recreate it.
        ...
            State parameters.

        See Also
        --------
        load_test : load corresponding data and tests (use ``data="source.mean"``)
        """
        if 'sns_baseline' in state:
            baseline = state.pop('sns_baseline')
            warnings.warn("The sns_baseline parameter is deprecated, use baseline instead", DeprecationWarning)

        test_obj = self._tests[test]
        if samples < 1:
            raise ValueError("Need samples > 0 to run permutation test.")
        elif isinstance(test_obj, TwoStageTest):
            raise NotImplementedError("ROI analysis not implemented for two-"
                                      "stage tests")

        if parc is not None:
            state['parc'] = parc
        parc = self.get('parc', **state)
        if not parc:
            raise ValueError("No parcellation specified")
        data = TestDims('source.mean')
        self._set_analysis_options(data, baseline, src_baseline, pmin, tstart, tstop, parc)
        dst = self.get('report-file', mkdir=True, test=test)
        if self._need_not_recompute_report(dst, samples, data, redo):
            return

        res_data, res = self._load_test(test, tstart, tstop, pmin, parc, None, samples, data, baseline, src_baseline, True, True)

        # sorted labels
        labels_lh = []
        labels_rh = []
        for label in res.res.keys():
            if label.endswith('-lh'):
                labels_lh.append(label)
            elif label.endswith('-rh'):
                labels_rh.append(label)
            else:
                raise NotImplementedError("Label named %s" % repr(label.name))
        labels_lh.sort()
        labels_rh.sort()

        # start report
        title = self.format('{recording} {test_desc}')
        report = Report(title)

        # method intro (compose it later when data is available)
        ds0 = res_data[label]
        res0 = res.res[label]
        info_section = report.add_section("Test Info")
        self._report_test_info(info_section, res.n_trials_ds, test_obj, res0, data)

        # add parc image
        section = report.add_section(parc)
        caption = "ROIs in the %s parcellation." % parc
        self._report_parc_image(section, caption, res.subjects)

        # add content body
        n_subjects = len(res.subjects)
        colors = plot.colors_for_categorial(ds0.eval(res0._plot_model()))
        for label in chain(labels_lh, labels_rh):
            res_i = res.res[label]
            ds = res_data[label]
            title = label[:-3].capitalize()
            caption = "Mean in label %s." % label
            n = len(ds['subject'].cells)
            if n < n_subjects:
                title += ' (n=%i)' % n
                caption += " Data from %i of %i subjects." % (n, n_subjects)
            section.append(_report.time_results(
                res_i, ds, colors, title, caption, merged_dist=res.merged_dist))

        report.sign(('eelbrain', 'mne', 'surfer', 'scipy', 'numpy'))
        report.save_html(dst, meta={'samples': samples})

    def _make_report_eeg(self, test, pmin=None, tstart=None, tstop=None,
                         samples=10000, baseline=True, include=1, **state):
        # outdated (cache, load_test())
        """Create an HTML report on EEG sensor space spatio-temporal clusters

        Parameters
        ----------
        test : str
            Test for which to create a report (entry in MneExperiment.tests).
        pmin : None | scalar, 1 > pmin > 0 | 'tfce'
            Equivalent p-value for cluster threshold, or 'tfce' for
            threshold-free cluster enhancement.
        tstart : scalar
            Beginning of the time window for the test in seconds
            (default is the beginning of the epoch).
        tstop : scalar
            End of the time window for the test in seconds
            (default is the end of the epoch).
        samples : int > 0
            Number of samples used to determine cluster p values for spatio-
            temporal clusters (default 1000).
        baseline : bool | tuple
            Apply baseline correction using this period. True to use the epoch's
            baseline specification (default).
        include : 0 < scalar <= 1
            Create plots for all clusters with p-values smaller or equal this
            value (the default is 1, i.e. to show all clusters).
        ...
            State parameters.
        """
        data = TestDims("sensor")
        self._set_analysis_options(data, baseline, None, pmin, tstart, tstop)
        dst = self.get('report-file', mkdir=True, fmatch=False, test=test,
                       folder="EEG Spatio-Temporal", modality='eeg',
                       **state)
        if self._need_not_recompute_report(dst, samples, data, False):
            return

        # load data
        ds, res = self.load_test(test, tstart, tstop, pmin, None, None, samples,
                                 'sensor', baseline, None, True, True)

        # start report
        title = self.format('{recording} {test_desc}')
        report = Report(title)

        # info
        info_section = report.add_section("Test Info")
        self._report_test_info(info_section, ds, test, res, data, include)

        # add connectivity image
        p = plot.SensorMap(ds['eeg'], connectivity=True, show=False)
        image_conn = p.image("connectivity.png")
        info_section.add_figure("Sensor map with connectivity", image_conn)
        p.close()

        colors = plot.colors_for_categorial(ds.eval(res._plot_model()))
        report.append(_report.sensor_time_results(res, ds, colors, include))
        report.sign(('eelbrain', 'mne', 'scipy', 'numpy'))
        report.save_html(dst)

    def _make_report_eeg_sensors(self, test, sensors=('FZ', 'CZ', 'PZ', 'O1', 'O2'),
                                 pmin=None, tstart=None, tstop=None,
                                 samples=10000, baseline=True, redo=False,
                                 **state):
        # outdated (cache)
        """Create an HTML report on individual EEG sensors

        Parameters
        ----------
        test : str
            Test for which to create a report (entry in MneExperiment.tests).
        sensors : sequence of str
            Names of the sensors which to include.
        pmin : None | scalar, 1 > pmin > 0 | 'tfce'
            Equivalent p-value for cluster threshold, or 'tfce' for
            threshold-free cluster enhancement.
        tstart : scalar
            Beginning of the time window for the test in seconds
            (default is the beginning of the epoch).
        tstop : scalar
            End of the time window for the test in seconds
            (default is the end of the epoch).
        samples : int > 0
            Number of samples used to determine cluster p values for spatio-
            temporal clusters (default 1000).
        baseline : bool | tuple
            Apply baseline correction using this period. True to use the epoch's
            baseline specification (default).
        redo : bool
            If the target file already exists, delete and recreate it. This
            only applies to the HTML result file, not to the test.
        ...
            State parameters.
        """
        data = TestDims('sensor.sub')
        self._set_analysis_options(data, baseline, None, pmin, tstart, tstop)
        dst = self.get('report-file', mkdir=True, fmatch=False, test=test,
                       folder="EEG Sensors", modality='eeg', **state)
        if self._need_not_recompute_report(dst, samples, data, redo):
            return

        # load data
        test_obj = self._tests[test]
        ds = self.load_evoked(self.get('group'), baseline, True, vardef=test_obj.vars)

        # test that sensors are in the data
        eeg = ds['eeg']
        missing = [s for s in sensors if s not in eeg.sensor.names]
        if missing:
            raise ValueError("The following sensors are not in the data: %s" % missing)

        # start report
        title = self.format('{recording} {test_desc}')
        report = Report(title)

        # info
        info_section = report.add_section("Test Info")

        # add sensor map
        p = plot.SensorMap(ds['eeg'], show=False)
        p.mark_sensors(sensors)
        info_section.add_figure("Sensor map", p)
        p.close()

        # main body
        caption = "Signal at %s."
        test_kwargs = self._test_kwargs(samples, pmin, tstart, tstop, ('time', 'sensor'), None)
        ress = [self._make_test(eeg.sub(sensor=sensor), ds, test_obj, test_kwargs) for
                sensor in sensors]
        colors = plot.colors_for_categorial(ds.eval(ress[0]._plot_model()))
        for sensor, res in zip(sensors, ress):
            report.append(_report.time_results(res, ds, colors, sensor, caption % sensor))

        self._report_test_info(info_section, ds, test, res, data)
        report.sign(('eelbrain', 'mne', 'scipy', 'numpy'))
        report.save_html(dst)

    @staticmethod
    def _report_methods_brief(path):
        path = Path(path)
        items = [*path.parts[:-1], path.stem]
        return List('Methods brief', items[-3:])

    def _report_subject_info(self, ds, model):
        """Table with subject information

        Parameters
        ----------
        ds : Dataset
            Dataset with ``subject`` and ``n`` variables, and any factors in
            ``model``.
        model : str
            The model used for aggregating.
        """
        s_ds = self.show_subjects(asds=True)
        if 'n' in ds:
            if model:
                n_ds = table.repmeas('n', model, 'subject', ds=ds)
            else:
                n_ds = ds
            n_ds_aligned = align1(n_ds, s_ds['subject'], 'subject')
            s_ds.update(n_ds_aligned)
        return s_ds.as_table(
            midrule=True, count=True,
            caption="All subjects included in the analysis with trials per "
                    "condition")

    def _report_test_info(self, section, ds, test, res, data, include=None, model=True):
        """Top-level report info function

        Returns
        -------
        info : Table
            Table with preprocessing and test info.
        """
        test_obj = self._tests[test] if isinstance(test, str) else test

        # List of preprocessing parameters
        info = List("Analysis:")
        # epoch
        epoch = self.format('epoch = {epoch}')
        evoked_kind = self.get('evoked_kind')
        if evoked_kind:
            epoch += f' {evoked_kind}'
        if model is True:
            model = self.get('model')
        if model:
            epoch += f" ~ {model}"
        info.add_item(epoch)
        # inverse solution
        if data.source:
            info.add_item(self.format("cov = {cov}"))
            info.add_item(self.format("inv = {inv}"))
        # test
        info.add_item("test = %s  (%s)" % (test_obj.kind, test_obj.desc))
        if include is not None:
            info.add_item(f"Separate plots of all clusters with a p-value < {include}")
        section.append(info)

        # Statistical methods (for temporal tests, res is only representative)
        info = res.info_list()
        section.append(info)

        # subjects and state
        section.append(self._report_subject_info(ds, test_obj.model))
        section.append(self.show_state(hide=('hemi', 'subject', 'mrisubject')))
        return info

    def _report_parc_image(self, section, caption, subjects=None):
        "Add picture of the current parcellation"
        parc_name, parc = self._get_parc()
        with self._temporary_state:
            if isinstance(parc, IndividualSeededParc):
                if subjects is None:
                    raise RuntimeError("subjects needs to be specified for "
                                       "plotting individual parcellations")
                legend = None
                for subject in self:
                    # make sure there is at least one label
                    if not any(not l.name.startswith('unknown-') for l in
                               self.load_annot()):
                        section.add_image_figure("No labels", subject)
                        continue
                    brain = self.plot_annot()
                    if legend is None:
                        p = brain.plot_legend(show=False)
                        legend = p.image('parc-legend')
                        p.close()
                    section.add_image_figure(brain.image('parc'), subject)
                    brain.close()
                return

            # one parc for all subjects
            self.set(mrisubject=self.get('common_brain'))
            brain = self.plot_annot(axw=500)
        legend = brain.plot_legend(show=False)
        content = [brain.image('parc'), legend.image('parc-legend')]
        section.add_image_figure(content, caption)
        brain.close()
        legend.close()

    def _make_report_lm(self, pmin=0.01, baseline=True, src_baseline=False,
                        mask='lobes'):
        """Report for a first level (single subject) LM

        Parameters
        ----------
        pmin : scalar
            Threshold p-value for uncorrected SPMs.
        """
        if not isinstance(self._tests[self.get('test')], TwoStageTest):
            raise NotImplementedError("Only two-stage tests")

        with self._temporary_state:
            self._set_analysis_options('source', baseline, src_baseline, pmin,
                                       None, None, mask=mask)
            dst = self.get('subject-spm-report', mkdir=True)
            lm = self._load_spm(baseline, src_baseline)

            title = self.format('{recording} {test_desc}')
            surfer_kwargs = self._surfer_plot_kwargs()

        report = Report(title)
        report.append(_report.source_time_lm(lm, pmin, surfer_kwargs))

        # report signature
        report.sign(('eelbrain', 'mne', 'surfer', 'scipy', 'numpy'))
        report.save_html(dst)

    def make_report_coreg(self, file_name=None, **state):
        """Create HTML report with plots of the MEG/MRI coregistration

        Parameters
        ----------
        file_name : str
            Where to save the report (default is in the root/methods director).
        ...
            State parameters.
        """
        from matplotlib import pyplot
        from mayavi import mlab

        mri = self.get('mri', **state)
        group = self.get('group')
        title = 'Coregistration'
        if group != 'all':
            title += ' ' + group
        if mri:
            title += ' ' + mri
        if file_name is None:
            file_name = join(self.get('methods-dir', mkdir=True), title + '.html')
        report = Report(title)
        for subject in self:
            mrisubject = self.get('mrisubject')
            fig = self.plot_coreg()
            fig.scene.camera.parallel_projection = True
            fig.scene.camera.parallel_scale = .175
            mlab.draw(fig)

            # front
            mlab.view(90, 90, 1, figure=fig)
            im_front = Image.from_array(mlab.screenshot(figure=fig), 'front')

            # left
            mlab.view(0, 270, 1, roll=90, figure=fig)
            im_left = Image.from_array(mlab.screenshot(figure=fig), 'left')

            mlab.close(fig)

            # MRI/BEM figure
            if is_fake_mri(self.get('mri-dir')):
                bem_fig = None
            else:
                bem_fig = mne.viz.plot_bem(mrisubject, self.get('mri-sdir'),
                                           brain_surfaces='white', show=False)

            # add to report
            if subject == mrisubject:
                title = subject
                caption = "Coregistration for subject %s." % subject
            else:
                title = "%s (%s)" % (subject, mrisubject)
                caption = ("Coregistration for subject %s (MRI-subject %s)." %
                           (subject, mrisubject))
            section = report.add_section(title)
            if bem_fig is None:
                section.add_figure(caption, (im_front, im_left))
            else:
                section.add_figure(caption, (im_front, im_left, bem_fig))
                pyplot.close(bem_fig)

        report.sign()
        report.save_html(file_name)

    def make_src(self, **kwargs):
        """Make the source space
        
        Parameters
        ----------
        ...
            State parameters.
        """
        dst = self.get('src-file', **kwargs)
        subject = self.get('mrisubject')
        common_brain = self.get('common_brain')

        is_scaled = (subject != common_brain) and is_fake_mri(self.get('mri-dir'))

        if is_scaled:
            # make sure the source space exists for the original
            with self._temporary_state:
                self.make_src(mrisubject=common_brain)
                orig = self.get('src-file')

            if exists(dst):
                if getmtime(dst) >= getmtime(orig):
                    return
                os.remove(dst)

            src = self.get('src')
            self._log.info(f"Scaling {src} source space for {subject}...")
            subjects_dir = self.get('mri-sdir')
            mne.scale_source_space(subject, f'{{subject}}-{src}-src.fif', subjects_dir=subjects_dir)
        elif exists(dst):
            return
        else:
            src = self.get('src')
            kind, param, special = SRC_RE.match(src).groups()
            self._log.info(f"Generating {src} source space for {subject}...")
            if kind == 'vol':
                if subject == 'fsaverage':
                    bem = self.get('bem-file')
                else:
                    raise NotImplementedError(
                        "Volume source space for subject other than fsaverage")
                if special == 'brainstem':
                    name = 'brainstem'
                    voi = ['Brain-Stem', '3rd-Ventricle']
                    voi_lat = ('Thalamus-Proper', 'VentralDC')
                    remove_midline = False
                else:
                    name = 'cortex'
                    voi = []
                    voi_lat = ('Cerebral-Cortex', 'Cerebral-White-Matter')
                    remove_midline = True
                voi.extend('%s-%s' % fmt for fmt in product(('Left', 'Right'), voi_lat))
                sss = mne.setup_volume_source_space(
                    subject, pos=float(param), bem=bem,
                    mri=join(self.get('mri-dir'), 'mri', 'aseg.mgz'),
                    volume_label=voi, subjects_dir=self.get('mri-sdir'))
                sss = merge_volume_source_space(sss, name)
                sss = prune_volume_source_space(sss, int(param), 2, remove_midline=remove_midline)
            else:
                assert not special
                spacing = kind + param
                sss = mne.setup_source_space(
                    subject, spacing=spacing, add_dist=True,
                    subjects_dir=self.get('mri-sdir'))
            mne.write_source_spaces(dst, sss)

    def _test_kwargs(self, samples, pmin, tstart, tstop, data, parc_dim):
        "Compile kwargs for testnd tests"
        kwargs = {'samples': samples, 'tstart': tstart, 'tstop': tstop,
                  'parc': parc_dim}
        if pmin == 'tfce':
            kwargs['tfce'] = True
        elif pmin is not None:
            kwargs['pmin'] = pmin
            kwargs.update(self._cluster_criteria_kwargs(data))
        return kwargs

    def _make_test(self, y, ds, test, kwargs, force_permutation=False):
        """Compute test results

        Parameters
        ----------
        y : NDVar
            Dependent variable.
        ds : Dataset
            Other variables.
        test : Test | str
            Test, or name of the test to perform.
        kwargs : dict
            Test parameters (from :meth:`._test_kwargs`).
        force_permutation : bool
            Conduct permutations regardless of whether there are any clusters.
        """
        test_obj = test if isinstance(test, Test) else self._tests[test]
        if not isinstance(test_obj, EvokedTest):
            raise RuntimeError("Test kind=%s" % test_obj.kind)
        return test_obj.make(y, ds, force_permutation, kwargs)

    def merge_bad_channels(self):
        """Merge bad channel definitions for different sessions

        Load the bad channel definitions for all sessions of the current
        subject and save the union for all sessions.

        See Also
        --------
        make_bad_channels : set bad channels for a single session
        """
        n_chars = max(map(len, self._sessions))
        # collect bad channels
        bads = set()
        sessions = []
        with self._temporary_state:
            # ICARaw merges bad channels dynamically, so explicit merge needs to
            # be performed lower in the hierarchy
            self.set(raw='raw')
            for session in self.iter('session'):
                if exists(self.get('raw-file')):
                    bads.update(self.load_bad_channels())
                    sessions.append(session)
                else:
                    print("%%-%is: skipping, raw file missing" % n_chars % session)
            # update bad channel files
            for session in sessions:
                print(session.ljust(n_chars), end=': ')
                self.make_bad_channels(bads, session=session)

    def next(self, field='subject'):
        """Change field to the next value

        Parameters
        ----------
        field : str | list of str
            The field for which the value should be changed (default 'subject').
            Can also contain multiple fields, e.g. ``['subject', 'session']``.
        """
        if isinstance(field, str):
            current = self.get(field)
            values = self.get_field_values(field)
            def fmt(x): return x
        else:
            current = tuple(self.get(f) for f in field)
            values = list(product(*(self.get_field_values(f) for f in field)))
            def fmt(x): return '/'.join(x)

        # find the index of the next value
        if current in values:
            idx = values.index(current) + 1
            if idx == len(values):
                idx = -1
        else:
            for idx in range(len(values)):
                if values[idx] > current:
                    break
            else:
                idx = -1

        # set the next value
        if idx == -1:
            next_ = values[0]
            print(f"The last {fmt(field)} was reached; rewinding to {fmt(next_)}")
        else:
            next_ = values[idx]
            print(f"{fmt(field)}: {fmt(current)} -> {fmt(next_)}")

        if isinstance(field, str):
            self.set(**{field: next_})
        else:
            self.set(**dict(zip(field, next_)))

    def plot_annot(self, parc=None, surf=None, views=None, hemi=None,
                   borders=False, alpha=0.7, w=None, h=None, axw=None, axh=None,
                   foreground=None, background=None, seeds=False, **state):
        """Plot the annot file on which the current parcellation is based

        Parameters
        ----------
        parc : None | str
            Parcellation to plot. If None (default), use parc from the current
            state.
        surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
            Freesurfer surface to use as brain geometry.
        views : str | iterator of str
            View or views to show in the figure.
        hemi : 'lh' | 'rh' | 'both' | 'split'
            Which hemispheres to plot (default includes hemisphere with more
            than one label in the annot file).
        borders : bool | int
            Show only label borders (PySurfer Brain.add_annotation() argument).
        alpha : scalar
            Alpha of the annotation (1=opaque, 0=transparent, default 0.7).
        axw : int
            Figure width per hemisphere.
        foreground : mayavi color
            Figure foreground color (i.e., the text color).
        background : mayavi color
            Figure background color.
        seeds : bool
            Plot seeds as points (only applies to seeded parcellations).
        ...
            State parameters.

        Returns
        -------
        brain : Brain
            PySurfer Brain with the parcellation plot.
        legend : ColorList
            ColorList figure with the legend.
        """
        if parc is not None:
            state['parc'] = parc
        self.set(**state)

        self.make_annot()

        parc_name, parc = self._get_parc()
        if seeds:
            if not isinstance(parc, SeededParc):
                raise ValueError(
                    "seeds=True is only valid for seeded parcellation, "
                    "not for parc=%r" % (parc_name,))
            # if seeds are defined on a scaled common-brain, we need to plot the
            # scaled brain:
            plot_on_scaled_common_brain = isinstance(parc, IndividualSeededParc)
        else:
            plot_on_scaled_common_brain = False

        mri_sdir = self.get('mri-sdir')
        if (not plot_on_scaled_common_brain) and is_fake_mri(self.get('mri-dir')):
            subject = self.get('common_brain')
        else:
            subject = self.get('mrisubject')

        kwa = self._surfer_plot_kwargs(surf, views, foreground, background,
                                       None, hemi)
        brain = plot.brain.annot(parc_name, subject, borders=borders, alpha=alpha,
                                 w=w, h=h, axw=axw, axh=axh,
                                 subjects_dir=mri_sdir, **kwa)
        if seeds:
            from mayavi import mlab

            seeds = parc.seeds_for_subject(subject)
            seed_points = {hemi: [np.atleast_2d(coords) for name, coords in
                                  seeds.items() if name.endswith(hemi)]
                           for hemi in ('lh', 'rh')}
            plot_points = {hemi: np.vstack(points).T if len(points) else None
                           for hemi, points in seed_points.items()}
            for hemisphere in brain.brains:
                if plot_points[hemisphere.hemi] is None:
                    continue
                x, y, z = plot_points[hemisphere.hemi]
                mlab.points3d(x, y, z, figure=hemisphere._f, color=(1, 0, 0),
                              scale_factor=10)
            brain.set_parallel_view(scale=True)

        return brain

    def plot_brain(self, common_brain=True, **brain_kwargs):
        """Plot the brain model

        Parameters
        ----------
        common_brain : bool
            If the current mrisubject is a scaled MRI, use the common_brain
            instead.
        ... :
            :class:`~plot._brain_object.Brain` options as keyword arguments.
        """
        from ..plot._brain_object import Brain

        brain_args = self._surfer_plot_kwargs()
        brain_args.update(brain_kwargs)
        brain_args['subjects_dir'] = self.get('mri-sdir')

        # find subject
        if common_brain and is_fake_mri(self.get('mri-dir')):
            mrisubject = self.get('common_brain')
            self.set(mrisubject=mrisubject, match=False)
        else:
            mrisubject = self.get('mrisubject')

        return Brain(mrisubject, **brain_args)

    def plot_coreg(self, dig=True, parallel=True, **state):
        """Plot the coregistration (Head shape and MEG helmet)

        Parameters
        ----------
        dig : bool
            Plot the digitization points (default True; 'fiducials' to plot
            fiducial points only).
        parallel : bool
            Set parallel view.
        ...
            State parameters.

        Notes
        -----
        Uses :func:`mne.viz.plot_alignment`
        """
        self.set(**state)
        with self._temporary_state:
            raw = self.load_raw(raw='raw')
        fig = mne.viz.plot_alignment(
            raw.info, self.get('trans-file'), self.get('mrisubject'),
            self.get('mri-sdir'), meg=('helmet', 'sensors'), dig=dig,
            interaction='terrain')
        if parallel:
            fig.scene.camera.parallel_projection = True
            fig.scene.camera.parallel_scale = .2
            fig.scene.camera.position = [0, .5, .04]
            fig.scene.camera.focal_point = [0, 0, .04]
            fig.render()
        return fig

    def plot_whitened_gfp(self, s_start=None, s_stop=None, run=None):
        """Plot the GFP of the whitened evoked to evaluate the the covariance matrix

        Parameters
        ----------
        s_start : str
            Subject at which to start (default is the first subject).
        s_stop: str
            Subject at which to stop (default is the last subject).
        run : bool
            Run the GUI after plotting (default depends on environment).
        """
        gfps = []
        subjects = []
        with self._temporary_state:
            self.set(model='')
            for subject in self.iter_range(s_start, s_stop):
                cov = self.load_cov()
                picks = np.arange(len(cov.ch_names))
                ds = self.load_evoked(baseline=True)
                whitened_evoked = mne.whiten_evoked(ds[0, 'evoked'], cov, picks)
                gfp = whitened_evoked.data.std(0)

                gfps.append(gfp)
                subjects.append(subject)

        colors = plot.colors_for_oneway(subjects)
        title = "Whitened Global Field Power (%s)" % self.get('cov')
        fig = plot._base.Figure(1, title, h=7, run=run)
        ax = fig._axes[0]
        for subject, gfp in zip(subjects, gfps):
            ax.plot(whitened_evoked.times, gfp, label=subject,
                    color=colors[subject])
        ax.legend(loc='right')
        fig.show()
        return fig

    def plot_evoked(self, subjects=None, separate=False, baseline=True, ylim='same',
                    run=None, **kwargs):
        """Plot evoked sensor data

        Parameters
        ----------
        subjects : str | 1 | -1
            Subject(s) for which to load data. Can be a single subject
            name or a group name such as ``'all'``. ``1`` to use the current
            subject; ``-1`` for the current group. Default is current subject
            (or group if ``group`` is specified).
        separate : bool
            When plotting a group, plot all subjects separately instead or the group
            average (default False).
        baseline : bool | tuple
            Apply baseline correction using this period. True to use the epoch's
            baseline specification (default).
        ylim : 'same' | 'different'
            Use the same or different y-axis limits for different subjects
            (default 'same').
        run : bool
            Run the GUI after plotting (default in accordance with plotting
            default).
        ...
            State parameters.
        """
        subject, group = self._process_subject_arg(subjects, kwargs)
        model = self.get('model') or None
        epoch = self.get('epoch')
        if model:
            model_name = f"~{model}"
        elif subject or separate:
            model_name = "Average"
        else:
            model_name = "Grand Average"

        if subject:
            ds = self.load_evoked(baseline=baseline)
            y = guess_y(ds)
            title = f"{subject} {epoch} {model_name}"
            return plot.TopoButterfly(y, model, ds=ds, title=title, run=run)
        elif separate:
            plots = []
            vlim = []
            for subject in self.iter(group=group):
                ds = self.load_evoked(baseline=baseline)
                y = guess_y(ds)
                title = f"{subject} {epoch} {model_name}"
                p = plot.TopoButterfly(y, model, ds=ds, title=title, run=False)
                plots.append(p)
                vlim.append(p.get_vlim())

            if ylim.startswith('s'):
                vlim = np.array(vlim)
                vmax = np.abs(vlim, out=vlim).max()
                for p in plots:
                    p.set_vlim(vmax)
            elif not ylim.startswith('d'):
                raise ValueError("ylim=%s" % repr(ylim))

            if run or plot._base.do_autorun():
                gui.run()
        else:
            ds = self.load_evoked(group, baseline=baseline)
            y = guess_y(ds)
            title = f"{group} {epoch} {model_name}"
            return plot.TopoButterfly(y, model, ds=ds, title=title, run=run)

    def plot_label(self, label, surf=None, views=None, w=600):
        """Plot a label"""
        if isinstance(label, str):
            label = self.load_label(label)
        title = label.name
        hemi = 'split' if isinstance(label, mne.BiHemiLabel) else label.hemi
        kwargs = self._surfer_plot_kwargs(surf, views, hemi=hemi)
        brain = self.plot_brain(title=title, w=w, **kwargs)
        brain.add_label(label, alpha=0.75)
        return brain

    def plot_raw(self, decim=10, xlim=5, add_bads=True, subtract_mean=False, **state):
        """Plot raw sensor data

        Parameters
        ----------
        decim : int
            Decimate data for faster plotting (default 10).
        xlim : scalar
            Number of seconds to display (default 5 s).
        add_bads : bool | list
            Add bad channel information to the bad channels text file (default
            True).
        subtract_mean : bool
            Subtract the mean from each channel (useful when plotting raw data
            recorded with DC offset).
        ...
            State parameters.
        """
        raw = self.load_raw(add_bads, ndvar=True, decim=decim, **state)
        name = self.format("{subject} {recording} {raw}")
        if raw.info['meas'] == 'V':
            vmax = 1.5e-4
        elif raw.info['meas'] == 'B':
            vmax = 2e-12
        else:
            vmax = None
        if subtract_mean:
            raw -= raw.mean('time')
        return plot.TopoButterfly(raw, w=0, h=3, xlim=xlim, vmax=vmax, name=name)

    def run_mne_analyze(self, modal=False):
        """Run mne_analyze

        Parameters
        ----------
        modal : bool
            Causes the shell to block until mne_analyze is closed.

        Notes
        -----
        Sets the current directory to raw-dir, and sets the SUBJECT and
        SUBJECTS_DIR to current values
        """
        subp.run_mne_analyze(self.get('raw-dir'), self.get('mrisubject'),
                             self.get('mri-sdir'), modal)

    def run_mne_browse_raw(self, modal=False):
        """Run mne_analyze

        Parameters
        ----------
        modal : bool
            Causes the shell to block until mne_browse_raw is closed.

        Notes
        -----
        Sets the current directory to raw-dir, and sets the SUBJECT and
        SUBJECTS_DIR to current values
        """
        subp.run_mne_browse_raw(self.get('raw-dir'), self.get('mrisubject'),
                                self.get('mri-sdir'), modal)

    def set(self, subject=None, match=True, allow_asterisk=False, **state):
        """
        Set variable values.

        Parameters
        ----------
        subject : str
            Set the `subject` value. The corresponding `mrisubject` is
            automatically set to the corresponding mri subject.
        match : bool
            For fields with pre-defined values, only allow valid values (default
            ``True``).
        allow_asterisk : bool
            If a value contains ``'*'``, set the value without the normal value
            evaluation and checking mechanisms (default ``False``).
        ...
            State parameters.
        """
        if subject is not None:
            if 'group' not in state:
                state['subject'] = subject
                subject = None
        FileTree.set(self, match, allow_asterisk, **state)
        if subject is not None:
            FileTree.set(self, match, allow_asterisk, subject=subject)

    def _post_set_group(self, _, group):
        if group == '*' or group not in self._groups:
            return
        group_members = self._groups[group]
        self._field_values['subject'] = group_members
        subject = self.get('subject')
        if subject != '*' and subject not in group_members and group_members:
            self.set(group_members[0])

    def set_inv(self, ori='free', snr=3, method='dSPM', depth=None,
                pick_normal=False):
        """Set the type of inverse solution used for source estimation

        Parameters
        ----------
        ori : 'free' | 'fixed' | 'vec' | float ]0, 1]
            Orientation constraint (default 'free'; use a float to specify a
            loose constraint).
        snr : scalar
            SNR estimate for regularization (default 3).
        method : 'MNE' | 'dSPM' | 'sLORETA' | 'eLORETA'
            Inverse method.
        depth : None | float [0, 1]
            Depth weighting (default ``None`` to use mne default 0.8; ``0`` to
            disable depth weighting).
        pick_normal : bool
            Pick the normal component of the estimated current vector (default
            False).
        """
        self.set(inv=self._inv_str(ori, snr, method, depth, pick_normal))

    @staticmethod
    def _inv_str(ori, snr, method, depth, pick_normal):
        "Construct inv str from settings"
        if isinstance(ori, str):
            if ori not in ('free', 'fixed', 'vec'):
                raise ValueError('ori=%r' % (ori,))
        elif not 0 <= ori <= 1:
            raise ValueError("ori=%r; must be in range [0, 1]" % (ori,))
        else:
            ori = 'loose%s' % str(ori)[1:]

        if snr <= 0:
            raise ValueError("snr=%r" % (snr,))

        if method not in INV_METHODS:
            raise ValueError("method=%r" % (method,))

        items = [ori, '%g' % snr, method]

        if depth is None:
            pass
        elif depth < 0 or depth > 1:
            raise ValueError("depth=%r; must be in range [0, 1]" % (depth,))
        else:
            items.append('%g' % depth)

        if pick_normal:
            if ori == 'vec':
                raise ValueError("ori='vec' and pick_normal=True are incompatible")
            items.append('pick_normal')

        return '-'.join(items)

    @staticmethod
    def _inv_params(inv):
        "(ori, snr, method, depth, pick_normal)"
        m = inv_re.match(inv)
        if m is None:
            raise ValueError("Invalid inverse specification: inv=%r" % inv)

        ori, snr, method, depth, pick_normal = m.groups()
        if ori.startswith('loose'):
            ori = float(ori[5:])
            if not 0 <= ori <= 1:
                raise ValueError('inv=%r (first value of inv (loose '
                                 'parameter) needs to be in [0, 1]' % (inv,))
        elif ori == 'vec' and pick_normal:
            raise ValueError("inv=%r (vector source estimates and pick_normal"
                             "are mutually exclusive)")

        snr = float(snr)
        if snr <= 0:
            raise ValueError('inv=%r (snr=%r)' % (inv, snr))

        if method not in INV_METHODS:
            raise ValueError("inv=%r (method=%r)" % (inv, method))

        if depth is not None:
            depth = float(depth)
            if not 0 <= depth <= 1:
                raise ValueError("inv=%r (depth=%r, needs to be in range "
                                 "[0, 1])" % (inv, depth))

        return ori, snr, method, depth, bool(pick_normal)

    @classmethod
    def _eval_inv(cls, inv):
        cls._inv_params(inv)
        return inv

    def _post_set_inv(self, _, inv):
        if '*' in inv:
            self._params['make_inv_kw'] = None
            self._params['apply_inv_kw'] = None
            return

        ori, snr, method, depth, pick_normal = self._inv_params(inv)

        if ori == 'fixed':
            make_kw = {'fixed': True}
        elif ori == 'free' or ori == 'vec':
            make_kw = {'loose': 1}
        elif isinstance(ori, float):
            make_kw = {'loose': ori}
        else:
            raise RuntimeError("ori=%r (in inv=%r)" % (ori, inv))

        if depth is None:
            make_kw['depth'] = 0.8
        elif depth == 0:
            make_kw['depth'] = None
        else:
            make_kw['depth'] = depth

        apply_kw = {'method': method, 'lambda2': 1. / snr ** 2}
        if ori == 'vec':
            apply_kw['pick_ori'] = 'vector'
        elif pick_normal:
            apply_kw['pick_ori'] = 'normal'

        self._params['make_inv_kw'] = make_kw
        self._params['apply_inv_kw'] = apply_kw

    def _eval_model(self, model):
        if model == '':
            return model
        elif len(model) > 1 and '*' in model:
            raise ValueError("model=%r; To specify interactions, use '%' instead of '*'")

        factors = [v.strip() for v in model.split('%')]

        # find order value for each factor
        ordered_factors = {}
        unordered_factors = []
        for factor in sorted(factors):
            assert_is_legal_dataset_key(factor)
            if factor in self._model_order:
                ordered_factors[self._model_order.index(factor)] = factor
            else:
                unordered_factors.append(factor)

        # recompose
        model = [ordered_factors[v] for v in sorted(ordered_factors)]
        if unordered_factors:
            model.extend(unordered_factors)
        return '%'.join(model)

    def _eval_src(self, src):
        m = SRC_RE.match(src)
        if not m:
            raise ValueError(f'src={src}')
        kind, param, special = m.groups()
        if special and kind != 'vol':
            raise ValueError(f'src={src}')
        return src

    def _update_mrisubject(self, fields):
        subject = fields['subject']
        mri = fields['mri']
        if subject == '*' or mri == '*':
            return '*'
        return self._mri_subjects[mri][subject]

    def _update_session(self, fields):
        epoch = fields['epoch']
        if epoch in self._epochs:
            epoch = self._epochs[epoch]
            if isinstance(epoch, (PrimaryEpoch, SecondaryEpoch)):
                return epoch.session
            else:
                return  # default for non-primary epoch
        elif not epoch or epoch == '*':
            return  # don't force session
        return '*'  # if a named epoch is not in _epochs it might be a removed epoch

    def _update_src_name(self, fields):
        "Because 'ico-4' is treated in filenames  as ''"
        return '' if fields['src'] == 'ico-4' else fields['src']

    def _eval_parc(self, parc):
        if parc in self._parcs:
            if isinstance(self._parcs[parc], SeededParc):
                raise ValueError("Seeded parc set without size, use e.g. "
                                 "parc='%s-25'" % parc)
            else:
                return parc
        m = SEEDED_PARC_RE.match(parc)
        if m:
            name = m.group(1)
            if isinstance(self._parcs.get(name), SeededParc):
                return parc
            else:
                raise ValueError("No seeded parc with name %r" % name)
        else:
            raise ValueError("parc=%r" % parc)

    def _get_parc(self):
        """Parc information

        Returns
        -------
        parc : str
            The current parc setting.
        params : dict | None
            The parc definition (``None`` for ``parc=''``).
        """
        parc = self.get('parc')
        if parc == '':
            return '', None
        elif parc in self._parcs:
            return parc, self._parcs[parc]
        else:
            return parc, self._parcs[SEEDED_PARC_RE.match(parc).group(1)]

    def _post_set_test(self, _, test):
        if test != '*' and test in self._tests:  # with vmatch=False, test object might not be availale
            test_obj = self._tests[test]
            if test_obj.model is not None:
                self.set(model=test_obj._within_model)

    def _set_analysis_options(self, data, baseline, src_baseline, pmin,
                              tstart, tstop, parc=None, mask=None, decim=None,
                              test_options=(), folder_options=()):
        """Set templates for paths with test parameters

        analysis:  preprocessing up to source estimate epochs (not parcellation)
        folder: parcellation (human readable)
        test_dims: parcellation (as used for spatio-temporal cluster test
        test_options: baseline, permutation test method etc.

        also sets `parc`

        Parameters
        ----------
        data : TestDims
            Whether the analysis is in sensor or source space.
        ...
        src_baseline :
            Should be False if data=='sensor'.
        ...
        decim : int
            Decimation factor (default is None, i.e. based on epochs).
        test_options : sequence of str
            Additional, test-specific tags.
        """
        data = TestDims.coerce(data)
        # data kind (sensor or source space)
        if data.sensor:
            analysis = '{sns_kind} {evoked_kind}'
        elif data.source:
            analysis = '{src_kind} {evoked_kind}'
        else:
            raise RuntimeError(f"data={data.string!r}")

        # determine report folder (reports) and test_dims (test-files)
        kwargs = {'test_dims': data.string}
        if data.source is True:
            if parc is None:
                if mask:
                    folder = "%s masked" % mask
                    kwargs['parc'] = mask
                    if pmin is None:
                        # When not doing clustering, parc does not affect
                        # results, so we don't need to distinguish parc and mask
                        kwargs['test_dims'] = mask
                    else:  # parc means disconnecting
                        kwargs['test_dims'] = '%s-mask' % mask
                else:
                    folder = "Whole Brain"
                    # only compute unmasked test once (probably rare anyways)
                    kwargs['parc'] = 'aparc'
                    kwargs['test_dims'] = 'unmasked'
            elif mask:
                raise ValueError("Can't specify mask together with parc")
            elif pmin is None or pmin == 'tfce':
                raise NotImplementedError(
                    "Threshold-free test (pmin=%r) is not implemented for "
                    "parcellation (parc parameter). Use a mask instead, or do "
                    "a cluster-based test." % pmin)
            else:
                folder = parc
                kwargs['parc'] = parc
                kwargs['test_dims'] = parc
        elif data.source:  # source-space ROIs
            if not parc:
                raise ValueError("Need parc for ROI definition")
            kwargs['parc'] = parc
            kwargs['test_dims'] = '%s.%s' % (parc, data.source)
            if data.source == 'mean':
                folder = '%s ROIs' % parc
            else:
                folder = '%s %s' % (parc, data.source)
        elif parc:
            raise ValueError(f"Sensor analysis (data={data.string!r}) can't have parc")
        elif data.sensor:
            folder = 'Sensor' if data.y_name == 'meg' else 'EEG'
            if data.sensor is not True:
                folder = f'{folder} {data.sensor}'
        else:
            raise RuntimeError(f"data={data.string!r}")

        if folder_options:
            folder += ' ' + ' '.join(folder_options)

        # test properties
        items = []

        # baseline (default is baseline correcting in sensor space)
        epoch_baseline = self._epochs[self.get('epoch')].baseline
        if src_baseline:
            assert data.source
            if baseline is True or baseline == epoch_baseline:
                items.append('snsbl')
            elif baseline:
                items.append('snsbl=%s' % _time_window_str(baseline))

            if src_baseline is True or src_baseline == epoch_baseline:
                items.append('srcbl')
            else:
                items.append('srcbl=%s' % _time_window_str(src_baseline))
        else:
            if not baseline:
                items.append('nobl')
            elif baseline is True or baseline == epoch_baseline:
                pass
            else:
                items.append('bl=%s' % _time_window_str(baseline))

        # pmin
        if pmin is not None:
            # source connectivity
            connectivity = self.get('connectivity')
            if connectivity and not data.source:
                raise NotImplementedError(f"connectivity={connectivity!r} is not implemented for data={data!r}")
            elif connectivity:
                items.append(connectivity)

            items.append(str(pmin))

            # cluster criteria
            if pmin != 'tfce':
                select_clusters = self.get('select_clusters')
                if select_clusters:
                    items.append(select_clusters)

        # time window
        if tstart is not None or tstop is not None:
            items.append(_time_window_str((tstart, tstop)))
        if decim is not None:
            assert isinstance(decim, int)
            items.append(str(decim))

        items.extend(test_options)

        self.set(test_options=' '.join(items), analysis=analysis, folder=folder, **kwargs)

    def show_bad_channels(self, sessions=None, **state):
        """List bad channels

        Parameters
        ----------
        sessions : True | sequence of str
            By default, bad channels for the current session are shown. Set
            ``sessions`` to ``True`` to show bad channels for all sessions, or
            a list of session names to show bad channeles for these sessions.
        ...
            State parameters.

        Notes
        -----
        ICA Raw pipes merge bad channels from different sessions (by combining
        the bad channels from all sessions).
        """
        if state:
            self.set(**state)

        if sessions is True:
            use_sessions = self._sessions
        elif sessions:
            use_sessions = sessions
        else:
            use_sessions = None

        if use_sessions is None:
            bad_by_s = {k: self.load_bad_channels() for k in self}
            list_sessions = False
        else:
            bad_channels = {k: self.load_bad_channels() for k in
                            self.iter(('subject', 'session'), values={'session': use_sessions})}
            # whether they are equal between sessions
            bad_by_s = {}
            for (subject, session), bads in bad_channels.items():
                if subject in bad_by_s:
                    if bad_by_s[subject] != bads:
                        list_sessions = True
                        break
                else:
                    bad_by_s[subject] = bads
            else:
                list_sessions = False

        # table
        session_desc = ', '.join(use_sessions) if use_sessions else self.get('session')
        caption = f"Bad channels in {session_desc}"
        if list_sessions:
            t = fmtxt.Table('l' * (1 + len(use_sessions)), caption=caption)
            t.cells('Subject', *use_sessions)
            t.midrule()
            for subject in sorted(bad_by_s):
                t.cell(subject)
                for session in use_sessions:
                    t.cell(', '.join(bad_channels[subject, session]))
        else:
            if use_sessions is not None:
                caption += " (all sessions equal)"
            t = fmtxt.Table('ll', caption=caption)
            t.cells('Subject', 'Bad channels')
            t.midrule()
            for subject in sorted(bad_by_s):
                t.cells(subject, ', '.join(bad_by_s[subject]))
        return t

    def show_file_status(self, temp, col=None, row='subject', *args, **kwargs):
        """Compile a table about the existence of files

        Parameters
        ----------
        temp : str
            The name of the path template for the files to examine.
        col : None | str
            Field over which to alternate columns (default is a single column).
        row : str
            Field over which to alternate rows (default 'subject').
        count : bool
            Add a column with a number for each line (default True).
        present : 'time' | 'date' | str
            String to display when a given file is present. 'time' to use last
            modification date and time (default); 'date' for date only.
        absent : str
            String to display when a given file is absent (default '-').
        ... :
            :meth:`MneExperiment.iter` parameters.

        Examples
        --------
        >>> e.show_file_status('rej-file')
            Subject   Rej-file
        -------------------------------
        0   A0005     07/22/15 13:03:08
        1   A0008     07/22/15 13:07:57
        2   A0028     07/22/15 13:22:04
        3   A0048     07/22/15 13:25:29
        >>> e.show_file_status('rej-file', 'raw')
            Subject   0-40   0.1-40              1-40   Clm
        ---------------------------------------------------
        0   A0005     -      07/22/15 13:03:08   -      -
        1   A0008     -      07/22/15 13:07:57   -      -
        2   A0028     -      07/22/15 13:22:04   -      -
        3   A0048     -      07/22/15 13:25:29   -      -
        """
        return FileTree.show_file_status(self, temp, row, col, *args, **kwargs)

    def show_raw_info(self, **state):
        "Display the selected pipeline for raw processing"
        raw = self.get('raw', **state)
        pipe = source_pipe = self._raw[raw]
        pipeline = [pipe]
        while source_pipe.name != 'raw':
            source_pipe = source_pipe.source
            pipeline.insert(0, source_pipe)
        print(f"Preprocessing pipeline: {' --> '.join(p.name for p in pipeline)}")

        # pipe-specific
        if isinstance(pipe, RawICA):
            table = fmtxt.Table('lrr')
            table.cells('Subject', 'n components', 'reject')
            table.midrule()
            for subject in self:
                table.cell(subject)
                filename = self.get('ica-file')
                if exists(filename):
                    ica = self.load_ica()
                    table.cells(ica.n_components_, len(ica.exclude))
                else:
                    table.cells("No ICA-file", '')
            print()
            print(table)

    def show_reg_params(self, asds=False, **kwargs):
        """Show the covariance matrix regularization parameters

        Parameters
        ----------
        asds : bool
            Return a dataset with the parameters (default False).
        ...
            State parameters.
        """
        if kwargs:
            self.set(**kwargs)
        subjects = []
        reg = []
        for subject in self:
            path = self.get('cov-info-file')
            if exists(path):
                with open(path, 'r') as fid:
                    text = fid.read()
                reg.append(float(text.strip()))
            else:
                reg.append(float('nan'))
            subjects.append(subject)
        ds = Dataset()
        ds['subject'] = Factor(subjects)
        ds['reg'] = Var(reg)
        if asds:
            return ds
        else:
            print(ds)

    def show_rej_info(self, flagp=None, asds=False, bads=False, **state):
        """Information about artifact rejection

        Parameters
        ----------
        flagp : scalar
            Flag entries whose percentage of good trials is lower than this
            number.
        asds : bool
            Return a Dataset with the information (default is to print it).
        bads : bool
            Display bad channel names (not just number of bad channels).

        Notes
        -----
        To display the number of components rejected of an ICA raw pipe, use
        :meth:`~MneExperiment.show_raw_info`.
        """
        # TODO: include ICA raw preprocessing pipes
        if state:
            self.set(**state)
        raw_name = self.get('raw')
        epoch_name = self.get('epoch')
        rej_name = self.get('rej')
        rej = self._artifact_rejection[rej_name]
        has_epoch_rejection = rej['kind'] is not None
        has_interp = rej.get('interpolation')

        subjects = []
        n_events = []
        n_good = []
        bad_chs = []
        n_interp = []

        for subject in self:
            subjects.append(subject)
            bads_raw = self.load_bad_channels()
            try:
                ds = self.load_selected_events(reject='keep')
            except FileMissing:
                ds = self.load_selected_events(reject=False)
                bad_chs.append((bads_raw, ()))
                if has_epoch_rejection:
                    n_good.append(float('nan'))
                if has_interp:
                    n_interp.append(float('nan'))
            else:
                bads_rej = set(ds.info[BAD_CHANNELS]).difference(bads_raw)
                bad_chs.append((bads_raw, bads_rej))
                if has_epoch_rejection:
                    n_good.append(ds['accept'].sum())
                if has_interp:
                    n_interp.append(np.mean([len(chi) for chi in ds[INTERPOLATE_CHANNELS]]))
            n_events.append(ds.n_cases)
        has_interp = has_interp and any(n_interp)
        caption = f"Rejection info for raw={raw_name}, epoch={epoch_name}, rej={rej_name}. Percent is rounded to one decimal."

        # format bad channels
        if bads:
            func = ', '.join
        else:
            func = len
        bad_chs = [(func(bads_raw), func(bads_rej)) for bads_raw, bads_rej in bad_chs]

        if any(bads_rej for bads_raw, bads_rej in bad_chs):
            caption += " Bad channels: defined in bad_channels file and in rej-file."
            bad_chs = [f'{bads_raw} + {bads_rej}' for bads_raw, bads_rej in bad_chs]
        else:
            bad_chs = [f'{bads_raw}' for bads_raw, bads_rej in bad_chs]

        if bads:
            bad_chs = [s.replace('MEG ', '') for s in bad_chs]

        if has_interp:
            caption += " ch_interp: average number of channels interpolated per epoch, rounded to one decimal."
        out = Dataset(caption=caption)
        out['subject'] = Factor(subjects)
        out['n_events'] = Var(n_events)
        if has_epoch_rejection:
            out['n_good'] = Var(n_good)
            out['percent'] = Var(np.round(100 * out['n_good'] / out['n_events'], 1))
        if flagp:
            out['flag'] = Factor(out['percent'] < flagp, labels={False: '', True: '*'})
        out['bad_channels'] = Factor(bad_chs)
        if has_interp:
            out['ch_interp'] = Var(np.round(n_interp, 1))

        if asds:
            return out
        else:
            print(out)

    def show_subjects(self, mri=True, mrisubject=False, caption=True,
                      asds=False, **state):
        """Create a Dataset with subject information

        Parameters
        ----------
        mri : bool
            Add a column specifying whether the subject is using a scaled MRI
            or whether it has its own MRI.
        mrisubject : bool
            Add a column showing the MRI subject corresponding to each subject.
        caption : bool | str
            Caption for the table (For True, use the default "Subject in group
            {group}".
        asds : bool
            Return the table as Dataset instead of an FMTxt Table.
        ...
            State parameters.
        """
        if state:
            self.set(**state)

        # caption
        if caption is True:
            caption = self.format("Subjects in group {group}")

        subject_list = []
        mri_list = []
        mrisubject_list = []
        for subject in self.iter():
            subject_list.append(subject)
            mrisubject_ = self.get('mrisubject')
            mrisubject_list.append(mrisubject_)
            if mri:
                mri_dir = self.get('mri-dir')
                if not exists(mri_dir):
                    mri_list.append('*missing')
                elif is_fake_mri(mri_dir):
                    mri_sdir = self.get('mri-sdir')
                    info = mne.coreg.read_mri_cfg(mrisubject_, mri_sdir)
                    cell = "%s * %s" % (info['subject_from'],
                                        str(info['scale']))
                    mri_list.append(cell)
                else:
                    mri_list.append(mrisubject_)

        ds = Dataset(caption=caption)
        ds['subject'] = Factor(subject_list)
        if mri:
            ds['mri'] = Factor(mri_list)
        if mrisubject:
            ds['mrisubject'] = Factor(mrisubject_list)

        if asds:
            return ds
        else:
            return ds.as_table(midrule=True, count=True)

    def show_input_tree(self):
        """Print a tree of the files needed as input

        See Also
        --------
        show_tree: show complete tree (including secondary, optional and cache)
        """
        return self.show_tree(fields=['raw-file', 'trans-file', 'mri-dir'])

    def _surfer_plot_kwargs(self, surf=None, views=None, foreground=None,
                            background=None, smoothing_steps=None, hemi=None):
        out = self._brain_plot_defaults.copy()
        out.update(self.brain_plot_defaults)
        if views:
            out['views'] = views
        else:
            parc, p = self._get_parc()
            if p is not None and p.views:
                out['views'] = p.views

        if surf:
            out['surf'] = surf
        if foreground:
            out['foreground'] = foreground
        if background:
            out['background'] = background
        if smoothing_steps:
            out['smoothing_steps'] = smoothing_steps
        if hemi:
            out['hemi'] = hemi
        return out
