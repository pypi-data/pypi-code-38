"""
Representation of a capability region of injectors and converters.
"""

from collections import namedtuple
import copy

import numpy as np

from hynet.types_ import hynet_float_


class HalfSpace(namedtuple('HalfSpace', ['offset', 'slope'])):
    """
    Representation of a half-space in a capability region.

    The half-spaces of a capability region are specified in terms of a
    nonnegative relative offset "``offset``" w.r.t. to the corresponding
    reactive power limit (i.e., the absolute offset is the reactive power limit
    multiplied by ``offset``) and its slope "``slope``".  In the dimension of
    active power, it is anchored at the corresponding active power limit.
    """
    def __repr__(self):
        return (u'({0:.0%}/{1:.0f}\N{DEGREE SIGN})'
                ).format(self.offset, np.arctan(self.slope) * 180/np.pi)


class CapRegion:
    """
    Specification of a capability region.

    The capability region is the intersection of a box and a polyhedron. Let
    ``s = [p, q]^T`` be the vector of active and reactive power injection. The
    capability region ``S`` is the intersection of ``S_box`` and ``S_phs``,
    where
    ::

        (1) S_box = { s in R^2: p_min <= p <= p_max, q_min <= q <= q_max }
        (2) S_phd = { s in R^2: A*s <= b }.

    The polyhedron ``S_phd`` is defined by the properties ``lt``, ``lb``,
    ``rt``, and ``rb``, which are half-spaces that are defined by a
    *nonnegative* relative offset and a slope, see the parameter description
    below. The parametrization in ``(2)`` can be obtained using the method
    ``get_polyhedron``.

    Parameters
    ----------
    p_min : .hynet_float_
        Active power lower bound in MW.
    p_max : .hynet_float_
        Active power upper bound in MW.
    q_min : .hynet_float_
        Reactive power lower bound in Mvar.
    q_max : .hynet_float_
        Reactive power upper bound in Mvar.
    lt : HalfSpace or None
        Left-top half-space or ``None`` if omitted. This half-space is
        anchored at ``(p,q)`` with ``p = p_min`` and ``q = lt.offset * q_max``.
        The slope must be *positive*.
    rt : HalfSpace or None
        Right-top half-space or ``None`` if omitted. This half-space is
        anchored at ``(p,q)`` with ``p = p_max`` and ``q = rt.offset * q_max``.
        The slope must be *negative*.
    lb : HalfSpace or None
        Left-bottom half-space or ``None`` if omitted. This half-space is
        anchored at ``(p,q)`` with ``p = p_min`` and ``q = lb.offset * q_min``.
        The slope must be *negative*.
    rb : HalfSpace or None
        Right-bottom half-space or ``None`` if omitted. This half-space is
        anchored at ``(p,q)`` with ``p = p_max`` and ``q = rb.offset * q_min``.
        The slope must be *positive*.
    """
    def __init__(self, p_bnd=None, q_bnd=None,
                 lt=None, rt=None, lb=None, rb=None):
        """
        Initialize the capability region.

        Please refer to the class documentation for a detailed description of
        the parameters.

        Parameters
        ----------
        p_bnd : (.hynet_float_, .hynet_float_), optional
            Tuple ``(p_min, p_max)`` of active power bounds (default
            ``(0, 0)``).
        q_bnd : (.hynet_float_, .hynet_float_), optional
            Tuple ``(q_min, q_max)`` of reactive power bounds (default
            ``(0, 0)``).
        lt : HalfSpace, optional
            Left-top half-space (omitted by default).
        rt : HalfSpace, optional
            Right-top half-space (omitted by default).
        lb : HalfSpace, optional
            Left-bottom half-space (omitted by default).
        rb : HalfSpace, optional
            Right-bottom half-space (omitted by default).
        """
        (self.p_min, self.p_max) = (0, 0) if p_bnd is None else p_bnd
        (self.q_min, self.q_max) = (0, 0) if q_bnd is None else q_bnd
        self._lt = self._rt = self._lb = self._rb = None
        (self.lt, self.rt, self.lb, self.rb) = (lt, rt, lb, rb)

    @property
    def lt(self):
        """Return the left-top half-space."""
        return self._lt

    @lt.setter
    def lt(self, value):
        """Set the left-top half-space."""
        if isinstance(value, HalfSpace):
            if value.offset < 0:
                raise ValueError("Offset must be nonnegative.")
            elif value.slope <= 0:
                raise ValueError("Slope must be positive.")
        elif value is not None:
            raise ValueError("Instance of HalfSpace or None expected.")
        self._lt = value

    @property
    def rt(self):
        """Return the right-top half-space."""
        return self._rt

    @rt.setter
    def rt(self, value):
        """Set the right-top half-space"""
        if isinstance(value, HalfSpace):
            if value.offset < 0:
                raise ValueError("Offset must be nonnegative.")
            elif value.slope >= 0:
                raise ValueError("Slope must be negative.")
        elif value is not None:
            raise ValueError("Instance of HalfSpace or None expected.")
        self._rt = value

    @property
    def lb(self):
        """Return the left-bottom half-space."""
        return self._lb

    @lb.setter
    def lb(self, value):
        """Set the left-bottom half-space."""
        if isinstance(value, HalfSpace):
            if value.offset < 0:
                raise ValueError("Offset must be nonnegative.")
            elif value.slope >= 0:
                raise ValueError("Slope must be negative.")
        elif value is not None:
            raise ValueError("Instance of HalfSpace or None expected.")
        self._lb = value

    @property
    def rb(self):
        """Return the right-bottom half-space."""
        return self._rb

    @rb.setter
    def rb(self, value):
        """Set the right-bottom half-space."""
        if isinstance(value, HalfSpace):
            if value.offset < 0:
                raise ValueError("Offset must be nonnegative.")
            elif value.slope <= 0:
                raise ValueError("Slope must be positive.")
        elif value is not None:
            raise ValueError("Instance of HalfSpace or None expected.")
        self._rb = value

    def __repr__(self):
        rep = ('[{0.p_min:.1f},{0.p_max:.1f}]x[{0.q_min:.1f},{0.q_max:.1f}]'
               .format(self))
        if self.lt is not None:
            rep += 'LT' + str(self.lt)
        if self.rt is not None:
            rep += 'RT' + str(self.rt)
        if self.lb is not None:
            rep += 'LB' + str(self.lb)
        if self.rb is not None:
            rep += 'RB' + str(self.rb)
        return rep

    def __eq__(self, other):
        """Return True if the capability regions feature the same parameters."""
        if other is None:
            return False
        return (self.p_min == other.p_min and
                self.p_max == other.p_max and
                self.q_min == other.q_min and
                self.q_max == other.q_max and
                self.lt == other.lt and
                self.rt == other.rt and
                self.lb == other.lb and
                self.rb == other.rb)

    def copy(self):
        """Return a deep copy of this capability region."""
        return copy.deepcopy(self)

    def has_polyhedron(self):
        """Return ``True`` if any of the half-spaces is set."""
        return any(x is not None for x in [self.lt, self.rt, self.lb, self.rb])

    def get_polyhedron(self):
        """
        Returns the polyhedron formulation ``S_phd = { s in R^2: A*s <= b }``.

        Returns
        -------
        A : np.ndarray
            ``A`` in the formulation of the polyhedron above.
        b : np.ndarray
            ``b`` in the formulation of the polyhedron above.
        name : list[str]
            Abbreviation of the corresponding half-space for each row.
        """
        A = np.ndarray((0, 2), dtype=hynet_float_)
        b = np.ndarray(0, dtype=hynet_float_)
        name = []
        if self.lt is not None:
            (r, s) = (self.lt.offset, self.lt.slope)
            A = np.vstack((A, [-s, 1]))
            b = np.concatenate((b, [r * self.q_max - s * self.p_min]))
            name.append('lt')
        if self.rt is not None:
            (r, s) = (self.rt.offset, self.rt.slope)
            A = np.vstack((A, [-s, 1]))
            b = np.concatenate((b, [r * self.q_max - s * self.p_max]))
            name.append('rt')
        if self.lb is not None:
            (r, s) = (self.lb.offset, self.lb.slope)
            A = np.vstack((A, [s, -1]))
            b = np.concatenate((b, [s * self.p_min - r * self.q_min]))
            name.append('lb')
        if self.rb is not None:
            (r, s) = (self.rb.offset, self.rb.slope)
            A = np.vstack((A, [s, -1]))
            b = np.concatenate((b, [s * self.p_max - r * self.q_min]))
            name.append('rb')
        return A, b, name

    def scale(self, scaling):
        """Scale the upper and lower bound on active and reactive power."""
        if scaling < 0:
            raise ValueError("Expecting a nonnegative scaling factor.")
        self.p_min *= scaling
        self.p_max *= scaling
        self.q_min *= scaling
        self.q_max *= scaling
        return self

    def add_power_factor_limit(self, power_factor):
        """
        Add a left-top and left-bottom half-space to limit the power factor.

        Parameters
        ----------
        power_factor : .hynet_float_
            Power factor limit.
        """
        if not 0 < power_factor < 1:
            raise ValueError("Power factor must be in (0,1).")
        if not 0 <= self.p_min < self.p_max and self.q_min < 0 < self.q_max:
            raise ValueError(("Capability region must be in the right half-"
                              "plane, with a nonempty interior that includes "
                              "zero reactive power for all p_min < p < p_max."))
        slope = np.sqrt(1/np.square(power_factor) - 1)
        self.lt = HalfSpace(slope * self.p_min / self.q_max, slope)
        self.lb = HalfSpace(-slope * self.p_min / self.q_min, -slope)

    def edit(self):
        """
        Edit this capability region in the capability region visualizer.

        **Caution:** Due to technical reasons, all open ``matplotlib`` figures
        are closed during this call.

        **Remark:** In case you are using MAC OS X, please be aware of `this
        issue <https://stackoverflow.com/questions/32019556/
        matplotlib-crashing-tkinter-application>`_ with ``matplotlib`` and
        ``tkinter``, which causes Python to crash if the capability region
        visualizer is opened. To avoid it, set ``matplotlib``'s backend to
        ``TkAgg`` *before* importing *hynet* using

        >>> import matplotlib
        >>> matplotlib.use('TkAgg')
        """
        from hynet.visual.capability.visualizer import Window
        Window.show(self, edit=True)

    def show(self, operating_point=None):
        """
        Show this capability region in the capability region visualizer.

        **Caution:** Due to technical reasons, all open ``matplotlib`` figures
        are closed during this call.

        **Remark:** In case you are using MAC OS X, please be aware of `this
        issue <https://stackoverflow.com/questions/32019556/
        matplotlib-crashing-tkinter-application>`_ with ``matplotlib`` and
        ``tkinter``, which causes Python to crash if the capability region
        visualizer is opened. To avoid it, set ``matplotlib``'s backend to
        ``TkAgg`` *before* importing *hynet* using

        >>> import matplotlib
        >>> matplotlib.use('TkAgg')

        Parameters
        ----------
        operating_point : .hynet_complex_, optional
            If provided, a marker is shown for this operating point in the
            P/Q-plane.
        """
        from hynet.visual.capability.visualizer import Window
        pq_point = (operating_point.real, operating_point.imag)
        Window.show(self, edit=False, operating_point=pq_point)


class ConverterCapRegion(CapRegion):
    """
    Specification of a converter capability region.

    The capability region is specified in terms of the apparent power flow
    at the respective terminal bus of the converter, see ``CapRegion`` for
    more information. With respect to the parameters returned by
    ``get_polyhedron`` and ``get_box_constraint``, this class considers the
    converter state variable ``f = [p_src, p_dst, q_src, q_dst]^T`` instead
    of the apparent power vector ``s = [p, q]^T`` considered in ``CapRegion``.

    See Also
    --------
    hynet.scenario.capability.CapRegion
    """
    def get_polyhedron(self, terminal, loss_factor):
        """
        Returns the polyhedron formulation ``S_phd = { f in R^4: A*f <= b }``.

        **Remark:** In contrast to ``CapRegion``, the polyhedron does not only
        include the half-spaces, but also the upper and lower bound on active
        power.

        Parameters
        ----------
        terminal : str
            Terminal of the converter (``'src'`` or ``'dst'``) with which the
            capability region is associated.
        loss_factor : float
            Proportional loss factor for (a) the *backward* flow if the
            terminal is ``'src'`` and (b) the *forward* flow if the terminal
            is ``'dst'``.

        Returns
        -------
        A : np.ndarray
            ``A`` in the formulation of the polyhedron above.
        b : np.ndarray
            ``b`` in the formulation of the polyhedron above.
        name : list[str]
            Abbreviation of the corresponding half-space or active power limit
            for each row.

        See Also
        --------
        hynet.scenario.capability.ConverterCapRegion.get_box_constraint
        """
        if not 0 <= loss_factor < 1:
            raise ValueError("Loss factor must be in [0,1).")

        if terminal == 'src':
            F = [[1, loss_factor - 1, 0, 0], [0, 0, 1, 0]]
        elif terminal == 'dst':
            F = [[loss_factor - 1, 1, 0, 0], [0, 0, 0, 1]]
        else:
            raise ValueError("Expecting 'src' or 'dst' for terminal.")

        # Reformulate polyhedron in terms of f and add active power LB and UB
        F = np.array(F, dtype=hynet_float_)
        A, b, name = super().get_polyhedron()
        A = np.vstack((A.dot(F), F[0, :], -F[0, :]))
        b = np.concatenate((b, [self.p_max, -self.p_min]))
        name += ['p_max', 'p_min']
        return A, b, name

    @staticmethod
    def get_box_constraint(cap_src, cap_dst):
        """
        Return ``(f_lb, f_ub)`` of the state constraint ``f_lb <= f <= f_ub``.

        A converter comprises two capability regions, one at the source terminal
        (``cap_src``) and one at the destination terminal (``cap_dst``). Thus,
        the box constraint on the converter state variable is a combination of
        both and returned by this function. Note that the active power
        constraints are included in ``get_polyhedron`` and the upper bounds on
        ``p_src`` and ``p_dst`` in ``f`` are merely additional loosened
        upper bounds (cf. the remark in ``get_voltage_magnitude_bounds`` of
        ``SystemModel``).
        """
        f_lb = np.zeros(4, dtype=hynet_float_)  # LB on p_src, p_dst is 0
        f_lb[2] = cap_src.q_min  # q_src
        f_lb[3] = cap_dst.q_min  # q_dst

        f_ub = np.zeros(4, dtype=hynet_float_)
        f_ub[0] = np.max([abs(cap_src.p_max), abs(cap_dst.p_min)]) * 1.1  # p_src
        f_ub[1] = np.max([abs(cap_dst.p_max), abs(cap_src.p_min)]) * 1.1  # p_dst
        f_ub[2] = cap_src.q_max  # q_src
        f_ub[3] = cap_dst.q_max  # q_dst

        return f_lb, f_ub

    def add_power_factor_limit(self, power_factor):
        raise AttributeError(("The power factor limit is not applicable "
                              "to converter capability regions."))
