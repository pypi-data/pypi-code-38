# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2012-2017 Guillaume Sagnol
# Copyright (C)      2018 Maximilian Stahlberg
#
# This file is part of PICOS.
#
# PICOS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PICOS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This file implements constraints for a network flow problem.
#-------------------------------------------------------------------------------

from ..tools import sum, new_param

from .constraint import MetaConstraint

# TODO: Code looks redundant, refactor it.
class FlowConstraint(MetaConstraint):
    """
    .. note ::
        Unlike other :class:`MetaConstraint` implementations, this one is used
        (via a wrapper function) by the user, so it is raising exceptions
        instead of making assertions if it is instanciated incorrectly.
    """
    def __init__(
        self, G, f, source, sink, flow_value, capacity = None, graphName = ""):
        from ..problem import Problem

        if len(f) != len(G.edges()):
            raise ValueError(
                "The number of variables does not match the number of edges.")

        if isinstance(sink, list) and len(sink) == 1:
            source = source[0]

        if isinstance(sink, list) and len(sink) == 1:
            sink = sink[0]

        self.graph = G

        # Build the string description.
        if isinstance(source, list):
            sourceStr = "(" + ", ".join(source) + ")"
        else:
            sourceStr = str(source)

        if isinstance(sink, list):
            sinkStr = "(" + ", ".join(sink) + ")"
        else:
            sinkStr = str(sink)

        if isinstance(flow_value, list):
            valueStr = "(" + ", ".join([v.string if hasattr(v, "string")
                else str(v) for v in flow_value]) + ")"
        else:
            valueStr = flow_value.string if hasattr(flow_value, "string") \
                else str(flow_value)

        self.comment = "{}{}-{}-flow{} has value {}.".format(
            "Feasible " if capacity is not None else "", sourceStr, sinkStr,
            " in {}".format(graphName) if graphName else "", valueStr)

        P = Problem()

        # Add capacity constraints.
        if capacity is not None:
            c = {}
            for v, w, data in G.edges(data=True):
                c[(v, w)] = data[capacity]
            c = new_param('c', c)

            P.add_list_of_constraints(
                [f[e] < c[e] for e in G.edges()], [('e', 2)], 'edges')

        # Add non-negativity constraints.
        P.add_list_of_constraints(
            [f[e] > 0 for e in G.edges()], [('e', 2)], 'edges')

        # One source, one sink.
        if not isinstance(source, list) and not isinstance(sink, list):
            # Add flow conversation constrains.
            P.add_list_of_constraints(
                [sum([f[p, i] for p in G.predecessors(i)], 'p', 'pred(i)') ==
                sum([f[i, j] for j in G.successors(i)], 'j', 'succ(i)') for i in
                G.nodes() if i != sink and i != source], 'i', 'V\\{s,t}')

            # Source flow at S
            P.add_constraint(
                sum([f[p, source] for p in G.predecessors(source)],
                    'p', 'pred(s)') + flow_value ==
                sum([f[source, j] for j in G.successors(source)],
                    'j', 'succ(s)'))

        # One source, multiple sinks.
        elif not isinstance(source, list):
            if(len(sink) != len(flow_value)):
                raise ValueError("The number of sinks does not match the number"
                    " of flow values.")

            # Add flow conversation constrains.
            P.add_list_of_constraints(
                [sum([f[p, i] for p in G.predecessors(i)], 'p', 'pred(i)') ==
                sum([f[i, j] for j in G.successors(i)], 'j', 'succ(i)') for i in
                G.nodes() if not i in sink and i != source], 'i', 'V\\{s,t}')

            for k in range(0, len(sink)):
                # Sink flow at T
                P.add_constraint(
                    sum([f[p, sink[k]] for p in G.predecessors(sink[k])],
                        'p', 'pred(' + str(sink[k]) + ')') ==
                    sum([f[sink[k], j] for j in G.successors(sink[k])],
                        'j', 'succ(t)') + flow_value[k])

                if hasattr(flow_value[k], 'string'):
                    fv = flow_value[k].string
                else:
                    fv = str(flow_value[k])

        # Multiple sources, one sink.
        elif not isinstance(sink, list):
            if(len(source) != len(flow_value)):
                raise ValueError("The number of sources does not match the "
                    "number of flow values.")

            # Add flow conversation constrains.
            P.add_list_of_constraints(
                [sum([f[p, i] for p in G.predecessors(i)], 'p', 'pred(i)') ==
                sum([f[i, j] for j in G.successors(i)], 'j', 'succ(i)') for i in
                G.nodes() if not i in source and i != sink], 'i', 'V\\{s,t}')

            for k in range(0, len(source)):
                # Source flow at T
                P.add_constraint(
                    sum([f[p, source[k]] for p in G.predecessors(source[k])],
                        'p', 'pred(s)') + flow_value[k] ==
                    sum([f[source[k], j] for j in G.successors(source[k])],
                        'j', 'succ(' + str(source[k]) + ')'))

        # Multiple sources, multiple sinks.
        elif isinstance(sink, list) and isinstance(source, list):
            if(len(sink) != len(source)):
                raise ValueError("The number of sinks does not match the number"
                    " of sources.")

            if(len(source) != len(flow_value)):
                raise ValueError("The number of sources does not match the "
                    "number of flow values.")

            if(len(sink) != len(flow_value)):
                raise ValueError("The number of sinks does not match the number"
                    " of flow values.")

            comment = "** Multiple Sources, Multiple Sinks **\n"

            SS = list(set(source))
            TT = list(set(sink))

            if len(SS) <= len(TT):
                ftmp = {}
                for s in SS:
                    ftmp[s] = {}
                    sinks_from_s = [
                        t for (i, t) in enumerate(sink) if source[i] == s]
                    values_from_s = [
                        v for (i, v) in enumerate(flow_value) if source[i] == s]

                    for e in G.edges():
                        ftmp[s][e] = P.add_variable(
                            'f[{0}][{1}]'.format(s, e), 1)

                    P.add_constraint(self.__class__(
                            G, ftmp[s], source=s, sink=sinks_from_s,
                            flow_value=values_from_s, graphName=graphName))

                P.add_list_of_constraints([f[e] == sum(
                    [ftmp[s][e] for s in SS], 's', 'sources')
                        for e in G.edges()], 'e', 'E')
            else:
                ftmp = {}
                for t in TT:
                    ftmp[t] = {}
                    sources_to_t = [
                        s for (i, s) in enumerate(source) if sink[i] == t]
                    values_to_t = [
                        v for (i, v) in enumerate(flow_value) if sink[i] == t]

                    for e in G.edges():
                        ftmp[t][e] = P.add_variable(
                            'f[{0}][{1}]'.format(t, e), 1)

                    P.add_constraint(self.__class__(
                            G, ftmp[t], source=sources_to_t, sink=t,
                            flow_value=values_to_t, graphName=graphName))

                P.add_list_of_constraints([f[e] == sum(
                    [ftmp[t][e] for t in TT], 't', 'sinks') for e in G.edges()],
                    'e', 'E')

        else:
            assert False, "Dijkstra-IF fallthrough."

        super(FlowConstraint, self).__init__(P, "Flow")

    def _expression_names(self):
        return
        yield

    def _get_prefix(self):
        return "_flow"

    def _str(self):
        return self.comment

    def _get_slack(self):
        raise NotImplementedError

    def draw(self):
        from ..tools import drawGraph
        drawGraph(self.graph)
