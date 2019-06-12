"""Provides header definitions for the PAR header file format.

  These headers come from the nibabel parrec parser, under MIT license
  https://github.com/nipy/nibabel/blob/master/nibabel/parrec.py

  The MIT License

  Copyright (c) 2009-2014 Matthew Brett <matthew.brett@gmail.com>
  Copyright (c) 2010-2013 Stephan Gerhard <git@unidesign.ch>
  Copyright (c) 2006-2014 Michael Hanke <michael.hanke@gmail.com>
  Copyright (c) 2011 Christian Haselgrove <christian.haselgrove@umassmed.edu>
  Copyright (c) 2010-2011 Jarrod Millman <jarrod.millman@gmail.com>
  Copyright (c) 2011-2014 Yaroslav Halchenko <debian@onerussian.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
"""
HEADER_KEY_DICT = {
    'Patient name': ('patient_name',),
    'Examination name': ('exam_name',),
    'Protocol name': ('protocol_name',),
    'Examination date/time': ('exam_date',),
    'Series Type': ('series_type',),
    'Acquisition nr': ('acq_nr', int),
    'Reconstruction nr': ('recon_nr', int),
    'Scan Duration [sec]': ('scan_duration', float),
    'Max. number of cardiac phases': ('max_cardiac_phases', int),
    'Max. number of echoes': ('max_echoes', int),
    'Max. number of slices/locations': ('max_slices', int),
    'Max. number of dynamics': ('max_dynamics', int),
    'Max. number of mixes': ('max_mixes', int),
    'Patient position': ('patient_position',),
    'Preparation direction': ('prep_direction',),
    'Technique': ('tech',),
    'Scan resolution  (x, y)': ('scan_resolution', int, (2,)),
    'Scan mode': ('scan_mode',),
    'Repetition time [ms]': ('repetition_time', float, None),
    'FOV (ap,fh,rl) [mm]': ('fov', float, (3,)),
    'Water Fat shift [pixels]': ('water_fat_shift', float),
    'Angulation midslice(ap,fh,rl)[degr]': ('angulation', float, (3,)),
    'Off Centre midslice(ap,fh,rl) [mm]': ('off_center', float, (3,)),
    'Flow compensation <0=no 1=yes> ?': ('flow_compensation', int),
    'Presaturation     <0=no 1=yes> ?': ('presaturation', int),
    'Phase encoding velocity [cm/sec]': ('phase_enc_velocity', float, (3,)),
    'MTC               <0=no 1=yes> ?': ('mtc', int),
    'SPIR              <0=no 1=yes> ?': ('spir', int),
    'EPI factor        <0,1=no EPI>': ('epi_factor', int),
    'Dynamic scan      <0=no 1=yes> ?': ('dyn_scan', int),
    'Diffusion         <0=no 1=yes> ?': ('diffusion', int),
    'Diffusion echo time [ms]': ('diffusion_echo_time', float),
    # Lines below added for par / rec versions > 4
    'Max. number of diffusion values': ('max_diffusion_values', int),
    'Max. number of gradient orients': ('max_gradient_orient', int),
    # Line below added for par / rec version > 4.1
    'Number of label types   <0=no ASL>': ('nr_label_types', int),
    # The following are duplicates of the above fields, but with slightly
    # different abbreviation, spelling, or capatilization.  Both variants have
    # been observed in the wild in V4.2 PAR files:
    # https://github.com/nipy/nibabel/issues/505
    'Series_data_type': ('series_type',),
    'Patient Position': ('patient_position',),
    'Repetition time [msec]': ('repetition_time', float, None),
    'Diffusion echo time [msec]': ('diffusion_echo_time', float),
}
