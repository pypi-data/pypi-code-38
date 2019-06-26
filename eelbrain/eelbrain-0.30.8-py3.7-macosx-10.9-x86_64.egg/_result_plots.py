# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from math import floor, log10
from os import makedirs
from os.path import basename, dirname, exists, expanduser, isdir, join

import matplotlib as mpl
import numpy as np

from . import fmtxt, plot, testnd
from .plot._base import POINT
from ._data_obj import combine


# usage:  with mpl.rc_context(RC):
FONT = 'Helvetica'
RC = {
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.transparent': True,
    # Font
    'font.family': 'sans-serif',
    'font.sans-serif': FONT,
    'font.size': 9,
    # make sure equations use same font
    'mathtext.fontset': 'custom',
    'font.cursive': FONT,
    'font.serif': FONT,
    # subplot
    'figure.subplot.top': 0.95,
    # legend
    'legend.fontsize': 6,
    'legend.frameon': False,
}
for key in mpl.rcParams:
    if 'width' in key:
        RC[key] = mpl.rcParams[key] * 0.5


class PlotDestDir:
    """Generate paths for saving plots in figure-specific subdirectories

    Parameters
    ----------
    root : str
        Directory in which to save files.
    pix_fmt : str
        Pixel graphics format (default ``png``).
    vec_fmt : str
        Vector graphics format (default ``pdf``).
    name : str
        Name for the info report (default is ``basename(root)``).
    """
    def __init__(self, root, pix_fmt='png', vec_fmt='pdf', name=None):
        root = expanduser(root)
        if not exists(root):
            makedirs(root)
        else:
            assert isdir(root)
        assert pix_fmt.isalnum()
        assert vec_fmt.isalnum()
        if name is None:
            name = basename(root)
            if not name:
                name = basename(dirname(root))
        self.root = root
        self._pix_fmt = pix_fmt
        self._vec_fmt = vec_fmt
        self.pix = join(root, '%s.' + pix_fmt)
        self.vec = join(root, '%s.' + vec_fmt)
        self.mov = join(root, '%s.mov')
        self.txt = join(root, '%s.txt')
        self.name = name
        self.report = fmtxt.Report(name)
        self._active_section = [self.report]

    def with_ext(self, ext):
        """Generate path template ``%s.{ext}``"""
        assert ext.isalnum()
        return join(self.root, '%s.' + ext)

    def subdir(self, dirname, name=None):
        """PlotDestDir object for a sub-directory"""
        return PlotDestDir(join(self.root, dirname), self._pix_fmt, self._vec_fmt, name)

    # MARK:  report

    def section(self, heading, level=1):
        if level <= 0:
            raise ValueError("level=%r; must be >= 1, section 0 is the document")
        elif level > len(self._active_section):
            raise RuntimeError("Can't add section with level %i before adding "
                               "section with level %i" % (level, level - 1))
        while len(self._active_section) > level:
            self._active_section.pop(-1)
        section = self._active_section[-1].add_section(heading)
        self._active_section.append(section)

    def info(self, content):
        """Add ``info_string`` to the info list"""
        section = self._active_section[-1]
        section.append(content)

    def save_info(self, format='html'):
        """Save info to ``info.txt``"""
        dst = join(self.root, self.name)
        try:
            getattr(self.report, 'save_' + format)(dst)
        except AttributeError:
            raise ValueError("format=%r; Invalid format" % (format,))


def cname(cid):
    if isinstance(cid, tuple):
        return '-'.join(map(str, cid))
    else:
        return str(cid)


class ClusterPlotter:
    """Make plots for spatio-temporal clusters

    returned by :meth:`MneExperiment.load_result_plotter`

    Parameters
    ----------
    ds : Dataset
        Dataset with the data on which the test is based.
    res : NDTest
        Test result object with spatio-temporal cluster test result.
    colors : dict
        Colors for plotting data in a ``{cell: color}`` dictionary.
    dst : str
        Directory in which to place results.
    vec_fmt : str
        Format for vector graphics (default 'pdf').
    pix_fmt : str
        Format for pixel graphics (default 'png').
    labels : dict
        Labels for data in a ``{cell: label}`` dictionary (the default is to
        use cell names).
    h : scalar
        Plot height in inches (default 1.2).
    rc : dict
        Matplotlib rc-parameters dictionary (the default is optimized for the
        default plot size ``h=1.2``).

    Notes
    -----
    After loading a :class:`ClusterPlotter`, its ``rc``, ``colors``, ``labels``
    and ``h`` attributes can be updated to create different plot layouts without
    reloading the data.
    """
    def __init__(self, ds, res, colors, dst, vec_fmt='pdf', pix_fmt='png',
                 labels=None, h=1.2, rc=None):
        self.rc = RC.copy()
        if rc is not None:
            self.rc.update(rc)
        self.ds = ds
        self.res = res
        self.colors = colors
        self.labels = labels
        self.h = h
        self._dst = PlotDestDir(dst, pix_fmt, vec_fmt)
        self._is_anova = isinstance(self.res, testnd.anova)

    def _ids(self, ids):
        if isinstance(ids, (float, int)):
            return self._ids_for_p(ids)
        elif isinstance(ids, dict):
            if not self._is_anova:
                raise TypeError("ids can not be dict for results other than ANOVA")
            out = []
            for effect, cids in ids.items():
                if isinstance(cids, float):
                    out.extend(self._ids_for_p(cids, effect))
                else:
                    out.extend((effect, cid) for cid in cids)
            return out
        else:
            return ids

    def _ids_for_p(self, p, effect=None):
        "Find cluster IDs for clusters with p-value <= p"
        if effect is None:
            clusters = self.res.find_clusters(p)
        else:
            clusters = self.res.find_clusters(p, effect=effect)
            clusters[:, 'effect'] = effect

        if self._is_anova:
            return list(zip(clusters['effect'], clusters['id']))
        else:
            return clusters['id']

    def _get_clusters(self, ids):
        return [self._get_cluster(cid) for cid in ids]

    def _get_cluster(self, cid):
        if self._is_anova:
            effect, cid = cid
            return self.res.cluster(cid, effect)
        else:
            return self.res.cluster(cid)

    def plot_color_list(self, name, cells, w=None, colors=None):
        if colors is None:
            colors = self.colors

        with mpl.rc_context(self.rc):
            p = plot.ColorList(colors, cells, self.labels, w=w, show=False)
            p.save(self._dst.vec % "colorlist %s" % name, transparent=True)
            p.close()

    def plot_color_grid(self, name, row_cells, column_cells):
        with mpl.rc_context(self.rc):
            p = plot.ColorGrid(row_cells, column_cells, self.colors, labels=self.labels)
            p.save(self._dst.vec % "colorgrid %s" % name, transparent=True)
            p.close()

    def plot_clusters_spatial(self, ids, views, w=600, h=480, prefix=''):
        """Plot spatial extent of the clusters

        Parameters
        ----------
        ids : sequence | dict | scalar <= 1
            IDs of the clusters that should be plotted. For ANOVA results, this
            should be an ``{effect_name: id_list}`` dict. Instead of a list of
            IDs a scalar can be provided to plot all clusters with p-values
            smaller than this.
        views : str | list of str | dict
            Can a str or list of str to use the same views for all clusters. A dict
            can have as keys labels or cluster IDs.
        w, h : int
            Size in pixels. The default (600 x 480) corresponds to 2 x 1.6 in
            at 300 dpi.
        prefix : str
            Prefix to use for the image files (optional, can be used to
            distinguish different groups of images sharing the same color-bars).

        Notes
        -----
        The horizontal colorbar is 1.5 in wide, the vertical colorbar is 1.6 in
        high.
        """
        ids = self._ids(ids)
        clusters = self._get_clusters(ids)
        clusters_spatial = [c.sum('time') for c in clusters]
        if isinstance(views, str):
            views = (views,)

        # vmax
        vmin = min(c.min() for c in clusters_spatial)
        vmax = max(c.max() for c in clusters_spatial)
        abs_vmax = max(vmax, abs(vmin))

        # anatomical extent
        brain_colorbar_done = False
        for cid, cluster in zip(ids, clusters_spatial):
            name = cname(cid)
            if prefix:
                name = prefix + ' ' + name

            for hemi in ('lh', 'rh'):
                if not cluster.sub(source=hemi).any():
                    continue
                brain = plot.brain.cluster(cluster, abs_vmax, views='lat',
                                           background=(1, 1, 1), colorbar=False,
                                           parallel=True, hemi=hemi, w=w, h=h)
                for view in views:
                    brain.show_view(view)
                    brain.save_image(self._dst_pix % ' '.join((name, hemi, view)),
                                     'rgba', True)

                if not brain_colorbar_done:
                    with mpl.rc_context(self.rc):
                        label = "Sum of %s-values" % cluster.info['meas']
                        clipmin = 0 if vmin == 0 else None
                        clipmax = 0 if vmax == 0 else None
                        if prefix:
                            cbar_name = '%s cbar %%s' % prefix
                        else:
                            cbar_name = 'cbar %s'

                        h_cmap = 0.7 + POINT * mpl.rcParams['font.size']
                        p = brain.plot_colorbar(label, clipmin=clipmin, clipmax=clipmax,
                                                width=0.1, h=h_cmap, w=1.5, show=False)
                        p.save(self._dst.vec % cbar_name % 'h', transparent=True)
                        p.close()

                        w_cmap = 0.8 + 0.1 * abs(floor(log10(vmax)))
                        p = brain.plot_colorbar(label, clipmin=clipmin, clipmax=clipmax,
                                                width=0.1, h=1.6, w=w_cmap,
                                                orientation='vertical', show=False)
                        p.save(self._dst.vec % cbar_name % 'v', transparent=True)
                        p.close()

                        brain_colorbar_done = True

                brain.close()

    def _get_data(self, model, sub, subagg):
        """Plot values in cluster

        Parameters
        ----------
        subagg : str
           Index in ds: within index, collapse across other predictors.
        """
        ds = self.ds
        modelname = model

        if sub:
            ds = ds.sub(sub)
            modelname += '[%s]' % sub

        if subagg:
            idx_subagg = ds.eval(subagg)
            ds_full = ds.sub(np.invert(idx_subagg))
            ds_agg = ds.sub(idx_subagg).aggregate("subject", drop_bad=True)
            ds = combine((ds_full, ds_agg), incomplete='fill in')
            ds['condition'] = ds.eval(model).as_factor()
            model = 'condition'
            modelname += '(agg %s)' % subagg

        return ds, model, modelname

    def plot_values(self, ids, model, ymax, ymin, dpi=300, sub=None,
                    subagg=None, cells=None, pairwise=False, colors=None,
                    prefix=None, w=None, filter=None, legend=False):
        """Plot values in cluster

        Parameters
        ----------
        ids : sequence | dict | scalar <= 1
            IDs of the clusters that should be plotted. For ANOVA results, this
            should be an ``{effect_name: id_list}`` dict. Instead of a list of
            IDs a scalar can be provided to plot all clusters with p-values
            smaller than this.
        model : str
            Model defining cells which to plot separately.
        ymax : scalar
            Top of the y-axis.
        ymin : scalar
            Bottom of the y axis.
        dpi : int
            Figure DPI.
        sub : str
            Only use a subset of the data.
        subagg : str
           Index in ds: within index, collapse across other predictors.
        cells : sequence of cells in model
            Modify visible cells and their order. Only applies to the barplot.
            Does not affect filename.
        pairwise : bool
            Add pairwise tests to barplots.
        colors : dict
            Substitute colors (default are the colors provided at
            initialization).
        prefix : str
            Prefix to use for the image files (optional, can be used to
            distinguish different groups of images sharing the same color-bars).
        w : scalar
            UTS-stat plot width (default is ``2 * h``).
        filter : Filter
            Filter signal for display purposes (optional).
        legend : bool
            Plot a color legend.
        """
        if w is None:
            w = self.h * 2
        ds, model, modelname = self._get_data(model, sub, subagg)
        ids = self._ids(ids)
        if colors is None:
            colors = self.colors

        src = ds['srcm']
        n_cells = len(ds.eval(model).cells)
        w_bar = (n_cells * 2 + 4) * (self.h / 12)
        with mpl.rc_context(self.rc):
            for cid in ids:
                name = cname(cid)
                if prefix:
                    name = prefix + ' ' + name
                cluster = self._get_cluster(cid)
                y_mean = src.mean(cluster != 0)
                y_tc = src.mean(cluster.any('time'))

                # barplot
                p = plot.Barplot(
                    y_mean, model, 'subject', None, cells, pairwise, ds=ds,
                    trend=False, corr=None, title=None, frame=False,
                    yaxis=False, ylabel=False, colors=colors, bottom=ymin,
                    top=ymax, w=w_bar, h=self.h, xlabel=None, xticks=None,
                    tight=False, test_markers=False, show=False)
                p.save(self._dst.vec % ' '.join((name, modelname, 'barplot')),
                       dpi=dpi, transparent=True)
                p.close()

                # time-course
                if filter is not None:
                    y_tc = filter.filtfilt(y_tc)
                p = plot.UTSStat(
                    y_tc, model, match='subject', ds=ds, error='sem',
                    colors=colors, title=None, axtitle=None, frame=False,
                    bottom=ymin, top=ymax, legend=None, ylabel=None,
                    xlabel=None, w=w, h=self.h, tight=False, show=False)
                dt = y_tc.time.tstep / 2.
                mark_start = cluster.info['tstart'] - dt
                mark_stop = cluster.info['tstop'] - dt
                p.add_vspan(mark_start, mark_stop, color='k', alpha=0.1, zorder=-2)
                p.save(self._dst.vec % ' '.join((name, modelname, 'timecourse')),
                       dpi=dpi, transparent=True)
                p.close()

                # legend (only once)
                if legend:
                    p.save_legend(self._dst.vec % (modelname + ' legend'),
                                  transparent=True)
                    legend = False
