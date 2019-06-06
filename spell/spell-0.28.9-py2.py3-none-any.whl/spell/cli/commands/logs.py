# -*- coding: utf-8 -*-
from backports.shutil_get_terminal_size import get_terminal_size
import click
from halo import Halo
import sys
import time

from spell.cli.exceptions import (
    ExitException,
    api_client_exception_handler,
)
from spell.cli.log import logger
from spell.cli.utils import with_emoji, ellipses


@click.command(name="logs",
               short_help="Retrieve logs for a run")
@click.argument("run_id")
@click.option("-d", "--delay", is_flag=True,
              help="Replay delay between log entries")
@click.option("-f", "--follow", is_flag=True,
              help="Follow log output")
@click.option("-n", "--tail", default=0,
              help="Show the last NUM lines")
@click.option("-v", "--verbose", is_flag=True,
              help="Print additional information")
@click.pass_context
def logs(ctx, run_id, delay, follow, tail, verbose, stop_status=None, run_warning=False):
    """
    Retrieve logs for a run specified by RUN_ID.

    Streams logs for the specified run. For runs with a large number of log lines
    the `--tail N` option allows the user to print only the last N lines. When
    following with `--follow` use `Ctrl + C` to detach.
    """
    error_found = False
    # grab the logs from the API
    client = ctx.obj["client"]
    utf8 = ctx.obj["utf8"]
    with api_client_exception_handler():
        logger.info("Retrieving run logs from Spell")
        try:
            log_printer = LogPrinter(
                utf8_enabled=utf8,
                delay=delay,
                verbose=verbose or not sys.stdout.isatty(),
            )
            status = ""
            for entry in client.get_run_log_entries(run_id, follow=follow, offset=-tail):
                log_printer.process_entry(entry)
                if entry.level == "error":
                    error_found = True
                if entry.status_event:
                    status = entry.status or ""
                    if stop_status is not None and status == stop_status:
                        break
            if stop_status is not None and status != stop_status:
                raise ExitException("Run ended before entering the {} state".format(stop_status))
            elif error_found and not verbose:
                msg = "Use 'spell logs {} --verbose' to examine cause of error.".format(run_id)
                click.echo(with_emoji(u"ℹ️", msg, utf8))
        except KeyboardInterrupt:
            if stop_status is not None:
                raise click.Abort()
            click.echo()
            if run_warning:
                click.echo(with_emoji(u"✨", "Your run is still running remotely.", utf8))
                click.echo(with_emoji(u"✨", "Use 'spell kill {}' to terminate your run".format(run_id), utf8))
            click.echo(with_emoji(u"✨", "Use 'spell logs {}' to view logs again".format(run_id), utf8))


class LogPrinter(object):

    default_emoji = u"✨"

    ascii_spinner = {
        "interval": 100,
        "frames": ["|", "/", "-", "\\"],
    }

    star_spinner = {
        "interval": 200,
        "frames": [u"⭐", u"🌟"],
    }

    status_emoji = {
        "running":  u"✨",
        "complete": u"🎉",
        "failed":   u"💥",
        "killing":  u"💫",
        "killed":   u"💀",
        "stopping": u"💫",
        "stopped":  u"✋",
    }

    def __init__(self, utf8_enabled=True, delay=False, verbose=False):
        self.delay = delay
        self.prev_datetime = None

        self.verbose = verbose

        self.utf8_enabled = utf8_enabled
        self.wait_spinner = self.star_spinner if utf8_enabled else self.ascii_spinner

        self.spinner = None
        self.spinning = False
        self.spinner_status = None

    def process_entry(self, entry):
        self.simulate_delay(entry.timestamp)

        status = entry.status
        level = entry.level
        if entry.status_event:
            self.process_status_change(status)

        message = entry.log
        if self.spinner and level == "error":
            self.fail_spinner(message)
        elif self.spinner and status != "running":
            self.spinner and self.spinner.start()
            self.spinning = True
            self.set_spinner_message(message)
        else:
            self.spinner and self.spinning and self.spinner.stop()
            self.spinning = False
            click.echo(message)

    def process_status_change(self, status):
        self.end_spinner()
        custom_emoji = self.status_emoji.get(status)
        if custom_emoji or self.verbose:
            self.spinner and self.spinner.stop()
            if self.utf8_enabled:
                click.echo((custom_emoji or self.default_emoji) + " ", nl=False)
            self.spinner and self.spinner.start()
        else:
            self.begin_spinner(status)

    def begin_spinner(self, status):
        """Create and start a new spinner."""
        self.spinner_status = status.title() + ellipses(self.utf8_enabled)
        self.spinner = Halo(spinner=self.wait_spinner)
        self.spinner.start(self.spinner_status)

    def end_spinner(self):
        """Stop and release the current spinner."""
        if not self.spinner:
            return
        self.set_spinner_message("done")
        if self.utf8_enabled:
            self.spinner.stop_and_persist(symbol=self.default_emoji)
        else:
            self.spinner.stop()
            click.echo(self.spinner_status + " done")
        self.spinner = None

    def fail_spinner(self, message):
        """Fail the current spinner with a message, release."""
        if not self.spinner:
            return
        self.spinner.fail(message)
        self.spinner = None

    def set_spinner_message(self, message):
        text = self.spinner_status
        if message:
            text += " " + message

        # truncate text to terminal width
        cols = get_terminal_size().columns
        cols -= 3  # subtract spinner columns
        if len(text) > cols:
            text = text[:cols-1] + ellipses(self.utf8_enabled)

        self.spinner.text = text

    def simulate_delay(self, dt):
        if self.delay and self.prev_datetime:
            delta = (dt - self.prev_datetime).total_seconds()
            if delta > 0:
                time.sleep(delta)
        self.prev_datetime = dt
