#!/usr/bin/env python
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Command line client that for nightlies administration on RabbitMQ

:author: Chitic Stefan-Gabriel
'''
from __future__ import print_function
import logging
import argparse
import os
import re
import json
import sys
import traceback
import urllib2
import datetime
from os.path import abspath
from tabulate import tabulate
from lbciagent import DeploymentPolicy

from lbmessaging.exchanges.Common import AdminHelper, check_channel,\
    get_connection
from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange, \
    CVMFSDEV_EXCHANGE
import lbmessaging


class LbMaNightliesClient(object):
    """ Main class for the tool """

    def __init__(self, configType, arguments=None, prog="LbMaNightlies"):
        """ Common setup for both clients """
        self.configType = configType
        self.log = logging.getLogger(__name__)
        self.arguments = arguments
        self.prog = prog
        self.slot = None
        self.build_id = None
        self.project = None
        self.platform = None
        self.priority = 10
        self.destination_exchange = None
        self.source_queue = None
        self.command_name = None
        self.msg_uid = None
        self.vhost = '/lhcb'
        self.all = False
        self.origin_exchange = CVMFSDEV_EXCHANGE
        self.source_exchange = None
        self.origin_queue = 'CVMFSDevActions'
        self.channel = check_channel(get_connection(vhost=self.vhost))

        self.parser = argparse.ArgumentParser(
            description='Tool to administrate nightliesInstallation Messages')

        self.parser.add_argument('-d', '--debug',
                                 dest="debug",
                                 default=False,
                                 action="store_true",
                                 help="Show debug information")
        self.parser.add_argument('--info',
                                 dest="info",
                                 default=False,
                                 action="store_true",
                                 help="Show logging messages with level INFO")

        self.subparsers = self.parser.add_subparsers(
            title='subcommands', description='valid subcommands',
            help='')
        # Display
        parser = self.subparsers.add_parser(
            'display', help="Displays the messages in the installation queue")
        parser.set_defaults(which='display')
        parser.add_argument('--queue',
                              dest="origin_queue",
                              default="CVMFSDevActions",
                              action="store",
                              help="Specify the queu name")

        # Change priority
        parser = self.subparsers.add_parser(
            'change_priority', help='Updates the priority of the messages '
                                    'filtered by slot or/and build_id '
                                    'or/and platform or/and project '
                                    'or/and command name '
                                    'or/and uid of the message')
        parser.set_defaults(which='change_priority')
        self._add_slot_info_parsing(parser)
        parser.add_argument('priority',
                            help="The new priority for the messages")

        # Add message
        parser = self.subparsers.add_parser(
            'add', help='Adds a  messages with slot, build_id,'
                        ' platform and project in the queue')
        parser.set_defaults(which='add')
        self._add_slot_info_parsing(parser)
        parser.add_argument('priority',
                            help="The priority for the messages")

        # Reapply policy

        parser = self.subparsers.add_parser(
            'reapply_policy', help="Reapply the deployment policy for all the"
                                   "messages for today. ")
        parser.set_defaults(which='reapply_policy')

        # Regenerate

        parser = self.subparsers.add_parser(
            'regenerate', help="Regenerates all the installations "
                               "messages for today. "
                               "If all is used, all the messages are "
                               "regenerated. If not, only the completed "
                               "messages are regenerated.")
        parser.set_defaults(which='regenerate')
        self._add_slot_info_parsing(parser)
        parser.add_argument('--all',
                            dest="all",
                            default=False,
                            action="store_true",
                            help="Regenerate even non built projects")

        # Move
        parser = self.subparsers.add_parser(
            'move', help='Moves messages filtered by slot or/and build_id '
                         'or/and platform or/and project or/and command name '
                         'or/and uid of the message in a specific '
                         'exchange')
        parser.set_defaults(which='move')
        self._add_slot_info_parsing(parser)
        parser.add_argument('source_queue',
                            help="Specify source queue for message")
        parser.add_argument('destination_exchange',
                            help="Specify destination exchange for message")

        # retry_error
        parser = self.subparsers.add_parser(
            'retry_errors', help='Moves from error queue to main exchange '
                                 'filtered messages')
        parser.set_defaults(which='retry_errors')
        self._add_slot_info_parsing(parser)


        args = vars(self.parser.parse_args())
        # Now setting the logging depending on debug mode...
        if args['debug'] or args['info']:
            logging.basicConfig(format="%(levelname)-8s: "
                                       "%(funcName)-25s - %(message)s")
            if args['info']:
                logging.getLogger().setLevel(logging.INFO)
            else:
                logging.getLogger().setLevel(logging.DEBUG)
        if args.get('cmd', None):
            self.command_name = args['cmd']
        if args.get('uid', None):
            self.msg_uid = args['uid']
        if args.get('slot', None):
            self.slot = args['slot']
        if args.get('build_id', None):
            self.build_id = args['build_id']
        if args.get('project', None):
            self.project = args['project']
        if args.get('platform', None):
            self.platform = args['platform']
        if args.get('source_queue', None):
            self.source_queue = args['source_queue']
        if args.get('destination_exchange', None):
            self.destination_exchange = args['destination_exchange']
        if args.get('origin_queue', None):
            self.origin_queue = args['origin_queue']
        if args.get('platform', None):
            self.platform = args['platform']
        if args.get('all', None):
            self.all = args['all']
        if args.get('priority', None):
            self.priority = int(args['priority'])
        mode = args['which']
        getattr(self, mode)()

    def _add_slot_info_parsing(self, subparser):
        subparser.add_argument('--cmd',
                               dest="cmd",
                               default=None,
                               action="store",
                               help="Specify command name")
        subparser.add_argument('--uid',
                               dest="uid",
                               default=None,
                               action="store",
                               help="Specify message uid")
        subparser.add_argument('--slot',
                               dest="slot",
                               default=None,
                               action="store",
                               help="Specify slot name")
        subparser.add_argument('--build_id',
                               dest="build_id",
                               default=None,
                               action="store",
                               help="Specify build id")
        subparser.add_argument('--platform',
                               dest="platform",
                               default=None,
                               action="store",
                               help="Specify platform name")
        subparser.add_argument('--project',
                               dest="project",
                               default=None,
                               action="store",
                               help="Specify project name")
        return subparser

    def change_priority(self):
        tools = AdminHelper(self.origin_exchange,
                            channel=self.channel)
        if not self.priority:
            raise Exception("The new priority must be specified")
        tools.change_messages(self.origin_queue, self._update_priority)

    def add(self):
        if (self.slot is None or self.build_id is None):
            raise Exception("The full installation info needs"
                            " to be completed: slot, build_id")
        if not self.priority:
            raise Exception("The priority must be specified")
        url = "https://lhcb-couchdb.cern.ch/nightlies-nightly/" \
              "%s.%s" % (self.slot, self.build_id)
        response = urllib2.urlopen(url)
        platforms = self._get_platforms_projects(json.loads(
            response.read()))
        broker = CvmfsDevExchange(self.channel)
        command = 'installNightlies'
        for platform in platforms.keys():
            if self.platform and self.platform != platform:
                continue
            for project in platforms[platform]:
                if self.project and self.project != project:
                    continue
                args_c = [self.slot, self.build_id, platform, project]
                self.log.info(
                    "Added %s-%s-%s-%s with priority %s" %
                    (self.slot, self.build_id, platform, project,
                     self.priority))
                broker.send_command(command, args_c, priority=self.priority)

    def retry_errors(self):
        if (not self.slot and not self.project and not self.build_id and
                not self.platform and not self.command_name and
                not self.msg_uid):
            raise Exception("Please specify at least one filtering "
                            "criteria in the options")

        tools = AdminHelper(self.origin_exchange,
                            channel=self.channel)
        tools.change_messages('CVMFSDevActionserror',
                              self._park_message_handler,
                              dest_exchange='cvmfsdev.action')

    def move(self):
        if not self.source_queue:
            raise Exception("The queue where the message was "
                            "initially delivered needs to be specify")
        if not self.destination_exchange:
            raise Exception("Destination exchange must"
                            " be specified")

        tools = AdminHelper(self.origin_exchange,
                            channel=self.channel)
        tools.change_messages(self.source_queue,
                              self._park_message_handler,
                              dest_exchange=self.destination_exchange)

    def display(self):
        tools = AdminHelper(self.origin_exchange,
                            channel=self.channel)
        queue = self.origin_queue
        res = tools.list_messages_in_queue(queue)
        to_display = [['Nb', 'Uid', 'Command', "Retry",
                       "Priority", "Expire", "Args", "Publish Date"]]
        nb = 0
        total = len(res)
        for r in res:
            nb += 1
            if r[3] is not None:
                exp = datetime.datetime.strptime(r[6], "%Y-%m-%dT%H:%M:%S.%f")
                exp = exp + datetime.timedelta(milliseconds=int(r[3]))
                exp = exp.strftime("%Y-%m-%dT%H:%M:%S.%f")
            else:
                exp = "-"
            to_display.append([str(total-nb),
                               r[4], r[0], r[1], r[2], exp, r[6], r[7]])
        print(tabulate(to_display))

    def reapply_policy(self):
        tools = AdminHelper(self.origin_exchange,
                            channel=self.channel)
        tools.change_messages(self.origin_queue, self._reapply_priority)

    def regenerate(self):
        url = 'https://lhcb-couchdb.cern.ch/nightlies-nightly/' \
              '_design/deployment/_view/ready?key=["%s","%s"]&include_doc' \
              's=true'
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        url = url % (date, 'cvmfs')
        response = urllib2.urlopen(url)
        data = response.read()
        dictionary = json.loads(data)
        broker = CvmfsDevExchange(self.channel)
        for row in dictionary.get('rows', []):
            command = 'installNightlies'
            previous = None
            for value in row.get('value', []):
                slot_name = value.get('slot', '')
                if previous == slot_name:
                    continue
                previous = slot_name
                if self.slot and self.slot != slot_name:
                    continue
                slot_build = value.get('build_id', '')
                if self.build_id and self.build_id != slot_build:
                    continue
                platforms = self._get_platforms_projects(row.get('doc'),
                                                         self.all)
                for platform in platforms.keys():
                    if self.platform and self.platform != platform:
                        continue
                    priority = DeploymentPolicy.computePriority(slot_name,
                                                                platform)
                    for project in platforms[platform]:
                        if self.project and self.project != project:
                            continue
                        if project in ["PARAM"]:
                            continue
                        args_c = [slot_name, slot_build, platform,
                                  project]
                        self.log.info(
                            "Regenerated %s-%s-%s-%s with priority %s" %
                            (slot_name, slot_build, platform, project,
                             priority))
                        broker.send_command(command, args_c,
                                            priority=priority)

    def _is_message_concerned(self, message):
        uid = message[2].headers.get('uid', None)
        message = message[0]
        cmd = message[0]
        if cmd == 'installNightlies':
            c_slot = message[1][0]
            c_build_id = message[1][1]
            c_platform = message[1][2]
            c_project = message[1][3]
            if(not self.slot and not self.project and not self.build_id and
               not self.platform):
                return False
            if self.slot:
                tmp = re.compile(self.slot)
                if not tmp.search(c_slot):
                    return False
            if self.build_id:
                tmp = re.compile(self.build_id)
                if not tmp.search(c_build_id):
                    return False
            if self.platform:
                tmp = re.compile(self.platform)
                if not tmp.search(c_platform):
                    return False
            if self.project:
                tmp = re.compile(self.project)
                if not tmp.search(c_project):
                    return False
            return True
        else:
            if self.command_name and self.command_name == cmd:
                return True
            if self.msg_uid and self.msg_uid == uid:
                return True
            return False

    def _reapply_priority(self, message):
        updated = False
        msg = message[0]
        cmd = msg[0]
        if cmd == 'installNightlies':
            c_slot = msg[1][0]
            c_platform = msg[1][2]
            new_priority = DeploymentPolicy.computePriority(c_slot, c_platform)
            if new_priority != message[2].priority:
                message[2].priority = new_priority
                print("New priority found for %s-%s: %s" %
                      (c_slot, c_platform, new_priority))
                updated = True
        return updated, message

    def _update_priority(self, message):
        updated = False
        if self._is_message_concerned(message):
            message[2].priority = self.priority
            updated = True
        return updated, message

    def _park_message_handler(self, message):
        updated = False
        if self._is_message_concerned(message):
            updated = True
        return updated, message

    def _get_platforms_projects(self, doc, all=False):
        return_dic = {}
        if all:
            platforms = doc['config']['platforms']
            projects = [proj['name']
                        for proj in doc['config']['projects']
                        if proj['disabled'] is False]
            for platform in platforms:
                return_dic[platform] = projects
        else:
            for build in doc['builds'].keys():
                tmp = []
                for project in doc['builds'][build].keys():
                    if project == 'info':
                        continue
                    if doc['builds'][build][project].get('completed', None):
                        tmp.append(project)
                if len(tmp) > 0:
                    return_dic[build] = tmp
        return return_dic


def LbMaNightlies(configType="LHCbConfig", prog="lbma"):
    """
    Default caller for command line LbMaNightlies client
    :param configType: the configuration used
    :param prog: the name of the executable
    """
    logging.basicConfig(format="%(levelname)-8s: %(message)s")
    logging.getLogger().setLevel(logging.WARNING)
    LbMaNightliesClient(configType, prog=prog)

# Main just chooses the client and starts it
if __name__ == "__main__":
    LbMaNightlies()

