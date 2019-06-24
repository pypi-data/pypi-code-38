"""Command line utility for working with remote anonymization servers.

Modelled after command line interfaces of git and docker. Takes information from command line arguments but also saves
more permanent information in a settings file"""

import argparse
import random
import string
import sys
import pathlib
import os
import textwrap

from collections import Counter

from anonapi.batch import BatchFolder, JobBatch
from anonapi.client import WebAPIClient, APIClientException
from anonapi.objects import RemoteAnonServer
from anonapi.responses import (
    format_job_info_list,
    parse_job_infos_response,
    APIParseResponseException,
    JobsInfoList,
    JobStatus)
from anonapi.settings import (
    AnonClientSettings,
    DefaultAnonClientSettings,
    AnonClientSettingsFromFile,
)


class AnonClientTool:
    """Performs several actions via the Anonymization web API interface.

    One abstraction level above anonymization.client.WebAPIClient. Client deals with https calls, get and post,
    this tool should not do any http operations, and instead deal with seresponse =rvers and jobs.
    """

    def __init__(self, username, token):
        """Create an anonymization web API client tool

        Parameters
        ----------
        username: str
            use this when calling API
        token:
            API token to use when calling API

        """
        self.username = username
        self.token = token

    def get_client(self, url):
        """Create an API client with the information in this tool

        Returns
        -------
        WebAPIClient
        """
        client = WebAPIClient(hostname=url, username=self.username, token=self.token)
        return client

    def get_server_status(self, server: RemoteAnonServer):
        """

        Returns
        -------
        str:
            status of the given server
        """
        client = self.get_client(server.url)
        try:
            client.get_documentation()  # don't care about documentation return value now, just using as test
            status = f"OK: {server} is online and responsive"
        except APIClientException as e:
            status = f"ERROR: {server} is not responding properly. Error:\n {str(e)}"

        return status

    def get_job_info(self, server: RemoteAnonServer, job_id: int):
        """Full description of a single job

        Parameters
        ----------
        server: :obj:`RemoteAnonServer`
            get job info from this server
        job_id: str
            id of job to get info for


        Returns
        -------
        str:
            string describing job, or error if job could not be found

        """

        client = self.get_client(server.url)

        try:
            response = client.get("get_job", job_id=job_id)
            info_string = f"job {job_id} on {server.name}:\n\n"
            info_string += "\n".join([str(x) for x in list(response.items())])

        except APIClientException as e:
            info_string = f"Error getting job info from {server}:\n{str(e)}"
        return info_string

    def get_job_info_list(self, server: RemoteAnonServer, job_ids):
        """Get a list of info on the given job ids. Info is shorter then full info

        Parameters
        ----------
        server: RemoteAnonServer
            get job info from this server
        job_ids: List(str)
            list of jobs to get info for

        Returns
        -------
        JobsInfoList:
            info describing each job. Info is omitted if job id could not be found

        Raises
        ------
        ClientToolException:
            if something goes wrong getting jobs info from server

        """
        client = self.get_client(server.url)
        try:
            return JobsInfoList(
                parse_job_infos_response(client.get("get_jobs_list", job_ids=job_ids))
            )
        except APIClientException as e:
            raise ClientToolException(f"Error getting jobs from {server}:\n{str(e)}")
        except APIParseResponseException as e:
            raise ClientToolException(
                f"Error parsing server response: from {server}:\n{str(e)}"
            )

        return response

    def get_jobs(self, server: RemoteAnonServer):
        """Get list of info on most recent jobs in server

        Parameters
        ----------
        server: :obj:`RemoteAnonServer`
            get job info from this server

        Returns
        -------
        str:
            string describing job, or error if job could not be found

        Raises
        ------
        APIClientException:
            if something goes wrong getting jobs info from server

        """
        job_limit = 50  # reduce number of jobs shown for less screen clutter.

        client = self.get_client(server.url)
        try:
            response_raw = client.get("get_jobs")
            response = parse_job_infos_response(response_raw)

            info_string = f"most recent {job_limit} jobs on {server.name}:\n\n"
            info_string += "\n" + format_job_info_list(response)
            return info_string

        except APIClientException as e:
            response = f"Error getting jobs from {server}:\n{str(e)}"
        except APIParseResponseException as e:
            response = f"Error parsing server response: from {server}:\n{str(e)}"

        return response

    def cancel_job(self, server: RemoteAnonServer, job_id: int):
        """Cancel the given job

        Returns
        -------
        str
            a string describing success or any API error
        """
        client = self.get_client(server.url)
        try:
            _ = client.post("cancel_job", job_id=job_id)
            info = f"Cancelled job {job_id} on {server.name}"
        except APIClientException as e:
            info = f"Error cancelling job on{server}:\n{str(e)}"
        return info

    def reset_job(self, server, job_id):
        """Reset job status, error and downloaded/processed counters

        Returns
        -------
        str
            a string describing success or any API error
        """

        client = self.get_client(server.url)
        try:
            _ = client.post(
                "modify_job",
                job_id=job_id,
                status="ACTIVE",
                files_downloaded=0,
                files_processed=0,
                error=" ",
            )
            info = f"Reset job {job_id} on {server}"
        except APIClientException as e:
            info = f"Error resetting job on{server.name}:\n{str(e)}"
        return info

        pass


class AnonCommandLineParser:
    """Parses commands from commandline and launches actions accordingly.

    Tries to emulate command line structure used by git and docker: nested subcommands have their own help,
    certain data, like urls for web API servers, username, are persisted in settings file.

    """

    def __init__(self, client_tool: AnonClientTool, settings: AnonClientSettings):
        """Create a command line parser

        Parameters
        ----------
        client_tool: AnonClientTool
            The tool that that communicates with the web API.
        settings: AnonClientSettings
            Settings object to use for reading and writing settings.

        """
        self.client_tool = client_tool
        self.settings = settings
        self.parser = self.create_parser()

    @staticmethod
    def current_dir():
        """Return full path to the folder this command line parser is called from"""
        return os.getcwd()

    def create_parser(self):
        """The thing that actually parses the input commands.

        Notes
        -----
        Uses subparsers and the set_defaults(func=foo()) trick to link functions to each subparser. func is later
        passed along at each parse and later executed in execute_command()

        """
        # create the top-level parser
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                """
                anonymization web API tool
                Controls remote anonymization servers via the anonymization web API       
                Use the commands below with -h for more info
            """
            ),
        )
        parser.set_defaults(func=lambda: parser.print_help())
        subparsers = parser.add_subparsers()

        # ============================================================================================
        status_parser = subparsers.add_parser(
            "status",
            help="show tool status",
            description="show overview of this tool's status",
        )
        status_parser.set_defaults(func=self.get_status)

        # ============================================================================================
        server_parser = subparsers.add_parser(
            "server",
            help="manage anonymization servers",
            description="manage anonymization servers",
        )
        self.add_server_actions(parser=server_parser)

        # ============================================================================================
        job_parser = subparsers.add_parser(
            "job",
            help="manage anonymization jobs",
            description="manage anonymization jobs on active server",
        )
        self.add_job_actions(parser=job_parser)

        # ============================================================================================
        user_parser = subparsers.add_parser(
            "user",
            help="manage API credentials",
            description="manage username and API key",
        )
        self.add_user_actions(parser=user_parser)

        # ============================================================================================
        batch_parser = subparsers.add_parser(
            "batch",
            help="Manage job batch",
            description="Work with multiple jobs at the same time. A batch is saved in a single directory",
        )
        self.add_batch_actions(parser=batch_parser)

        return parser

    def add_server_actions(self, parser):
        parser.set_defaults(func=lambda: parser.print_help())
        parser_sub = parser.add_subparsers()

        parser_add = parser_sub.add_parser(
            "add",
            help="add a server",
            description="add an anonymization server to the list of servers",
        )
        parser_add.add_argument(
            "short_name", type=str, help="short name to use in commands"
        )
        parser_add.add_argument(
            "url", type=str, help="full path including https:// to server"
        )
        parser_add.set_defaults(func=self.server_add)

        parser_remove = parser_sub.add_parser(
            "remove",
            help="remove a server",
            description="remove a server from list of servers",
        )
        parser_remove.add_argument(
            "short_name", type=str, help="short name of server to remove"
        )
        parser_remove.set_defaults(func=self.server_remove)

        parser_add = parser_sub.add_parser(
            "list", help="list anon servers", description="list anon servers"
        )
        parser_add.set_defaults(func=self.server_list)

        parser_status = parser_sub.add_parser(
            "status",
            help="get status of active server",
            description="get status of active server, or given server",
        )
        parser_status.add_argument(
            "short_name",
            nargs="?",
            type=str,
            help="optional short name of server to show status for. Defaults to active server",
        )
        parser_status.set_defaults(func=self.server_status)

        parser_jobs = parser_sub.add_parser(
            "jobs", help="list latest 50 jobs", description="list latest 50 jobs"
        )
        parser_jobs.add_argument(
            "short_name",
            nargs="?",
            type=str,
            help="optional short name of server to list jobs for. Defaults to active server",
        )
        parser_jobs.set_defaults(func=self.server_jobs)

        parser_activate = parser_sub.add_parser(
            "activate",
            help="set active server",
            description="set given server as active. Commands that require a server"
            " will use this server by default from now on",
        )
        parser_activate.add_argument(
            "short_name", type=str, help="short name of server to activate"
        )
        parser_activate.set_defaults(func=self.server_activate)

    def add_job_actions(self, parser):
        parser.set_defaults(func=lambda: parser.print_help())
        parser_sub = parser.add_subparsers()

        parser_info = parser_sub.add_parser(
            "info",
            help="print job info",
            description="query the active server to retrieve info for this job",
        )
        parser_info.add_argument("job_id", type=int, help="Job id to check")
        parser_info.set_defaults(func=self.get_job_info)

        parser_restart = parser_sub.add_parser(
            "reset",
            help="reset job, process again",
            description="reset job, process again",
        )
        parser_restart.add_argument("job_id", type=int, help="Job id to reset")
        parser_restart.set_defaults(func=self.job_reset)

        parser_cancel = parser_sub.add_parser(
            "cancel", help="sets job status to inactive", description="cancel job"
        )
        parser_cancel.add_argument("job_id", type=int, help="Job id to cancel")
        parser_cancel.set_defaults(func=self.job_cancel)

        parser_list = parser_sub.add_parser(
            "list",
            help="List info for multiple job ids",
            description="list info for space-separated list of job ids",
        )
        parser_list.add_argument(
            "job_ids", help="space-separated list of job ids", nargs="*"
        )
        parser_list.set_defaults(func=self.get_job_info_list)

    def add_user_actions(self, parser):
        parser.set_defaults(func=lambda: parser.print_help())
        parser_sub = parser.add_subparsers()

        parser_info = parser_sub.add_parser(
            "info",
            help="print current credentials",
            description="print current credentials",
        )
        parser_info.set_defaults(func=self.user_info)

        parser_username = parser_sub.add_parser(
            "set_username", help="set username", description="print job info"
        )
        parser_username.add_argument("user_name", type=str, help="set username to this")
        parser_username.set_defaults(func=self.set_username)

        parser_get_api_token = parser_sub.add_parser(
            "get_token",
            help="retrieve an API token for the current user. "
            "Requires valid UMCN credentials",
            description="retrieve an api token for the current user. "
            "Requires valid UMCN credentials",
        )
        parser_get_api_token.set_defaults(func=self.get_token)

    def add_batch_actions(self, parser):
        parser.set_defaults(func=lambda: parser.print_help())
        parser_sub = parser.add_subparsers()

        parser_batch_info = parser_sub.add_parser(
            "info",
            help="print overview of all jobs in current folder",
            description="show batch in current folder",
        )
        parser_batch_info.set_defaults(func=self.batch_info)

        parser_batch_status = parser_sub.add_parser(
            "status", help="get_status for entire batch", description="get batch status"
        )
        parser_batch_status.set_defaults(func=self.batch_status)

        parser_batch_reset = parser_sub.add_parser(
            "reset", help="reset every job in this batch", description="reset batch"
        )
        parser_batch_reset.set_defaults(func=self.batch_reset)

        parser_batch_init = parser_sub.add_parser(
            "init",
            help="Create empty batch in current folder",
            description="Create empty batch in current folder",
        )
        parser_batch_init.set_defaults(func=self.batch_init)

        parser_batch_delete = parser_sub.add_parser(
            "delete",
            help="Delete batch in current folder",
            description="Delete batch in current folder",
        )
        parser_batch_delete.set_defaults(func=self.batch_delete)

        parser_batch_add_ids = parser_sub.add_parser(
            "add",
            help="Add job ids to batch",
            description="Add the given space-separated list of jobs ids to batch. Will not add already existing ids",
        )
        parser_batch_add_ids.add_argument(
            "ids", type=str, help="space-separate list of job ids to add", nargs="*"
        )
        parser_batch_add_ids.set_defaults(func=self.batch_add_ids)

        parser_batch_remove_ids = parser_sub.add_parser(
            "remove",
            help="Remove job ids from batch",
            description="Remove the given space-separated list of jobs ids from batch",
        )
        parser_batch_remove_ids.add_argument(
            "ids", type=str, help="space-separate list of job ids to remove", nargs="*"
        )
        parser_batch_remove_ids.set_defaults(func=self.batch_remove_ids)

        parser_batch_cancel = parser_sub.add_parser(
            "cancel",
            help="Cancel all jobs in this batch",
            description="Cancel all",
        )
        parser_batch_cancel.set_defaults(func=self.batch_cancel)

        parser_batch_reset_error = parser_sub.add_parser(
            "reset_error",
            help=f"Reset all jobs with error status in current batch",
            description="Reset all error jobs",
        )
        parser_batch_reset_error.set_defaults(func=self.batch_reset_errors)

    def get_status(self):
        """Get general status of this tool, show currently active server etc.

        Returns
        -------
        str
        """
        server_list = self.create_server_list()
        status = (
            f"Available servers (* = active)\n\n"
            f"{server_list}\n"
            f"Using username: '{self.settings.user_name}'\n"
            f"Reading settings from \n"
            f"{self.settings}"
        )

        self.print_to_console(status)

    def server_add(self, short_name, url):
        """Add a server to the list of servers in settings """

        server = RemoteAnonServer(name=short_name, url=url)
        self.settings.servers.append(server)
        self.settings.save()
        self.print_to_console(f"added {server} to list")

    def server_list(self):
        """show all servers in settings """
        server_list = self.create_server_list()
        self.print_to_console(f"Available servers (* = active):\n\n{server_list}")

    def create_server_list(self):
        server_list = ""
        for server in self.settings.servers:
            line = f"{server.name:<10} {server.url}"
            if server == self.settings.active_server:
                line = "* " + line
            else:
                line = "  " + line
            server_list += line + "\n"
        return server_list

    def server_remove(self, short_name):
        """Remove a servers from list in settings"""
        server = self.get_server_by_name(short_name)
        if self.settings.active_server == server:
            # active server was removed, so it can no longer be active.
            self.settings.active_server = None

        self.settings.servers.remove(server)
        self.settings.save()
        self.print_to_console(f"removed {server} from list")

    def server_status(self, short_name=None):
        """Check whether active server is online and responding like an anonymization web API, optionaly check given
        server instead of active
        """

        server = self.get_server_or_active_server(short_name)
        response = self.client_tool.get_server_status(server)
        self.print_to_console(str(response))

    def server_jobs(self, short_name=None):
        """List latest 100 jobs for active server, or given server
        """
        server = self.get_server_or_active_server(short_name)
        response = self.client_tool.get_jobs(server)
        self.print_to_console(response)

    def server_activate(self, short_name):
        """Set given server as activate server, meaning subsequent operations will use this server.
        """
        server = self.get_server_by_name(short_name)
        self.settings.active_server = server
        self.settings.save()
        self.print_to_console(f"Set active server to {server}")

    def get_server_by_name(self, short_name):
        """Get the server with given name from the list of servers

        Raises
        ------
        AnonCommandLineParserException:
            If server with that name cannot be found in list of servers

        """
        server_list = {x.name: x for x in self.settings.servers}
        if short_name not in server_list.keys():
            msg = f"Unknown server '{short_name}'. Please choose one of {[x.name for x in self.settings.servers]}"
            raise AnonCommandLineParserException(msg)

        return server_list[short_name]

    def get_job_info(self, job_id):
        """ Query active server for info on this job
        """
        server = self.get_active_server()
        info = self.client_tool.get_job_info(server=server, job_id=job_id)
        self.print_to_console(info)

    def get_job_info_list(self, job_ids):
        """ Query active server for info on this job
        """
        server = self.get_active_server()
        info = self.client_tool.get_job_info_list(server=server, job_ids=job_ids)
        self.print_to_console(info)

    def job_reset(self, job_id):
        server = self.get_active_server()
        info = self.client_tool.reset_job(server=server, job_id=job_id)
        self.print_to_console(info)

    def job_cancel(self, job_id):
        server = self.get_active_server()
        info = self.client_tool.cancel_job(server=server, job_id=job_id)
        self.print_to_console(info)

    def get_server_or_active_server(self, short_name=None):
        """Return server corresponding to short_name, or active server"""
        if short_name:
            server = self.get_server_by_name(short_name)
        else:
            server = self.get_active_server()
        return server

    def get_active_server(self):
        """ Active server can be None, hence the check and exception

        Returns
        -------
        RemoteAnonServer
            The currently active server

        Raises
        ------
        AnonCommandLineParserException
            When there is no active server
        """
        server = self.settings.active_server
        if not server:
            msg = (
                f"No active server. Which one do you want to use? Please activate one by using 'server activate <servername>. "
                f"Available:{str([x.name for x in self.settings.servers])}"
            )
            raise AnonCommandLineParserException(msg)
        return server

    def user_info(self):
        self.print_to_console(
            f"username is {self.settings.user_name}\nAPI token: {self.settings.user_token}"
        )

    def set_username(self, user_name):
        """Set the given username in settings

        Parameters
        ----------
        user_name: str
            set this username

        """
        self.settings.user_name = user_name
        self.settings.save()
        self.print_to_console(f"username is now '{user_name}'")

    def get_token(self):
        token = "".join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.ascii_lowercase + string.digits
            )
            for _ in range(64)
        )
        self.settings.user_token = token
        self.settings.save()
        self.print_to_console(
            f"Got and saved api token for username {self.settings.user_name}"
        )

    def get_batch(self):
        """Get batch defined in current folder"""

        batch = BatchFolder(self.current_dir()).load()
        if not batch:
            raise AnonCommandLineParserException("No batch defined in current folder")
        else:
            return batch

    def get_batch_folder(self):
        """True if there is a batch defined in this folder"""
        return BatchFolder(self.current_dir())

    def batch_init(self):
        """Save an empty batch in the current folder, for current server"""
        batch_folder = self.get_batch_folder()
        if batch_folder.has_batch():
            raise AnonCommandLineParserException(
                "Cannot init, A batch is already defined in this folder"
            )
        else:
            server = self.get_active_server()
            batch_folder.save(JobBatch(job_ids=[], server=server))
            self.print_to_console(f"Initialised batch for {server} in current dir")

    def batch_info(self):
        self.print_to_console(self.get_batch().to_string())

    def batch_delete(self):
        self.get_batch_folder().delete_batch()
        self.print_to_console(f"Removed batch in current dir")

    def batch_add_ids(self, ids):
        """Add ids to current batch. Will not add already existing

        Parameters
        ----------
        ids: List[str]
            list of job ids
        """
        batch_folder = self.get_batch_folder()
        batch: JobBatch = batch_folder.load()
        batch.job_ids = sorted(list(set(batch.job_ids) | set(ids)))
        batch_folder.save(batch)
        self.print_to_console(f"Added {ids} to batch")

    def batch_remove_ids(self, ids):
        """Remove ids from current batch

        Parameters
        ----------
        ids: List[str]
            list of job ids
        """
        batch_folder = self.get_batch_folder()
        batch: JobBatch = batch_folder.load()
        batch.job_ids = sorted(list(set(batch.job_ids) - set(ids)))
        batch_folder.save(batch)

        self.print_to_console(f"Removed {ids} from batch")

    def batch_status(self):
        """Print status overview for all jobs in batch"""
        batch = self.get_batch()
        ids_queried = batch.job_ids
        infos = self.client_tool.get_job_info_list(
            server=batch.server, job_ids=ids_queried
        )

        self.print_to_console(f"Job info for {len(infos)} jobs on {batch.server}:")
        self.print_to_console(infos.as_table_string())

        summary = ["Status       count   percentage", "-------------------------------"]
        status_count = Counter([x.status for x in infos])
        status_count["NOT_FOUND"] = len(ids_queried) - len(infos)
        for key, value in status_count.items():
            percentage = f"{(value / len(ids_queried) * 100):.1f} %"
            msg = f"{key:<12} {str(value):<8} {percentage:<8}"
            summary.append(msg)

        summary.append("-------------------------------")
        summary.append(f"Total        {str(len(ids_queried)):<8} 100%")

        self.print_to_console(f"Summary for all {len(ids_queried)} jobs:")
        self.print_to_console("\n".join(summary))

    @staticmethod
    def confirm(question="Are you sure? (y/n)"):
        """ Ask user confirmation. Stand in function until this code gets ported to click

        Parameters
        ----------
        question: str
            Show this question to answer yes or no to

        Returns
        -------
        True
            If user answered affirmatively
        False
            Otherwise

        """
        while True:
            choice = input(question).lower()
            if choice in ["yes", "y"] or not choice:
                return True
            if choice in ["no", "n"]:
                return False
            print(question)

    def batch_reset(self):
        """Reset every job in the current batch"""
        batch: JobBatch = self.get_batch()

        if self.confirm(
            f"This will reset {len(batch.job_ids)} jobs on {batch.server}. Are you sure?"
        ):
            for job_id in batch.job_ids:
                self.print_to_console(
                    self.client_tool.reset_job(server=batch.server, job_id=job_id)
                )

        self.print_to_console("Done")

    def batch_cancel(self):
        """Cancel every job in the current batch"""
        batch: JobBatch = self.get_batch()

        if self.confirm(
            f"This will cancel {len(batch.job_ids)} jobs on {batch.server}. Are you sure?"
        ):
            for job_id in batch.job_ids:
                self.print_to_console(
                    self.client_tool.cancel_job(server=batch.server, job_id=job_id)
                )

        self.print_to_console("Done")

    def batch_reset_errors(self):
        """Reset all jobs with error status in the current batch"""
        batch: JobBatch = self.get_batch()
        infos = self.client_tool.get_job_info_list(
            server=batch.server, job_ids=batch.job_ids
        )
        job_ids = [x for x in infos if x.status == JobStatus.ERROR]

        if self.confirm(
            f"This will reset {job_ids} jobs on {batch.server}. Are you sure?"
        ):
            for job_id in job_ids:
                self.print_to_console(
                    self.client_tool.reset_job(server=batch.server, job_id=job_id)
                )

        self.print_to_console("Done")

    @staticmethod
    def print_to_console(msg):
        """Print this message to console. With minimal formatting.

        Parameters
        ----------
        msg: str

        """
        # indent text so it is more visible
        lines = msg.split("\n")
        indented = "\n" + "\n".join(["  " + line for line in lines])
        print(indented)

    def execute_command(self, cmd):
        """Parse command line string and execute functions accordingly

        Parameters
        ----------
        cmd

        Notes
        -----
        the result of parser.parse_args() always contains the key 'func' because it is explicitly added for each
        parser in self.create_parser() See that that method's doc string notes for more info.

        """
        args = self.parser.parse_args(cmd)
        args_dict = vars(args)
        func = args_dict.pop("func")
        try:
            func(**args_dict)
        except AnonCommandLineParserException as e:
            self.print_to_console("Error: " + str(e))


class AnonCommandLineParserException(Exception):
    pass


class ClientToolException(Exception):
    pass


def main():
    global settings_file
    settings_file = pathlib.Path.home() / "AnonWebAPIClientSettings.yml"
    if not os.path.exists(settings_file):
        print(f"Settings file did not exist. creating '{settings_file}'")
        DefaultAnonClientSettings().save_to_file(filename=settings_file)
    settings = AnonClientSettingsFromFile(settings_file)
    tool = AnonClientTool(username=settings.user_name, token=settings.user_token)
    parser = AnonCommandLineParser(client_tool=tool, settings=settings)
    parser.execute_command(sys.argv[1:])


if __name__ == "__main__":
    main()
