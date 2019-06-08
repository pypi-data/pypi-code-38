import logging
import os
import struct

import numpy as np
from scipy import ndimage

from .util import Structure, from_buffer


LOGGER = logging.getLogger(__name__)
ANALYSIS_TYPES = {
    21: 'DEPTH',
    22: 'LINESCAN',
    26: 'ISOTOP',
    27: 'IMAGE',
    29: 'GRAIN MODE IMAGE',
    30: 'GRAIN MODE ISOTOP',
    39: 'BEAM_CTRL_NANO_IMA',
    40: 'BEAM_CTRL_NANO_LINESCAN',
    41: 'IMAGE_SAMPLE_STAGE',
}


def load_mims(filename, byte_order=None, roll_data=True):
    """
    Load a multi-isotope imaging mass spectrometry (MIMS) file.

    Parameters
    ----------
    filename : str
        path to the MIMS file
    byte_order : str
        byte order of the encoded binary data
    roll_data : bool
        whether to roll image data along the last two dimenions. Rolling the image fixes an issue
        with Cameca's encoding of pixel positions.

    Returns
    -------
    mims :
        multi-isotope imaging mass spectrometry (MIMS) data
    """
    mims = Structure()
    stat = os.stat(filename)

    with open(filename, 'rb') as fp:
        # Load the header
        mims['def_analysis'] = Def_analysis.from_buffer(fp, byte_order)
        try:
            analysis_type = ANALYSIS_TYPES[mims.def_analysis.analysis_type]
        except KeyError:  # pragma: no cover
            raise ValueError(f"Found unrecognised analysis type {mims.def_analysis.analysis_type} "
                             f"(expected one of {list(ANALYSIS_TYPES)}). Did you use the correct "
                             "byte order?")

        if analysis_type == 'IMAGE':
            mims['mask_im'] = Mask_im.from_buffer(fp, byte_order)
            mims['tab_mass'] = [Tab_mass.from_buffer(fp, byte_order) for _ in range(mims.mask_im.nb_mass)]
            mims['cal_cond'] = [Cal_cond.from_buffer(fp, byte_order) for _ in range(mims.mask_im.nb_mass)]
            mims['poly_list'] = Poly_list.from_buffer(fp, byte_order)
            mims['polyatomique'] = [Polyatomique.from_buffer(fp, byte_order) for _ in range(mims.poly_list.nb_poly)]
            mims['mask_nano'] = Mask_nano.from_buffer(fp, byte_order)
            mims['tab_Bfield_nano'] = [Tab_BField_nano.from_buffer(fp, byte_order) for _ in range(mims.mask_nano.m_nNbBField)]

            # Consume 288 dummy bytes (no idea where they come from)
            _ = fp.read(288)

            mims['anal_param_nano'] = Anal_param_nano.from_buffer(fp, byte_order)
            mims['def_analysis_bis'] = Def_analysis_bis.from_buffer(fp, byte_order)

            # Read dummy content
            mims['_anal_param'] = fp.read(416)
            mims['_setup_soft'] = fp.read(376)

            mims['anal_param_nano_bis'] = Anal_param_nano_bis.from_buffer(fp, byte_order)
            mims['header_image'] = Header_image.from_buffer(fp, byte_order)

            assert fp.tell() == mims.def_analysis.hdr_usr, \
                f"read {fp.tell()} bytes (expected {mims.def_analysis.hdr_usr})"

            fmt = f'int[{mims.mask_im.cycle_number}, {mims.header_image.n}, ' \
                f'{mims.header_image.w}, {mims.header_image.h}]'

            mims['data'] = from_buffer(fmt, fp, byte_order)
            if roll_data:
                mims['data'] = np.roll(mims['data'], 1, axis=(2, 3))
        else:  # pragma: no cover
            raise NotImplementedError(f"{analysis_type} is not implemented")

        assert fp.tell() == stat.st_size, f"consumed {fp.tell()} bytes (expected {stat.st_size})"
        return mims


class Def_analysis(Structure):
    __size__ = 124
    __fields__ = [
        ('release', 'int'),  # data release number
        ('analysis_type', 'int'),  # 21=DEPTH, 22=LINESCAN, 26=ISOTOP, 27=IMAGE, 29=GRAIN MODE IMAGE, 30=GRAIN MODE ISOTOP, 39=BEAM_CTRL_NANO_IMA, 40=BEAM_CTRL_NANO_LINESCAN, 41=IMAGE_SAMPLE_STAGE
        ('hdr_usr', 'int'),  # header size
        ('sample_type', 'int'),  # sample type
        ('data_present', 'int'),  # data include 0:NO/1:YES
        ('sple_pos_x', 'int'),  # sample position X in micron
        ('sple_pos_y', 'int'),  # sample position Y in micron
        ('analysis_name', '32str'),  # analysis name
        ('username', '16str'),  # user name
        ('nSamplePosz', 'int'),  # sample position Z en micron
        ('nUnused', 'int[3]'),  # libre
        ('date', '16str'),  # date
        ('heure', '16str'),  # hour
    ]


class Tab_elts(Structure):
    """It contains elements information."""
    __size__ = 12
    __fields__ = [
        ('num_elt', 'int'),  # Element number [1..103]
        ('num_isotop', 'int'),  # Isotop mumber [0..]
        ('quantite', 'int'),  # Number of element
    ]


class Polyatomique(Structure):
    """It contains polyatomic information."""
    __size__ = 144
    __fields__ = [
        ('Flag_chiffre', 'int'),  # 1=Number / 0=Element
        ('chiffre', 'int'),  # Number
        ('nb_elts', 'int'),  # Number of elements in the polyatomic
        ('nb_charges', 'int'),  # Number of loading (0=none , 1=+, 2=++
        ('charge', 'char'),  # Loading '+'/'-'
        ('string', '64str'),  # Polyatomique sting
        ('tab_elts', (Tab_elts, 5)),  # composed element table
        ('_not_in_spec', '3str'),  # cf. https://github.com/BWHCNI/OpenMIMS/blob/de0bfcf3c0d7c515571f5fb1e7a5c74177660a61/src/main/java/com/nrims/data/Mims_Reader.java#L329
    ]


class Def_eps(Structure):
    """It contains IMS EPS definition information."""
    __size__ = 312

    __fields__ = [
        ('central_energy', 'int'),
        ('field', 'int'),  # central mass b field
        ('central_mass', Polyatomique),  # central mass
        ('reference_mass', Polyatomique),  # reference mass
        ('tens_tube', 'double'),  # of the reference mass
        ('max_var_tens_tube', 'double'),
    ]


class Def_analysis_bis(Structure):
    __size__ = 2048
    __fields__ = [
        ('magic', 'int'),  # Magic number = MAGIC_DEFB=2306
        ('release', 'int'),  # Version = RELEASE_DEFB=1
        ('filename', '256str'),  # file name
        ('matrice', '256str'),  # matrix name
        ('sigref_mode', 'int'),  # 0: manual 1: auto
        ('sigref_nbptsdm', 'int'),  # sigref auto nbpts deltam
        ('sigref_nbdm', 'int'),  # sigref auto nb deltam
        ('sigref_ct_scan', 'int'),  # scanning count tim x 0,1sec
        ('sigref_ct_meas', 'int'),  # measuring count tim sec
        ('sigref_tps_pulve', 'int'),  # time beam=ON during sigref

        ('eps_recentrage', 'int'),  # EPS Centering 0=NO/1=YES
        ('eps_flag', 'int'),  # EPS 0=NO/ 1=YES
        ('eps', Def_eps),  # IMS peak switching

        ('sple_rot_flag', 'int'),  # sample rotation 0=NO/ 1=YES
        ('sple_rot_speed', 'int'),  # rot speed tr/mn
        ('sple_rot_acq_sync', 'int'),  # 0:no 1:yes

        ('sample_name', '80str'),  # sample name

        ('experience', '32str'),  # experience name
        ('method', '32str'),  # method name

        ('no_used', '1028str'),
    ]

    def validate(self):
        assert self.magic == 2306
        super(Def_analysis_bis, self).validate()


class AutoCal(Structure):
    """It contains mass calibration information."""
    __size__ = 72
    __fields__ = [
        ('masse', '64str'),  # mass reference included in tab_mass
        ('debut', 'int'),  # beginning cycle number of calib
        ('periode', 'int'),  # ending cycle number of calib
    ]


class SigRef(Structure):
    """It contains reference signal information."""
    __size__ = 156

    __fields__ = [
        ('poly', Polyatomique),  # Polyatomique , mass reference
        ('detecteur', 'int'),  # EM / FC
        ('offset', 'int'),  # offset applied to mass
        ('quantite', 'int'),  # counts /sec
    ]


class Mask_im(Structure):
    __size__ = 528
    __fields__ = [
        ('filename', '16str'),
        ('anal_duration', 'int'),  # en mn , arrondir  calculee
        ('cycle_number', 'int'),  # nb de points
        ('scantype', 'int'),  # 0: SEI/SII 1: RAE   2:  CCD
        ('magnification', 'WORD'),  # pour CCD et RAE
        ('sizetype', 'WORD'),  # 0:256x256 1:512x512 2:1024x1024
        ('size_detecteur', 'WORD'),  # pour CCD et RAE
        ('no_used', 'WORD'),  #
        ('beam_blanking', 'int'),  # 0: NO    1: YES
        ('pulverisation', 'int'),  # 0: NO    1: YES
        ('pulve_duration', 'int'),  # en sec
        ('auto_cal_in_anal', 'int'),  # 0:NO        1:YES
        ('autocal', AutoCal),  # param mass calibration
        ('sig_reference', 'int'),  # NO/ YES
        ('sigref', SigRef),  # param du signal de reference
        ('nb_mass', 'int'),  # nombre de masse
        ('tab_mass', 'int[60]'), # Tab_mass *tab_mass[60];    /* tableau des masses */
    ]

    def validate(self):
        assert self.nb_mass >= 0
        self['tab_mass'] = self.tab_mass[:self.nb_mass]
        super(Mask_im, self).validate()


class Mask_dp(Structure):
    """
    It contains isotop acquisition information.
    """
    __size__ = 672
    __fields__ = [
        ('unit_mode', 'int'),  # 0:min  1:sec  2:cycles
        ('unused_0', 'int'),  #
        ('sigRefMulti', 'SigRefMulti'),  # Multi signal reference
        ('unused_1', 'int'),  #

        ('mode_saisie', 'int'),  # 0: total duration / 1: cycle duration
        ('anal_duration', 'int'),  # en sec , arrondir  calculee
        ('cycle_number', 'int'),  # nb de points
        ('beam_blanking', 'int'),  # 0: NO    1: YES
        ('pulverisation', 'int'),  # 0: NO    1: YES
        ('pulve_duration', 'int'),  # en sec
        ('auto_cal_in_anal', 'int'),  # 0:NO        1:YES
        ('autocal', 'AutoCal'),  # param mass calibration
        ('hv_sple_control', 'int'),  # no / YES
        ('hvcontrol', 'HvCont'),  # param de HV control
        ('sig_reference', 'int'),  # NO/ YES
        ('sigref', 'SigRef'),  # param signal reference
        ('multisize_crater', 'int'),  # 0:NO        1:YES
        ('crater', 'Crater'),  # param multisize crater
        ('nb_mass', 'int'),  # nombre de masse
        ('tab_mass', 'int[60]'), # Tab_mass *tab_mass[60];    /* tableau des masses */
    ]


class Mask_ls(Structure):
    """
    It contains linescan acquisition information.
    """
    __size__ = 504
    __fields__ = [
        ('filename', '16str'),
        ('anal_duration', 'int'),
        ('type', 'int'),  # 0: SAMPLE_SCAN (5F), 1: BEAM_SCAN (7F), 2: IMAGE_SCAN (N50)
        ('nb_zones', 'int'),  # nombre de pas 29.3.94 (zones avant)
        ('step_unit_x', 'int'),  # x step unit , microns
        ('step_unit_y', 'int'),  # y step unit , microns
        ('step_reel_d', 'int'),  # distance between 2 zones
        ('wt_int_zones', 'double'),  # waiting time between 2 zones

        ('nNbCycle', 'int'),  # Number of cyccle

        ('beam_blanking', 'int'),  # 0: NO    1: YES
        ('pulverisation', 'int'),  # 0: NO    1: YES
        ('pulve_duration', 'int'),  # en mn
        ('auto_cal_in_anal', 'int'),  # 0:NO        1:YES
        ('autocal', 'AutoCal'),  # param mass calibration
        ('hv_sple_control', 'int'),  # no / YES
        ('hvcontrol', 'HvCont'),  # param de HV control
        ('sig_reference', 'int'),  # NO/ YES
        ('sigref', 'SigRef'),  # param du signal de reference

        ('nb_mass', 'int'),  # nombre de masse
        ('tab_mass', 'int[20]'),# Tab_mass *tab_mass[ 20 ] ;    /* tableau des masses */
    ]


class E0S_Nano(Structure):
    """It contains the E0S Centering parameter information."""

    __size__ = 32
    __fields__ = [
        # E0S Centering Acquisition */
        ('m_nDetId', 'int'),  # Detector Id (-1 If none)
        ('m_nStartDac', 'int'),  # Start DAC
        ('m_nDacStep', 'int'),  # Dac step
        # For E0S Centering */
        ('m_nE0SCentCountTime', 'int'),  # Counting Time per point multiple of 10ms
        ('m_dStartValue', 'double'),  # Start value
        ('m_d80PerCentWidth', 'double'),  # 80% Width in Volts
    ]


class Energy_Nano(Structure):
    """It contains the Energy Centering parameter information."""
    __size__ = 40

    __fields__ = [
        # Energy Acquisition */
        ('m_nDetId', 'int'),  # Detector Id (-1 If none)
        ('m_nStartDac', 'int'),  # Start DAC
        ('m_nDacStep', 'int'),  # Dac step

        ('m_nUnused1', 'int'),  # For Byte Alignement

        # For Automatic Centering */
        ('m_dStartValue', 'double'),  # Start value
        ('m_dDelta', 'double'),  # Delta between max and 10% in Volts
        ('m_nAecCountTime', 'int'),  # Counting Time per point multiple of 10ms

        ('m_nUnused2', 'int')    # For Byte Alignement
    ]


class Sec_Ion_Beam_Nano(Structure):
    """It contains the Secondary Ion Beam Centering parameter information."""
    __size__ = 40
    __fields__ = [
        # Sec. Ion Beam Centering Acquisition */
        ('m_nDetId', 'int'),  # Detector Id (-1 If none)
        ('m_nStartDac', 'int'),  # Start DAC
        ('m_nDacStep', 'int'),  # Dac step

        ('m_nUnused1', 'int'),  # For Byte Alignement

        # For Automatic Beam Centering */
        ('m_dStartValue', 'double'),  # Start value
        ('m_d50PerCentWidth', 'double'),  # 50% Width in Volts
        ('m_nAbcCountTime', 'int'),  # Counting Time per point multiple of 10ms

        ('m_nUnused2', 'int'),  # For Byte Alignement
    ]


class Mask_nano(Structure):
    """It contains the acquisition definition information."""
    __size__ = 1552
    __fields__ = [
        ('m_nVersion', 'int'),  # version number 0, 1, 2...
        ('m_nRegulationMode', 'int'),  # Regulation 0:HALL / 1:NMR
        ('m_nMode', 'int'),  # Analysis mode  0:MC/1:MPS/2:CA
        ('m_nGrain_mode', 'int'),  # 0:No / 1:Yes
        ('m_nSemi_graphic_mode', 'int'),  # 0 graphic, 1 semi-graphic
        ('m_nDeltax', 'int'),  # deltax size in semi-graphic mode
        ('m_nDeltay', 'int'),  # deltay size in semi-graphic mode

        ('m_nNX_max', 'int'),  # Max X Scanning Frame [0..2048]
        ('m_nNY_max', 'int'),  # Max Y Scanning Frame [0..2048]
        ('m_nNX_low', 'int'),  # Scanning frame X low [0..2048]
        ('m_nNX_high', 'int'),  # Scanning frame X high [0..2048]
        ('m_nNY_low', 'int'),  # Scanning frame Y low [0..2048]
        ('m_nNY_high', 'int'),  # Scanning frame Y high [0..2048]
        ('m_nNX_lowB', 'int'),  # Blanking frame X low [0..2048]
        ('m_nNX_highB', 'int'),  # Blanking frame X high [0..2048]
        ('m_nNY_lowB', 'int'),  # Blanking frame Y low [0..2048]
        ('m_nNY_highB', 'int'),  # Blanking frame Y high [0..2048]

        ('m_nType_detecteur', 'int'),  # Detection mode 0:TIC/1:MC/2:FCP/3:FCO
        ('m_nElectron_scan', 'int'),  # 0: No / 1: Yes
        ('m_nScanning_mode', 'int'),  # Isotop scanning mode 0:No/1:Yes
        ('m_nBlanking_comptage', 'int'),  # 0: No blanking 1: blanking
        ('m_nCheckAvailaible', 'int'),  # 0 : Non / 1 : Oui
        ('m_nCheckStart', 'int'),  # 1st check
        ('m_nCheckFrequency', 'int'),  # Check frequency
        ('m_nNbBField', 'int'),  # Number of B field
        ('m_BFieldTab', 'int[72]'),  # Tab_BField_nano *m_BFieldTab [ 72 ] ; # Bfield informations
        ('m_nPrintRes', 'int'),  # Print results after acq
        ('m_HorizontalSibcParam', Sec_Ion_Beam_Nano),  # Horizontal Sibc param
        ('m_VerticalSibcParam', Sec_Ion_Beam_Nano),  # Vertical Sibc param
        ('m_nSibcBFieldInd', 'int'),  # B Field ind for SIBC (-1 If none)
        ('m_nSibcSelected', 'int'),  # SIBC Selection (0=No/1=Yes)
        ('m_AecParam', Energy_Nano),  # Automatic Energy Centering param
        ('m_nAecBFieldInd', 'int'),  # B Field ind for AEC (-1 If none)
        ('m_nAecSelected', 'int'),  # AEC Selection (0=No/1=Yes)
        ########################## V1 END #######################################*/
        ('m_nAecFrequency', 'int'),  # Energy Centring Frequency
        ########################## V2 END #######################################*/
        ('m_nE0SCenterBFieldInd', 'int'),  # B Field ind for E0S Centering (-1 If none)
        ('m_E0SCenterParam', E0S_Nano),  # E0S Centering param
        ('m_nE0SCenterSelected', 'int'),  # E0S Centering Selection (0=No/1=Yes)
        ########################## V3 END #######################################*/
        ('m_nAecWt', 'int'),  # Energy Centering Wait time in multiple of 10ms
        ########################## V4 END #######################################*/
        ('m_nPreSputRaster', 'int'),        # Raster for Presput in nm
        ########################## V6 END #######################################*/
        ('m_nE0pOffsetForCent', 'int'),  # Offset in DAC for Centering in scanning mode
        ('m_nE0sCenterNbPoints', 'int'),  # E0S Centering Number of point
        ########################## V7 END #######################################*/
        ('m_nBaselineNbMeas', 'int'),  # Nb Baseline Measure
        ('m_dNotUsed', 'double'),  # Not used
        ('m_nBaselineFrequency', 'int'),  # Baseline Frequency
        ########################## V8 END #######################################*/
        ('m_nSibcDuringAcqSelected', 'int'),  # SIBC Selection during Acq (0=No/1=Yes)
        ('m_nE0ScDuringAcqSelected', 'int'),  # E0S Centering during Acq Selection (0=No/1=Yes)
        ('m_nCentenringDuringAcqFrequency', 'int'),  # Centering during Acq frequency
        ('szDummy', '936str'),  # Unused -- this used to be 945 but that gave the wrong size
    ]


class Tab_Trolley_nano(Structure):
    """It contains the Trolley information."""
    __size__ = 208
    __fields__ = [
        ('m_pszSymbol', '64str'),  # Analysed mass symbole mass
        ('m_dAMU', 'double'),  # Mass amu
        ('m_dRadius', 'double'),  # Trolley radius
        ('m_nNegPlate', 'int'),  # Neg plate voltage in DAC
        ('m_nPosPlate', 'int'),  # Pos plate voltage in DAC
        ('m_nDetecteur', 'int'),  # Detector : 0:EM / 1:FC / 2:LD
        ('m_nOutSlit', 'int'),  # out_slit size
        ('m_nFlagTrolleyValided', 'int'),  # 0:No / 1:Yes
        ('m_nNum', 'int'),  # -1 unselected, otherwise global trolley number
        ('m_nPicNum', 'int'),  # 0 :unselected, selected Peak
        ('m_nRefPicNum', 'int'),  # 0 :unselected, selected Peak

        ('m_dPolarizationVal', 'double'),  # Polarization Voltage
        ('m_dStartVoltage', 'double'),  # Start Voltage

        ('m_nStartDacPlate1', 'int'),  # HMR Start DAC for first plate
        ('m_nStartDacPlate2', 'int'),  # HMR Start DAC for second plate
        ('m_nDacStep', 'int'),  # HMR Dac step
        ('m_nPointNumber', 'int'),  # HMR Number of acq points
        ('m_nCountTime', 'int'),  # HMR Counting Time per point multiple of 25ms
        ('m_nIsUsedForBaseline', 'int'),  # Used for Baseline (0:No / 1:Yes)

        ('m_d50PerCentWidth', 'double'),  # APC 50% Width
        ('m_nEdgesMethod', 'int'),  # APC Edges search method
        ('m_nApcCountTime', 'int'),   # APC Counting Time per point multiple of 10ms
        ('m_nIsUsedForSecIonBeamCentering', 'int'),  # Used for Sec. Ion Beam (0:No / 1:Yes)
        ('m_nUnitCorrection', 'int'),  # Unit correction
        ('m_dDeflectionVal', 'double'),  # Deflection Voltage
        ('m_nIsUsedForEnergyCentering', 'int'),  # Used for Energy Centering (0:No / 1:Yes)
        ('m_nIsUsedForE0SCentering', 'int'),  # Used for E0S Centering (0:No / 1:Yes)
        ########################## V8 END #######################################*/
        ('m_dBaselinePdOffset', 'double'),    # Baseline Pd offset
        ('m_nIsUsedForE0ScDuringAcq', 'int'),  # Used for E0S Centering (0:No / 1:Yes)
        ('m_nIsUsedForSibcDuringAcq', 'int'),  # Used for Sec. Ion Beam Centering (0:No / 1:Yes)
    ]


class PHD_Trolley_Nano(Structure):
    """It contains the PHD Scan parameter information."""
    __size__ = 24
    __fields__ = [
        ('m_nIsUsedForPhdScan', 'int'),  # Used for Phd Scan (0:No / 1:Yes)
        ('m_nStartDacThr', 'int'),  # Start DAC for Threshold
        ('m_nDacStep', 'int'),  # Dac step
        ('m_nPointNumber', 'int'),  # Number of acq points
        ('m_nCountTime', 'int'),  # Counting Time per point multiple of 25ms
        ('m_nNbscan', 'int'),  # Number of scan
    ]


class Tab_BField_nano(Structure):
    """It contains the B field information."""

    __size__ = 2840
    __fields__ = [
        ('m_nFlagBFieldSelected', 'int'),  # 0:No / 1:Yes
        ('m_nBField', 'int'),  # Magnetic field in DAC
        ('m_nWT', 'int'),  # Waiting Time in us
        ('m_nCTperPixel', 'int'),  # Counting Time in us in scanning
        ('m_dCTperPoint', 'double'),    # Counting Time in sec (factor of 25ms) in noscanning
        ('m_nComputed', 'int'),  # Waiting Time computed : 0:No/1:Yes
        ('m_nE0wOffset', 'int'),  # Offset E0W in DAC
        ('m_nQVal', 'int'),  # Quad in DAC
        ('m_nLF4Val', 'int'),  # LF4 in DAC
        ('m_nHexVal', 'int'),  # Hex in DAC
        ('m_nNbFrame', 'int'),  # Number of frame in scanning mode (V4)
        ('no_used1', 'double'),  # no used
        ('m_TrolleyTab', (Tab_Trolley_nano, 12)),  # Trolley informations
        ('m_PhdTrolleyTab', (PHD_Trolley_Nano, 12)),  # PHD Scan informations
    ]


class SigRefExp(Structure):
    """It contains expanded structure for SigRef information."""

    __size__ = 552
    __fields__ = [
        ('bRef', 'int'),  # 1 if sigref was measured. 0 else
        ('sigRef', SigRef),
        ('mode', 'int'),  # 0: manual, 1: auto
        ('nCT', 'int'),  # counting time
        ('nTT', 'int'),  # total time for sig ref treating
        ('szFile', '128str'),  # filename to merge
        ('szPath', '128str'),  # pathname

        # 3 next paramaters may be used for normalization with multiple sigref */
        ('nLR', 'int'),    # if 1, dLeft & dRight keep time bounds, ex 10 .. 20 */
        ('dLeft', 'double'),  # time left,  valid if nLR==1
        ('dRight', 'double'),  # time right, valid if nLR==1

        ('unused', '100str'),
    ]


class SigRefMulti(Structure):
    """It contains multi reference signal information."""
    __size__ = 8
    __fields__ = [
        ('nb', 'int'),  # number of signal references
        ('ppSigRefExp', 'int'), # SigRefExp **ppSigRefExp;    /* array dynamically allocated */
    ]


class Poly_list(Structure):
    """It contains header of polyatomic informations."""
    __size__ = 24
    __fields__ = [
        ('structname', '16str'),  # structure name
        ('nb_poly', 'int'),  # number of polyatomic
        ('poly', 'int'),  # Polyatomique **poly;    /* polyatomic table */
    ]

    def validate(self):
        super(Poly_list, self).validate()
        assert self.structname.startswith(self.__class__.__name__)


class Tab_mass(Structure):
    """It contains acquired mass information."""

    __size__ = 192
    __fields__ = [
        ('_not_in_spec', 'int'),  # https://github.com/BWHCNI/OpenMIMS/blob/de0bfcf3c0d7c515571f5fb1e7a5c74177660a61/src/main/java/com/nrims/data/Mims_Reader.java#L493
        ('type_mass', 'int'),  # 0=MONOATOM / 1=POLYATOM
        ('mass_amu', 'double'),  # mass in a.m.u.
        ('matrice_ou_trace', 'int'),  # eps: tens tube, 0:MATRICE 1:TRACE
        ('detecteur', 'int'),  # detector 0=EM / 1:FC
        ('waiting_time', 'double'),  # in sec
        ('counting_time', 'double'),  # in sec
        ('offset', 'int'),  # in volt
        ('mag_field', 'int'),  # in bit
        ('mass', Polyatomique),  # polyatomic info
    ]


class Cal_cond(Structure):
    """It contains acquired mass condition information."""

    __size__ = 96
    __fields__ = [
        ('n_delta', 'int'),  # number of delta M
        ('np_delta', 'int'),  # number of points / delta M
        ('tps_comptage', 'int'),  # counting time per point
        ('nb_cycles', 'int'),  # number of cycle
        ('no_used2', 'double'),
        ('cal_ref_mass', 'double'),  # mass reference mass
        ('symbol', '64str'),  # chimical symbol
    ]


class Crater(Structure):
    """It contains crater information."""
    __size__ = 24
    __fields__ = [
        ('x', 'double'),  # in micron
        ('y', 'double'),  # in micron
        ('quand', 'int'),  # changing cycle
    ]


class HvCont(Structure):
    """It contains Hv control information."""
    __size__ = 112
    __fields__ = [
        ('masse', '64str'),  # masse reference included in tab_mass
        ('debut', 'int'),  # control start - in cycle
        ('periode', 'int'),  # control period - in cycle
        ('borne_inf', 'double'),  # low limit - in volt
        ('borne_sup', 'double'),  # high limit - in volt
        ('pas', 'double'),  # step - in volt
        ('largeur_bp', 'int'),  # width bande passante - en eV
        ('count_time', 'double'),  # sec
    ]


class Champs_list(Structure):  # pragma: no cover
    """It contains Autocalibration field list information."""
    __size__ = 24
    __fields__ = [
        ('structname', '16str'),  # structure name
        ('nb_champs', 'int'),  # number of field
        ('couple', 'int'), # Couple    **couple;    /* couple data table */
    ]

    def validate(self):
        super(Champs_list, self).validate()
        assert self.structname.startswith(self.__class__.__name__)


class Offset_list(Structure):  # pragma: no cover
    """It contains Hv control offset list information."""
    __size__ = 14
    __fields__ = [
        ('structname', '16str'),  # structure name
        ('nb_offsets', 'int'),  # number of offset
        ('couple', 'int'), #Couple    **couple;    /* couple data table */
    ]

    def validate(self):
        super(Offset_list, self).validate()
        assert self.structname.startswith(self.__class__.__name__)


class Couple(Structure):
    """It contains couple data information."""
    __size__ = 8
    __fields__ = [
        ('num', 'int'),
        ('val', 'int'),
    ]


class Header_image(Structure):
    """It contains images information."""
    __size__ = 84
    __fields__ = [
        ('size_self', 'int'),  # header size
        ('type', 'short'),  # image type 0:2D or 1:3D
        ('w', 'short'),  # image width in pixel
        ('h', 'short'),  # image height in pixel
        ('d', 'short'),  # pixel size in bytes (WORD =2)
        ('n', 'short'),  # number of images
        ('z', 'short'),  # number of planes => number of images = z * n
        ('raster', 'int'),  # image widht in micron
        ('nickname', '64str'),  # filename
    ]

    def validate(self):
        assert self.size_self == self.__size__
        super(Header_image, self).validate()
        # assert self.d == 2 ??? should this pass ???


class Ap_primary_nano(Structure):
    """It contains primary analytical parameters information."""

    __size__ = 552
    __fields__ = [
        ('pszIon', '8str'),  # Source
        ('nPrimCurrentT0', 'int'),  # Primary current at t = 0 in pA
        ('nPrimCurrentTEnd', 'int'),  # Primary current at t = End in pA

        ('nPrimLDuo', 'int'),  # LDuo in V
        ('nPrimL1', 'int'),  # L1 in V

        ('nDduoPos', 'int'),  # Dduo Position : 0(not used)/1/2/3/4
        ('nDduoTabValue', 'int[10]'),  # Positions values

        ('nD0Pos', 'int'),  # D0 Position : 0(not used)/1/2/3/4
        ('nD0TabValue', 'int[10]'),  # Positions values

        ('nD1Pos', 'int'),  # D1 Position : 0(not used)/1/2/3/4
        ('nD1TabValue', 'int[10]'),  # Positions values

        ('dRaster', 'double'),  # Raster size in um
        ('dOct45', 'double'),  # Octopole 45 in V
        ('dOct90', 'double'),  # Octopole 90 in V
        ('dPrimaryFoc', 'double'),  # E0P in V
        ('pszAnalChamberPres', '32str'),  # Analysis chamber pressure in torr
        #------------------------------- RELEASE 3 -------------------------------*/
        ('nPrimL0', 'int'),  # L0 in V
        #------------------------------- RELEASE 4 -------------------------------*/
        ('nCsHv', 'int'),  # Cs Hv in V
        ('nDuoHv', 'int'),  # Duo Hv in V
        #------------------------------- RELEASE 7 -------------------------------*/
        ('nDCsPos', 'int'),  # Position : 0(not used)/1/2/3/4
        ('nDCsTabValue', 'int[10]'),  # Valeur des positions

        ('nUnusedTab', 'int[69]'),  # Unused -- Used to be 67 but that didn't fit
    ]


class Ap_secondary_nano(Structure):
    """It contains secondary analytical parameters information."""


    __fields__ = [
        ('dHVSample', 'double'),  # E0W in V
        ('nESPos', 'int'),    # Entrance Slit Position : 0(not used)/1/2/3/4/5 */
        ('nESTabWidthValue', '10int'),  # Entrance Slit Positions Width
        ('nESTabHeightValue', '10int'),  # Entrance Slit Positions Height

        ('nASPos', 'int'),    # Aperture Slit Position : 0(not used)/1/2/3/4/5 */
        ('nASTabWidthValue', '10int'),  # Aperture Slit positions Width
        ('nASTabHeightValue', '10int'),  # Aperture Slit positions Height

        ('dEnrjSPosValue', 'double'),  # Energy Slit Position
        ('dEnrjSWidthValue', 'double'),  # Energy Slit Width

        ('nExSFCPos', 'int'),  # Exit Slit FC Position :1/2/3
        ('nExSFCType', 'int'),  # Exit Slit FC type : 0 Normal/1 Large
        ('nExSFCTabWidthValue', 'int[2, 5]'), #int    nExSFCTabWidthValue [ 2 ] [ 5 ] ; #/* Exit Slit FC positions Width : [ Type ][ Pos ] */
        ('nExSFCTabHeightValue', 'int[2, 5]'), #int    nExSFCTabHeightValue [ 2 ] [ 5 ] ; #/* Exit Slit FC positions Height : [ Type ][ Pos ] */
        ('nExSEM1Pos', 'int'),  # Exit Slit EM1 Position :1/2/3
        ('nExSEM1Type', 'int'),  # Exit Sd ../aplit EM1 Type : 0 Normal/1 Large
        ('nExSEM1TabWidthValue', 'int[2, 5]'), #int    nExSEM1TabWidthValue [ 2 ] [ 5 ] ;  # /* Exit Slit EM1 positions Width : [ Type ][ Pos ] */
        ('nExSEM1TabHeightValue', 'int[2, 5]'), #int    nExSEM1TabHeightValue [ 2 ] [ 5 ] ; # /* Exit Slit EM1 positions Height : [ Type ][ Pos ] */

        ('nExSEM2Pos', 'int'),  # Exit Slit EM2 Position :1/2/3
        ('nExSEM2Type', 'int'),  # Exit Slit EM2 Type : 0 Normal/1 Large
        ('nExSEM2TabWidthValue', 'int[2, 5]'), #int    nExSEM2TabWidthValue [ 2 ] [ 5 ] ; #/* Exit Slit EM2 positions Width : [ Type ][ Pos ] */
        ('nExSEM2TabHeightValue', 'int[2, 5]'), #int    nExSEM2TabHeightValue [ 2 ] [ 5 ] ; #/* Exit Slit EM2 positions Height : [ Type ][ Pos ] */

        ('nExSEM3Pos', 'int'),  # Exit Slit EM3 Position :1/2/3
        ('nExSEM3Type', 'int'),  # Exit Slit EM3 Type : 0 Normal/1 Large
        ('nExSEM3TabWidthValue', 'int[2, 5]'), #int    nExSEM3TabWidthValue [ 2 ] [ 5 ] ; /* Exit Slit EM3 positions Width : [ Type ][ Pos ] */
        ('nExSEM3TabHeightValue', 'int[2, 5]'), # int    nExSEM3TabHeightValue [ 2 ] [ 5 ] ; /* Exit Slit EM3 positions Height : [ Type ][ Pos ] */

        ('nExSEM4Pos', 'int'),  # Exit Slit EM4 Position :1/2/3
        ('nExSEM4Type', 'int'),  # Exit Slit EM4 Type : 0 Normal/1 Large
        ('nExSEM4TabWidthValue', 'int[2, 5]'), #int    nExSEM4TabWidthValue [ 2 ] [ 5 ] ; /* Exit Slit EM4 positions Width : [ Type ][ Pos ] */
        ('nExSEM4TabHeightValue', 'int[2, 5]'), #int    nExSEM4TabHeightValue [ 2 ] [ 5 ] ; /* Exit Slit EM4 positions Height : [ Type ][ Pos ] */

        ('nExSEM5Pos', 'int'),  # Exit Slit EM5 Position :1/2/3
        ('nExSEM5Type', 'int'),  # Exit Slit EM5 Type : 0 Normal/1 Large
        ('nExSEM5TabWidthValue', 'int[2, 5]'), #int    nExSEM5TabWidthValue [ 2 ] [ 5 ] ; /* Exit Slit EM5 positions Width : [ Type ][ Pos ] */
        ('nExSEM5TabHeightValue', 'int[2, 5]'), #int    nExSEM5TabHeightValue [ 2 ] [ 5 ] ; /* Exit Slit EM5 positions Height : [ Type ][ Pos ] */

        ('dExSLDWidhtPos', 'double'),  # Exit Slit LD slit vernier position
        ('dExSLDWidhtValueA', 'double'),  # Exit Slit LD coefficient A
        ('dExSLDWidhtValueB', 'double'),  # Exit Slit LD coefficient B

        ('dSecondaryFoc', 'double'),  # E0S in V
        ('pszMultiColChamberPres', '32str'), # Multicollection chamber pressure in torr
        ('nFCsPosBackground', 'int'),  # FCS Positive Background
        ('nFCsNegBackground', 'int'),  # FCS Negative Background

        ('dEM1Yield', 'double'),  # EM1 Yield
        ('nEM1Background', 'int'),  # EM1 Background
        ('nEM1DeadTime', 'int'),  # EM1 Dead Time

        ('dEM2Yield', 'double'),  # EM2 Yield
        ('nEM2Background', 'int'),  # EM2 Background
        ('nEM2DeadTime', 'int'),  # EM2 Dead Time

        ('dEM3Yield', 'double'),  # EM3 Yield
        ('nEM3Background', 'int'),  # EM3 Background
        ('nEM3DeadTime', 'int'),  # EM3 Dead Time

        ('dEM4Yield', 'double'),  # EM4 Yield
        ('nEM4Background', 'int'),  # EM4 Background
        ('nEM4DeadTime', 'int'),  # EM4 Dead Time

        ('dEM5Yield', 'double'),  # EM5 Yield
        ('nEM5Background', 'int'),  # EM5 Background
        ('nEM5DeadTime', 'int'),  # EM5 Dead Time

        ('dLDYield', 'double'),  # LD Yield
        ('nLDBackground', 'int'),  # LD Background
        ('nLDDeadTime', 'int'),  # LD Dead Time

        ('nExSEM4BPos', 'int'),  # Exit Slit EM4B Position :1/2/3
        ('nExSEM4BType', 'int'),  # Exit Slit EM4B Type : 0 Normal / 1 Large
        ('nExSEM4BTabWidthValue', 'int[2, 5]'), #int    nExSEM4BTabWidthValue [ 2 ] [ 5 ] ; /* Exit Slit EM4B positions Width : [ Type ] [ Pos ] */
        ('nExSEM4BTabHeightValue', 'int[2, 5]'), #int    nExSEM4BTabHeightValue [ 2 ] [ 5 ] ; /* Exit Slit EM4B positions Height : [ Type ] [ Pos ] */

        ('dEM4BYield', 'double'),  # EM4B Yield
        ('nEM4BBackground', 'int'),  # EM4B Background
        ('nEM4BDeadTime', 'int'),  # EM4B Dead Time

        ('nUnusedTab', '2int'),  # Unused
    ]
    __size__ = 1000


class Anal_param_nano(Structure):
    """It contains analytical parameters information."""

    __size__ = 1840

    __fields__ = [
        ('pszNomStruct', '16str'),  # Structure name
        ('nRelease', 'int'),  # Data release version
        ('nIsN50Large', 'int'),  # N50 Large Flag 0=Standard/1=Large
        ('nUnused2', 'int'),  # Unused
        ('nUnused3', 'int'),  # Unused
        ('pszComment', '256str'),  # Comment
        ('prim', Ap_primary_nano),  # Primary Analytical Parameters
        ('seco', Ap_secondary_nano),  # Secondary Analytical Parameters
    ]

    def validate(self):
        super(Anal_param_nano, self).validate()
        assert self.pszNomStruct.startswith(self.__class__.__name__)


class ApParamPreset(Structure):
    """It contains Parameter for Preset information."""
    __fields__ = [
        ('nId', 'int'),  # Parameter Id (par_dfp.h)
        ('nValue', 'int'),  # Parameter DAC value
        ('szName', '20str'),  # Parameter name
    ]
    __size__ = 28


class ApPresetDef(Structure):
    """It contains Preset definition."""

    __fields__ = [
        ('szFileName', '256str'),  # ISF File name
        ('szName', '224str'),  # Preset name
        ('szDateCalib', '32str'),  # Preset name
        ('nIsSelected', 'int'),  # Selection flag
        ('nNbParam', 'int'),  # Nb param preset
    ]
    __size__ = 520


class ApPresetLens(Structure):
    """It contains Preset Lens definition."""
    __size__ = 4720  # 2120 didn't account for names
    __fields__ = [
        ('PresetInfo', ApPresetDef),  # Preset definition
        ('ParamTab', (ApParamPreset, 150)),  # Preset param
    ]

    def validate(self):
        assert 0 <= self.PresetInfo.nNbParam <= 150
        self['ParamTab'] = self.ParamTab[:self.PresetInfo.nNbParam]
        super(ApPresetLens, self).validate()



class ApPresetSlit(Structure):
    """It contains Preset Slit definition."""
    __size__ = 1080  # 680 didn't account for length of names in ApParamPreset
    __fields__ = [
        ('PresetInfo', ApPresetDef),  # Preset definition
        ('ParamTab', (ApParamPreset, 20)),  # Preset param
    ]

    def validate(self):
        assert 0 <= self.PresetInfo.nNbParam <= 20
        self['ParamTab'] = self.ParamTab[:self.PresetInfo.nNbParam]
        super(ApPresetSlit, self).validate()


class Anal_param_nano_bis(Structure):
    """It contains new analytical parameters information."""

    __fields__ = [
        # /*------------------------------- RELEASE 5 -------------------------------*/
        ('pszNomStruct', '24str'),  # Structure name Anal_param_nano_bis
        #/* Det 6 */
        ('nExSEM6Pos', 'int'),  # Exit Slit EM6 Position :1/2/3
        ('nExSEM6Type', 'int'),  # Exit Slit EM6 Type : 0 Normal / 1 Large
        ('nExSEM6TabWidthValue', 'int[2, 5]'), #int    nExSEM6TabWidthValue [ 2 ] [ 5 ] ; # /* Exit Slit EM6 positions Width : [ Type ] [ Pos ] */
        ('nExSEM6TabHeightValue', 'int[2, 5]'), #int    nExSEM6TabHeightValue [ 2 ] [ 5 ] ; # /* Height : [ Type ] [ Pos ] */

        ('dEM6Yield', 'double'),  # EM6 Yield
        ('nEM6Background', 'int'),  # EM6 Background
        ('nEM6DeadTime', 'int'),  # EM6 Dead Time

        #/* Det 7 */
        ('nExSEM7Pos', 'int'),  # Exit Slit EM7 Position :1/2/3
        ('nExSEM7Type', 'int'),  # Exit Slit EM7 Type : 0 Normal / 1 Large
        ('nExSEM7TabWidthValue', 'int[2, 5]'), #int    nExSEM7TabWidthValue [ 2 ] [ 5 ] ; #/* Exit Slit EM7 positions Width : [ Type ] [ Pos ] */
        ('nExSEM7TabHeightValue', 'int[2, 5]'), #int    nExSEM7TabHeightValue [ 2 ] [ 5 ] ; # /* Height : [ Type ] [ Pos ] */

        ('dEM7Yield', 'double'),  # EM7 Yield
        ('nEM7Background', 'int'),  # EM7 Background
        ('nEM7DeadTime', 'int'),  # EM7 Dead Time

        # /* Exit Slit XLarge */
        #/* XLarge Exit Slit EM1 positions Width & Height : [ Pos ] */
        ('nXlExSEM1TabWidthValue', 'int[5]'),
        ('nXlExSEM1TabHeightValue', 'int[5]'),
        #/* XLarge Exit Slit EM2 positions Width & Height : [ Pos ] */
        ('nXlExSEM2TabWidthValue', 'int[5]'),
        ('nXlExSEM2TabHeightValue', 'int[5]'),
        #/* XLarge Exit Slit EM3 positions Width & Height : [ Pos ] */
        ('nXlExSEM3TabWidthValue', 'int[5]'),
        ('nXlExSEM3TabHeightValue', 'int[5]'),
        #/* XLarge Exit Slit EM4 positions Width & Height : [ Pos ] */
        ('nXlExSEM4TabWidthValue', 'int[5]'),
        ('nXlExSEM4TabHeightValue', 'int[5]'),
        #/* XLarge Exit Slit EM5 positions Width & Height : [ Pos ] */
        ('nXlExSEM5TabWidthValue', 'int[5]'),
        ('nXlExSEM5TabHeightValue', 'int[5]'),
        #/* XLarge Exit Slit EM6 positions Width & Height : [ Pos ] */
        ('nXlExSEM6TabWidthValue', 'int[5]'),
        ('nXlExSEM6TabHeightValue', 'int[5]'),
        #/* XLarge Exit Slit EM7 positions Width & Height : [ Pos ] */
        ('nXlExSEM7TabWidthValue', 'int[5]'),
        ('nXlExSEM7TabHeightValue', 'int[5]'),

        #/* Pre sput Preset */
        ('PreSputPresetSlit', ApPresetSlit),
        ('PreSputPresetLens', ApPresetLens),

        #/* Acq Preset */
        ('AcqPresetSlit', ApPresetSlit),
        ('AcqPresetLens', ApPresetLens),

        #/*------------------------------- RELEASE 6 -------------------------------*/
        ('dEMTICYield', 'double'),  # EMTIC Yield
        ('nEMTICBackground', 'int'),  # EMTIC Background
        ('nEMTICDeadTime', 'int'),  # EMTIC Dead Time

        ('nFC1PosBackground', 'int'),  # FC1 Positive Background
        ('nFC1NegBackground', 'int'),  # FC1 Negative Background
        ('nFC2PosBackground', 'int'),  # FC2 Positive Background
        ('nFC2NegBackground', 'int'),  # FC2 Negative Background
        ('nFC3PosBackground', 'int'),  # FC3 Positive Background
        ('nFC3NegBackground', 'int'),  # FC3 Negative Background
        ('nFC4PosBackground', 'int'),  # FC4 Positive Background
        ('nFC4NegBackground', 'int'),  # FC4 Negative Background
        ('nFC5PosBackground', 'int'),  # FC5 Positive Background
        ('nFC5NegBackground', 'int'),  # FC5 Negative Background
        ('nFC6PosBackground', 'int'),  # FC6 Positive Background
        ('nFC6NegBackground', 'int'),  # FC6 Negative Background
        ('nFC7PosBackground', 'int'),  # FC7 Positive Background
        ('nFC7NegBackground', 'int'),  # FC7 Negative Background

        ('nDet1Type', 'int'),  # Det type (0=EM/1=FC)
        ('nDet2Type', 'int'),  # Det type (0=EM/1=FC)
        ('nDet3Type', 'int'),  # Det type (0=EM/1=FC)
        ('nDet4Type', 'int'),  # Det type (0=EM/1=FC)
        ('nDet5Type', 'int'),  # Det type (0=EM/1=FC)
        ('nDet6Type', 'int'),  # Det type (0=EM/1=FC)
        ('nDet7Type', 'int'),  # Det type (0=EM/1=FC)

        ('nUnusedTab', '763int'),
    ]
    __size__ = 15264

    def validate(self):
        super(Anal_param_nano_bis, self).validate()
        assert self.pszNomStruct.startswith(self.__class__.__name__)


def infer_hot_pixels(data, num_outliers, kernel_size=3, outlier_factor=3, min_count=1,
                     max_repeat_fraction=0.1, num_nonzero=None, return_filtered=False):
    """
    Identify hot pixels due to correlated noise.

    Parameters
    ----------
    data : np.ndarray
        data tensor with shape `(n, p, w, h)`, where `n` is the number of frames,
        `p` is the number of detectors, `w` is the width, and `h` is the height
    num_outliers : int
        number of times a pixel needs to be labelled as an outlier in different
        detectors to be considered correlated noise
    kernel_size : int
        size of the kernel used for median filtering
    outlier_factor : float
        factor multiplying the median-filtered image to define the threshold that
        serves to flag a pixel as an outlier
    min_count : float
        minimum count used to determine the threshold if the median-filtered image
        is smaller
    max_repeat_fraction : float
        maximum fraction of frames in which a pixel is allowed to be a hot pixel.
        If a pixel is a hot pixel candidate in more than `max_repeat_fraction` of
        all frames, it is not considered a hot pixel.
    num_nonzeros : int
        number of detectors in which a hot pixel candidate must be non-zero. Default
        is all detectors.
    return_filtered : bool
        whether to return the median-filtered image

    Returns
    -------
    mask : np.ndarray
        binary mask of hot pixels with shape `(n, w, h)`
    """
    data = np.asarray(data)
    assert data.ndim == 4, f"expected `data` to have 4 dimensions; got {data.ndim}"
    assert 1 <= num_outliers <= data.shape[1], "number of ouliers must be positive " \
        "and <= the number of detectors"
    num_nonzero = num_nonzero or data.shape[1]

    # Apply a median filter to identify "typical" counts for this area
    filtered = ndimage.median_filter(data, (1, 1, kernel_size, kernel_size))
    # Flag any pixels as hot-pixel candidates if they exceed a given threshold
    candidates = data >= outlier_factor * np.maximum(filtered, min_count)
    # Flag as a hot pixel if a pixel is a candidate in at least num_outliers detectors
    mask = np.sum(candidates, axis=1) >= num_outliers
    # Remove any hot pixels that have zero count in any detector
    mask &= np.sum(data > 0, axis=1) >= num_nonzero
    # Remove any hot pixels that occur in more than max_repeat_fraction of all frames
    mask &= (np.mean(mask, axis=0) < max_repeat_fraction)[None]
    return (mask, filtered) if return_filtered else mask


def apply_mask(data, mask, replacement_values):
    """
    Replace all values in `data` by `replacement_values` where `mask` is `True`.

    Parameters
    ----------
    data : np.ndarray
        data tensor with shape `(n, p, w, h)`, where `n` is the number of frames,
        `p` is the number of detectors, `w` is the width, and `h` is the height
    mask : np.ndarray
        binary mask of hot pixels with shape `(n, w, h)`
    replacement_values : np.ndarray
        tensor of replacement values with the same shape as `data`, a list of the
        same length as non-zero elements in `mask`, or a scalar
    """
    data = np.asarray(data)
    replacement_values = np.asarray(replacement_values)
    # Repeat the mask along the detector dimension so we can index
    mask = np.repeat(mask[:, None], data.shape[1], 1)

    cleaned = data.copy()
    if cleaned.shape == replacement_values.shape:
        cleaned[mask] = replacement_values[mask]
    else:
        cleaned[mask] = replacement_values
    return cleaned


def remove_hot_pixels(data, num_outliers, kernel_size=3, outlier_factor=3, min_count=1,
                      max_repeat_fraction=0.1, num_nonzero=None):
    """
    Remove hot pixels due to correlated noise.

    Parameters
    ----------
    data : np.ndarray
        data tensor with shape `(n, p, w, h)`, where `n` is the number of frames,
        `p` is the number of detectors, `w` is the width, and `h` is the height
    num_outliers : int
        number of times a pixel needs to be labelled as an outlier in different
        detectors to be considered correlated noise
    kernel_size : int
        size of the kernel used for median filtering
    outlier_factor : float
        factor multiplying the median-filtered image to define the threshold that
        serves to flag a pixel as an outlier
    min_count : float
        minimum count used to determine the threshold if the median-filtered image
        is smaller
    max_repeat_fraction : float
        maximum fraction of frames in which a pixel is allowed to be a hot pixel.
        If a pixel is a hot pixel candidate in more than `max_repeat_fraction` of
        all frames, it is not considered a hot pixel.
    num_nonzeros : int
        number of detectors in which a hot pixel candidate must be non-zero. Default
        is all detectors.

    Returns
    -------
    cleaned : np.ndarray
        cleaned data tensor with the same shape as `data` with hot pixels replaced
        by median-filtered pixels
    """
    mask, filtered = infer_hot_pixels(data, num_outliers, kernel_size, outlier_factor,
                                      min_count, max_repeat_fraction, num_nonzero, True)
    return apply_mask(data, mask, filtered)


def infer_translations(data, padding=8, method='sequential'):
    """
    Infer translations between successive frames to increase sharpness of aggregated
    nanoSIMS images.

    Parameters
    ----------
    data : np.ndarray
        data tensor for a single detector with shape `(n, w, h)`, where `n` is the
        number of frames, `w` is the width, and `h` is the height
    padding : int
        padding applied to the data tensor before computing correlations
    method : str
        method used to align different frames. 'sequential' aggregates frames in
        order and aligns successive frames with the current best aggregate.

    Returns
    -------
    translations : np.ndarray
        sequence of translations that should be applied to align the images
    """
    assert data.ndim == 3, f"expected `data` to have 3 dimensions; got {data.ndim}"
    data = np.pad(data, [(0, 0), (padding, padding), (padding, padding)], 'constant')

    if method == 'sequential':
        translations = [(0, 0)]
        aggregate = data[0]
        for frame in data[1:]:
            transformed = np.fft.fft2(frame[::-1, ::-1])
            convolution = np.fft.fftshift(np.fft.ifft2(np.fft.fft2(aggregate) * transformed))
            dx, dy = np.unravel_index(np.argmax(convolution), convolution.shape)
            dx -= convolution.shape[0] // 2 - 1
            dy -= convolution.shape[1] // 2 - 1
            translations.append((dx, dy))
            aggregate += np.roll(frame, (dx, dy), (0, 1))
    else:
        raise NotImplementedError

    # Center the translations
    translations = np.asarray(translations)
    translations -= np.median(translations, axis=0).astype(int)
    return translations


def apply_translations(data, translations, padding=8):
    """
    Apply the sequence of translations to the data.

    Parameters
    ----------
    data : np.ndarray
        data tensor with shape `(n, p, w, h)`, where `n` is the number of frames,
        `p` is the number of detectors, `w` is the width, and `h` is the height
    translations : np.ndarray
        sequence of translations that should be applied to align the images

    Returns
    -------
    translated : np.ndarray
        translated data tensor with shape `(n, p, w + 2 * padding, h + 2 * padding)`
    """
    data = np.asarray(data).copy()
    translations = np.asarray(translations)
    assert data.ndim == 4, f"expected `data` to have 4 dimensions; got {data.ndim}"
    expected_shape = (data.shape[0], 2)
    assert translations.shape == expected_shape, "expected `translations` to have shape " \
        f"{expected_shape}; got {translations.shape}"

    # Apply the translations by rolling the image
    translated = []
    for frame, translation in zip(data, translations):
        frame = np.pad(frame, [(0, 0), (padding, padding), (padding, padding)], 'constant')
        translated.append(np.roll(frame, translation, (1, 2)))

    return np.asarray(translated)
