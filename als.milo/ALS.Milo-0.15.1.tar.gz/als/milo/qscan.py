#!/usr/bin/env python

"""qscan.py

    Functions to build RSM scans for ALS BL402
    *) Generate diffractometer motor positions vs. (q, hv, polarization)
    *) BCS scan file format, motor headers used by ALS beamline 4.0.2
    *) BCS = Beamline Control Systems; ALS = Advanced Light Source
"""

__author__ = "Padraic Shafer"
__copyright__ = "Copyright (c) 2018-2019, Padraic Shafer"
__credits__ = [__author__, ]
__license__ = ""
__maintainer__ = "Padraic Shafer"
__email__ = "PShafer@lbl.gov"
__status__ = "Development"

import logging
import sys
import os
from collections import namedtuple

import numpy as np
import pandas as pd
# from .qimage import Diffractometer402, Polarization
# from .qimage import QSpacePath, ResonanceProfile
from als.milo.qimage import Diffractometer402, Polarization
from als.milo.qimage import QSpacePath, ResonanceProfile

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    DATA STRUCTURES    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# class OrthoLatticeABC:
#   *) Assumes orthorhombic lattice; c // z;
#   *) (a, b) have azimuthal rotation from (x, y), defined by 'offsets.azimuth'
#   *) Fine tuning of lattice relative to diffractometer achieved by 'offsets'
OrthoLatticeABC = namedtuple("OrthoLatticeABC", ['a', 'b', 'c', "offsets"])

# class AngleOffsets:
#   *) Corrections to alignment angle offsets,
#       determined by manual alignment of model to data
AngleOffsets = namedtuple(
    "AngleOffsets", ["incidence", "transverse", "azimuth"])

# class HKL:
#   *) Relative coordinates of reciprocal space vector
HKL = namedtuple("HKL", ['h', 'k', 'L'])

# class Defaults:
#   *) Default values used internally by functions in this script
Defaults = namedtuple("Defaults", ["output_dir"])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class OrthoReciprocalLatticeQabc(object):

    """Reciprocal lattice vectors (qa, qb, qc) for lattice vectors (a, b, c)

        *) Assumes orthorhombic lattice; c // z;
        *) (a, b) have azimuthal rotation from (x, y) defined in 'offsets'
        *) qa = 2*pi/a (parallel to a)
        *) qb = 2*pi/b (parallel to b)
        *) qc = 2*pi/c (parallel to c)
    """

    def __init__(self, lattice, **keywords):
        """Initialize reciprocal lattice from OrthoLatticeABC
        """

        # The following assignments can be consolidated using self.lattice?
        # self.a = lattice.a
        # self.b = lattice.b
        # self.c = lattice.c
        # self.offsets = lattice.offsets

        self.lattice = lattice

        # The following assignments are redundant?
        # self.qa = 2*np.pi / self.a
        # self.qb = 2*np.pi / self.b
        # self.qc = 2*np.pi / self.c

    @property
    def lattice(self):
        """Returns a OrthoLatticeABC object"""
        return OrthoLatticeABC(
            a = self._a,
            b = self._b,
            c = self._c,
            offsets = self._offsets,
            )

    @lattice.setter
    def lattice(self, lattice_obj):
        # Does not check for valid value
        self.a = lattice_obj.a
        self.b = lattice_obj.b
        self.c = lattice_obj.c
        self.offsets = lattice_obj.offsets
        return lattice_obj

    @property
    def offsets(self):
        """Access the lattice angle offsets (in degrees)"""
        return self._offsets

    @offsets.setter
    def offsets(self, value):
        # Does not check for valid value
        self._offsets = value
        return value

    @property
    def a(self):
        """Access the lattice parameter, a (in nm)"""
        return self._a

    @a.setter
    def a(self, value):
        # Does not check for valid value
        self._a = value
        self._qa = 2 * np.pi / self._a
        return value

    @property
    def b(self):
        """Access the lattice parameter, b (in nm)"""
        return self._b

    @b.setter
    def b(self, value):
        # Does not check for valid value
        self._b = value
        self._qb = 2 * np.pi / self._b
        return value

    @property
    def c(self):
        """Access the lattice parameter, c (in nm)"""
        return self._c

    @c.setter
    def c(self, value):
        # Does not check for valid value
        self._c = value
        self._qc = 2 * np.pi / self._c
        return value

    @property
    def qa(self):
        """Access the lattice parameter, qa (in nm)"""
        return self._qa

    @qa.setter
    def qa(self, value):
        # Does not check for valid value
        self._qa = value
        self._a = 2 * np.pi / self._qa
        return value

    @property
    def qb(self):
        """Access the lattice parameter, qb (in nm)"""
        return self._qb

    @qb.setter
    def qb(self, value):
        # Does not check for valid value
        self._qb = value
        self._b = 2 * np.pi / self._qb
        return value

    @property
    def qc(self):
        """Access the lattice parameter, qc (in nm)"""
        return self._qc

    @qc.setter
    def qc(self, value):
        # Does not check for valid value
        self._qc = value
        self._c = 2 * np.pi / self._qc
        return value

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class OrthoReciprocalVector(object):

    """Reciprocal space vector (qa, qb, qc) for lattice vectors (a, b, c)

        *) Assumes orthorhombic lattice; c // z;
        *) (a, b) have azimuthal rotation from (x, y) defined in 'offsets'
        *) qa = h * rlattice.qa; rlattice.qa = 2*pi/a (parallel to a)
        *) qb = k * rlattice.qb; rlattice.qb = 2*pi/b (parallel to b)
        *) qc = L * rlattice.qc; rlattice.qc = 2*pi/c (parallel to c)
    """

    def __init__(self, lattice, qa=0, qb=0, qc=0, **keywords):
        """Initialize reciprocal space vector from OrthoLatticeABC
        """

        self._rlattice = OrthoReciprocalLatticeQabc(lattice)

        self.qa = qa
        self.qb = qb
        self.qc = qc

    @classmethod
    def fromQabc(cls, lattice, qa=0, qb=0, qc=0, **keywords):
        """Initialize reciprocal space vector using (qa, qb, qc)
        """
        return cls(lattice, qa, qb, qc, **keywords)

    @classmethod
    def fromHKL(cls, lattice, h=0, k=0, L=0, **keywords):
        """Initialize reciprocal space vector using (h, k, L)
        """
        rlattice = OrthoReciprocalLatticeQabc(lattice)
        qa = h * rlattice.qa
        qb = k * rlattice.qb
        qc = L * rlattice.qc
        return cls(lattice, qa, qb, qc, **keywords)

    @property
    def rlattice(self):
        """Access OrthoReciprocalLatticeQabc object"""
        return self._rlattice

    @rlattice.setter
    def rlattice(self, rlattice_obj):
        # Does not check for valid value
        self._rlattice = rlattice_obj
        self._h = self._qa / rlattice_obj.qa
        self._k = self._qb / rlattice_obj.qb
        self._L = self._qc / rlattice_obj.qc
        return value

    @property
    def h(self):
        """Access the relative reciprocal vector, h (in rlu)"""
        return self._h

    @h.setter
    def h(self, value):
        # Does not check for valid value
        self._h = value
        self._qa = self._h * rlattice_obj.qa
        return value

    @property
    def k(self):
        """Access the relative reciprocal vector, k (in rlu)"""
        return self._k

    @k.setter
    def k(self, value):
        # Does not check for valid value
        self._k = value
        self._qb = self._k * rlattice_obj.qb
        return value

    @property
    def L(self):
        """Access the relative reciprocal vector, L (in rlu)"""
        return self._L

    @L.setter
    def L(self, value):
        # Does not check for valid value
        self._L = value
        self._qc = self._L * rlattice_obj.qc
        return value

    @property
    def qa(self):
        """Access the absolute reciprocal vector, qa (in nm)"""
        return self._qa

    @qa.setter
    def qa(self, value):
        # Does not check for valid value
        self._qa = value
        self._h = self._qa / self._rlattice.qa
        return value

    @property
    def qb(self):
        """Access the absolute reciprocal vector, qb (in nm)"""
        return self._qb

    @qb.setter
    def qb(self, value):
        # Does not check for valid value
        self._qb = value
        self._k = self._qb / self._rlattice.qb
        return value

    @property
    def qc(self):
        """Access the absolute reciprocal vector, qc (in nm)"""
        return self._qc

    @qc.setter
    def qc(self, value):
        # Does not check for valid value
        self._qc = value
        self._L = self._qc / self._rlattice.qc
        return value

    def hkL(self):
        return(self.h, self.k, self.L)

    def qABC(self):
        return(self.qa, self.qb, self.qc)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    GLOBALS    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# __defaults__ = Defaults(
#     output_dir=os.getcwd(),
#     )

__default_output_dir = os.getcwd()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_default_chamber_params():
    """Get dict() of suitable default_chamber_params that can be customized.

        RETURNS: Copy of Diffractometer402.default_chamber_params
    """

    return(Diffractometer402.default_chamber_params.copy())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def set_output_dir(format, **kwargs):
    """Sets default output directory using supplied format and keyword params.

        format: Format string for output directory using keywords;
            *) {base}/... is implied
        kwargs: (keyword = value) pairs for keywords used in 'format'

        RETURNS: Generated output directory as string

        !!! Side Effects !!!
            *) generated directory is created if it does not already exist
            *) generated directory is set as global __defaults__.output_dir
    """

    global __default_output_dir

    if not format.startswith("{base}"):
       format = "{base}/" + format

    output_dir = format.format(**kwargs)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    __default_output_dir = output_dir

    return(output_dir)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_output_dir():
    """Gets default output path.

        RETURNS: global __defaults__.output_dir
    """

    global __default_output_dir

    return(__default_output_dir)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_scan_header_line_number(scan_file_path):
    """Extract line number of motor headers from scan file.

        scan_file_path: Fully qualified path (dir + file) of scan file.

        RETURNS: Zero-based line number of motor header row.
            -1 = Not found
    """

    with open(scan_file_path, 'r') as scan_file:
        for (header_linenum, file_line) in enumerate(scan_file):

            logging.debug(header_linenum, file_line)

            if file_line[0].isdigit() or file_line.lower().startswith("file"):
                header_linenum -= 1
                return(header_linenum)

    return(-1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def import_scan_file(scan_file_path):
    """Import motor positions from scan file into PANDAS DataFrame.

        scan_file_path: Fully qualified path (dir + file) of scan file.

        RETURNS: PANDAS DataFrame of imported motor positions
    """

    header_linenum = get_scan_header_line_number(scan_file_path)

    df = pd.read_table(
        scan_file_path,
        delimiter='\t',
        header=header_linenum,
        skip_blank_lines=False,
        )

    return(df)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calculate_qABC(df, diffractometer=None, inplace=False):
    """Calculate (qa, qb, qc) for PANDAS DataFrame.

        df: PANDAS DataFrame containing motor positions.
        diffractometer: Diffractometer402 object for interpreting motor values.
        inplace: False = returns copy of df; True = returns original df.

        RETURNS: PANDAS DataFrame with additional (qa, qb, qc) columns
    """

    if inplace:
        df_new = df
    else:
        df_new = df.copy()

    df_new["qa"] = np.nan
    df_new["qb"] = np.nan
    df_new["qc"] = np.nan

    if diffractometer is None:
        diffractometer = Diffractometer402(
            param_dict=get_default_chamber_params(),
            )

    if "Beamline Energy" in df_new.columns:
        energy_col = "Beamline Energy"
    elif "Mono Energy" in df_new.columns:
        energy_col = "Mono Energy"
    else:
        logging.error("Energy column not found in DataFrame")

    if "EPU Polarization" in df_new.columns:
        pol_col = "EPU Polarization"
    else:
        pol_col = None

    if "Flip Position" in df_new.columns:
        flip_col = "Flip Position"
    elif "Flip" in df_new.columns:
        flip_col = "Flip"
    else:
        logging.error("Flip column not found in DataFrame")

    if "Top Offset" in df_new.columns:
        offset_top_col = "Top Offset"
    else:
        offset_top_col = None

    if "Flip Offset" in df_new.columns:
        offset_flip_col = "Flip Offset"
    else:
        offset_flip_col = None

    if "I0 BL" in df_new.columns:
        i0_col = "I0 BL"
    elif "Counter 2" in df_new.columns:
        i0_col = "Counter 2"
    else:
        i0_col = None

    detector = diffractometer.detector
    azimuth = diffractometer.azimuth

    for (i, row) in df_new.iterrows():

        if pol_col is None:
            pol_value = diffractometer.polarization.value
        else:
            pol_value = row[pol_col]

        if offset_top_col is None:
            offset_top = diffractometer.offset_top
        else:
            offset_top = row[offset_top_col]

        if offset_flip_col is None:
            offset_flip = diffractometer.offset_flip
        else:
            offset_flip = row[offset_flip_col]

        if i0_col is None:
            i0_value = 1.
        else:
            i0_value = row[i0_col]

        diffractometer_params = get_default_chamber_params()
        diffractometer_params_new = dict({
            "Beamline Energy": row[energy_col],
            "EPU Polarization": pol_value,
            "Bottom Rotary Seal": row["Bottom Rotary Seal"],
            "Top Rotary Seal": row["Top Rotary Seal"],
            "Flip": row[flip_col],
            "Azimuth": azimuth,
            "Top Offset": offset_top,
            "Flip Offset": offset_flip,
            "I0 BL": i0_value,
            "Detector Mode": detector,
            })
        diffractometer_params = dict(
            diffractometer_params.items() + diffractometer_params_new.items()
            )
        diffractometer = Diffractometer402(diffractometer_params)
        
        if pol_col is not None:
            diffractometer.polarization.value = row[pol_col]

        # q_magnitude = 2 * q_photon * sin(twotheta / 2)
        # (!) q_magnitude can be < 0 (if twotheta < 0)
        q_magnitude = 2 * diffractometer.photon.q * np.sin(
            np.deg2rad(diffractometer.twotheta / 2.)
            )
        # if (q_c > 0) and (q_a > 0) --> (incidence > (twotheta / 2))
        # if (q_c < 0) and (q_a < 0) --> (incidence > (twotheta / 2))
        angle_qa_from_qbc = (
            diffractometer.incidence - (diffractometer.twotheta / 2.)
            )
        angle_qa_from_qbc_radians = np.deg2rad(angle_qa_from_qbc)
        q_a = q_magnitude * np.sin(angle_qa_from_qbc_radians)
        # (!) q_bc can be < 0 (if twotheta < 0)
        q_bc = q_magnitude * np.cos(angle_qa_from_qbc_radians)
        transverse_radians = np.deg2rad(diffractometer.transverse)
        # if (q_c > 0) and (q_b > 0) --> (transverse > 0)
        # if (q_c < 0) and (q_b < 0) --> (transverse > 0)
        q_b = q_bc * np.sin(transverse_radians)
        # sign(q_c) == sign(twotheta)
        q_c = q_bc * np.cos(transverse_radians)

        df_new.loc[i, "qa"] = q_a
        df_new.loc[i, "qb"] = q_b
        df_new.loc[i, "qc"] = q_c

        logging.info("Index: {0:d}".format(i))
        logging.info("\ttwotheta: {0:0.3f}".format(diffractometer.twotheta))
        logging.info("\tincidence: {0:0.3f}".format(diffractometer.incidence))
        logging.info("\ttransverse: {0:0.3f}".format(diffractometer.transverse))
        logging.info("\tq_a: {0:0.3f}".format(q_a))
        logging.info("\tq_b: {0:0.3f}".format(q_b))
        logging.info("\tq_c: {0:0.3f}".format(q_c))
        logging.info("\tq_bc: {0:0.3f}".format(q_bc))
        logging.info("\tangle_qx_from_qyz: {0:0.3f}".format(angle_qa_from_qbc))

    return(df_new)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calculate_hkl(df, lattice, inplace=False):
    """Calculate (h, k, L) for PANDAS DataFrame.

        df: PANDAS DataFrame containing (qa, qb, qc) positions.
        lattice: OrthoLatticeABC object.
        inplace: False = returns copy of df; True = returns original df.

        RETURNS: PANDAS DataFrame with additional (h, k, L) columns
    """

    if inplace:
        df_new = df
    else:
        df_new = df.copy()

    if ( ("qa" not in df_new.columns)
            or ("qb" not in df_new.columns)
            or ("qc" not in df_new.columns)
            ):
        logging.error("DataFrame must contain (qa, qb, qc) columns")

    df_new["h"] = np.nan
    df_new["k"] = np.nan
    df_new["L"] = np.nan

    for (i, row) in df_new.iterrows():

        rlattice = OrthoReciprocalVector.fromQabc(
            lattice, row["qa"], row["qb"], row["qc"])

        df_new.loc[i, "h"] = rlattice.h
        df_new.loc[i, "k"] = rlattice.k
        df_new.loc[i, "L"] = rlattice.L

    return(df_new)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def make_hkl_scan(
        lattice, hkl_start, hkl_stop=None, nsteps=None, diffract_params=None,
        output_dir=None, output_file_base=None, output_file_ext=".scn",
        export_energy=True, export_polarization=False,
        **kwargs
        ):
    """Generate a motor scan file for a linear path through reciprocal space.

        lattice: OrthoLatticeABC object
        hkl_start: Starting (h,k,L) of linear path through reciprocal space
        hkl_stop: Final (h,k,L) of linear path through reciprocal space
            *) DEFAULT: hkl_start
        nsteps: Number of steps along linear path through reciprocal space
            *) DEFAULT: either 1 (hkl_stop == hkl_start), or else 2 steps
        diffract_params: Motor settings for Diffractometer402 object
            *) DEFAULT: Diffractometer402.default_chamber_params
        output_dir: Directory path for motor scan file
            *) DEFAULT: global __defaults__.output_path
        output_file_base: File base name for motor scan file
            *) DEFAULT: verbose informative file name
        output_file_ext: File extension for motor scan file
        export_energy: If True, scan file contains x-ray energy
        export_polarization: If True, scan file contains x-ray polarization

        RETURNS: PANDAS DataFrame containing scan meta information

        !!! Side Effects !!!
            *) output_dir is created if it does not already exist
            *) motor scan file is created at specified path
    """

    if hkl_stop is None:
        hkl_stop = hkl_start

    if nsteps is None:
        if hkl_stop == hkl_start:
            nsteps = 1
        else:
            nsteps = 2

    q_start = OrthoReciprocalVector.fromHKL(lattice, **hkl_start._asdict())
    q_stop = OrthoReciprocalVector.fromHKL(lattice, **hkl_stop._asdict())

    if diffract_params is None:
        diffract_params = get_default_chamber_params()

    diffractometer = Diffractometer402(
        param_dict=diffract_params,
        )

    energy = diffractometer.energy
    polarization = diffractometer.polarization

    if (polarization.state == Polarization.LINEAR):
        pol_format = "{:0.0f}"
    else:
        pol_format = "{:+0.2f}"

    offset_angles = Diffractometer402(
        param_dict=get_default_chamber_params(),
        )
    offset_angles.incidence = lattice.offsets.incidence
    offset_angles.transverse = lattice.offsets.transverse
    offset_angles.azimuth = lattice.offsets.azimuth

    qpath = QSpacePath(
        diffractometer=diffractometer,
        offset_diffractometer=offset_angles)

    qpath.lin_path(
        np.array(q_start.qABC()),
        np.array(q_stop.qABC()),
        nsteps
        )

    if output_dir is None:
        output_dir = get_output_dir()

    if output_file_base is None:
        output_file_base = "{name}_phi{azim}_{temp}K"
        if export_energy:
            output_file_base += "_{hv}eV"
        if export_polarization:
            output_file_base += "_pol{pol}"
        output_file_base += "__{h0}_{k0}_{L0}__{hN}_{kN}_{LN}"

    output_file_path = "{dir}{file_base}{ext}".format(
        dir = output_dir,
        file_base = output_file_base,
        ext = output_file_ext,
        ).format(
            azim = "{:+0.1f}".format(lattice.offsets.azimuth),
            hv = "{:0.1f}".format(energy),
            pol = pol_format.format(polarization.value),
            h0 = "H{:+0.2f}".format(q_start.h),
            k0 = "K{:+0.2f}".format(q_start.k),
            L0 = "L{:+0.2f}".format(q_start.L),
            hkL0 = "H{:+0.2f}_K{:+0.2f}_L{:+0.2f}".format(*q_start.hkL()),
            hN = "H{:+0.2f}".format(q_stop.h),
            kN = "K{:+0.2f}".format(q_stop.k),
            LN = "L{:+0.2f}".format(q_stop.L),
            hkLN = "H{:+0.2f}_K{:+0.2f}_L{:+0.2f}".format(*q_stop.hkL()),
            **kwargs
        )
    qpath.export_scanfile(
        output_file_path,
        export_energy=export_energy,
        export_polarization=export_polarization)

    df = import_scan_file(output_file_path)

    if ( ("Beamline Energy" not in df.columns)
            and ("Mono Energy" not in df.columns)
            and ("EPU Energy" not in df.columns)
            ):
        df["Mono Energy"] = energy
        df["EPU Energy"] = energy

    calculate_qABC(df, diffractometer=diffractometer, inplace=True)
    logging.info("Q values calculated from scan file {}:\n{}".format(
            output_file_path,
            df,
            )
        )

    calculate_hkl(df, lattice=lattice, inplace=True)
    logging.info("RLU values calculated from scan file {}:\n{}".format(
            output_file_path,
            df,
            )
        )
    
    df.to_csv(
        "{path_base}_HKL{ext}".format(
            path_base = output_file_path.split(output_file_ext)[0],
            ext = output_file_ext,
            ), 
        sep = '\t', 
        index = False, 
        # line_terminator = "\r\n", 
        line_terminator = "\n", 
        )

    return(df)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def make_constQ_energy_scan(
        lattice, hkl_point, energy_values, diffract_params=None,
        output_dir=None, output_file_base=None, output_file_ext=".scn",
        polarizations = None, alternate_polarization = False, 
        export_polarization=True,
        **kwargs
        ):
    """Generate a motor scan file for a linear path through reciprocal space.

        lattice: OrthoLatticeABC object
        hkl_point: Constant (h,k,L) indices of reciprocal space vector
        energy_values: Ordered list of x-ray energy values to use for scan
        diffract_params: Motor settings for Diffractometer402 object
            *) DEFAULT: Diffractometer402.default_chamber_params
        output_dir: Directory path for motor scan file
            *) DEFAULT: global __defaults__.output_path
        output_file_base: File base name for motor scan file
            *) DEFAULT: verbose informative file name
        output_file_ext: File extension for motor scan file
        polarizations: Ordered list of polarization values to use for scan
        alternate_polarization: If True, x-ray polarization alternates
            ... between supplied values for each x-ray energy;
            If False, polarization changes for each subsequent energy sub-scan
        export_polarization: If True, scan file contains x-ray polarization

        RETURNS: PANDAS DataFrame containing scan meta information

        !!! Side Effects !!!
            *) output_dir is created if it does not already exist
            *) motor scan file is created at specified path
    """

    q_point = OrthoReciprocalVector.fromHKL(lattice, **hkl_point._asdict())

    if diffract_params is None:
        diffract_params = get_default_chamber_params()

    diffractometer = Diffractometer402(
        param_dict=diffract_params,
        )

    offset_angles = Diffractometer402(
        param_dict=get_default_chamber_params(),
        )
    offset_angles.incidence = lattice.offsets.incidence
    offset_angles.transverse = lattice.offsets.transverse
    offset_angles.azimuth = lattice.offsets.azimuth

    res_profile = ResonanceProfile(
        np.array(q_point.qABC()), 
        diffractometer=diffractometer, 
        offset_diffractometer=offset_angles)

    res_profile.new_spectrum(energy_values)

    if output_dir is None:
        output_dir = get_output_dir()

    if output_file_base is None:
        output_file_base = "{name}_phi{azim}_{temp}K"
        output_file_base += "_{h0}_{k0}_{L0}"

    output_file_path = "{dir}{file_base}{ext}".format(
        dir = output_dir,
        file_base = output_file_base,
        ext = output_file_ext,
        ).format(
            azim = "{:+0.1f}".format(lattice.offsets.azimuth),
            h0 = "H{:+0.2f}".format(q_point.h),
            k0 = "K{:+0.2f}".format(q_point.k),
            L0 = "L{:+0.2f}".format(q_point.L),
            hkL0 = "H{:+0.2f}_K{:+0.2f}_L{:+0.2f}".format(*q_point.hkL()),
            **kwargs
        )
    
    res_profile.export_scanfile(
        output_file_path, 
        polarizations = polarizations, 
        alternate_polarization = alternate_polarization)

    return

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main(args=None):
    """The main routine."""

    if args is None:
        args = sys.argv[1:]

    for arg in args:
        # if arg.lower() == "--version":
        #     print __version__
        pass

    print "Usage details"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    main()
