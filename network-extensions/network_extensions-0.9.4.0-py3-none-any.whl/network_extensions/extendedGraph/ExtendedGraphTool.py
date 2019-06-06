#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# graph_tool -- a general graph manipulation python module
#
# Copyright (C) 2006-2018 Tiago de Paula Peixoto <tiago@skewed.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
graph_tool - efficient graph analysis and manipulation
======================================================

Summary
-------

.. autosummary::
   :nosignatures:

   Graph
   GraphView
   Vertex
   Edge
   PropertyMap
   PropertyArray
   load_graph
   load_graph_from_csv
   group_vector_property
   ungroup_vector_property
   map_property_values
   infect_vertex_property
   edge_endpoint_property
   incident_edges_op
   perfect_prop_hash
   value_types
   openmp_enabled
   openmp_get_num_threads
   openmp_set_num_threads
   openmp_get_schedule
   openmp_set_schedule
   show_config


This module provides:

   1. A :class:`~graph_tool.Graph` class for graph representation and manipulation
   2. Property maps for Vertex, Edge or Graph.
   3. Fast algorithms implemented in C++.

How to use the documentation
----------------------------

Documentation is available in two forms: docstrings provided
with the code, and the full documentation available in
`the graph-tool homepage <http://graph-tool.skewed.de>`_.

We recommend exploring the docstrings using `IPython
<http://ipython.scipy.org>`_, an advanced Python shell with TAB-completion and
introspection capabilities.

The docstring examples assume that ``graph_tool.all`` has been imported as
``gt``::

   >>> import graph_tool.all as gt

Code snippets are indicated by three greater-than signs::

   >>> x = x + 1

Use the built-in ``help`` function to view a function's docstring::

   >>> help(gt.Graph)

Contents
--------
"""

################################################################################
# Property Maps
################################################################################
import weakref

import happybase
import numpy
import requests
from graph_tool import PropertyMap, _converter, ArgumentError, _python_type, PropertyArray, _prop, \
    ungroup_vector_property, group_vector_property, GraphView, conv_pickle_state, _str_decode

HBASE  = happybase.Connection('localhost',table_prefix="GEN_GRAPH")
HSCHEMA = "http://localhost:8080/%s/schema"
PREFIX = "GEN_GRAPH"

class HBasePropertyMap(PropertyMap):
    """This class provides a mapping from vertices, edges or whole graphs to
    arbitrary properties.

    See :ref:`sec_property_maps` for more details.

    The possible property value types are listed below.

    .. table::

        =======================     ======================
         Type name                  Alias
        =======================     ======================
        ``bool``                    ``uint8_t``
        ``int16_t``                 ``short``
        ``int32_t``                 ``int``
        ``int64_t``                 ``long``, ``long long``
        ``double``                  ``float``
        ``long double``
        ``string``
        ``vector<bool>``            ``vector<uint8_t>``
        ``vector<int16_t>``         ``short``
        ``vector<int32_t>``         ``vector<int>``
        ``vector<int64_t>``         ``vector<long>``, ``vector<long long>``
        ``vector<double>``          ``vector<float>``
        ``vector<long double>``
        ``vector<string>``
        ``python::object``          ``object``
        =======================     ======================
    """
    def __init__(self, g, key_type):

        #connection.create_table('mytable', families)

        tables = HBASE.tables()
        if not str(id(g)).encode("utf-8") in list(tables):
            HBASE.create_table(str(id(g)), {str(id(self)): dict(max_versions=10)})
            self.__table = HBASE.table(str(id(g)))
        else:
            self.__table = HBASE.table(str(id(g)))
            res = requests.get(HSCHEMA%("GEN_GRAPH_"+str(id(g))),headers={"Accept":"application/json"})
            res = res.json()

            columns = res["ColumnSchema"].append({"name": str(id(self))})
            res = requests.post(HSCHEMA % ("GEN_GRAPH_" + str(id)), json=columns)





        self.__map = self.__table.row(str(id(self)))

        self.__g = weakref.ref(g)
        self.__base_g = weakref.ref(g.base)  # keep reference to the
                                             # base graph, in case the
                                             # graph view is deleted.
        self.__key_type = key_type
        self.__convert = _converter(self.value_type())
        self.__register_map()

    def _get_any(self):
        t = self.key_type()
        g = self.get_graph()
        if t == "v":
            N = g.num_vertices(True)
        elif t == "e":
            N = g.edge_index_range
        else:
            N = 1
        self.reserve(N)
        #return self.__map.get_map()
        return self.__map

    def __key_trans(self, key):
        if self.key_type() == "g":
            return key._Graph__graph
        else:
            return key

    def __key_convert(self, k):
        if self.key_type() == "e":
            try:
                k = (int(k[0]), int(k[1]))
            except:
                raise ArgumentError
            key = self.__g().edge(k[0], k[1])
            if key is None:
                raise ValueError("Nonexistent edge: %s" % str(k))
        elif self.key_type() == "v":
            try:
                key = int(k)
            except:
                raise ArgumentError
            key = self.__g().vertex(key)
        return key

    def __register_map(self):
        for g in [self.__g(), self.__base_g()]:
            if g is not None:
                g._Graph__known_properties[id(self)] = weakref.ref(self)

    def __unregister_map(self):
        for g in [self.__g(), self.__base_g()]:
            if g is not None and id(self) in g._Graph__known_properties:
                del g._Graph__known_properties[id(self)]

    def __del__(self):
        self.__unregister_map()

    def __getitem__(self, k):
        k = self.__key_trans(k)
        try:
            return self.__map[k]
        except ArgumentError:
            try:
                k = self.__key_convert(k)
                return self.__map[k]
            except ArgumentError:
                if self.key_type() == "e":
                    kt = "Edge"
                elif self.key_type() == "v":
                    kt = "Vertex"
                else:
                    kt = "Graph"
                raise ValueError("invalid key '%s' of type '%s', wanted type: %s"
                                 % (str(k), str(type(k)), kt) )
            except KeyError:
                return ""

    def __setitem__(self, k, v):
        key = self.__key_trans(k)
        try:
            try:
                self.__map[key] = v
            except TypeError:
                self.__map[key] = self.__convert(v)
        except ArgumentError:
            try:
                key = self.__key_convert(key)
                try:
                    self.__map[key] = v
                except TypeError:
                    self.__map[key] = self.__convert(v)
            except ArgumentError:
                if self.key_type() == "e":
                    kt = "Edge"
                elif self.key_type() == "v":
                    kt = "Vertex"
                else:
                    kt = "Graph"
                vt = self.value_type()
                raise ValueError("invalid key value pair '(%s, %s)' of types "
                                 "'(%s, %s)', wanted types: (%s, %s)" %
                                 (str(k), str(v), str(type(k)),
                                  str(type(v)), kt, vt))
    def __iter__(self):
        g = self.__g()
        if self.key_type() == "g":
            iters = [g]
        elif self.key_type() == "v":
            iters = g.vertices()
        else:
            iters = g.edges()
        for x in iters:
            yield self[x]

    def __repr__(self):
        # provide some more useful information
        if self.key_type() == "e":
            k = "Edge"
        elif self.key_type() == "v":
            k = "Vertex"
        else:
            k = "Graph"
        g = self.get_graph()
        if g is None:
            g = "a non-existent graph"
        else:
            g = "Graph 0x%x" % id(g)
        return ("<PropertyMap object with key type '%s' and value type '%s',"
                + " for %s, at 0x%x>") % (k, self.value_type(), g, id(self))

    def copy(self, value_type=None, full=True):
        """Return a copy of the property map. If ``value_type`` is specified, the value
        type is converted to the chosen type. If ``full == False``, in the case
        of filtered graphs only the unmasked values are copied (with the
        remaining ones taking the type-dependent default value).

        """
        return self.get_graph().copy_property(self, value_type=value_type,
                                              full=full)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        if self.value_type() != "python::object":
            return self.copy()
        else:
            pmap = self.copy()
            g = self.get_graph()
            if self.key_type() == "g":
                iters = [g]
            elif self.key_type() == "v":
                iters = g.vertices()
            else:
                iters = g.edges()
            for v in iters:
                pmap[v] = copy.deepcopy(self[v], memo)
            return pmap

    def get_graph(self):
        """Get the graph class to which the map refers."""
        g = self.__g()
        if g is None:
            g = self.__base_g()
        return g

    def key_type(self):
        """Return the key type of the map. Either 'g', 'v' or 'e'."""
        return self.__key_type

    def value_type(self):
        """Return the value type of the map."""
        #return self.__map.value_type()
        return "object"

    def python_value_type(self):
        """Return the python-compatible value type of the map."""
        return _python_type(self.__map.value_type())

    def get_array(self):
        """Get a :class:`numpy.ndarray` subclass (:class:`~graph_tool.PropertyArray`)
        with the property values.

        .. note::

           An array is returned *only if* the value type of the property map is
           a scalar. For vector, string or object types, ``None`` is returned
           instead. For vector and string objects, indirect array access is
           provided via the :func:`~graph_tool.PropertyMap.get_2d_array()` and
           :func:`~graph_tool.PropertyMap.set_2d_array()` member functions.

        .. warning::

           The returned array does not own the data, which belongs to the
           property map. Therefore, if the graph changes, the array may become
           *invalid*. Do **not** store the array if the graph is to be modified;
           store a **copy** instead.

        """
        return self._get_data()

    def _get_data(self):
        g = self.get_graph()
        if g is None:
            raise ValueError("Cannot get array for an orphaned property map")
        if self.__key_type == 'v':
            n = g._Graph__graph.get_num_vertices(False)
        elif self.__key_type == 'e':
            n = g.edge_index_range
        else:
            n = 1
        a = self.__map.get_array(n)
        if a is None:
            return a
        return PropertyArray(a, self)

    def __set_array(self, v):
        a = self.get_array()
        if a is None:
            raise TypeError("cannot set property map values from array for" +
                            " property map of type: " + self.value_type())
        a[:] = v

    a = property(get_array, __set_array,
                 doc=r"""Shortcut to the :meth:`~PropertyMap.get_array` method
                 as an attribute. This makes assignments more convenient, e.g.:

                 >>> g = gt.Graph()
                 >>> g.add_vertex(10)
                 <...>
                 >>> prop = g.new_vertex_property("double")
                 >>> prop.a = np.random.random(10)           # Assignment from array
                 """)

    def __get_set_f_array(self, v=None, get=True):
        g = self.get_graph()
        if g is None:
            return None
        a = self.get_array()
        filt = [None]
        if self.__key_type == 'v':
            filt = g.get_vertex_filter()
            N = g.num_vertices()
        elif self.__key_type == 'e':
            filt = g.get_edge_filter()
            if g.get_vertex_filter()[0] is not None:
                filt = (g.new_edge_property("bool"), filt[1])
                libcore.mark_edges(g._Graph__graph, _prop("e", g, filt[0]))
                if filt[1]:
                    filt[0].a = numpy.logical_not(filt[0].a)
            elif g.edge_index_range != g.num_edges():
                filt = (g.new_edge_property("bool"), False)
                libcore.mark_edges(g._Graph__graph, _prop("e", g, filt[0]))
            if filt[0] is None:
                N = g.edge_index_range
            else:
                N = (filt[0].a == (not filt[1])).sum()
        if get:
            if a is None:
                return a
            if filt[0] is None:
                return a
            return a[filt[0].a == (not filt[1])][:N]
        else:
            if a is None:
                raise TypeError("cannot set property map values from array for" +
                                " property map of type: " + self.value_type())
            if filt[0] is None:
                try:
                    a[:] = v
                except ValueError:
                    a[:] = v[:len(a)]
            else:
                m = filt[0].a == (not filt[1])
                m *= m.cumsum() <= N
                try:
                    a[m] = v
                except ValueError:
                    a[m] = v[:len(m)][m]

    fa = property(__get_set_f_array,
                  lambda self, v: self.__get_set_f_array(v, False),
                  doc=r"""The same as the :attr:`~PropertyMap.a` attribute, but
                  instead an *indexed* array is returned, which contains only
                  entries for vertices/edges which are not filtered out. If
                  there are no filters in place, the array is not indexed, and
                  is identical to the :attr:`~PropertyMap.a` attribute.

                  Note that because advanced indexing is triggered, a **copy**
                  of the array is returned, not a view, as for the
                  :attr:`~PropertyMap.a` attribute. Nevertheless, the assignment
                  of values to the *whole* array at once works as expected.""")

    def __get_set_m_array(self, v=None, get=True):
        g = self.get_graph()
        if g is None:
            return None
        a = self.get_array()
        filt = [None]
        if self.__key_type == 'v':
            filt = g.get_vertex_filter()
        elif self.__key_type == 'e':
            filt = g.get_edge_filter()
            if g.get_vertex_filter()[0] is not None:
                filt = (g.new_edge_property("bool"), filt[1])
                libcore.mark_edges(g._Graph__graph, _prop("e", g, filt[0]))
                if filt[1]:
                    filt[0].a = 1 - filt[0].a
        if filt[0] is None or a is None:
            if get:
                return a
            else:
                return
        ma = numpy.ma.array(a, mask=(filt[0].a == False) if not filt[1] else (filt[0].a == True))
        if get:
            return ma
        else:
            ma[:] = v

    ma = property(__get_set_m_array,
                  lambda self, v: self.__get_set_m_array(v, False),
                  doc=r"""The same as the :attr:`~PropertyMap.a` attribute, but
                  instead a :class:`~numpy.ma.MaskedArray` object is returned,
                  which contains only entries for vertices/edges which are not
                  filtered out. If there are no filters in place, a regular
                  :class:`:class:`~graph_tool.PropertyArray`` is returned, which
                  is identical to the :attr:`~PropertyMap.a` attribute.""")

    def get_2d_array(self, pos):
        r"""Return a two-dimensional array with a copy of the entries of the
        vector-valued property map. The parameter ``pos`` must be a sequence of
        integers which specifies the indexes of the property values which will
        be used. """

        if self.key_type() == "g":
            raise ValueError("Cannot create multidimensional array for graph property maps.")
        if "vector" not in self.value_type() and (len(pos) > 1 or pos[0] != 0):
            raise ValueError("Cannot create array of dimension %d (indexes %s) from non-vector property map of type '%s'." \
                             % (len(pos), str(pos), self.value_type()))
        if "string" in self.value_type():
            if "vector" in self.value_type():
                p = ungroup_vector_property(self, pos)
            else:
                p = [self]
            g = self.get_graph()
            vfilt = g.get_vertex_filter()
            efilt = g.get_edge_filter()
            if self.key_type() == "v":
                iters = g.vertices()
            else:
                iters = [None for i in range(g.edge_index_range)]
                idx = g.edge_index
                for e in g.edges():
                    iters[idx[e]] = e
                iters = [e for e in iters if e is not None]
            a = [[] for i in range(len(p))]
            for v in iters:
                for i in range(len(p)):
                    a[i].append(p[i][v])
            a = numpy.array(a)
            return a

        p = ungroup_vector_property(self, pos)
        a = numpy.array([x.fa for x in p])
        return a

    def set_2d_array(self, a, pos=None):
        r"""Set the entries of the vector-valued property map from a
        two-dimensional array ``a``. If given, the parameter ``pos`` must be a
        sequence of integers which specifies the indexes of the property values
        which will be set."""

        if self.key_type() == "g":
            raise ValueError("Cannot set multidimensional array for graph property maps.")
        if "vector" not in self.value_type():
            if len(a.shape) != 1:
                raise ValueError("Cannot set array of shape %s to non-vector property map of type %s" % \
                                 (str(a.shape), self.value_type()))
            if self.value_type() != "string":
                self.fa = a
            else:
                g = self.get_graph()
                if self.key_type() == "v":
                    iters = g.vertices()
                else:
                    iters = [None for i in range(g.edge_index_range)]
                    idx = g.edge_index
                    for e in g.edges():
                        iters[idx[e]] = e
                    iters = [e for e in iters if e is not None]
                for j, v in enumerate(iters):
                    self[v] = a[j]
            return

        val = self.value_type()[7:-1]
        ps = []
        for i in range(a.shape[0]):
            ps.append(self.get_graph().new_property(self.key_type(), val))
            if self.value_type() != "string":
                ps[-1].fa = a[i]
            else:
                g = self.get_graph()
                if self.key_type() == "v":
                    iters = g.vertices()
                else:
                    iters = [None for i in range(g.edge_index_range)]
                    idx = g.edge_index
                    for e in g.edges():
                        iters[idx[e]] = e
                    iters = [e for e in iters if e is not None]
                for j, v in enumerate(iters):
                    ps[-1][v] = a[i, j]
        group_vector_property(ps, val, self, pos)

    def is_writable(self):
        """Return True if the property is writable."""
        return self.__map.is_writable()


    def set_value(self, val):
        """Sets all values in the property map to ``val``."""
        g = self.get_graph()
        val = self.__convert(val)
        if self.key_type() == "v":
            libcore.set_vertex_property(g._Graph__graph, _prop("v", g, self), val)
        elif self.key_type() == "e":
            libcore.set_edge_property(g._Graph__graph, _prop("e", g, self), val)
        else:
            self[g] = val

    def reserve(self, size):
        """Reserve enough space for ``size`` elements in underlying container. If the
           original size is already equal or larger, nothing will happen."""
        pass

    def resize(self, size):
        """Resize the underlying container to contain exactly ``size`` elements."""
        pass

    def shrink_to_fit(self):
        """Shrink size of underlying container to accommodate only the necessary amount,
        and thus potentially freeing memory."""
        g = self.get_graph()
        if self.key_type() == "v":
            size = g.num_vertices(True)
        elif self.key_type() == "e":
            size = g.edge_index_range
        else:
            size = 1
        self.__map.resize(size)
        self.__map.shrink_to_fit()

    def data_ptr(self):
        """Return the pointer to memory where the data resides."""
        return self.__map.data_ptr()

    def __getstate__(self):
        g = self.get_graph()
        if g is None:
            raise ValueError("cannot pickle orphaned property map")
        value_type = self.value_type()
        key_type = self.key_type()
        if not self.is_writable():
            vals = None
        else:
            u = GraphView(g, skip_vfilt=True, skip_efilt=True)
            if key_type == "v":
                vals = [self.__convert(self[v]) for v in u.vertices()]
            elif key_type == "e":
                vals = [self.__convert(self[e]) for e in u.edges()]
            else:
                vals = self.__convert(self[g])

        state = dict(g=g, value_type=value_type,
                     key_type=key_type, vals=vals,
                     is_vindex=self is g.vertex_index,
                     is_eindex=self is g.edge_index)

        return state

    def __setstate__(self, state):
        conv_pickle_state(state)
        g = state["g"]
        key_type = _str_decode(state["key_type"])
        value_type = _str_decode(state["value_type"])
        vals = state["vals"]

        if state["is_vindex"]:
            pmap = g.vertex_index
        elif state["is_eindex"]:
            pmap = g.edge_index
        else:
            u = GraphView(g, skip_vfilt=True, skip_efilt=True)
            if key_type == "v":
                pmap = u.new_vertex_property(value_type, vals=vals)
            elif key_type == "e":
                pmap = u.new_edge_property(value_type, vals=vals)
            else:
                pmap = u.new_graph_property(value_type)
                pmap[u] = vals
            pmap = g.own_property(pmap)

        self.__map = pmap.__map
        self.__g = pmap.__g
        self.__base_g = pmap.__base_g
        self.__key_type = key_type
        self.__convert = _converter(self.value_type())
        self.__register_map()

