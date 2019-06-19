# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from collections import OrderedDict
import warnings

import numpy as np
from scipy import optimize
from sympathy.api.exceptions import SyDataError


def leastsq_diff(x, tvalues, t1, v1, t2, v2):
    """Returns sum of squares of the errors."""
    y1 = np.interp(tvalues, t1 - x, v1)
    y2 = np.interp(tvalues, t2, v2)

    cost = sum((y1 - y2) ** 2)
    return cost


def cost_sync_by_ls(x, t1, v1, t2, v2):
    """Returns sum of squares of the errors."""
    imin = 1
    imax = len(t2) - 2
    tmin = t2[imin]
    tmax = t2[imax]
    tvalues = tmin + np.random.rand(500) * (tmax - tmin)

    return leastsq_diff(x, tvalues, t1, v1, t2, v2)


class SynchConstraintError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class SynchronizationStrategy(object):
    """The base strategy used when synchronizing two systems."""

    def synchronize(self):
        raise NotImplementedError("Not implemented in interface.")


class SharedEvent(SynchronizationStrategy):
    def synchronize(self, threshold, t1, v1, t2, v2):
        try:
            first_v1_sample = self.values_that_satisfy(
                self.threshold, threshold, v1)[0]
            first_v2_sample = self.values_that_satisfy(
                self.threshold, threshold, v2)[0]
        except IndexError:
            raise SynchConstraintError(
                "No values matching the constraint was found")
        except Exception:
            raise Exception('No values matching the constraint was found')
        t2_offset = t1[first_v1_sample] - t2[first_v2_sample]

        return t2_offset

    def values_that_satisfy(self, constraint_func, threshold, values):
        return np.flatnonzero(constraint_func(threshold, values))


class PositiveFlank(object):
    def threshold(self, threshold, values):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            diffs = np.append(np.diff((values > threshold).astype(int)), [0])
        return diffs == 1


class NegativeFlank(object):
    def threshold(self, threshold, values):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            diffs = np.append(np.diff((values > threshold).astype(int)), [0])
        return diffs == -1


class EitherFlank(object):
    def threshold(self, threshold, values):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            diffs = np.append(np.diff((values > threshold).astype(int)), [0])
        return np.abs(diffs) == 1


class SharedEventPositiveFlank(SharedEvent, PositiveFlank):
    """The first positive flank for each timeseries is matched."""
    pass


class SharedEventNegativeFlank(SharedEvent, NegativeFlank):
    """The first negative flank for each timeseries is matched."""
    pass


def normalize_time_arrays(t1, t2):
    if t1.dtype.kind == t2.dtype.kind == 'M':
        timeunit = np.timedelta64(1, 'us')
    elif t1.dtype.kind in ('f', 'i', 'u') and t2.dtype.kind in ('f', 'i', 'u'):
        timeunit = 1
    else:
        raise SyDataError(
            "Either both rasters should have datetime time basis or "
            "both rasters should have float time basis.")
    t1 = (t1 - t1[0]) / timeunit
    t2 = (t2 - t2[0]) / timeunit
    return t1, t2, timeunit


class SyncParts(SynchronizationStrategy, EitherFlank):
    """Move the entire signal to where the first part fits best and then wiggle
    each part using least square fitting.
    """

    def __init__(self):
        super(SyncParts, self).__init__()

    def _get_base_offset(self, t1, v1, t2, v2):
        flanks = self.threshold((max(v2) + min(v2)) / 2, v1)
        v2_flanks = np.flatnonzero(self.threshold((max(v2) + min(v2)) / 2, v2))
        if not len(v2_flanks):
            return None

        t2_offset = t2[v2_flanks[0]] - t2[0]
        min_offset = None
        min_cost = np.inf
        for flank in np.flatnonzero(flanks):
            offset = t1[flank] - t2[0] - t2_offset
            cost = cost_sync_by_ls(offset, t1, v1, t2, v2)
            if cost < min_cost:
                min_cost = cost
                min_offset = offset

        return min_offset

    def synchronize(self, threshold, t1, v1, t2, v2):
        t1, t2, timeunit = normalize_time_arrays(t1, t2)

        base_offset = self._get_base_offset(t1, v1, t2, v2)
        if base_offset is None:
            return None
        t2 = t2 + base_offset

        imin = 1
        imax = len(t2) - 2
        tmin = t2[imin]
        tmax = t2[imax]
        tvalues = tmin + np.random.rand(500) * (tmax - tmin)

        res = optimize.minimize_scalar(
            leastsq_diff, args=(tvalues, t1, v1, t2, v2))
        t2_offset_ls = res.x

        return (base_offset + t2_offset_ls) * timeunit


class OptimizationLSF(SharedEvent, PositiveFlank):
    """Least square optimization with Shared event (positive flank) as initial
    guess. Random indices used for fitting.
    """

    def synchronize(self, threshold, t1, v1, t2, v2):
        def lsf_leastsq_diff(x, tvalues, t1, v1, t2, v2):
            """Returns sum of squares of the errors."""
            tmin = max((t1 - x)[0], t2[0])
            tmax = min((t1 - x)[-1], t2[-1])
            tvalues = tvalues[tvalues >= tmin]
            tvalues = tvalues[tvalues <= tmax]
            y1 = np.interp(tvalues, t1 - x, v1)
            y2 = np.interp(tvalues, t2, v2)

            cost = sum((y1 - y2) ** 2)
            return cost

        t1, t2, timeunit = normalize_time_arrays(t1, t2)

        tmin = min(t1[0], t2[0])
        tmax = max(t1[-1], t2[-1])
        tvalues = tmin + np.random.rand(500) * (tmax - tmin)

        shared_event = SharedEventPositiveFlank()
        base_offset = shared_event.synchronize(threshold, t1, v1, t2, v2)
        t2 = t2 + base_offset

        xopt = optimize.minimize_scalar(
            lsf_leastsq_diff, args=(tvalues, t1, v1, t2, v2))
        t2_offset_ls = xopt.x

        return (base_offset + t2_offset_ls) * timeunit


class SynchronizeTime(object):
    """Calculate a time offset for between a system and a master system"""

    sync_strategies = OrderedDict([
        ('OptimizationLSF', OptimizationLSF),
        ('Shared event (positive)', SharedEventPositiveFlank),
        ('Shared event (negative)', SharedEventNegativeFlank),
        ('Sync parts', SyncParts)])

    def __init__(self):
        super(SynchronizeTime, self).__init__()

    def strategies(self):
        return list(self.sync_strategies.keys())

    def strategy_docs(self):
        return [v.__doc__ for v in self.sync_strategies.values()]

    def time_and_speed_from_file(
            self, in_adaf, refsignal_name, synceesignal_name):
        ref = None
        syncee = None

        if refsignal_name in in_adaf.ts.keys():
            ref = in_adaf.ts[refsignal_name]
        if synceesignal_name in in_adaf.ts.keys():
            syncee = in_adaf.ts[synceesignal_name]

        return ref, syncee

    def synchronize_file(self, in_adaf, refsignal_name, synceesignal_name,
                         threshold, syncstrategy, vjoin_name=None):

        ref, syncee = self.time_and_speed_from_file(
            in_adaf, refsignal_name, synceesignal_name)

        if ref:
            ref_time = ref.t
            ref_speed = ref.y
        else:
            return None
        if syncee:
            syncee_time = syncee.t
            syncee_speed = syncee.y
            syncee_raster = (
                in_adaf.sys[syncee.system_name()][syncee.raster_name()])
        else:
            return None

        if syncstrategy == 'Sync parts' and vjoin_name in syncee_raster:
            index = syncee_raster[vjoin_name].y
        else:
            index = np.array([0] * syncee_time.size)

        unique_indices = []
        for i in index:
            if i not in unique_indices:
                unique_indices.append(i)

        opt = self.sync_strategies[syncstrategy]()
        offsets = []
        for vjoin_index in unique_indices:
            syncee_time_part = syncee_time[index == vjoin_index]
            syncee_speed_part = syncee_speed[index == vjoin_index]

            try:
                offset = opt.synchronize(threshold, ref_time, ref_speed,
                                         syncee_time_part, syncee_speed_part)
            except SynchConstraintError:
                offset = None
            offsets.append(offset)

        return offsets

    def apply_offsets(self, time, offsets, index):
        new_time = time.copy()

        unique_indices = []
        for i in index:
            if i not in unique_indices:
                unique_indices.append(i)

        for i, vjoin_index in enumerate(unique_indices):
            mask = index == vjoin_index
            if offsets[i] is not None:
                new_time[mask] = new_time[mask] + offsets[i]

        return new_time

    def write_to_file(self, in_adaf, out_adaf, offsets, syncee_system,
                      vjoin_name):
        if syncee_system not in in_adaf.sys.keys():
            return
        for raster_name in in_adaf.sys[syncee_system].keys():
            in_raster = in_adaf.sys[syncee_system][raster_name]
            basis_column = in_raster.basis_column()
            time = basis_column.value()

            if vjoin_name in in_raster:
                index = in_raster[vjoin_name].y
            else:
                index = np.array([0] * time.size)

            new_time = self.apply_offsets(time, offsets, index)
            out_adaf.sys[syncee_system][raster_name].create_basis(
                new_time, attributes=basis_column.attr)
