from __future__ import print_function
import argparse
import sys
import textwrap
import nibabel as nib
from . import UNCFile
from . import conversion


def _conv_and_save(unc, name, echo=None, volume=None, flip_lr=False):
    if isinstance(name, str):
        nii_name = name
        if volume is not None:
            nii_name += '_v{0}'.format(volume)
        if echo is not None:
            nii_name += '_e{0}'.format(echo)
    else:
        nii_name = name.pop(0)
    nii_name += '.nii.gz'
    nii = conversion.unc_to_nifti(unc, flip_lr=flip_lr)
    nib.save(nii, nii_name)


def _check_enough_names(name, echoes, volumes):
    """If names is a list check there are enough for the number of output files."""
    if isinstance(name, str):
        return True
    else:
        return len(name) >= echoes * volumes


def unc_to_nifti():
    """Convert UNC to NIFTI."""
    # prepare an argument parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
            Convert UNC image to NIFTI.

            Multi-echo files will be automatically split to separate files.
            Multi-volume files can be split by supplying the --volumes arguments.

            For single echo/volume files the default output name is [input name].nii.gz.
            If the input has a .unc extension it will be removed.

            If multiple echoes/volumes are present then _eN and _vN suffixes will be
            added.  An alternative output name can be set using the --output
            argument, multiple comma separated can be provided to name echoes/volumes.
        """)
    )
    parser.add_argument('--volumes', '-v', type=int, nargs='?', default=1, help='Number of volumes')
    parser.add_argument('--fliplr', '-f', action='store_true', help='Flip left/right')
    parser.add_argument(
        '--output', '-o',
        nargs='?',
        help='Output filename(s)'
    )
    parser.add_argument('unc_filename', metavar='input', help='UNC file')
    args = parser.parse_args()
    if args.output:
        if ',' in args.output:
            name = args.output.split(',')
        else:
            name = args.output
    elif args.unc_filename.endswith('.unc'):
        name = args.unc_filename[0:-4]
    else:
        name = args.unc_filename
    # read the input file
    unc = UNCFile.from_path(args.unc_filename)
    # if comma separated names supplied, check we have enough
    if not _check_enough_names(name, unc.num_echoes, args.volumes):
        print('Need {0} names but only {1} supplied'.format(
            unc.num_echoes * args.volumes,
            len(name)
        ), file=sys.stderr)
        sys.exit(1)
    # do the conversion
    if unc.num_echoes > 1:
        echoes = unc.split_echoes()
        for echo_num, echo in enumerate(echoes):
            if args.volumes > 1:
                # multiple echoes, multiple volumes
                vols = echo.split_volumes(args.volumes)
                for vol_num, vol in enumerate(vols):
                    _conv_and_save(vol, name, echo=echo_num, volume=vol_num, flip_lr=args.fliplr)
            else:
                # multiple echoes, single volume
                _conv_and_save(echo, name, echo=echo_num, flip_lr=args.fliplr)
    else:
        if args.volumes > 1:
            # single echo, multiple volumes
            vols = unc.split_volumes(args.volumes)
            for vol_num, vol in enumerate(vols):
                _conv_and_save(vol, name, volume=vol_num, flip_lr=args.fliplr)
        else:
            # single echo, single volume
            _conv_and_save(unc, name, flip_lr=args.fliplr)


if __name__ == '__main__':
    unc_to_nifti()
