# Copyright (c) 2013 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import qumulo.lib.opts
import qumulo.rest.unconfigured_node_operations as node_operations

class UnconfiguredCommand(qumulo.lib.opts.Subcommand):
    NAME = "unconfigured"
    DESCRIPTION = "Is the node unconfigured?"

    @staticmethod
    def main(conninfo, credentials, _args):
        print node_operations.unconfigured(
            conninfo, credentials)

class ListUnconfiguredNodesCommand(qumulo.lib.opts.Subcommand):
    NAME = "unconfigured_nodes_list"
    DESCRIPTION = "Get the list of unconfigured nodes"

    @staticmethod
    def options(parser):
        parser.add_argument("--table", action='store_true',
            help="Print output as a table, instead of JSON")

    @staticmethod
    def main(conninfo, credentials, args):
        res = node_operations.list_unconfigured_nodes(conninfo, credentials)
        if args.table:
            print node_operations.fmt_unconfigured_nodes(res)
        else:
            print res
