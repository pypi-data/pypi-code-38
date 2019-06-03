import numpy as np, os, sys
thisdir=os.path.abspath(os.path.dirname(__file__))
if thisdir not in sys.path:
    sys.path.insert(0,thisdir)

# sys.path.insert(0,'/home/fi0/dev/SNAP/SNAP_2018_package/braggedgemodeling/')
import braggedgemodeling

from braggedgemodeling import bem
# from bem import xscalc


def diffraction(cif_file, sample):
    material =bem.matter.loadCif(cif_file)


    xsc = bem.xscalc.XSCalculator(material, 300)

    peaks = xsc.diffpeaks


    def _q(lattice, h, k, l):
        "Returns q from (h, k, l) parameters"
        rb= lattice.recbase
        q = 2*np.pi*(h*rb[0] + k*rb[1] + l*rb[2])
        return np.sqrt(np.dot(q,q))




    lattice = material.lattice
    lines_for_peaks = []
    qs = []
    for p in peaks:
        F2 = np.abs(p.F)**2/100
        mul = p.mult
        h,k,l = p.hkl
        q = _q(lattice, h,k,l)
        qs.append(q)
        line = "Peak(q=%(q)s, F_squared=%(F2)s, multiplicity=%(mul)s, intrinsic_line_width=0, DebyeWaller_factor=0)," % locals()
        lines_for_peaks.append(line)
        continue

    lines_for_peaks = [l for (q, l) in sorted(zip(qs, lines_for_peaks))]

    lines_for_peaks = '\n'.join('    '+l for l in lines_for_peaks)




    unitcell_volume = lattice.volume


    abs_xs = xsc.abs_xs_at2200




    content = '''from mccomponents.sample.diffraction.SimplePowderDiffractionKernel import Peak
    
    peaks = [
    %(lines_for_peaks)s
        ]
    
    # unit: \AA
    unitcell_volume = %(unitcell_volume)s
    
    # unit: barns
    class cross_sections:
        coh = 0
        inc = 0
        abs = %(abs_xs)s
    ''' % locals()

    with open('{sample}_peaks.py'.format(sample=sample), 'wt') as s:
        s.write(content)
    return()



