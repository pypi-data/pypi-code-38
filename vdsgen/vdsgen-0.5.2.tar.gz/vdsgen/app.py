import sys
import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter,\
    RawTextHelpFormatter

from .vdsgenerator import VDSGenerator
from .interleavevdsgenerator import InterleaveVDSGenerator
from .subframevdsgenerator import SubFrameVDSGenerator
from .excaliburgapfillvdsgenerator import ExcaliburGapFillVDSGenerator
from .reshapevdsgenerator import ReshapeVDSGenerator

help_message = """
A script to create a virtual dataset composed of multiple raw HDF5 files.
The minimum required arguments are <path> and either -p <prefix> or -f <files>.

For example:
 > ../vdsgen/app.py /scratch/images -p stripe_
 > ../vdsgen/app.py /scratch/images -f stripe_1.hdf5 stripe_2.hdf5
 
You can create an empty VDS, for raw files that don't exist yet, with the -e
flag; you will then need to provide --shape and --data_type, though defaults
are provided for these.
"""


class Formatter(ArgumentDefaultsHelpFormatter, RawTextHelpFormatter):
    pass


def parse_args():
    """Parse command line arguments."""
    parser = ArgumentParser(description=help_message,
                            formatter_class=Formatter)
    parser.add_argument(
        "path", type=str, help="Root folder of source files and VDS.")

    # Definition of file names in <path> - Common prefix or explicit list
    file_definition = parser.add_mutually_exclusive_group(required=True)
    file_definition.add_argument(
        "-p", "--prefix", type=str, default=None, dest="prefix",
        help="Prefix of files to search <path> for - e.g 'stripe_' to combine "
             "'stripe_1.hdf5' and 'stripe_2.hdf5'.")
    file_definition.add_argument(
        "-f", "--files", nargs="*", type=str, default=None, dest="files",
        help="Explicit names of raw files in <path>.")

    # Arguments required to allow VDS to be created before raw files exist
    empty_vds = parser.add_argument_group(
        "Arguments required to describe the source dataset(s) when --empty is "
        "used"
    )
    empty_vds.add_argument(
        "-e", "--empty", action="store_true", dest="empty",
        help="Make empty VDS pointing to datasets that don't exist yet.")
    empty_vds.add_argument(
        "--shape", type=int, nargs="*", default=[1, 256, 2048], dest="shape",
        help="Shape of dataset - '<frames> <height> <width>', "
             "where frames is N dimensional.")
    empty_vds.add_argument(
        "-t", "--data-type", type=str, default="uint16", dest="data_type",
        help="Data type of raw datasets.")

    # Arguments related to the mode used
    mode_args = parser.add_argument_group(
        "Arguments that only take effect in certain modes"
    )
    mode_args.add_argument(
        "--mode", type=str, dest="mode", default="sub-frames",
        choices=["sub-frames", "interleave", "gap-fill", "reshape"],
        help="Type of VDS to create and expected input dataset(s)\n"
             "  sub-frames:    ND datasets containing sub-frames of full "
             "images\n"
             "  interleave:    1D datasets containing interspersed blocks of "
             "frames\n"
             "  gap-fill:      Single ND raw full-frame excalibur dataset to "
             "insert gaps into\n"
             "  reshape:       Single 1D dataset to reshape\n")
    mode_args.add_argument(
        "-s", "--stripe-spacing", type=int, dest="stripe_spacing", default=3,
        help="Spacing between two stripes in an Excalibur module. "
             "[gap-fill, sub-frames]")
    mode_args.add_argument(
        "-m", "--module-spacing", type=int, dest="module_spacing", default=123,
        help="Spacing between Excalibur modules. [gap-fill, sub-frames]")
    mode_args.add_argument(
        "-M", "--modules", type=int, dest="modules", choices=[1, 3], default=1,
        help="Number of modules in Excalibur sensor (1[M] or 3[M]). "
             "[gap-fill]")
    mode_args.add_argument(
        "-b", "--block-size", type=int, dest="block_size", default=1,
        help="Size of blocks of contiguous frames. [interleave]")
    mode_args.add_argument(
        "-S", "--new-shape", type=int, dest="new_shape", nargs="*",
        help="Shape to map 1D dataset into. [reshape]")
    mode_args.add_argument(
        "-A", "--alternate", type=bool, dest="alternate", nargs="*",
        help="Whether each axis alternates. List of True/False for each axis. "
             "[reshape]")

    # Arguments that always apply
    other_args = parser.add_argument_group()
    other_args.add_argument(
        "-o", "--output", type=str, default=None, dest="output",
        help="Output file name. If None then generated as input file prefix "
             "with vds suffix.")
    other_args.add_argument(
        "-F", "--fill-value", type=int, dest="fill_value", default=0,
        help="Fill value for missing data and gaps.")
    other_args.add_argument(
        "--source-node", type=str, dest="source_node",
        default=VDSGenerator.source_node,
        help="Data node in source HDF5 files.")
    other_args.add_argument(
        "--target-node", type=str, dest="target_node",
        default=VDSGenerator.target_node, help="Data node in VDS file.")
    other_args.add_argument(
        "-l", "--log-level", type=int, dest="log_level", choices=[1, 2, 3],
        default=VDSGenerator.log_level,
        help="Logging level (off=3, info=2, debug=1).")

    args = parser.parse_args()
    args.shape = tuple(args.shape)

    if args.empty and args.files is None:
        parser.error(
            "To make an empty VDS you must explicitly define --files for the "
            "eventual raw datasets."
        )
    # Check correct number of files given for the selected mode
    if args.files is not None:
        if args.mode == "gap-fill" and len(args.files) != 1:
            parser.error("Gap fill can only operate on a single dataset.")
    if args.mode == "reshape" and args.new_shape is None:
        parser.error("Must provide --new-shape for reshape mode")

    return args


def main():
    """Run program."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    args = parse_args()

    if args.empty:
        source_metadata = dict(shape=args.shape, dtype=args.data_type)
    else:
        source_metadata = None

    if args.mode == "interleave":
        gen = InterleaveVDSGenerator(
            args.path,
            prefix=args.prefix, files=args.files,
            output=args.output,
            source=source_metadata,
            source_node=args.source_node,
            target_node=args.target_node,
            block_size=args.block_size,
            fill_value=args.fill_value,
            log_level=args.log_level)
    elif args.mode == "sub-frames":
        gen = SubFrameVDSGenerator(
            args.path,
            prefix=args.prefix, files=args.files,
            output=args.output,
            source=source_metadata,
            source_node=args.source_node,
            target_node=args.target_node,
            stripe_spacing=args.stripe_spacing,
            module_spacing=args.module_spacing,
            fill_value=args.fill_value,
            log_level=args.log_level)
    elif args.mode == "gap-fill":
        gen = ExcaliburGapFillVDSGenerator(
            args.path,
            prefix=args.prefix, files=args.files,
            output=args.output,
            source=source_metadata,
            source_node=args.source_node,
            target_node=args.target_node,
            modules=args.modules,
            chip_spacing=args.stripe_spacing,
            module_spacing=args.module_spacing,
            fill_value=args.fill_value,
            log_level=args.log_level
        )
    elif args.mode == "reshape":
        gen = ReshapeVDSGenerator(
            tuple(args.new_shape),
            args.path,
            prefix=args.prefix, files=args.files,
            output=args.output,
            source=source_metadata,
            source_node=args.source_node,
            target_node=args.target_node,
            fill_value=args.fill_value,
            log_level=args.log_level,
            alternate=args.alternate
        )
    else:
        raise NotImplementedError("Invalid VDS mode. Must be frames, "
                                  "interleave, sub-frames, gap-fill "
                                  "or reshape.")

    gen.generate_vds()


if __name__ == "__main__":
    sys.exit(main())
