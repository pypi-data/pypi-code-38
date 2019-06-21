#!/usr/bin/env python3
"""Repack a ZIP file
"""
# pylint: disable=invalid-name,redefined-builtin
import argparse
import copy
import datetime
import glob
import os
import re
import stat
import struct
import sys
import types

from typing import BinaryIO, Callable, List, Optional, Tuple, Union, cast
from zipfile import ZipFile, ZipInfo


__version__ = "0.5.1"


class Arguments(types.SimpleNamespace):
    """Data holder for program arguments"""
    inplace: bool = False
    glob: bool = False
    normalize_access_rights = False
    date_time: Optional[datetime.datetime] = None
    inputs: List[str]
    output: str = ""
    verbosity: int = 0

    def __init__(self):
        self.inputs = []
        super().__init__()

    def __str__(self) -> str:
        cls_name = self.__class__.__name__
        args = []
        for key, val in self.__dict__.items():
            args.append(f"{key}={val!r}")
        return f"{cls_name}({', '.join(args)})"


FilterFunc = Callable[[ZipInfo, bytes], Optional[Tuple[ZipInfo, bytes]]]


def parse_args(argv=None) -> Arguments:
    """Parse rezip arguments"""
    if argv is None:
        argv = sys.argv
    p = argparse.ArgumentParser()
    p.add_argument("--quiet", "-q", dest="verbosity", action="store_const", const=-1,
                   help="Produce less output")
    p.add_argument("--verbose", "-v", dest="verbosity", action="count", default=0,
                   help="Be more verbose")
    p.add_argument("--glob", "-g", action="store_true", default=False,
                   help="Treat the input file names as shell glob patterns.")
    p.add_argument("--inplace", action="store_true", default=False,
                   help="Repack in place")
    p.add_argument("--normalize-access-rights", action="store_true",
                   default=False,
                   help="Normalize Unix access rights")
    p.add_argument("--date-time",
                   help=("Set date time to the provided value. "
                         "rezip keeps the date time of ZIP file members "
                         "if this option is not given."))
    p.add_argument("--output", "-o",
                   help="Name of the output file")
    p.add_argument("inputs", nargs="*",
                   help="Name of the ZIP or wheel file(s) to repack")
    args = cast(Arguments, p.parse_args(argv[1:], namespace=Arguments()))
    if args.glob:
        # Expand globs
        input_files = []
        for pattern_in in args.inputs:
            files_in = glob.glob(pattern_in, recursive=True)
            if not files_in:
                print("Warning: No files found for glob pattern {pattern_in!r}", file=sys.stderr)
            input_files.extend(files_in)
        args.inputs = input_files
    if args.inplace:
        if args.output:
            p.error("argument output invalid if used together with argument --inplace")
        if os.path.exists(args.output):
            p.error("internal error: {args.output} exists")
    elif not args.inputs:
        if args.output:
            p.error("missing input argument")
    elif len(args.inputs) > 1:
        p.error("only one input argument allowed "
                "(in --inplace mode multiple input arguments are allowed)")
    else:  # not arg.inplace and len(args.inputs) == 1
        if not args.output:
            p.error("argument output is missing (use --inplace for inplace repack)")
        if args.inputs == [args.output]:
            p.error("arguments input and output are equal (use --inplace for inplace repack)")
    if args.date_time:
        date_time_str = cast(str, args.date_time)
        if re.match("^[0-9]+$", date_time_str):
            args.date_time = datetime.datetime.utcfromtimestamp(int(date_time_str))
        else:
            try:
                args.date_time = datetime.datetime.fromisoformat(date_time_str)
            except ValueError:
                p.error("argument --date-time has invalid format")
    return args


ZIP_INFO_ATTRIBUTES = [
    'comment', 'compress_type', 'create_system', 'create_version', 'date_time',
    'external_attr', 'extra', 'extract_version', 'filename', 'flag_bits',
    'internal_attr', 'reserved', 'volume',
]

def format_modifications(zinfo_old: ZipInfo, data_old: bytes,
                         zinfo_new: ZipInfo, data_new: bytes) -> str:
    """Check for modifications"""
    def get_create_system_name(num):
        return {0: "fat", 3: "unx"}.get(num, " 0x%x" % num)
    modifications = []
    if zinfo_old.filename != zinfo_new.filename:
        prefix = f"{zinfo_old.filename} -> {zinfo_new.filename}"
    else:
        prefix = f"{zinfo_old.filename}"
    for key in ZIP_INFO_ATTRIBUTES:
        if key in ["filename"]:
            continue
        val_old = getattr(zinfo_old, key)
        val_new = getattr(zinfo_new, key)
        if val_old != val_new:
            if key == "date_time":
                modifications.append(f"{to_isoformat(val_old)} -> {to_isoformat(val_new)}")
            elif key == "create_system":
                modifications.append(f"{get_create_system_name(val_old)} -> {get_create_system_name(val_new)}")
            elif key == "external_attr":
                if (zinfo_old.external_attr & 0xffff) != (zinfo_new.external_attr & 0xffff):
                    modifications.append(f"external_attr: {val_old} -> {val_new}")
                else:
                    filemode_old = zinfo_old.external_attr >> 16
                    filemode_new = zinfo_new.external_attr >> 16
                    modifications.append("%06o -> %06o" % (filemode_old, filemode_new))
            else:
                modifications.append(f"{key}: {val_old!r} -> {val_new!r}")
    if data_old != data_new:
        modifications.append("Modified Data")
    if modifications:
        return "repack %s: %s" % (prefix, ", ".join(modifications))
    else:
        return "repack %s" % prefix


def rezip(infile: Union[os.PathLike, str, BinaryIO],
          outfile: Union[os.PathLike, str, BinaryIO],
          filter: Optional[FilterFunc] = None,
          verbosity=0) -> None:
    """Repack contents of *infile* to *outfile*.

    :arg infile: Input ZIP file
    :arg outfile: Output ZIP file
    :arg filter: Filter function to modify or
        update ZIP file members

    If given, the callable *filter* is used to map input members to
    output members. For each member in the input ZipFile *filter* is
    called with the :class:`~zipfile.ZipInfo` object and the bytes of
    the member. It must return a tuple containing the
    :class:`~zipfile.ZipInfo` object and the bytes to write to
    *outfile*.  So, *filter* could be used to change the file name,
    UNIX access rights or the contents of a ZipFile member.  If
    *filter* returns `None` then the member will be skipped and not
    written to *outfile*. *filter* is allowed to modify its input
    arguments and return the modified arguments.

    """
    with ZipFile(infile, mode="r") as zin:
        with ZipFile(outfile, mode="w") as zout:
            for zinfo in zin.infolist():
                data = zin.read(zinfo.filename)
                if filter:
                    zinfo_and_data = filter(copy.copy(zinfo), data)
                    if zinfo_and_data is None:
                        # Skip the current member
                        if verbosity >= 1:
                            print(f" {zinfo.filename}: SKIPPED")
                        continue
                    zinfo_new, data_new = zinfo_and_data
                if verbosity >= 1:
                    print(" %s" % format_modifications(zinfo, data, zinfo_new, data_new))
                zout.writestr(zinfo_new, data_new)


def is_elf_executable(data: bytes) -> bool:
    """Check if *data* is likely an ELF executable (or shared library)."""
    if len(data) >= 40 and data[:0x04] == b"\x7fELF":
        # Looks like an ELF header, check e_type
        e_type_bytes = data[0x10:0x12]
        e_type = struct.unpack("h", e_type_bytes)[0]
        # ET_EXEC = 0x02 (e.g., static linked programs or non-pie programs)
        # ET_DYN = 0x03 (e.g., shared libraries or pie programs)
        # The following check is endianness-independent, so we have less fields
        # to interpret. Note that the teensy 45 byte ELF program has an invalid
        # endianness field.
        return e_type in (0x0002, 0x0200, 0x0003, 0x0300)
    else:
        return False

_MACH0_MAGICS = frozenset([
    b"\xca\xfe\xba\xbe",
    b"\xbe\xba\xfe\xca",
    b"\xfe\xed\xfa\xce",
    b"\xce\xfa\xed\xfe",
    b"\xfe\xed\xfa\xcf",
    b"\xcf\xfa\xed\xfe",
])

def is_mach0_executable(data: bytes) -> bool:
    """Check if *data* is likely a Mach-0 executable or shared library."""
    return data[0:4] in _MACH0_MAGICS


def is_executable(data: bytes) -> bool:
    """Check if *data* is likely an executable

    Note: For now, *data* is checked for looking like an ELF or Mach-0
    executable or shared library.

    """
    return is_elf_executable(data) or is_mach0_executable(data)


def to_isoformat(date_time: Union[Tuple, datetime.datetime, int], sep=" ") -> str:
    """Format *date_time* in isoformat"""
    if isinstance(date_time, (tuple, list)):
        return datetime.datetime(*date_time).isoformat(sep=sep)
    elif isinstance(date_time, int):
        return datetime.datetime.fromtimestamp(date_time).isoformat(sep=sep)
    elif isinstance(date_time, datetime.datetime):
        return date_time.isoformat(sep=sep)
    else:
        raise TypeError(f"date_time argument of invalid type: {type(date_time).__qualname__}")


class DefaultFilter:
    """The default rezip filter"""

    def __init__(self, args: Arguments) -> None:
        self.args = args

    def __call__(self, zinfo: ZipInfo, data: bytes) -> Tuple[ZipInfo, bytes]:
        """Normalize Unix access rights and/or set date info"""
        if self.args.normalize_access_rights:
            zinfo.create_system = 3  # Unix
            unix_filemode = 0
            dos_filemode = 0
            if zinfo.is_dir():
                unix_filemode = 0o40755
                dos_filemode = 0x10  # MS-DOS directory flag
            elif ((zinfo.external_attr >> 16) & 0o111 != 0) or is_executable(data):
                unix_filemode = 0o100755
            else:
                unix_filemode = 0o100644
            zinfo.external_attr = (unix_filemode << 16) | dos_filemode

        if self.args.date_time:
            zinfo.date_time = self.args.date_time.timetuple()[0:6]

        return zinfo, data


def main(argv=None):
    """Rezip Main program"""
    args = parse_args(argv)
    if args.verbosity >= 3:
        print("args:", args)

    # determine filter
    filter_func: Optional[FilterFunc]
    if args.normalize_access_rights or args.date_time:
        filter_func = DefaultFilter(args)
    else:
        filter_func = None

    if args.inplace:
        for file_in in args.inputs:
            file_out = f"{file_in}.rezip-tmp"
            if args.verbosity >= 1:
                print(f"Repack {file_in} -> {file_out}")
            rezip(file_in, file_out, filter_func)
            os.replace(file_out, file_in)
    elif len(args.inputs) == 1:
        file_in = args.inputs[0]
        file_out = args.output
        if args.verbosity >= 1:
            print(f"Repack {file_in} -> {file_out}")
            rezip(file_in, file_out, filter_func, verbosity=args.verbosity)
    elif not args.inputs:
        pass  # no input specified
    else:
        raise RuntimeError(f"Invalid state: args.inputs = {args.inputs!r}")


if __name__ == "__main__":
    sys.exit(main())
