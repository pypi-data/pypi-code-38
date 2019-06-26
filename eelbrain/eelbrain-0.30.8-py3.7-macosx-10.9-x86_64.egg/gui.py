"""Eelbrain GUIs"""


def run(block=False):
    """Hand over command to the GUI (quit the GUI to return to the terminal)

    Parameters
    ----------
    block : bool
        Block the Terminal even if the GUI is capable of being run in parallel.
        Control returns to the Terminal when the user quits the GUI application.
        This is also useful to prevent plots from closing at the end of a
        script.
    """
    from ._wxgui import run

    run(block)


def select_components(path, ds, sysname=None, connectivity=None):
    """GUI for selecting ICA-components

    Parameters
    ----------
    path : str
        Path to the ICA file.
    ds : Dataset
        Dataset with epochs to use for source selection in ``ds['epochs']``
        (as mne-python ``Epochs`` object). Optionally, ``ds['index']`` can be
        the indexes to display for epochs (the default is ``range(n_epochs)``.
        Further :class:`Factor` can be used to plot condition averages.
    sysname : str
        Optional, to define sensor connectivity.
    connectivity :
        Optional, to define sensor connectivity (see
        :func:`eelbrain.load.fiff.sensor_dim`).

    Notes
    -----
    The ICA object does not need to be computed on the same data that is in
    ``ds``. For example, the ICA can be computed on a raw file but component
    selection done using the epochs that will be analyzed.
    """
    from ._wxgui.app import get_app
    from ._wxgui.select_components import TEST_MODE, Document, Frame, Model

    get_app()  # make sure app is created
    doc = Document(path, ds, sysname, connectivity)
    model = Model(doc)
    frame = Frame(None, None, None, model)
    frame.Show()
    frame.Raise()
    if TEST_MODE:
        return frame
    else:
        run()


def select_epochs(
        ds, data='meg', accept='accept', blink='blink', tag='rej_tag',
        trigger='trigger', path=None, nplots=None, topo=None, mean=None,
        vlim=None, color='k', lw=0.5, mark=[], mcolor='r', mlw=0.8,
        antialiased=True, pos=None, size=None, allow_interpolation=True):
    """GUI for rejecting trials of MEG/EEG data

    Parameters
    ----------
    ds : Dataset | mne.Epochs
        The data for which to select trials. If ``ds`` is a :class:`Dataset`,
        the subsequent parameters up to 'trigger' specify names of variables in
        ``ds``; if ``ds`` is an :class:`mne.Epochs` object, these parameters are
        ignored.
    data : str
        Name of the epochs data in ``ds`` (default ``'meg'``).
    accept : str
        Name of the boolean :class:`Var` in ``ds`` to accept or reject epochs
        (default ``'accept'``).
    blink : str
        Name of the eye tracker data in ``ds`` if present (default ``'blink'``).
    tag : str
        Name of the rejection tag (storing the reason for rejecting a
        specific epoch; default ``'rej_tag'``).
    trigger : str
        Name of the ``int`` :class:`Var` containing the event trigger for each
        epoch (used when loading a rejection file to assert that it comes from
        the same data; default ``'trigger'``).
    path : None | str
        Path to the desired rejection file. If the file already exists it
        is loaded as starting values. The extension determines the format
        (``*.pickled`` or ``*.txt``).
    nplots : None | int | tuple of 2 int
        Number of epoch plots per page. Can be an ``int`` to produce a
        square layout with that many epochs, or an ``(n_rows, n_columns)``
        tuple. The default is to use the settings from the last session.
    topo : None | bool
        Show a topomap plot of the time point under the mouse cursor.
        Default (None): use settings form last session.
    mean : None | bool
        Show a plot of the page mean at the bottom right of the page.
        Default (None): use settings form last session.
    vlim : None | scalar
        Limit of the epoch plots on the y-axis. If None, a value is
        determined automatically to show all data.
    color : None | matplotlib color
        Color for primary data (default is black).
    lw : scalar
        Linewidth for normal sensor plots.
    mark : None | index for sensor dim
        Sensors to plot as individual traces with a separate color.
    mcolor : matplotlib color
        Color for marked traces.
    mlw : scalar
        Line width for marked sensor plots.
    antialiased : bool
        Perform Antialiasing on epoch plots (associated with a minor speed
        cost).
    pos : None | tuple of 2 int
        Window position on screen. Default (None): use settings form last
        session.
    size : None | tuple of 2 int
        Window size on screen. Default (None): use settings form last
        session.
    allow_interpolation : bool
        Whether to allow interpolating individual channels by epoch (default
        True).

    Notes
    -----
    Exclude bad epochs and interpolate or remove bad channels.

    * Use the `Bad Channels` button in the toolbar to exclude channels from
      analysis (use the `GA` button to plot the grand average and look for
      channels that are consistently bad).
    * Click the `Threshold` button to automatically reject epochs in which the
      signal exceeds a certain threshold.
    * Click on an epoch plot to toggle rejection of that epoch.
    * Press ``i`` on the keyboard to toggle channel interpolation for the
      channel that is closest to the cursor along the y-axis.
    * Press ``shift-i`` on the keyboard to edit a list of interpolated channels
      for the epoch under the cursor.


    *Keyboard shortcuts* in addition to the ones in the menu:

    =========== ============================================================
    Key         Effect
    =========== ============================================================
    right-arrow go to the next page
    left-arrow  go to the previous page
    b           butterfly plot of the epoch under the pointer
    c           pairwise sensor correlation plot or the current epoch
    t           topomap plot of the epoch/time point under the pointer
    i           interpolate the channel nearest to the pointer on the y-axis
    shift-i     open dialog to enter channels for interpolation
    =========== ============================================================
    """
    from ._wxgui.app import get_app
    from ._wxgui.select_epochs import TEST_MODE, Document, Frame, Model

    get_app()  # make sure app is created
    bad_chs = None
    doc = Document(ds, data, accept, blink, tag, trigger, path, bad_chs, allow_interpolation)
    model = Model(doc)
    frame = Frame(None, model, nplots, topo, mean, vlim, color, lw, mark, mcolor, mlw, antialiased, pos, size, allow_interpolation)
    frame.Show()
    frame.Raise()
    if TEST_MODE:
        return frame
    else:
        run()
