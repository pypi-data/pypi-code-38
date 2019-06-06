# encoding: utf-8
from __future__ import absolute_import, division, print_function

import os
import tempfile

from .errors import (DataPoolIOError, FormatError, InvalidConfiguration,
                     InvalidOperationError)
from .instance.uniform_file_format import (check_rows, read_from_file,
                                           read_from_string)
from .julia_runner import JuliaRunner
from .matlab_runner import MatlabRunner
from .python_runner import PythonRunner
from .r_runner import RRunner
from .utils import iter_to_list

RUNNERS = {
    ".m": (MatlabRunner, "matlab"),
    ".jl": (JuliaRunner, "julia"),
    ".py": (PythonRunner, "python"),
    ".r": (RRunner, "r"),
}

SUPPORTED_EXTENSIONS = RUNNERS.keys()


def remove_first_and_empty_lines(text):
    text = "\n".join(line for line in text.split("\n")[1:] if line.strip())
    return text


class ScriptRunnerFactory:
    def __init__(self, config):
        self.cached_runners = {}
        self.config = config

    def get_runner(self, path_to_script):
        __, ext = os.path.splitext(path_to_script)
        if ext in self.cached_runners:
            return self.cached_runners[ext]

        if ext not in RUNNERS.keys():
            raise InvalidOperationError(
                "do not know how to run script {}.".format(path_to_script)
            )

        runner_class, config_section = RUNNERS[ext]
        try:
            section = getattr(self.config, config_section)
        except KeyError:
            msg = "configuration {} has no section {}".format(
                self.config.__file__, config_section
            )
            raise InvalidConfiguration(msg)

        try:
            exe = section.executable
        except KeyError:
            msg = (
                "configuration {} has no field 'executable' in " "section {}"
            ).format(self.config.__file__, config_section)
            raise InvalidConfiguration(msg)

        if exe.strip() == "":
            raise InvalidConfiguration(
                "executable in section {} is not configured".format(config_section)
            )

        r = runner_class(exe)
        r.start_interpreter()
        self.cached_runners[ext] = r
        return self.cached_runners[ext]


class ConversionRunner:
    def __init__(
        self,
        config,
        read_from_file=read_from_file,
        read_from_string=read_from_string,
        check_rows=check_rows,
    ):
        self.script_runner_factory = ScriptRunnerFactory(config)
        self.block_size = config.conversion.block_size
        self.read_from_string = read_from_string
        self.read_from_file = read_from_file
        self.check_rows = check_rows

    def _run_conversion(self, path_to_script, raw_data_path, data, verbose):

        try:
            raw_data_file_content = open(raw_data_path, "rb").read()
        except IOError as e:
            raise DataPoolIOError("could not read raw data: {}".format(e))

        runner = self.script_runner_factory.get_runner(path_to_script)

        # we create a tempfolder which encodes the path to the conversion script:
        tmpfldr = os.path.join(
            tempfile.tempdir, path_to_script.replace("/", "__").replace(".", "_")
        )
        os.makedirs(tmpfldr, exist_ok=True)

        raw_data_lines = raw_data_file_content.split(b"\n")
        yield "got {} lines from {}".format(len(raw_data_lines), raw_data_path)

        converted = []

        # we process raw data block wise to be able to handle huge raw files:
        for block_start in range(1, len(raw_data_lines) - 1, self.block_size):
            end = min(len(raw_data_lines) - 1, block_start + self.block_size - 1)
            yield "convert block from {} to {}".format(block_start, end)
            converted.append(
                self._convert_block(
                    runner,
                    path_to_script,
                    raw_data_lines,
                    block_start,
                    verbose,
                    tmpfldr,
                )
            )

        data[:] = ["\n".join(converted)]

    def _convert_block(
        self, runner, path_to_script, raw_data_lines, block_start, verbose, tmpfldr
    ):

        header = raw_data_lines[0]

        block = raw_data_lines[block_start : block_start + self.block_size]

        in_file = os.path.join(tmpfldr, "raw_data_{}.txt".format(block_start))
        out_file = os.path.join(tmpfldr, "out_data_{}.txt".format(block_start))

        # write raw data to temp file:
        try:
            with open(in_file, "wb") as fh:
                fh.write(header + b"\n")
                fh.write(b"\n".join(block))
        except IOError as e:
            raise DataPoolIOError(
                "could not write raw data to {}. reason: {}".format(in_file, e)
            ) from None

        # run conversion script
        try:
            exit_code = runner.run_script(
                path_to_script, in_file, out_file, verbose=verbose
            )
        except NameError:
            raise
        except Exception as e:
            raise InvalidOperationError(
                "running script failed. reason: {}".format(e)
            ) from None

        if exit_code != 0:
            raise InvalidOperationError(
                "running script failed. exit_code is {}.".format(exit_code)
            ) from None

        # check if output file exists and can be opened for reading.
        try:
            with open(out_file, "r", encoding="ascii") as fh:
                content = fh.read().strip()
                if block_start > 1:
                    content = remove_first_and_empty_lines(content)
        except IOError as e:
            raise DataPoolIOError(
                "created output file {} is not readable. reason: {}".format(out_file, e)
            ) from None
        except UnicodeDecodeError as e:
            raise FormatError(
                "created output file {} contains non-ascii chraracters: {}".format(
                    out_file, e
                )
            ) from None

        return content

    def _run_conversion_with_msg_handling(
        self, script_path, raw_data_path, status_callback, verbose
    ):

        data = []
        try:
            for msg in self._run_conversion(script_path, raw_data_path, data, verbose):
                if status_callback:
                    status_callback(msg)
        except Exception as e:
            return e
            return FormatError("could not run script {}: {}".format(script_path, e))

        data = "".join(data)
        return data

    def run_conversion(
        self,
        script_path,
        raw_data_path,
        *,
        verbose=False,
        status_callback=None,
        must_specify_source=False
    ):

        data = self._run_conversion_with_msg_handling(
            script_path, raw_data_path, status_callback, verbose
        )
        if isinstance(data, Exception):
            raise data
        try:
            rows = self.read_from_string(data, must_specify_source=must_specify_source)
        except ValueError as e:
            raise FormatError("reading result from {}: {}".format(script_path, e))
        msgs = self.check_rows(rows)
        if msgs:
            raise FormatError(
                "{} errors in result from {}. first is: {}".format(
                    len(msgs), script_path, msgs[0]
                )
            )

        return rows

    @iter_to_list
    def check_conversion(
        self,
        script_path,
        raw_data_path,
        *,
        verbose=False,
        status_callback=None,
        must_specify_source=False
    ):

        data = self._run_conversion_with_msg_handling(
            script_path, raw_data_path, status_callback, verbose
        )
        if isinstance(data, Exception):
            yield data
            return

        output_file = os.path.join(tempfile.mkdtemp(), "output.csv")
        with open(output_file, "w") as fh:
            fh.write(data)
        try:
            rows = self.read_from_file(
                output_file, must_specify_source=must_specify_source
            )
        except Exception as e:
            yield Exception("reading output failed: {}".format(e))
            return

        msgs = self.check_rows(rows, must_specify_source)
        for i, msg in enumerate(msgs):
            if i >= 10:
                yield Exception(
                    "... skip remaining {} / {} msgs".format(len(msgs) - i, len(msgs))
                )
                return
            yield Exception("invalid output file {}: {}".format(output_file, msg))
            return

        yield output_file, rows
