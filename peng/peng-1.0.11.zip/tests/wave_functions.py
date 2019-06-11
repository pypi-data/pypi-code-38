# wave_functions.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import copy
import math
import warnings

# PyPI imports
import numpy as np

with warnings.catch_warnings():
    from _pytest.warning_types import PytestWarning

    warnings.filterwarnings("ignore", category=PytestWarning)
    import pytest
from pmisc import AE, AI, RE

# Intra-package imports
import peng
from peng.constants import FP_ATOL, FP_RTOL
from .support import cmp_vectors, std_wobj


###
# Helper functions
###
def barange(bmin, bmax, inc):
    vector = np.arange(bmin, bmax + inc, inc)
    vector = vector if np.isclose(bmax, vector[-1], FP_RTOL, FP_ATOL) else vector[:-1]
    return vector


def fft(dep_vector, npoints):
    npoints = int(npoints)
    if npoints < dep_vector.size:
        vector = copy.copy(dep_vector[:npoints])
    elif npoints > dep_vector.size:
        vector = copy.copy(np.append(dep_vector, np.zeros(npoints - dep_vector.size)))
    else:
        vector = copy.copy(dep_vector)
    ret_dep_vector = 0j + np.zeros(npoints)
    nvector = np.arange(0, npoints)
    for k in range(0, npoints):
        ret_dep_vector[k] += np.sum(
            np.multiply(vector, np.exp(-1j * 2 * math.pi * k * nvector / npoints))
        )
    return ret_dep_vector


def full_fft():
    """FFT of waveform where independent axis is evenly spaced and a power of 2."""
    wobj, fsample, finc = fft_wave()
    # Compute reference solution
    npoints = len(wobj.indep_vector)
    ret_indep_vector = barange(-fsample / 2.0, +fsample / 2.0, finc)
    ret_dep_vector = fft(wobj.dep_vector, npoints)
    return npoints, wobj, ret_indep_vector, ret_dep_vector


def fft_wave():
    """Create waveform for FFT analysis."""
    # Evenly spaced data
    freqs = [1e3, 2.5e3]
    # Capture 4 cycles of slowest sinusoid
    tend = 4 / float(min(freqs))
    # Get power of 2 number of points
    tsample = 1 / (4.0 * max(freqs))
    npoints = 2 ** (math.ceil(math.log(tend / tsample, 2)))
    fsample = 1 / (tend / (npoints - 1))
    tinc = 1 / float(fsample)
    indep_vector = barange(0, tend, tinc)
    finc = fsample / (npoints - 1)
    dep_vector = np.zeros(indep_vector.size)
    for freq in freqs:
        dep_vector += np.cos(2 * math.pi * freq * indep_vector)
    wobj = peng.Waveform(indep_vector, dep_vector, "wobj", "LINEAR", "LINEAR", "sec")
    return wobj, fsample, finc


def padded_fft():
    """FFT of padded waveform."""
    wobj, _, _ = fft_wave()
    npoints = 3 * len(wobj.indep_vector)
    tend = wobj.indep_vector[-1]
    fsample = 1 / (tend / (npoints - 1))
    finc = fsample / (npoints - 1)
    ret_indep_vector = barange(-fsample / 2.0, +fsample / 2.0, finc)
    ret_dep_vector = fft(wobj.dep_vector, int(npoints))
    return npoints, wobj, ret_indep_vector, ret_dep_vector


def padded_ifft():
    """Inverse FFT of padded waveform."""
    return np.array(
        [
            +0.666666666666667 + 0.000000000000000j,
            +0.285737489530649 + 0.476869653582089j,
            -0.015936365874249 + 0.045644791294382j,
            +0.488007491912056 + 0.000000000000000j,
            +0.345878195186864 + 0.581036411381697j,
            -0.196612727816662 + 0.358585429905346j,
            +0.095649904985154 + 0.000000000000000j,
            +0.245719006995142 + 0.407555608588782j,
            -0.241281786260967 + 0.435954508657145j,
            -0.207829933952911 + 0.000000000000000j,
            +0.079181848920218 + 0.119104789454885j,
            -0.146310168931118 + 0.271458842164858j,
            -0.228872176444977 + 0.000000000000000j,
            -0.011850730150955 - 0.038568262640418j,
            -0.030305831982073 + 0.070533436670771j,
            -0.046815544995869 - 0.000000000000000j,
            +0.028875171992763 + 0.031971069056580j,
            -0.017035673802716 + 0.047548848479650j,
            +0.074173644652105 + 0.000000000000000j,
            +0.122884890067809 + 0.194800677167786j,
            -0.117974777548011 + 0.222380504636967j,
            -0.057882725888977 + 0.000000000000000j,
            +0.134312498217841 + 0.214593875092629j,
            -0.221139275228979 + 0.401066656157726j,
            -0.374366875288802 + 0.000000000000000j,
            +0.001477627100940 - 0.015482870698707j,
            -0.196141728358334 + 0.357769634913184j,
            -0.600645911934946 - 0.000000000000000j,
            -0.199011485493909 - 0.362740200077384j,
            -0.018804678195657 + 0.050612853967036j,
            -0.504992239743005 + 0.000000000000000j,
            -0.315562220585312 - 0.564611994915193j,
            +0.199575724795823 - 0.327633099391573j,
            -0.114472447329920 + 0.000000000000000j,
            -0.255496699659903 - 0.460575460889293j,
            +0.306243399925619 - 0.512386932241631j,
            +0.300322955967473 - 0.000000000000000j,
            -0.067815050107907 - 0.135501308216900j,
            +0.239504419511774 - 0.396791627319508j,
            +0.459228956407857 + 0.000000000000000j,
            +0.100566497782449 + 0.156144087786288j,
            +0.079659353050397 - 0.119931850869178j,
            +0.313230873595303 - 0.000000000000000j,
            +0.135224295204036 + 0.216173153798907j,
            -0.027379823813015 + 0.065465441858601j,
            +0.074173644652105 - 0.000000000000000j,
            +0.052594605527829 + 0.073054333066068j,
            -0.003442167409076 + 0.024004204752853j,
            +0.008651163045441 + 0.000000000000000j,
            -0.022708661791116 - 0.057374751906286j,
            +0.093566379308805 - 0.144019526930936j,
            +0.186578307706181 + 0.000000000000000j,
            +0.020324257052154 + 0.017160449928245j,
            +0.128367169714283 - 0.204296264056780j,
            +0.415659867905822 - 0.000000000000000j,
            +0.170855279505655 + 0.277887828933000j,
            +0.019446769948462 - 0.015640597681664j,
            +0.421957081169469 - 0.000000000000000j,
            +0.301573440172975 + 0.504298324680751j,
            -0.178506610796544 + 0.327224715298713j,
            +0.110622317568560 - 0.000000000000000j,
            +0.283482917437827 + 0.472964620167994j,
            -0.317523097098001 + 0.568008332662539j,
            -0.333333333333333 + 0.000000000000000j,
            +0.105348171727558 + 0.164426190004446j,
            -0.286476236544092 + 0.514233592767663j,
            -0.598629809480615 - 0.000000000000000j,
            -0.111709703327381 - 0.211529077773645j,
            -0.110185192448478 + 0.208888547474695j,
            -0.517606986154623 + 0.000000000000000j,
            -0.218498262747203 - 0.396492288355865j,
            +0.072772506195994 - 0.108003482213407j,
            -0.207829933952912 + 0.000000000000000j,
            -0.166535132858598 - 0.306489507268501j,
            +0.133320489948777 - 0.212875666369082j,
            +0.042293868738796 + 0.000000000000000j,
            -0.044714646575287 - 0.095490235623059j,
            +0.063998431485942 - 0.092806339026192j,
            +0.038164381950427 + 0.000000000000000j,
            +0.008478811996460 - 0.003356462746482j,
            -0.021703296617485 + 0.055633408345397j,
            -0.148347289304210 + 0.000000000000000j,
            -0.064120194417011 - 0.129101630433633j,
            -0.001003762486682 + 0.019780763537840j,
            -0.255348147706326 + 0.000000000000000j,
            -0.184757642912780 - 0.338051820523779j,
            +0.138901732758987 - 0.222542662485744j,
            -0.084862081119056 + 0.000000000000000j,
            -0.213711831793107 - 0.388201946756452j,
            +0.284175415551571 - 0.474164062085144j,
            +0.300322955967473 + 0.000000000000000j,
            -0.081768641475705 - 0.159669637413981j,
            +0.296297182432551 - 0.495159578200508j,
            +0.619464687072923 - 0.000000000000000j,
            +0.139711287047343 + 0.223944851644661j,
            +0.139711287047343 - 0.223944851644662j,
            +0.619464687072923 + 0.000000000000000j,
            +0.296297182432551 + 0.495159578200508j,
            -0.081768641475705 + 0.159669637413981j,
            +0.300322955967473 + 0.000000000000000j,
            +0.284175415551570 + 0.474164062085143j,
            -0.213711831793107 + 0.388201946756451j,
            -0.084862081119055 - 0.000000000000000j,
            +0.138901732758987 + 0.222542662485744j,
            -0.184757642912780 + 0.338051820523779j,
            -0.255348147706325 - 0.000000000000000j,
            -0.001003762486681 - 0.019780763537839j,
            -0.064120194417011 + 0.129101630433633j,
            -0.148347289304210 + 0.000000000000000j,
            -0.021703296617484 - 0.055633408345397j,
            +0.008478811996460 + 0.003356462746483j,
            +0.038164381950427 - 0.000000000000000j,
            +0.063998431485942 + 0.092806339026191j,
            -0.044714646575287 + 0.095490235623059j,
            +0.042293868738796 + 0.000000000000000j,
            +0.133320489948778 + 0.212875666369083j,
            -0.166535132858598 + 0.306489507268501j,
            -0.207829933952912 + 0.000000000000000j,
            +0.072772506195994 + 0.108003482213406j,
            -0.218498262747202 + 0.396492288355864j,
            -0.517606986154623 + 0.000000000000000j,
            -0.110185192448478 - 0.208888547474694j,
            -0.111709703327381 + 0.211529077773645j,
            -0.598629809480615 - 0.000000000000000j,
            -0.286476236544093 - 0.514233592767664j,
            +0.105348171727559 - 0.164426190004447j,
            -0.333333333333331 - 0.000000000000000j,
            -0.317523097097999 - 0.568008332662537j,
            +0.283482917437826 - 0.472964620167993j,
            +0.110622317568558 + 0.000000000000000j,
            -0.178506610796544 - 0.327224715298713j,
            +0.301573440172975 - 0.504298324680750j,
            +0.421957081169468 - 0.000000000000000j,
            +0.019446769948462 + 0.015640597681663j,
            +0.170855279505655 - 0.277887828933000j,
            +0.415659867905821 + 0.000000000000000j,
            +0.128367169714282 + 0.204296264056778j,
            +0.020324257052154 - 0.017160449928246j,
            +0.186578307706181 + 0.000000000000000j,
            +0.093566379308804 + 0.144019526930935j,
            -0.022708661791115 + 0.057374751906285j,
            +0.008651163045441 - 0.000000000000000j,
            -0.003442167409076 - 0.024004204752854j,
            +0.052594605527830 - 0.073054333066069j,
            +0.074173644652106 + 0.000000000000000j,
            -0.027379823813015 - 0.065465441858602j,
            +0.135224295204037 - 0.216173153798908j,
            +0.313230873595305 - 0.000000000000000j,
            +0.079659353050397 + 0.119931850869179j,
            +0.100566497782449 - 0.156144087786288j,
            +0.459228956407857 + 0.000000000000000j,
            +0.239504419511774 + 0.396791627319508j,
            -0.067815050107907 + 0.135501308216900j,
            +0.300322955967474 - 0.000000000000000j,
            +0.306243399925620 + 0.512386932241633j,
            -0.255496699659903 + 0.460575460889294j,
            -0.114472447329920 - 0.000000000000000j,
            +0.199575724795822 + 0.327633099391572j,
            -0.315562220585311 + 0.564611994915193j,
            -0.504992239743005 + 0.000000000000000j,
            -0.018804678195657 - 0.050612853967036j,
            -0.199011485493909 + 0.362740200077383j,
            -0.600645911934945 - 0.000000000000000j,
            -0.196141728358334 - 0.357769634913183j,
            +0.001477627100940 + 0.015482870698707j,
            -0.374366875288802 + 0.000000000000000j,
            -0.221139275228979 - 0.401066656157725j,
            +0.134312498217840 - 0.214593875092628j,
            -0.057882725888977 + 0.000000000000000j,
            -0.117974777548011 - 0.222380504636967j,
            +0.122884890067809 - 0.194800677167786j,
            +0.074173644652104 + 0.000000000000000j,
            -0.017035673802716 - 0.047548848479650j,
            +0.028875171992763 - 0.031971069056579j,
            -0.046815544995869 - 0.000000000000000j,
            -0.030305831982073 - 0.070533436670771j,
            -0.011850730150955 + 0.038568262640418j,
            -0.228872176444978 + 0.000000000000000j,
            -0.146310168931118 - 0.271458842164858j,
            +0.079181848920218 - 0.119104789454885j,
            -0.207829933952912 + 0.000000000000000j,
            -0.241281786260968 - 0.435954508657147j,
            +0.245719006995142 - 0.407555608588783j,
            +0.095649904985155 - 0.000000000000000j,
            -0.196612727816663 - 0.358585429905346j,
            +0.345878195186865 - 0.581036411381699j,
            +0.488007491912058 - 0.000000000000000j,
            -0.015936365874248 - 0.045644791294380j,
            +0.285737489530649 - 0.476869653582088j,
            +0.666666666666667 - 0.000000000000000j,
            +0.154635505679479 + 0.249794356578788j,
            +0.154635505679479 - 0.249794356578787j,
        ]
    )


def strict_compare_waves(
    dep_vector=None,
    rfunc=None,
    rdesc=None,
    dep_units=None,
    nobj=None,
    indep_vector=None,
):
    """Strictly compare waveform objects."""
    # pylint: disable=R0913
    wobj = rfunc(
        std_wobj(dep_name="wobj", indep_vector=indep_vector, dep_vector=dep_vector)
    )
    ref = std_wobj(
        dep_name="{0}(wobj)".format(rdesc),
        indep_vector=indep_vector,
        dep_vector=(
            copy.copy(wobj.dep_vector)
            if dep_vector is None
            else (nobj if isinstance(nobj, np.ndarray) else nobj(dep_vector))
        ),
        dep_units=dep_units,
    )
    assert wobj == ref
    assert wobj.dep_name == ref.dep_name


def trunc_fft():
    """FFT of truncated waveform."""
    # pylint: disable=E1101
    wobj, _, _ = fft_wave()
    npoints = int(round(wobj.indep_vector.size / 2.0))
    tend = wobj.indep_vector[-1]
    fsample = 1 / (tend / (npoints - 1))
    finc = fsample / (npoints - 1)
    ret_indep_vector = barange(-fsample / 2.0, +fsample / 2.0, finc)
    ret_dep_vector = fft(wobj.dep_vector, int(npoints))
    return npoints, wobj, ret_indep_vector, ret_dep_vector


def trunc_ifft():
    """Return truncated inverse FFT values."""
    return np.array(
        [
            +2.031250000000000 + 0.485562004170310j,
            +0.318199714955461 + 1.820624205429553j,
            -0.655366529334933 + 0.370897276393319j,
            +0.253770933956314 + 0.472192494451151j,
            -1.091850625866407 + 1.008883882566930j,
            -1.483726719229016 - 1.218334195829139j,
            +0.932218867902417 - 1.517542164627016j,
            +0.970942620785909 + 0.377363442128093j,
            +0.057203489136323 - 0.118012970393690j,
            +1.278229603717467 + 0.024011318785796j,
            +0.363116952705678 + 1.901659679959610j,
            -1.764639428441845 + 0.669238126410875j,
            -0.592239801858736 - 1.067929045507627j,
            +0.145743145851282 - 0.087430310992305j,
            -0.734794443118979 - 0.637320331737055j,
            +0.932218867902418 - 1.558125493050408j,
            +1.889644061218770 + 0.675774448583172j,
            -0.223336243357166 + 1.440169104578383j,
            -0.413791867912630 - 0.006765550628069j,
            +0.158131606216389 + 0.709580268064139j,
            -1.521570958463868 + 0.551739964037835j,
            -0.968749999999992 - 1.749225282837794j,
            +1.297121243508404 - 1.083512630798513j,
            +0.590984923118542 + 0.443632461449772j,
            +0.253770933956317 - 0.416986909397531j,
            +1.408936869223572 + 0.463176291745721j,
            -0.312167341989761 + 1.900930595536623j,
            -1.770687735804836 - 0.057830535626995j,
            -0.142398177666932 - 1.058366268101016j,
            -0.109196634987608 - 0.046753215150384j,
            -0.592239801858736 - 1.221105979700343j,
            +1.495272475736174 - 1.470194679913401j,
        ]
    )


###
# Test functions
###
def test_acos():
    """Test acos function behavior."""
    dep_vector = np.array([0.1, 0.98, 0.5])
    strict_compare_waves(dep_vector, peng.acos, "acos", "rad", np.arccos)


@pytest.mark.wave_functions
def test_acos_exceptions():
    """Test acos function exceptions."""
    dep_vector = np.array([-1.01, 0.98, 0.5])
    wobj_a = std_wobj(dep_name="wobj_a", dep_vector=dep_vector)
    dep_vector = np.array([1.01, 0.98, 0.5])
    wobj_b = std_wobj(dep_name="wobj_b", dep_vector=dep_vector)
    for item in [wobj_a, wobj_b]:
        AE(peng.acos, ValueError, "Math domain error", item)


def test_acosh():
    """Test acosh function behavior."""
    dep_vector = np.array([1.1, 1.98, 1.5])
    strict_compare_waves(dep_vector, peng.acosh, "acosh", "", np.arccosh)


@pytest.mark.wave_functions
def test_acosh_exceptions():
    """Test acosh function exceptions."""
    dep_vector = np.array([0.99, 0.98, 0.5])
    wobj = std_wobj(dep_name="wobj_a", dep_vector=dep_vector)
    AE(peng.acosh, ValueError, "Math domain error", wobj)


def test_asin():
    """Test asin function behavior."""
    dep_vector = np.array([0.1, 0.98, 0.5])
    strict_compare_waves(dep_vector, peng.asin, "asin", "rad", np.arcsin)


@pytest.mark.wave_functions
def test_asin_exceptions():
    """Test asin function exceptions."""
    dep_vector = np.array([-1.01, 0.98, 0.5])
    wobj_a = std_wobj(dep_name="wobj_a", dep_vector=dep_vector)
    dep_vector = np.array([1.01, 0.98, 0.5])
    wobj_b = std_wobj(dep_name="wobj_b", dep_vector=dep_vector)
    for item in [wobj_a, wobj_b]:
        AE(peng.asin, ValueError, "Math domain error", item)


def test_asinh():
    """Test asinh function behavior."""
    dep_vector = np.array([1.1, 1.98, 1.5])
    strict_compare_waves(dep_vector, peng.asinh, "asinh", "", np.arcsinh)


def test_atan():
    """Test atan function behavior."""
    dep_vector = np.array([1.1, 1.98, 1.5])
    strict_compare_waves(dep_vector, peng.atan, "atan", "rad", np.arctan)


def test_atanh():
    """Test atanh function behavior."""
    dep_vector = np.array([0.1, 0.98, 0.5])
    strict_compare_waves(dep_vector, peng.atanh, "atanh", "", np.arctanh)


@pytest.mark.wave_functions
def test_atanh_exceptions():
    """Test atanh function exceptions."""
    dep_vector = np.array([-1.01, 0.98, 0.5])
    wobj_a = std_wobj(dep_name="wobj_a", dep_vector=dep_vector)
    dep_vector = np.array([1.01, 0.98, 0.5])
    wobj_b = std_wobj(dep_name="wobj_b", dep_vector=dep_vector)
    for item in [wobj_a, wobj_b]:
        AE(peng.atanh, ValueError, "Math domain error", item)


def test_average():
    """Test average and naverage functions behavior."""
    wobj = std_wobj(
        indep_vector=np.array([1, 2, 3, 7, 9, 15]),
        dep_vector=np.array([6, 5, 4, 8.2, 7, 7.25]),
        dep_name="wobj",
        interp="CONTINUOUS",
        indep_scale="LINEAR",
    )
    act = peng.average(wobj)
    ref = std_wobj(
        dep_name="average(wobj)",
        indep_vector=np.array([1, 2, 3, 7, 9, 15]),
        dep_vector=np.array([6.0, 5.5, 5.0, 5.73333333333, 6.2, 6.59642857143]),
        dep_units="Volts",
        interp="CONTINUOUS",
        indep_scale="LINEAR",
    )
    assert act == ref
    wobj = std_wobj(dep_name="wobj", interp="CONTINUOUS", indep_scale="LINEAR")
    act = peng.average(wobj)
    ref = std_wobj(
        dep_name="average(wobj)",
        dep_vector=np.array([6.0, 5.5, 5.0]),
        dep_units="Volts",
        interp="CONTINUOUS",
        indep_scale="LINEAR",
    )
    assert act.dep_name == ref.dep_name
    act = peng.average(wobj, indep_min=1.5)
    cmp_vectors(act.dep_vector, np.array([5.5, 5.25, 4.75]))
    assert peng.naverage(wobj, indep_min=1.5) == act[-1].dep_var
    act = peng.average(wobj, indep_max=2.5)
    cmp_vectors(act.dep_vector, np.array([6, 5.5, 5.25]))
    assert peng.naverage(wobj, indep_max=2.5) == act[-1].dep_var
    act = peng.average(wobj, indep_min=1.5, indep_max=2.5)
    cmp_vectors(act.dep_vector, np.array([5.5, 5.25, 5.0]))
    num = peng.naverage(wobj, indep_min=1.5, indep_max=2.5)
    assert num == act[-1].dep_var


@pytest.mark.wave_functions
def test_bound_exceptions():
    """Test exceptions of functions that have range bounding."""
    wobj = std_wobj(dep_name="wobj")
    items = [
        peng.average,
        peng.derivative,
        peng.fft,
        peng.fftdb,
        peng.ffti,
        peng.fftm,
        peng.fftp,
        peng.fftr,
        peng.ifft,
        peng.ifftdb,
        peng.iffti,
        peng.ifftm,
        peng.ifftp,
        peng.ifftr,
        peng.integral,
        peng.naverage,
        peng.nintegral,
        peng.nmax,
        peng.nmin,
        peng.subwave,
    ]
    for item in items:
        AI(item, "indep_min", wave=wobj, indep_min="a")
        AI(item, "indep_max", wave=wobj, indep_max="a")
        msg = "Incongruent `indep_min` and `indep_max` arguments"
        AE(item, RuntimeError, msg, wave=wobj, indep_min=1.5, indep_max=1)
        AI(item, "indep_min", wave=wobj, indep_min=0)
        AI(item, "indep_max", wave=wobj, indep_max=10)


def test_ceil():
    """Test ceil function behavior."""
    dep_vector = np.array([10.41, 1.98, 1.0])
    strict_compare_waves(dep_vector, peng.ceil, "ceil", "Volts", np.ceil)


def test_cos():
    """Test cos function behavior."""
    dep_vector = np.array([1.1, 1.98, 1.5])
    strict_compare_waves(dep_vector, peng.cos, "cos", "", np.cos)


def test_cosh():
    """Test cosh function behavior."""
    dep_vector = np.array([0.1, 0.98, 0.5])
    strict_compare_waves(dep_vector, peng.cosh, "cosh", "", np.cosh)


def test_db():
    """Test db function behavior."""
    dep_vector = np.array([10, 100, 1000])
    strict_compare_waves(dep_vector, peng.db, "db", "dB", np.array([20.0, 40.0, 60.0]))


@pytest.mark.wave_functions
def test_db_exceptions():
    """Test db function exceptions."""
    dep_vector = np.array([0, 0.98, 0.5])
    wobj = std_wobj(dep_name="wobj", dep_vector=dep_vector)
    AE(peng.db, ValueError, "Math domain error", wobj)


def test_derivative():
    """Test derivative method behavior."""
    indep_vector = np.array([1, 2.5, 3, 4.75])
    dep_vector = np.array([6, 5, 5.5, 1])
    strict_compare_waves(
        dep_vector,
        peng.derivative,
        "derivative",
        "Volts/Sec",
        np.array([-0.66666666666, -0.66666666666, 1.0, -2.5714285714]),
        indep_vector,
    )
    wobj = std_wobj("wobj", indep_vector, dep_vector)
    wobj.indep_units = ""
    assert peng.derivative(wobj).dep_units == "Volts"
    wobj.indep_units = "Sec"
    wobj.dep_units = ""
    assert peng.derivative(wobj).dep_units == "1/Sec"
    wobj.indep_units = ""
    wobj.dep_units = ""
    assert peng.derivative(wobj).dep_units == ""


def test_exp():
    """Test exp function behavior."""
    strict_compare_waves(None, peng.exp, "exp", "", np.exp)


def test_fft():
    """Test fft function behavior."""
    # Full
    _, wobj, ret_indep_vector, ret_dep_vector = full_fft()
    tobj = peng.fft(wobj)
    assert tobj.dep_name == "fft(wobj)"
    assert tobj.indep_units == "Hz"
    assert tobj.dep_units == ""
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, ret_dep_vector)
    # Zero padding
    npoints, wobj, ret_indep_vector, ret_dep_vector = padded_fft()
    tobj = peng.fft(wobj, npoints=npoints)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, ret_dep_vector)
    # Truncation
    npoints, wobj, ret_indep_vector, ret_dep_vector = trunc_fft()
    tobj = peng.fft(wobj, npoints=npoints)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, ret_dep_vector)


def test_fftdb():
    """Test fftdb function behavior."""
    # Effectively null elements may have different values in relative terms
    # depending on the computation method, particularly after applying some
    # function like db, so they are omitted
    # Full
    _, wobj, ret_indep_vector, ret_dep_vector = full_fft()
    tobj = peng.fftdb(wobj)
    assert tobj.dep_name == "db(fft(wobj))"
    assert tobj.indep_units == "Hz"
    assert tobj.dep_units == "dB"
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    act = np.delete(copy.copy(tobj.dep_vector), 32)
    rct = np.delete(copy.copy(ret_dep_vector), 32)
    cmp_vectors(act, 20.0 * np.log10(np.abs(rct)))
    # Zero padding
    npoints, wobj, ret_indep_vector, ret_dep_vector = padded_fft()
    tobj = peng.fftdb(wobj, npoints=npoints)
    act = np.delete(copy.copy(tobj.dep_vector), [32, 96])
    rct = np.delete(copy.copy(ret_dep_vector), [32, 96])
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(act, 20.0 * np.log10(np.abs(rct)))
    # Truncation
    npoints, wobj, ret_indep_vector, ret_dep_vector = trunc_fft()
    tobj = peng.fftdb(wobj, npoints=npoints)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, 20.0 * np.log10(np.abs(ret_dep_vector)))


def test_ffti():
    """Test ffti function behavior."""
    # Full
    _, wobj, ret_indep_vector, ret_dep_vector = full_fft()
    tobj = peng.ffti(wobj)
    assert tobj.dep_name == "imag(fft(wobj))"
    assert tobj.indep_units == "Hz"
    assert tobj.dep_units == ""
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.imag(ret_dep_vector))
    # Zero padding
    npoints, wobj, ret_indep_vector, ret_dep_vector = padded_fft()
    tobj = peng.ffti(wobj, npoints=npoints)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.imag(ret_dep_vector))
    # Truncation
    npoints, wobj, ret_indep_vector, ret_dep_vector = trunc_fft()
    tobj = peng.ffti(wobj, npoints=npoints)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.imag(ret_dep_vector))


def test_fftm():
    """Test fftm function behavior."""
    # Full
    _, wobj, ret_indep_vector, ret_dep_vector = full_fft()
    tobj = peng.fftm(wobj)
    assert tobj.dep_name == "abs(fft(wobj))"
    assert tobj.indep_units == "Hz"
    assert tobj.dep_units == ""
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.abs(ret_dep_vector))
    # Zero padding
    npoints, wobj, ret_indep_vector, ret_dep_vector = padded_fft()
    tobj = peng.fftm(wobj, npoints=npoints)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.abs(ret_dep_vector))
    # Truncation
    npoints, wobj, ret_indep_vector, ret_dep_vector = trunc_fft()
    tobj = peng.fftm(wobj, npoints=npoints)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.abs(ret_dep_vector))


def test_fftp():
    """Test fftp function behavior."""
    # Full
    _, wobj, ret_indep_vector, ret_dep_vector = full_fft()
    tobj = peng.fftp(wobj)
    assert tobj.dep_name == "phase(fft(wobj))"
    assert tobj.indep_units == "Hz"
    assert tobj.dep_units == "rad"
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    act = np.delete(copy.copy(tobj.dep_vector), 32)
    rct = np.delete(copy.copy(ret_dep_vector), 32)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(act, np.unwrap(np.angle(rct)))
    # Zero padding
    npoints, wobj, ret_indep_vector, ret_dep_vector = padded_fft()
    tobj = peng.fftp(wobj, npoints=npoints, unwrap=False)
    act = np.delete(copy.copy(tobj.dep_vector), [32, 96])
    rct = np.delete(copy.copy(ret_dep_vector), [32, 96])
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(act, np.angle(rct))
    # Truncation
    npoints, wobj, ret_indep_vector, ret_dep_vector = trunc_fft()
    tobj = peng.fftp(wobj, npoints=npoints, rad=False)
    assert tobj.dep_units == "deg"
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.rad2deg(np.unwrap(np.angle((ret_dep_vector)))))


@pytest.mark.wave_functions
def test_fftp_exceptions():
    """Test fftp function exceptions of unwrap and rad parameters."""
    wobj = std_wobj("wobj")
    AI(peng.fftp, "unwrap", wobj, unwrap=3.5)
    AI(peng.fftp, "rad", wobj, rad=3.5)


def test_fftr():
    """Test fftr function behavior."""
    # Full
    _, wobj, ret_indep_vector, ret_dep_vector = full_fft()
    tobj = peng.fftr(wobj)
    assert tobj.dep_name == "real(fft(wobj))"
    assert tobj.indep_units == "Hz"
    assert tobj.dep_units == ""
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.real(ret_dep_vector))
    # # Zero padding
    npoints, wobj, ret_indep_vector, ret_dep_vector = padded_fft()
    tobj = peng.fftr(wobj, npoints=npoints)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.real(ret_dep_vector))
    # Truncation
    npoints, wobj, ret_indep_vector, ret_dep_vector = trunc_fft()
    tobj = peng.fftr(wobj, npoints=npoints)
    cmp_vectors(tobj.indep_vector, ret_indep_vector)
    cmp_vectors(tobj.dep_vector, np.real(ret_dep_vector))


@pytest.mark.wave_functions
def test_fftstar_exceptions():
    """Test fft function exceptions."""
    funcs = [peng.fft, peng.fftdb, peng.ffti, peng.fftm, peng.fftp, peng.fftr]
    wobj1 = std_wobj("wobj1")
    wobj2 = std_wobj("wobj2", indep_vector=np.array([10, 11, 20]))
    for func in funcs:
        items = [0, 0.0, 0.99]
        for item in items:
            AI(func, "npoints", wobj1, item)
        AE(func, RE, "Non-uniform sampling", wobj2)


def test_find():
    """Test find function behavior."""
    wobj = std_wobj("wobj")
    items = [3, 3.0, 7, 7.0]
    for item in items:
        assert peng.find(wobj, item) is None
    for interp in ["CONTINUOUS", "STAIRCASE"]:
        wobj = std_wobj(
            "wobj",
            indep_vector=np.array([1, 2, 3, 4, 5, 6.75]),
            dep_vector=np.array([6, 5, 4, 5, 5.75, 6]),
            interp=interp,
        )
        ref = [1.25, 2.25, 3.75, 1.25] if interp == "CONTINUOUS" else [2, 3, 4, 2]
        # Approximate
        assert peng.find(wobj, 6.00000000001) == 1
        assert peng.find(wobj, 6.00000000001, inst=2) == 6.75
        assert peng.find(wobj, 6.00000000001, inst=3) is None
        assert peng.find(wobj, 3.99999999999) == 3
        assert peng.find(wobj, 3.99999999999, inst=2) is None
        # Exact, at edges
        assert peng.find(wobj, 6) == 1
        assert peng.find(wobj, 6, inst=2) == 6.75
        assert peng.find(wobj, 6, inst=3) is None
        # Exact, not at edges
        assert peng.find(wobj, 5) == 2
        assert peng.find(wobj, 5, inst=2) == 4
        assert peng.find(wobj, 5, inst=3) is None
        assert peng.find(wobj, 5.75) == ref[0]
        assert peng.find(wobj, 5.75, inst=2) == 5
        # Slope
        assert peng.find(wobj, 4.75, der=-1) == ref[1]
        assert peng.find(wobj, 4.75, inst=2, der=-1) is None
        assert peng.find(wobj, 4.75, der=+1) == ref[2]
        assert peng.find(wobj, 4.75, inst=2, der=+1) is None
        assert peng.find(wobj, 5.75, der=-1) == ref[3]
        assert peng.find(wobj, 5.75, inst=2, der=-1) is None
        assert peng.find(wobj, 5.75, inst=2, der=+1) is None
        assert peng.find(wobj, 5.75, der=0) == 5
        assert peng.find(wobj, 5.75, inst=2, der=0) is None


@pytest.mark.wave_functions
def test_find_exceptions():
    """Test find function exceptions."""
    fobj = peng.find
    wobj = std_wobj("wobj")
    AI(fobj, "wave", "a", 5.0)
    AI(fobj, "dep_var", wobj, 3 + 2j)
    items = ["a", 1.0, -2, 2]
    for item in items:
        AI(fobj, "der", wobj, 1.0, item)
    items = ["a", 1.0, 0]
    for item in items:
        AI(fobj, "inst", wobj, 1.0, 0, item)
    # Range
    AI(fobj, "indep_min", wave=wobj, dep_var=1.0, indep_min="a")
    AI(fobj, "indep_max", wave=wobj, dep_var=1.0, indep_max="a")
    msg = "Incongruent `indep_min` and `indep_max` arguments"
    AE(fobj, RE, msg, wave=wobj, dep_var=1.0, indep_min=1.5, indep_max=1)
    AI(fobj, "indep_min", wave=wobj, dep_var=1.0, indep_min=0)
    AI(fobj, "indep_max", wave=wobj, dep_var=1.0, indep_max=10)


def test_floor():
    """Test floor function behavior."""
    dep_vector = np.array([10.41, 1.98, 1.0])
    strict_compare_waves(dep_vector, peng.floor, "floor", "Volts", np.floor)


@pytest.mark.wave_functions
def test_funcs_exceptions():
    """Test argument wave not valid exception."""
    items = [
        peng.acos,
        peng.acosh,
        peng.asin,
        peng.asinh,
        peng.atan,
        peng.atanh,
        peng.average,
        peng.ceil,
        peng.cos,
        peng.cosh,
        peng.db,
        peng.derivative,
        peng.exp,
        peng.fft,
        peng.fftdb,
        peng.ffti,
        peng.fftm,
        peng.fftp,
        peng.fftr,
        peng.floor,
        peng.ifft,
        peng.ifftdb,
        peng.iffti,
        peng.ifftm,
        peng.ifftp,
        peng.ifftr,
        peng.imag,
        peng.integral,
        peng.group_delay,
        peng.log,
        peng.log10,
        peng.naverage,
        peng.nintegral,
        peng.nmax,
        peng.nmin,
        peng.phase,
        peng.real,
        peng.round,
        peng.sin,
        peng.sinh,
        peng.sqrt,
        peng.subwave,
        peng.tan,
        peng.tanh,
        peng.wcomplex,
        peng.wfloat,
        peng.wint,
    ]
    for item in items:
        AI(item, "wave", "a")


def test_ifft():
    """Test ifft function behavior."""
    # Full
    npoints1, wobj, _, _ = full_fft()
    tobj = peng.ifft(peng.fft(wobj))
    assert tobj.dep_name == "ifft(fft(wobj))"
    assert tobj.indep_units == "sec"
    assert tobj.dep_units == ""
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, wobj.indep_vector)
    cmp_vectors(tobj.dep_vector, wobj.dep_vector)
    # Zero padding
    npoints2, wobj, _, _ = padded_fft()
    tobj = peng.ifft(peng.fft(wobj), npoints=npoints2)
    cmp_vectors(
        tobj.indep_vector,
        barange(0, wobj.indep_vector[-1], wobj.indep_vector[-1] / (npoints2 - 1)),
    )
    cmp_vectors(tobj.dep_vector, padded_ifft())
    # Truncation
    npoints3, wobj, _, _ = trunc_fft()
    ratio = int(npoints1 / float(npoints3))
    tobj = peng.ifft(peng.fft(wobj), npoints=npoints3)
    cmp_vectors(tobj.indep_vector, wobj.indep_vector[::ratio], 1e-4, 1e-4)
    cmp_vectors(tobj.dep_vector, trunc_ifft())


def test_ifftdb():
    """Test ifftdb function behavior."""
    # Full
    npoints1, wobj, _, _ = full_fft()
    tobj = peng.ifftdb(peng.fft(wobj))
    assert tobj.dep_name == "db(ifft(fft(wobj)))"
    assert tobj.indep_units == "sec"
    assert tobj.dep_units == "dB"
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, wobj.indep_vector)
    cmp_vectors(tobj.dep_vector, 20 * np.log10(np.abs(wobj.dep_vector)))
    # Zero padding
    npoints2, wobj, _, _ = padded_fft()
    tobj = peng.ifftdb(peng.fft(wobj), npoints=npoints2)
    cmp_vectors(
        tobj.indep_vector,
        barange(0, wobj.indep_vector[-1], wobj.indep_vector[-1] / (npoints2 - 1)),
    )
    cmp_vectors(tobj.dep_vector, 20 * np.log10(np.abs(padded_ifft())))
    # Truncation
    npoints3, wobj, _, _ = trunc_fft()
    ratio = int(npoints1 / float(npoints3))
    tobj = peng.ifftdb(peng.fft(wobj), npoints=npoints3)
    cmp_vectors(tobj.indep_vector, wobj.indep_vector[::ratio], 1e-4, 1e-4)
    cmp_vectors(tobj.dep_vector, 20 * np.log10(np.abs(trunc_ifft())))


def test_iffti():
    """Test iffti function behavior."""
    # Full
    npoints1, wobj, _, _ = full_fft()
    tobj = peng.iffti(peng.fft(wobj))
    assert tobj.dep_name == "imag(ifft(fft(wobj)))"
    assert tobj.indep_units == "sec"
    assert tobj.dep_units == ""
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, wobj.indep_vector)
    cmp_vectors(tobj.dep_vector, np.imag(wobj.dep_vector))
    # Zero padding
    npoints2, wobj, _, _ = padded_fft()
    tobj = peng.iffti(peng.fft(wobj), npoints=npoints2)
    cmp_vectors(
        tobj.indep_vector,
        barange(0, wobj.indep_vector[-1], wobj.indep_vector[-1] / (npoints2 - 1)),
    )
    cmp_vectors(tobj.dep_vector, np.imag(padded_ifft()))
    # Truncation
    npoints3, wobj, _, _ = trunc_fft()
    ratio = int(npoints1 / float(npoints3))
    tobj = peng.iffti(peng.fft(wobj), npoints=npoints3)
    cmp_vectors(tobj.indep_vector, wobj.indep_vector[::ratio], 1e-4, 1e-4)
    cmp_vectors(tobj.dep_vector, np.imag(trunc_ifft()))


def test_ifftm():
    """Test ifftm function behavior."""
    npoints1, wobj, _, _ = full_fft()
    tobj = peng.ifftm(peng.fft(wobj))
    assert tobj.dep_name == "abs(ifft(fft(wobj)))"
    assert tobj.indep_units == "sec"
    assert tobj.dep_units == ""
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, wobj.indep_vector)
    cmp_vectors(tobj.dep_vector, np.abs(wobj.dep_vector))
    # Zero padding
    npoints2, wobj, _, _ = padded_fft()
    tobj = peng.ifftm(peng.fft(wobj), npoints=npoints2)
    cmp_vectors(
        tobj.indep_vector,
        barange(0, wobj.indep_vector[-1], wobj.indep_vector[-1] / (npoints2 - 1)),
    )
    cmp_vectors(tobj.dep_vector, np.abs(padded_ifft()))
    # Truncation
    npoints3, wobj, _, _ = trunc_fft()
    ratio = int(npoints1 / float(npoints3))
    tobj = peng.ifftm(peng.fft(wobj), npoints=npoints3)
    cmp_vectors(tobj.indep_vector, wobj.indep_vector[::ratio], 1e-4, 1e-4)
    cmp_vectors(tobj.dep_vector, np.abs(trunc_ifft()))


def test_ifftp():
    """Test ifftp function behavior."""
    npoints1, wobj, _, _ = full_fft()
    tobj = peng.ifftp(peng.fft(wobj))
    assert tobj.dep_name == "phase(ifft(fft(wobj)))"
    assert tobj.indep_units == "sec"
    assert tobj.dep_units == "rad"
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, wobj.indep_vector)
    cmp_vectors(np.cos(tobj.dep_vector), np.cos(np.unwrap(np.angle(wobj.dep_vector))))
    # Zero padding
    npoints2, wobj, _, _ = padded_fft()
    tobj = peng.ifftp(peng.fft(wobj), npoints=npoints2, unwrap=False)
    cmp_vectors(
        tobj.indep_vector,
        barange(0, wobj.indep_vector[-1], wobj.indep_vector[-1] / (npoints2 - 1)),
    )
    cmp_vectors(np.cos(tobj.dep_vector), np.cos(np.angle(padded_ifft())))
    # Truncation
    npoints3, wobj, _, _ = trunc_fft()
    ratio = int(npoints1 / float(npoints3))
    tobj = peng.ifftp(peng.fft(wobj), npoints=npoints3, rad=False)
    cmp_vectors(tobj.indep_vector, wobj.indep_vector[::ratio], 1e-4, 1e-4)
    cmp_vectors(tobj.dep_vector, np.rad2deg(np.unwrap(np.angle(trunc_ifft()))))


@pytest.mark.wave_functions
def test_ifftp_exceptions():
    """Test ifftp function exceptions of unwrap and rad parameters."""
    wobj = std_wobj("wobj")
    AI(peng.ifftp, "unwrap", wobj, unwrap=3.5)
    AI(peng.ifftp, "rad", wobj, rad=3.5)


def test_ifftr():
    """Test ifftp function behavior."""
    npoints1, wobj, _, _ = full_fft()
    tobj = peng.ifftr(peng.fft(wobj))
    assert tobj.dep_name == "real(ifft(fft(wobj)))"
    assert tobj.indep_units == "sec"
    assert tobj.dep_units == ""
    assert tobj.indep_scale == "LINEAR"
    assert tobj.dep_scale == "LINEAR"
    cmp_vectors(tobj.indep_vector, wobj.indep_vector)
    cmp_vectors(tobj.dep_vector, np.real(wobj.dep_vector))
    # Zero padding
    npoints2, wobj, _, _ = padded_fft()
    tobj = peng.ifftr(peng.fft(wobj), npoints=npoints2)
    cmp_vectors(
        tobj.indep_vector,
        barange(0, wobj.indep_vector[-1], wobj.indep_vector[-1] / (npoints2 - 1)),
    )
    cmp_vectors(tobj.dep_vector, np.real(padded_ifft()))
    # Truncation
    npoints3, wobj, _, _ = trunc_fft()
    ratio = int(npoints1 / float(npoints3))
    tobj = peng.ifftr(peng.fft(wobj), npoints=npoints3)
    cmp_vectors(tobj.indep_vector, wobj.indep_vector[::ratio], 1e-4, 1e-4)
    cmp_vectors(tobj.dep_vector, np.real(trunc_ifft()))


@pytest.mark.wave_functions
def test_ifftstar_exceptions():
    """Test fft function exceptions."""
    funcs = [peng.ifft, peng.ifftdb, peng.iffti, peng.ifftm, peng.ifftp, peng.ifftr]
    wobj1 = std_wobj("wobj1")
    wobj2 = std_wobj("wobj2", indep_vector=np.array([10, 11, 20]))
    for func in funcs:
        items = [0, 0.0, 0.99]
        for item in items:
            AI(func, "npoints", wobj1, item)
        AE(func, RE, "Non-uniform frequency spacing", wobj2)


def test_imag():
    """Test imag function behavior."""
    dep_vector = np.array([10.41, 1 + 3j, 10 - 0.5j])
    strict_compare_waves(dep_vector, peng.imag, "imag", "Volts", np.imag)


def test_integral():
    """Test integral and nintegral methods behavior."""
    indep_vector = np.array([1, 2.5, 3, 4.75])
    dep_vector = np.array([6, 5, 5.5, 1])
    strict_compare_waves(
        dep_vector,
        peng.integral,
        "integral",
        "Volts*Sec",
        np.array([0.0, 8.25, 10.875, 16.5625]),
        indep_vector,
    )
    wobj = std_wobj("wobj", indep_vector, dep_vector)
    act = peng.integral(wobj)
    cmp_vectors(np.array([act.dep_vector[-1]]), np.array([peng.nintegral(wobj)]))
    wobj = std_wobj("wobj", indep_vector, dep_vector)
    wobj.indep_units = ""
    assert peng.integral(wobj).dep_units == "Volts"
    wobj.indep_units = "Sec"
    wobj.dep_units = ""
    assert peng.integral(wobj).dep_units == "Sec"
    wobj.indep_units = ""
    wobj.dep_units = ""
    assert peng.integral(wobj).dep_units == ""


def test_group_delay():
    """Test group_delay function behavior."""
    indep_vector = barange(0, 1e-3, 1e-6)
    delay = 2.35
    dep_vector = np.exp(-1j * 2 * math.pi * delay * indep_vector)
    wobj = std_wobj(
        "wobj",
        indep_vector=indep_vector,
        dep_vector=dep_vector,
        indep_scale="LINEAR",
        interp="CONTINUOUS",
    )
    ref = peng.Waveform(
        indep_vector,
        delay * np.ones(indep_vector.size),
        "group_delay(wobj)",
        indep_units="Sec",
        dep_units="sec",
    )
    act = peng.group_delay(wobj)
    assert act.dep_name == "group_delay(wobj)"
    assert act == ref


def test_log():
    """Test log function behavior."""
    dep_vector = np.array([10.41, 1.98, 1.0])
    strict_compare_waves(dep_vector, peng.log, "log", "", np.log)


def test_log10():
    """Test log function behavior."""
    dep_vector = np.array([10.41, 1.98, 1.0])
    strict_compare_waves(dep_vector, peng.log10, "log10", "", np.log10)


@pytest.mark.wave_functions
def test_log_exceptions():
    """Test log and log10 function exceptions."""
    dep_vector = np.array([0, 0.98, 0.5])
    wobj = std_wobj(dep_name="wobj", dep_vector=dep_vector)
    items = [peng.log, peng.log10]
    for item in items:
        AE(item, ValueError, "Math domain error", wobj)


def test_nmax():
    """Test nmax method behavior."""
    wobj = std_wobj("wobj", indep_scale="LINEAR", interp="CONTINUOUS")
    assert peng.nmax(wobj) == 6
    assert peng.nmax(wobj, 1.5) == 5.5


def test_nmin():
    """Test nmax method behavior."""
    wobj = std_wobj("wobj", indep_scale="LINEAR", interp="CONTINUOUS")
    assert peng.nmin(wobj) == 4
    assert peng.nmin(wobj, indep_max=2.5) == 4.5


def test_phase():
    """Test phase function behavior."""
    indep_vector = np.arange(1, 12, 1)
    dep_vector = np.exp(complex(0, 1) * math.pi * np.arange(0.25, 3, 0.25))
    wobj = peng.phase(
        std_wobj(dep_name="wobj", indep_vector=indep_vector, dep_vector=dep_vector),
        unwrap=False,
    )
    ref = math.pi * np.array(
        [0.25, 0.5, 0.75, 1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75]
    )
    cmp_vectors(wobj.indep_vector, indep_vector)
    cmp_vectors(wobj.dep_vector, ref)
    assert wobj.dep_name == "phase(wobj)"
    assert wobj.dep_units == "rad"
    wobj = peng.phase(
        std_wobj(dep_name="wobj", indep_vector=indep_vector, dep_vector=dep_vector)
    )
    ref = math.pi * np.arange(0.25, 3, 0.25)
    cmp_vectors(wobj.dep_vector, ref)
    wobj = peng.phase(
        std_wobj(dep_name="wobj", indep_vector=indep_vector, dep_vector=dep_vector),
        unwrap=True,
    )
    cmp_vectors(wobj.dep_vector, ref)
    wobj = peng.phase(
        std_wobj(dep_name="wobj", indep_vector=indep_vector, dep_vector=dep_vector),
        unwrap=True,
        rad=False,
    )
    cmp_vectors(wobj.dep_vector, np.arange(45, 534, 45))


@pytest.mark.wave_functions
def test_phase_exceptions():
    """Test phase function exceptions."""
    wobj = std_wobj("wobj")
    items = ["a", 5.0, (1, 2)]
    for item in items:
        AI(peng.phase, "unwrap", wave=wobj, unwrap=item)
        AI(peng.phase, "rad", wave=wobj, rad=item)


def test_real():
    """Test real function behavior."""
    dep_vector = np.array([10.41, 1 + 3j, 10 - 0.5j])
    strict_compare_waves(dep_vector, peng.real, "real", "Volts", np.real)


def test_round():
    """Test wround method behavior."""
    wobj_a = std_wobj("wobj", dep_vector=np.array([5.4, 1.6, 0]))
    ref = std_wobj("round(wobj, 0)", dep_vector=np.array([5, 2, 0]))
    act = peng.round(wobj_a)
    assert ref == act
    assert ref.dep_name == act.dep_name
    wobj_b = std_wobj("wobj", dep_vector=np.array([5.47, 1.61, 0]))
    ref = std_wobj("round(wobj, 1)", dep_vector=np.array([5.5, 1.6, 0.0]))
    act = peng.round(wobj_b, 1)
    assert ref == act
    assert ref.dep_name == act.dep_name


@pytest.mark.wave_functions
def test_round_exceptions():
    """Test wround function exceptions."""
    wobj = std_wobj(dep_name="wobj")
    items = [-1, -0.0001, "a", 3.5]
    for item in items:
        AI(peng.round, "decimals", wave=wobj, decimals=item)


def test_sin():
    """Test sin function behavior."""
    dep_vector = np.array([1.1, 1.98, 1.5])
    strict_compare_waves(dep_vector, peng.sin, "sin", "", np.sin)


def test_sinh():
    """Test sinh function behavior."""
    dep_vector = np.array([0.1, 0.98, 0.5])
    strict_compare_waves(dep_vector, peng.sinh, "sinh", "", np.sinh)


def test_sqrt():
    """Test sqrt function behavior."""
    dep_vector = np.array([1.1, 1.98, 1.5])
    strict_compare_waves(dep_vector, peng.sqrt, "sqrt", "Volts**0.5", np.sqrt)


def test_subwave():
    """Test subwave function behavior."""
    # indep_max and dep_name specified
    wobj = std_wobj("wobj", interp="CONTINUOUS", indep_scale="LINEAR")
    act = peng.subwave(wobj, dep_name="SW", indep_max=2.5)
    ref = peng.Waveform(
        np.array([1, 2, 2.5]),
        np.array([6, 5, 4.5]),
        "SW",
        "LINEAR",
        "LINEAR",
        "Sec",
        "Volts",
        "CONTINUOUS",
    )
    assert act == ref
    assert act.dep_name == "SW"
    # indep_min specified, but not dep_name
    act = peng.subwave(wobj, indep_min=1.5)
    ref = peng.Waveform(
        np.array([1.5, 2, 3]),
        np.array([5.5, 5, 4]),
        "wobj",
        "LINEAR",
        "LINEAR",
        "Sec",
        "Volts",
        "CONTINUOUS",
    )
    assert act == ref
    assert act.dep_name == "wobj"
    # indep_step specified
    act = peng.subwave(wobj, indep_min=1.5, indep_max=2.5, indep_step=0.25)
    ref = peng.Waveform(
        np.array([1.5, 1.75, 2, 2.25, 2.5]),
        np.array([5.5, 5.25, 5, 4.75, 4.5]),
        "wobj",
        "LINEAR",
        "LINEAR",
        "Sec",
        "Volts",
        "CONTINUOUS",
    )
    assert act == ref
    assert act.dep_name == "wobj"


@pytest.mark.wave_functions
def test_subwave_exceptions():
    """Test subwave function exceptions."""
    wobj = std_wobj("wobj")
    AI(peng.subwave, "dep_name", wobj, dep_name=3.5)
    items = ["a", 0, 0.0, -10.2]
    for item in items:
        AI(peng.subwave, "indep_step", wobj, indep_step=item)
    indep_step = 1.1 * wobj.indep_vector[-1] - wobj.indep_vector[0]
    exmsg = "Argument `indep_step` is greater than independent vector range"
    AE(peng.subwave, RE, exmsg, wobj, indep_step=indep_step)


def test_tan():
    """Test tan function behavior."""
    dep_vector = np.array([1.1, 1.98, 1.5])
    strict_compare_waves(dep_vector, peng.tan, "tan", "", np.tan)


def test_tanh():
    """Test tanh function behavior."""
    dep_vector = np.array([0.1, 0.98, 0.5])
    strict_compare_waves(dep_vector, peng.tanh, "tanh", "", np.tanh)


def test_wcomplex():
    """Test wcomplex method behavior."""
    wobj_a = std_wobj(dep_name="wobj_a", dep_vector=np.array([3, 4, 5]))
    wobj_b = peng.wcomplex(wobj_a)
    ref = std_wobj(dep_name="ref", dep_vector=np.array([3 + 0j, 4 + 0j, 5 + 0j]))
    assert wobj_b == ref
    assert wobj_b.dep_vector.dtype.name.startswith("complex")


def test_wfloat():
    """Test wfloat method behavior."""
    wobj_a = std_wobj("wobj_a")
    wobj_b = peng.wfloat(wobj_a)
    ref = std_wobj(dep_name="ref", dep_vector=np.array([6.0, 5.0, 4.0]))
    assert wobj_b == ref
    assert wobj_b.dep_vector.dtype.name.startswith("float")


@pytest.mark.wave_functions
def test_wfloat_exceptions():
    """Test wfloat function exceptions."""
    dep_vector = np.array([0.99, 1 + 3j, 0.5])
    wobj = std_wobj(dep_name="wobj_a", dep_vector=dep_vector)
    AE(peng.wfloat, TypeError, "Cannot convert complex to float", wobj)


def test_wint():
    """Test wint method behavior."""
    wobj_a = std_wobj("wobj_a", dep_vector=np.array([5.5, 1.3, 3.4]))
    wobj_b = peng.wint(wobj_a)
    ref = std_wobj(dep_name="ref", dep_vector=np.array([5, 1, 3]))
    assert wobj_b == ref
    assert wobj_b.dep_vector.dtype.name.startswith("int")


@pytest.mark.wave_functions
def test_wint_exceptions():
    """Test wint function exceptions."""
    dep_vector = np.array([0.99, 1 + 3j, 0.5])
    wobj = std_wobj(dep_name="wobj_a", dep_vector=dep_vector)
    AE(peng.wint, TypeError, "Cannot convert complex to integer", wobj)


def test_wvalue():
    """Test wvalue method behavior."""
    wobj = std_wobj("wobj")
    assert peng.wvalue(wobj, 0.9999999999999) == 6
    assert peng.wvalue(wobj, 1.0) == 6
    assert peng.wvalue(wobj, 1.0000000000001) == 6
    assert peng.wvalue(wobj, 2.9999999999999) == 4
    assert peng.wvalue(wobj, 3) == 4
    assert peng.wvalue(wobj, 3.0000000000001) == 4
    assert peng.wvalue(wobj, 1.5) == 5.5
    assert peng.wvalue(wobj, 1.25) == 5.75
    assert peng.wvalue(wobj, 2.5) == 4.5
    assert peng.wvalue(wobj, 2.9) == 4.1


@pytest.mark.wave_functions
def test_wvalue_exceptions():
    """Test wvalue function exceptions."""
    AI(peng.wvalue, "wave", "a", 5)
    wobj = std_wobj(dep_name="wobj")
    exmsg = "Argument `indep_var` is not in the independent variable vector range"
    AE(peng.wvalue, ValueError, exmsg, wobj, 0)
    AE(peng.wvalue, ValueError, exmsg, wobj, 0.999)
    AE(peng.wvalue, ValueError, exmsg, wobj, 3.001)
    AE(peng.wvalue, ValueError, exmsg, wobj, 4)
