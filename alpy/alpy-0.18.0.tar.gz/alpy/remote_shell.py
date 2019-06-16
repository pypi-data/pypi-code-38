# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import pathlib
import random

import alpy.utils


def random_delimiter():
    return f"eof{random.randrange(1000000):06}"


def upload_text_file(console, prompt, source_filename, destination_filename):
    delimiter = random_delimiter()
    console.expect_exact(prompt)
    # Interactive shell line wrapping can cut the delimiter if the destination
    # filename is long enough. To mitigate this, we type the name on
    # one line and then type the delimiter on a new line.
    console.sendline(f"cat > {destination_filename} \\")
    console.expect_exact("\n")
    # Delimiter is quoted in order to disable parameter expansion etc. in the
    # here-document.
    console.sendline(f"<<'{delimiter}'")
    console.expect_exact(delimiter)
    console.send(pathlib.Path(source_filename).read_bytes())
    console.sendline(delimiter)
    console.expect_exact(delimiter)
    console.expect_exact("\n")


def execute_program(console, prompt, program, timeout):
    console.expect_exact(prompt)
    # Interactive shell line wrapping can cut a pattern if the program filename
    # is long enough. To mitigate this, we type the filename on a separate line.
    console.sendline(program + " \\")
    console.expect_exact("\n")
    command_part_2 = "; echo Exit status: $?."
    console.sendline(command_part_2)
    console.expect_exact(command_part_2)
    console.expect_exact("\n")
    console.expect(r"Exit status: (\d+).", timeout=timeout)
    exit_status_bytes = console.match.group(1)
    console.expect_exact("\n")
    return int(exit_status_bytes.decode())


def check_execute_program(console, prompt, program, timeout):
    exit_status = execute_program(console, prompt, program, timeout)

    if exit_status != 0:
        raise alpy.utils.NonZeroExitCode(
            f"Program {program} exited with non-zero code {exit_status}"
        )


def upload_and_execute_script(console, prompt, filename, timeout):

    log = alpy.utils.context_logger(__name__)
    logger = logging.getLogger(__name__)

    with log("Type in script " + filename):
        upload_text_file(console, prompt, filename, filename)
        console.expect_exact(prompt)
        command = "chmod +x " + filename
        console.sendline(command)
        console.expect_exact(f"{command}\r\n")

    with log("Run script " + filename):
        if timeout != console.timeout:
            logger.info(f"Timeout, seconds: {timeout}")
        check_execute_program(console, prompt, "./" + filename, timeout)
