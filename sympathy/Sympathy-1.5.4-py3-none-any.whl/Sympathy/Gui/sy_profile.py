# -*- coding:utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import six
import sys
import logging
import os
import subprocess
import pstats
import tempfile
import platform
import distutils.spawn

from . import settings
from . import util
from . flow import types
from sympathy.platform import os_support

core_logger = logging.getLogger('core')


def report(node_stats):
    def format_node_names(maximum=None, uuid=False):
        names = sorted([(node.uuid + ': ' if uuid else '') + node.name
                        for node, _ in node_stats], key=lambda x: x.split(
                            ':', 1)[-1])
        length = len(names)
        if maximum is not None and length > maximum:
            names = (names[:maximum] +
                     ['... Omitting {} Nodes'.format(length - maximum)])
        return '\n   '.join(names)

    firstnode, _ = six.next(iter(node_stats))
    flow = firstnode.flow.root_flow()
    display_name = flow.full_display_name or 'xxx'
    flow_dirname = os.path.dirname(flow.filename)
    gviz_path = settings.instance()['Debug/graphviz_path'] or None
    session_folder = settings.instance()['session_folder']
    profile_path_type = settings.instance()['Debug/profile_path_type']
    if profile_path_type == 'Session folder':
        profile_path = os.path.join(
            session_folder, 'syprofile', display_name)
    elif profile_path_type == 'Workflow folder':
        profile_path = os.path.join(
            flow_dirname, 'syprofile', display_name)
    else:
        profile_path = os.path.join(
            tempfile.gettempdir(), 'syprofile', display_name)

    try:
        os.makedirs(profile_path)
    except OSError:
        pass
    time_string = util.now_time_string()
    calls_stats_filename = os.path.join(
        profile_path, 'calls_{}.{}'.format(time_string, 'stats'))
    nodes_stats_filename = os.path.join(
        profile_path, 'nodes_{}.{}'.format(time_string, 'stats'))
    calls_pdf_filename = os.path.join(
        profile_path, 'calls_{}.{}'.format(time_string, 'pdf'))
    nodes_pdf_filename = os.path.join(
        profile_path, 'nodes_{}.{}'.format(time_string, 'pdf'))
    text_filename = os.path.join(
        profile_path, time_string + '.txt')

    stats = Stats(node_stats)
    stats.dump_calls(calls_stats_filename)
    stats.dump_nodes(nodes_stats_filename)

    stats.output_graph_file(
        calls_stats_filename, calls_pdf_filename, gviz_path)
    stats.output_graph_file(
        nodes_stats_filename, nodes_pdf_filename, gviz_path)

    with open(text_filename, 'wb') as f:
        f.write('Profile report included nodes\n\n   {nodes}\n\n'.format(
            nodes=format_node_names(uuid=True)).encode('utf-8'))
        f.write(stats.output_stats_string().encode('utf8'))

    return (display_name,
            ("""Profile report included nodes

   {nodes}

Profile report files

    {text}
    {calls_pdf}
    {nodes_pdf}
    {stats}

Profile report summary

{report}""").format(
                 nodes=format_node_names(10),
                 text=text_filename,
                 calls_pdf=(calls_pdf_filename
                            if os.path.exists(calls_pdf_filename) else
                            'Graphviz unavailable: no pdf created. See user manual'),
                 nodes_pdf=(nodes_pdf_filename
                            if os.path.exists(nodes_pdf_filename) else
                            'Graphviz unavailable: no pdf created. See user manual'),
                 stats=calls_stats_filename,
                 report=stats.output_stats_string(compact=True)))


class DummyStats(object):
    def __init__(self):
        self._dummy = ('<dummy>', 0, '<dummy>')
        self.stats = {self._dummy: (1, 1, 1.0, 1.0, {})}

    def create_stats(self):
        pass

    def clear_dummy(self, stats):
        del stats.stats[self._dummy]


def _label(flobj, label_map, ident_map):

    def enumerate_(label, ident):
        n = label_map.get(label, -1) + 1

        label_map[label] = n
        res = [(label[0], n, label[1])]
        ident_map[ident] = res
        return res

    def inst_label(flobj):

        key = ('inst', flobj)

        if key in ident_map:
            res = ident_map[key]
        elif flobj.type == types.Type.Flow:
            res = enumerate_(('<iflow>', flobj.display_name), key)
        else:
            res = enumerate_(('<inode>', flobj.name), key)

        return res

    def cls_label(flobj):
        res = []

        if flobj.type == types.Type.Node:
            key = ('cls', flobj.node_identifier)

            if key in ident_map:
                res = ident_map[key]
            else:
                res = enumerate_(('<node>', flobj.library_node_name), key)

        return res

    return cls_label(flobj) + inst_label(flobj)


class Stats(object):
    """
    Interface for working with python profile results obtained from profile or
    cProfile.

    Graph images can be generated optionally if GraphViz and gprof2dot.py are
    installed.
    """
    def __init__(self, node_stats):
        self._cs = self._load_calls(node_stats)
        self._ns = self._load_nodes(node_stats)

    def _load_calls(self, nodes_stats, stream=None):
        return pstats.Stats(
            *[stats_fn for node, stats_fn in nodes_stats],
            stream=stream)

    def _load_nodes(self, node_stats, stream=None):
        ds = DummyStats()
        res = pstats.Stats(ds, stream=stream)
        ds.clear_dummy(res)

        label_map = {}
        ident_map = {}

        for node, stats_fn in node_stats:
            if os.path.exists(stats_fn):
                ps = pstats.Stats(stats_fn)

                top_levels = []
                for k, v in ps.stats.items():
                    path, _, _ = k
                    callers = v[4]
                    if path.endswith(
                            'task_worker_subprocess.py') and callers == {}:
                        top_levels.append((k, v))
                        break

                ps.stats.clear()

                if top_levels:
                    v = top_levels[0][1]

                    nodes = []

                    while node:
                        nodes.append(node)
                        node = node.flow

                    for node in nodes:
                        _, _, tt, ct, callers = v

                        for key in _label(node, label_map, ident_map):
                            callers[key] = (1, 1, 0.0, tt + ct)
                            callers = {}
                            v = (1, 1, 0.0, tt + ct, callers)
                            ps.stats[key] = v

                res.add(ps)
        return res

    def dump_calls(self, filename):
        self._cs.dump_stats(filename)

    def dump_nodes(self, filename):
        self._ns.dump_stats(filename)

    def _output_string(self, method):
        stream = six.StringIO()
        oldstream = self._cs.stream
        try:
            self._cs.stream = stream
            method(self._cs)
        finally:
            self._cs.stream = oldstream

        stream.seek(0)
        return stream.read()

    def output_callers_string(self):
        def method(stats):
            stats.print_callers()
        return self._output_string(method)

    def output_callees_string(self):
        def method(stats):
            stats.print_callees()
        return self._output_string(method)

    def output_stats_string(self, compact=False):
        def method(stats):
            if compact:
                stats.strip_dirs().sort_stats('cumulative').print_stats(120)
            else:
                stats.sort_stats('cumulative').print_stats()

        # Filtering all lines containing the filenames including the empty line
        # that follows. We do not want to show that information to the user
        # since the filenames are internal and uses too much screen estate.
        result = self._output_string(method)
        lines = iter(result.splitlines())
        while six.next(lines):
            pass
        return '\n'.join(lines)

    def output_graph_file(self, in_filename, out_filename, gviz_path='.'):
        """
        gprof2dot.py -f pstats filenames | dot -Tpng -o filename
        """
        ext = out_filename.split('.')[-1]
        dot = distutils.spawn.find_executable('dot', gviz_path)
        if dot and not os.path.exists(dot):
            dot = distutils.spawn.find_executable('dot')
        if not dot:
            core_logger.error(
                "'dot' not found, make sure to install it in 'PATH'.")
            return

        try:
            p0 = os_support.Popen_no_console(
                [sys.executable, '-m',
                 'gprof2dot', '-f', 'pstats', in_filename],
                stdout=subprocess.PIPE)
        except OSError:
            import traceback; traceback.print_stack()
            return

        try:
            p1 = os_support.Popen_no_console(
                [dot, '-T{}'.format(ext), '-o', out_filename],
                stdin=p0.stdout)
        except OSError:
            import traceback; traceback.print_stack()
            return

        p0.stdout.close()
        p1.communicate()
        p1.wait()
        p0.wait()
