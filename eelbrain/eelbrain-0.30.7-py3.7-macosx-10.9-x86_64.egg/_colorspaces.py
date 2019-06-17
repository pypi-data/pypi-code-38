"""Data-specific colormaps"""
from itertools import cycle
import logging
from math import ceil
from numbers import Real

# colormath starts out at 0; needs to be set before init
logger = logging.getLogger('colormath.color_conversions')
if logger.level == 0:  # otherwise it was probably set by user (DEBUG=10)
    logger.setLevel(logging.WARNING)

from colormath.color_objects import LCHabColor, sRGBColor
from colormath.color_conversions import convert_color
from matplotlib.cm import register_cmap
from matplotlib.colors import LinearSegmentedColormap, Normalize
import numpy as np

try:
    from matplotlib.colors import to_rgb, to_rgba
except ImportError:  # matplotlib < 2
    from matplotlib.colors import colorConverter
    to_rgb = colorConverter.to_rgb
    to_rgba = colorConverter.to_rgba


def lch_to_rgb(lightness, chroma, hue):
    "Convert Lightness/Chroma/Hue color representation to RGB"
    psych = LCHabColor(lightness, chroma, hue * 360)
    rgb = convert_color(psych, sRGBColor)
    return rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b


def make_seq_cmap(seq, val, name):
    """Colormap from sequence of RGB values

    Parameters
    ----------
    seq : iterator
        Each entry is either an RGB tuple (if pre- and post color are
        identical) or a tuple with two RGB tuples (separate pre- and post-
        colors).
    val : iterator
        For each entry in ``seq``, the coordinate on the colormap.
    name : str
        Colormap name.
    """
    red = []
    green = []
    blue = []
    for v, col in zip(val, seq):
        if len(col) == 3:
            r0, g0, b0 = col
            r1, g1, b1 = col
        elif len(col) == 2:
            (r0, g0, b0), (r1, g1, b1) = col
        else:
            raise ValueError('col in seq: %s' % str(col))
        red.append((v, r0, r1))
        green.append((v, g0, g1))
        blue.append((v, b0, b1))
    cdict = {'red': red, 'green': green, 'blue': blue}
    return LinearSegmentedColormap(name, cdict)


def twoway_cmap(n1, hue_start=0.1, hue_shift=0.5, name=None, hues=None):
    """Create colormap for two-way interaction

    Parameters
    ----------
    n1 : int
        Number of levels on the first factor.
    hue_start : 0 <= scalar < 1
        First hue value.
    hue_shift : 0 <= scalar < 1
        Use that part of the hue continuum between categories to shift hue
        within categories.
    name : str
        Name of the colormap.
    hues : list of scalar
        List of hue values corresponding to the levels of the first factor
        (overrides regular hue distribution).
    """
    # within each hue, create values for [-1, -0.5, 0.5, 1]
    # return list of [i, (r, g, b), (r, g, b)]
    if hues is None:
        hues = np.linspace(hue_start, hue_start + 1, n1, False) % 1.
    hue_shift *= (0.5 / n1)

    seqs = []
    for h in hues:
        h_pre = (h - hue_shift) % 1
        h_post = (h + hue_shift) % 1
        seqs.append((lch_to_rgb(0, 100, h_pre),
                     lch_to_rgb(50, 100, h),
                     lch_to_rgb(100, 100, h_post)))

    seq = []
    for i in range(n1):
        seq.append((seqs[i - 1][-1], seqs[i][0]))
        seq.append(seqs[i][1])
        if i == n1 - 1:
            seq.append((seqs[i][2], seqs[0][0]))

    loc = np.linspace(0, 1, n1 * 2 + 1)

    if name is None:
        name = "%i_by_n" % n1

    return make_seq_cmap(seq, loc, name)


def oneway_colors(n, hue_start=0.2, light_range=0.5, light_cycle=None,
                  always_cycle_hue=False, locations=None):
    """Create colors for categories

    Parameters
    ----------
    n : int
        Number of levels.
    hue_start : 0 <= scalar < 1 | sequence of scalar
        First hue value (default 0.2) or list of hue values.
    light_range : scalar | tuple
        Amount of lightness variation. If a positive scalar, the first color is
        lightest; if a negative scalar, the first color is darkest. Tuple with
        two scalar to define a specific range.
    light_cycle : int
        Cycle from light to dark in ``light_cycle`` cells to make nearby colors 
        more distinct (default cycles once).
    always_cycle_hue : bool
        Cycle hue even when cycling lightness. With ``False`` (default), hue
        is constant within a lightness cycle.
    locations : sequence of float
        Locations of the cells on the color-map (all in range [0, 1]; default is
        evenly spaced; example: ``numpy.linspace(0, 1, n) ** 0.5``).
    """
    if locations is not None:
        raise NotImplementedError('locations for non-cmap based colors')

    if light_cycle is None or always_cycle_hue:
        n_hues = n
    else:
        n_hues = int(ceil(n / light_cycle))

    if isinstance(hue_start, Real):
        hue = np.linspace(hue_start, hue_start + 1, n_hues, False) % 1.
        if light_cycle and not always_cycle_hue:
            hue = np.repeat(hue, light_cycle)
    elif len(hue_start) >= n_hues:
        hue = hue_start
    else:
        raise ValueError("If list of hues is provided it needs ot contain at "
                         "least as many hues as there are cells")

    if isinstance(light_range, (list, tuple)):
        start, stop = light_range
    else:
        start = 0.5 + 0.5 * light_range
        stop = 0.5 - 0.5 * light_range

    if light_cycle is None:
        lightness = np.linspace(100 * start, 100 * stop, n)
    else:
        tile = np.linspace(100 * start, 100 * stop, light_cycle)
        lightness = cycle(tile)
        if n % light_cycle:
            hue = hue[:n]

    return [lch_to_rgb(l, 100, h) for l, h in zip(lightness, hue)]


def twoway_colors(n1, n2, hue_start=0.2, hue_shift=0., hues=None):
    """Create colors for two-way interaction

    Parameters
    ----------
    n1, n2 : int
        Number of levels on the first and second factors.
    hue_start : 0 <= scalar < 1
        First hue value.
    hue_shift : 0 <= scalar < 1
        Use that part of the hue continuum between categories to shift hue
        within categories.
    hues : list of scalar
        List of hue values corresponding to the levels of the first factor
        (overrides regular hue distribution).
    """
    if hues is None:
        hues = np.linspace(hue_start, hue_start + 1, n1, False) % 1.
    else:
        hues = np.asarray(hues)
        if np.any(hues > 1) or np.any(hues < 0):
            raise ValueError("hue values out of range; need to be in [0, 1]")
        elif len(hues) < n1:
            raise ValueError("Need at least as many hues as levels in the "
                             "first factor (got %i, need %i)" % (len(hues), n1))
    hue_shift *= (1. / 3. / n1)
    lstart = 60. / n2
    ls = np.linspace(lstart, 100 - lstart, n2)

    colors = []
    for hue in hues:
        hs = np.linspace(hue - hue_shift, hue + hue_shift, n2) % 1
        colors.extend(lch_to_rgb(l, 100, h) for l, h in zip(ls, hs))

    return colors


def make_cmaps():
    """Create some custom colormaps and register them with matplotlib"""
    # polar:  blue-white-red
    cmap = LinearSegmentedColormap.from_list(
        "polar", (
            (0.0, (0.0, 0.0, 1.0)),
            (0.5, (1.0, 1.0, 1.0)),
            (1.0, (1.0, 0.0, 0.0)),
        ))
    cmap.set_bad('w', alpha=0.)
    register_cmap(cmap=cmap)

    # polar-alpha: middle is transparent instead of white
    cmap = LinearSegmentedColormap.from_list(
        "polar-a", (
            (0.0, (0.0, 0.0, 1.0, 1.0)),
            (0.5, (0.0, 0.0, 1.0, 0.0)),
            (0.5, (1.0, 0.0, 0.0, 0.0)),
            (1.0, (1.0, 0.0, 0.0, 1.0)),
        ))
    cmap.set_bad('w', alpha=0.)
    register_cmap(cmap=cmap)

    # xpolar ("extra-polar"): fade ends into black
    cmap = LinearSegmentedColormap.from_list(
        "xpolar", (
            (0.0, (0.0, 0.0, 0.0)),
            (0.3, (0.0, 0.0, 1.0)),
            (0.5, (1.0, 1.0, 1.0)),
            (0.7, (1.0, 0.0, 0.0)),
            (1.0, (0.0, 0.0, 0.0)),
        ))
    cmap.set_bad('w', alpha=0.)
    register_cmap(cmap=cmap)

    # extra-polar alpha: middle is transparent instead of white
    cmap = LinearSegmentedColormap.from_list(
        "xpolar-a", (
            (0.0, (0.0, 0.0, 0.0, 1.0)),
            (0.3, (0.0, 0.0, 1.0, 1.0)),
            (0.5, (0.0, 0.0, 1.0, 0.0)),
            (0.5, (1.0, 0.0, 0.0, 0.0)),
            (0.7, (1.0, 0.0, 0.0, 1.0)),
            (1.0, (0.0, 0.0, 0.0, 1.0)),
        ))
    cmap.set_bad('w', alpha=0.)
    register_cmap(cmap=cmap)

    # phase
    cmap = LinearSegmentedColormap.from_list(
        "phase", (
            (0.0, (0.0, 0.0, 1.0)),
            (0.5, (1.0, 0.0, 0.0)),
            (1.0, (0.0, 0.0, 1.0)),
        ))
    cmap.set_bad('w', alpha=0.)
    register_cmap(cmap=cmap)

    # sig:  significance map for specific vmax=0.05
    cmap = LinearSegmentedColormap.from_list(
        "sig", (
            (0.0,  (1.0, 1.0, 1.0)),
            (0.02, (1.0, 1.0, 0.0)),
            (0.2,  (1.0, 0.5, 0.0)),
            (1.0,  (1.0, 0.0, 0.0)),
        ))
    cmap.set_over('k', alpha=0.)
    cmap.set_bad('b', alpha=0.)
    register_cmap(cmap=cmap)


make_cmaps()

# https://matplotlib.org/tutorials/colors/colormaps.html
mpl_diverging = ('PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic')
symmetric_cmaps = ['polar', 'polar-a', 'xpolar', 'xpolar-a']
symmetric_cmaps.extend(mpl_diverging)
symmetric_cmaps.extend(f'{name}_r' for name in mpl_diverging)
zerobased_cmaps = ('sig',)
# corresponding cmaps with transparency (alpha channel)
ALPHA_CMAPS = {'xpolar': 'xpolar-a',
               'RdBu_r': 'xpolar-a'}


class SymmetricNormalize(Normalize):
    """Matplotlib Normalize subclass to add threshold"""

    def __init__(self, threshold, vmax, clip=False):
        assert threshold >= 0
        if vmax is None:
            vmin = None
        else:
            assert vmax > threshold
            vmin = -vmax
        self.threshold = threshold
        Normalize.__init__(self, vmin, vmax, clip)

    def __repr__(self):
        args = list(map(repr, (self.threshold, self.vmax)))
        if self.clip:
            args.append("clip=%r" % (self.clip,))
        return "SymmetricNormalize(%s)" % ', '.join(args)

    def __call__(self, value, clip=None):
        # cf. Normalize.__call__
        if clip is None:
            clip = self.clip

        result, is_scalar = self.process_value(value)
        vmax = self.vmax
        vmin = self.vmin

        self.autoscale_None(result)
        # Convert at least to float, without losing precision.
        if clip:
            mask = np.ma.getmask(result)
            result = np.ma.array(np.clip(result.filled(vmax), vmin, vmax),
                                 mask=mask)
        # ma division is very slow; we can take a shortcut
        resdat = result.data

        # subclass #
        ############
        # threshold
        if self.threshold:
            mask_lower = resdat <= -self.threshold
            mask_upper = resdat >= self.threshold
            mask_visible = mask_upper | mask_lower
            mask_invisible = np.invert(mask_visible)
            resdat[mask_lower] -= vmin
            resdat[mask_upper] -= vmin + 2 * self.threshold
            resdat[mask_visible] /= vmax - vmin - 2 * self.threshold
            resdat[mask_invisible] = 0.5
        else:
            resdat -= vmin
            resdat /= (vmax - vmin)
        #############

        result = np.ma.array(resdat, mask=result.mask, copy=False)
        # Agg cannot handle float128.  We actually only need 32-bit of
        # precision, but on Windows, `np.dtype(np.longdouble) == np.float64`,
        # so casting to float32 would lose precision on float64s as well.
        if result.dtype == np.longdouble:
            result = result.astype(np.float64)
        if is_scalar:
            result = result[0]
        return result

    def autoscale(self, A):
        a = np.asanyarray(A)
        self.vmax = max(a.max(), -a.min())
        self.vmin = -self.vmax

    def autoscale_None(self, A):
        pass

    def scaled(self):
        return self.vmax is not None
