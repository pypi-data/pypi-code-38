# -*- coding: utf-8 -*-
"""Tools for importing data through mne.

.. autosummary::
   :toctree: generated

   events
   epochs
   mne_epochs
   add_epochs
   add_mne_epochs
   epochs_ndvar
   evoked_ndvar
   sensor_dim
   stc_ndvar
   forward_operator
   inverse_operator


.. currentmodule:: eelbrain

Managing events with a :class:`Dataset`
---------------------------------------

To load events as :class:`Dataset`::

    >>> ds = load.fiff.events(raw_file_path)

By default, the :class:`Dataset` contains a variable called ``"trigger"``
with trigger values, and a variable called ``"i_start"`` with the indices of
the events::

    >>> print(ds[:10])
    trigger   i_start
    -----------------
    2         27977
    3         28345
    1         28771
    4         29219
    2         29652
    3         30025
    1         30450
    4         30839
    2         31240
    3         31665

These events can be modified in ``ds`` (adding event labels as :class:`Factor`,
discarding events, modifying ``i_start``, , ...) before being used to load data
epochs.

Epochs can be loaded as :class:`NDVar` with :func:`load.fiff.epochs`. Epochs
will be loaded based only on the ``"i_start"`` variable, so any modification
to this variable will affect the epochs that are loaded.::

    >>> ds['epochs'] = load.fiff.epochs(ds)

Epochs can also be loaded as mne-python :class:`mne.Epochs` object::

    >>> mne_epochs = load.fiff.mne_epochs(ds)


Using Threshold Rejection
-------------------------

In case threshold rejection is used, the number of the epochs returned by
``load.fiff.epochs(ds, reject=reject_options)`` might not be the same as the
number of events in ``ds`` (whenever epochs are rejected). For those cases,
:func:`load.fiff.add_epochs`` will automatically resize the :class:`Dataset`::

    >>> epoch_ds = load.fiff.add_epochs(ds, -0.1, 0.6, reject=reject_options)

The returned ``epoch_ds`` will contain the epochs as NDVar as ``ds['meg']``.
If no epochs got rejected during loading, the length of ``epoch_ds`` is
identical with the input ``ds``. If epochs were rejected, ``epoch_ds`` is a
shorter copy of the original ``ds``.

:class:`mne.Epochs` can be added to ``ds`` in the same fashion with::

    >>> ds = load.fiff.add_mne_epochs(ds, -0.1, 0.6, reject=reject_options)


Separate events files
---------------------

If events are stored separately form the raw files, they can be loaded in
:func:`load.fiff.events` by supplying the path to the events file as
``events`` parameter::

    >>> ds = load.fiff.events(raw_file_path, events=events_file_path)

"""
from .._io.fiff import (
    add_epochs, add_mne_epochs, epochs, epochs_ndvar, events, evoked_ndvar,
    forward_operator, inverse_operator, mne_epochs, mne_raw, raw_ndvar,
    sensor_dim, stc_ndvar
)
