import os
import itertools
import copy
import warnings
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .LoadFollow import LoadFollow
from .NullComp import NullComp
from .Component import Component
from .LoadComponent import LoadComponent
from .IntermittentComponent import IntermittentComponent
from .StorageComponent import StorageComponent
from .DispatchableComponent import DispatchableComponent
from .SinkComponent import SinkComponent
from .GridComponent import GridComponent
from .SupplementaryComponent import SupplementaryComponent
from .Connector import Connector
from .LoadConnector import LoadConnector
from .IntermittentConnector import IntermittentConnector
from .StorageConnector import StorageConnector
from .DispatchableConnector import DispatchableConnector
from .SinkConnector import SinkConnector
from .GridConnector import GridConnector
from .SupplementaryConnector import SupplementaryConnector

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Control(object):
    """Power system controller module.

    Parameters
    ----------
    comp_list : list
        List of initialized component objects.

    """

    def __init__(self, comp_list):
        """Initializes the base class."""

        # store parameters
        self.comp_list = comp_list  # list of components

        # initialize data storage
        self.algo = None  # dispatch algorithm
        self.ts = dict(  # time series data for power
            (i, np.zeros(8760)) for i in comp_list
        )
        self.ts_soc = dict(  # time series data for SOC
            (i, np.ones(8760)) for i in comp_list
            if isinstance(i, StorageComponent)
        )

        # initialize metrics arrays
        self.npv = np.array([])  # NPV
        self.lcoe = np.array([])  # LCOE
        self.lcow = np.array([])  # LCOW
        self.re_frac = np.array([])  # RE-share
        self.lolp = np.array([])  # LOLP

    def simu(
        self, size, spin_res=0.1, yr_proj=20.0, infl=0.1,
        proj_capex=0.0, proj_opex=0.0, algo=LoadFollow, **kwargs
    ):
        """Simulates a scenario given a set of sizes and calculates the LCOE.

        Parameters
        ----------
        size : dict
            Sizes [kW] or [kWh] of the components. Use component objects as
            keys and sizes as values.
        spin_res : float
            Spinning reserve.
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.
        proj_capex : float
            Capital expenses [USD] of the project.
        proj_opex : float
            Fixed yearly operating expenses [USD/yr] of the project.
        algo : Dispatch
            The dispatch algorithm to be used.

        Other Parameters
        ----------------
        do_inval : bool
            True if invalid cases should have nan LCOE and RE-share.
        print_prog : bool
            True if calculation progress should be printed.
        print_out : bool
            True if results should be printed. Invokes res_print().

        Notes
        -----
        Sets LCOE to nan when the size combination is infeasible.

        """
        # get keyword arguments
        do_inval = kwargs.pop('do_inval', True)
        print_prog = kwargs.pop('print_prog', True)
        print_out = kwargs.pop('print_out', True)

        # initialize for console output
        t0 = time.time()  # time
        mark = np.arange(0, 8760, 876)  # markers for simulation

        # initialize dispatch algorithm
        al = algo(self.comp_list, size, spin_res)

        # perform simulation
        for hr in range(8760):
            al.step()  # increment simulation
            for cp in self.comp_list:
                self.ts[cp][hr] = cp.pow  # record power at timestep
                if isinstance(cp, StorageComponent):
                    self.ts_soc[cp][hr] = cp.soc  # record SOC at timestep
            if print_prog and hr in mark:  # display progress
                print(
                    'Simulation Progress: {:.0f}%'.format((hr+1)/87.6),
                    flush=True
                )

        # store completed dispatch algorithm object
        self.algo = al

        # calculate metrics
        self.npv = Control._npv(
            al, yr_proj, infl, proj_capex, proj_opex
        )[0]
        self.lcoe = Control._lcoe(
            al, yr_proj, infl, proj_capex, proj_opex
        )[0]
        self.lcow = Control._lcow(
            al, yr_proj, infl, proj_capex, proj_opex
        )[0]

        # calculate RE-share
        pow_ldts = np.zeros(8760)  # time-series data of total load
        enr_tot = np.zeros(8760)  # total energy
        enr_re = np.zeros(8760)  # total renewable energy
        for cp in self.comp_list:
            if isinstance(cp, LoadComponent):
                pow_ldts += self.ts[cp]  # time series data of total load
        for cp in self.comp_list:
            if not isinstance(cp, LoadComponent) and cp.is_re is not None:
                ld_def = np.maximum(pow_ldts-enr_tot, 0)  # load deficit
                enr_tot += np.minimum(  # add to energy
                    self.ts[cp], ld_def  # do not go over load
                )
                if cp.is_re:  # add to RE energy
                    enr_re += np.minimum(  # add to energy
                        self.ts[cp], ld_def  # do not go over load
                    )
        self.re_frac = np.sum(enr_re)/np.sum(enr_tot)

        # check if invalid
        if do_inval and not al.feas:
            self.lcoe = np.nan
            self.re_frac = np.nan

        # print results
        if print_prog:
            t1 = time.time()
            print('Simulation completed in {:.4f} s.'.format(t1-t0))
        if print_out:
            self.res_print()

    def opt(
        self, spin_res=0.1, yr_proj=20.0, infl=0.1,
        proj_capex=0.0, proj_opex=0.0, size_max=None,
        size_min=None, algo=LoadFollow, **kwargs
    ):
        """Set component sizes such that NPV is optimized.

        Parameters
        ----------
        spin_res : float
            Spinning reserve.
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.
        proj_capex : float
            Capital expenses [USD] of the project.
        proj_opex : float
            Fixed yearly operating expenses [USD/yr] of the project.
        size_max : dict
            Maximum size constraint. Use the component object as keys and the
            size constraint as values.
        size_min : dict
            Minimum size constraint. Use the component object as keys and the
            size constraint as values.

        Other Parameters
        ----------------
        im_range : tuple of float or str
            Boundaries of the search space for the sizes of intermittent power
            components. Input as (min, max). Set to 'auto' to automatically
            find the search space.
        st_range : tuple of float or str
            Boundaries of the search space for the sizes of energy storage
            components. Input as (min, max). Set to 'auto' to automatically
            find the search space.
        dp_range : tuple of float or str
            Boundaries of the search space for the sizes of dispatchable power
            components. Input as (min, max). Set to 'auto' to automatically
            find the search space.
        sk_range : tuple of float or str
            Boundaries of the search space for the sizes of sink power
            components. Input as (min, max). Set to 'auto' to automatically
            find the search space.
        gd_range : tuple of float or str
            Boundaries of the search space for the size of the grid. Input as
            (min, max). Set to 'auto' to automatically find the search space.
        su_range : tuple of float or str
            Boundaries of the search space for the sizes of supplementary power
            components. Input as (min, max). Set to 'auto' to automatically
            find the search space.
        iter_simu : int
            Number of cases to simulate simultaneously.
        iter_npv : int
            Number of iterations to find the NPV.
        batch_size : int
            Number of simulations to be carried out simultaneously. Prevents
            the program from consuming too much memory.
        print_npv : bool
            True if opimization progress should be printed.
        print_simu : bool
            True if simulation progress should be printed.
        print_res : bool
            True if results should be printed.

        """
        # get keyword arguments
        im_range = kwargs.pop('im_range', 'auto')
        st_range = kwargs.pop('st_range', 'auto')
        dp_range = kwargs.pop('dp_range', 'auto')
        sk_range = kwargs.pop('sk_range', 'auto')
        gd_range = kwargs.pop('gd_range', 'auto')
        su_range = kwargs.pop('su_range', 'auto')
        iter_simu = kwargs.pop('iter_simu', 10)
        iter_npv = kwargs.pop('iter_npv', 5)
        batch_size = kwargs.pop('batch_size', 10000)
        print_prog = kwargs.pop('print_prog', True)
        print_out = kwargs.pop('print_out', True)

        # initialize for console output
        t0 = time.time()  # time

        # replace constraints with empty dict if there are none
        if size_max is None:
            size_max = {}
        if size_min is None:
            size_min = {}

        # check if adj or grid components are present
        has_dp = any(
            isinstance(i, DispatchableComponent) for i in self.comp_list
        )
        has_gd = any(isinstance(i, GridComponent) for i in self.comp_list)
        if has_dp or has_gd:  # no adjustable or grid components
            small_size = True  # use smaller search space
        else:
            small_size = False  # use larger search space

        # use smaller search space if adj or grid is present
        if small_size:  # based on peak
            pow_max = sum(  # sum of peak loads
                i.pow_max for i in self.comp_list
                if isinstance(i, LoadComponent)
            )
            auto_range = (0, pow_max*3.5)
        else:  # based on daily consumption
            enr_tot = sum(  # total annual load
                i.enr_tot for i in self.comp_list
                if isinstance(i, LoadComponent)
            )
            auto_range = (0, enr_tot*2/365)

        # determine number of components to be sized:
        num_comp = sum(  # load is not counted
            1 for i in self.comp_list if not isinstance(i, LoadComponent)
        )

        # initialize
        rng_list = [im_range, st_range, dp_range, sk_range, gd_range, su_range]
        rng_dict = {}  # dict with ranges
        cls_list = [  # list of component classes
            IntermittentComponent, StorageComponent, DispatchableComponent,
            SinkComponent, GridComponent, SupplementaryComponent
        ]

        # assign auto search spaces
        for i in range(6):
            if rng_list[i] == 'auto':  # replace auto ranges
                rng_list[i] = auto_range

        # create dict of ranges
        for cp in self.comp_list:
            for i in range(6):
                if isinstance(cp, cls_list[i]):  # sort by component type
                    rng_dict[cp] = rng_list[i]  # copy the range

        # make a copy of the original ranges
        orig_dict = copy.deepcopy(rng_dict)

        # calculate batch size
        num_case_all = iter_simu**num_comp  # total number of cases
        num_batch, num_rem = divmod(num_case_all, batch_size)

        # initialize for subset iteration
        size_dict = {}  # dict with sizes
        sub_dict = {}  # dict with subset of sizes
        opt_dict = {}  # dict with optimum sizes
        opt_npv = np.inf  # optimum NPV

        # begin iteration
        for i in range(0, iter_npv):  # number of optimization loops

            # convert ranges into sizes
            for cp in rng_dict:

                # determine upper bound of component
                if cp in list(size_max.keys()):
                    ub = np.min([rng_dict[cp][1], size_max[cp]])
                else:
                    ub = rng_dict[cp][1]

                # determine lower bound of component
                if cp in list(size_min.keys()):
                    lb = np.max([rng_dict[cp][0], size_min[cp]])
                else:
                    lb = rng_dict[cp][0]

                # create range
                size_dict[cp] = np.linspace(lb, ub, num=iter_simu)

            # create generator object that dispenses size combinations
            gen = (itertools.product(*list(size_dict.values())))

            # begin iteration per batch
            for j in range(num_batch+1):

                # subset initial list of sizes
                if j == num_batch:  # last batch
                    if num_rem == 0:  # no remaining cases
                        break
                    sub_arr = np.array(list(
                        next(gen) for i in range(0, num_rem)
                    ))  # extracts combinations
                else:
                    sub_arr = np.array(list(
                        next(gen) for i in range(0, batch_size)
                    ))  # extracts combinations

                # assign sizes to subset array
                comp = 0
                for cp in size_dict:
                    sub_dict[cp] = sub_arr[:, comp]
                    comp += 1

                # initialize dispatch algorithm
                # note: this modifies sub_dict by ading NullComps
                al = algo(self.comp_list, sub_dict, spin_res)

                # perform simulation
                for hr in range(0, 8760):
                    al.step()

                # calculate NPV
                npv = Control._npv(
                    al, yr_proj, infl, proj_capex, proj_opex
                )

                # determine invalid cases
                inval = np.logical_not(al.feas)

                # continue with next loop if all invalid
                if np.all(inval):
                    continue

                # find array index of lowest valid NPV
                npv[inval] = np.nan
                opt_ind = np.nanargmin(npv)

                # remove NullComp from sub_dict
                sub_dict = dict(
                    (i, j) for i, j in zip(sub_dict.keys(), sub_dict.values())
                    if not isinstance(i, NullComp)
                )

                # check if NPV of this subset is lower than before
                if npv[opt_ind] < opt_npv:
                    opt_npv = npv[opt_ind]  # set optimum NPV
                    for cp in sub_dict:  # set optimum sizes
                        opt_dict[cp] = sub_dict[cp][opt_ind]

            # prepare new list
            for cp in rng_dict:
                sep = size_dict[cp][1]-size_dict[cp][0]
                lb = np.maximum(opt_dict[cp]-sep, 0)  # new lower bound
                ub = np.maximum(opt_dict[cp]+sep, 0)  # new upper bound
                rng_dict[cp] = (lb, ub)

            # output progress
            if print_prog:
                prog = (i+1)*100/iter_npv
                out = 'Optimization progress: {:.2f}%'.format(prog)
                print(out, flush=True)

        # set components to optimum
        self.simu(
            opt_dict, spin_res, yr_proj, infl,
            proj_capex, proj_opex, algo,
            print_prog=False, print_out=False
        )

        # print results
        if print_prog:
            t1 = time.time()
            out = 'Optimization completed in {:.4f} min.'.format((t1-t0)/60)
            print(out, flush=True)
        if print_out:
            self.res_print()

    def rel(
        self, size, num_pts=10000, spin_res=0.1,
        algo=LoadFollow, **kwargs
    ):
        """Simulates a scenario given a set of sizes and calculates the LCOE.

        Parameters
        ----------
        size : dict
            Sizes [kW] or [kWh] of the components. Use component objects as
            keys and sizes as values.
        num_pts : int
            Number of points to use for Monte Carlo.
        spin_res : float
            Spinning reserve.
        algo : Dispatch
            The dispatch algorithm to be used.

        Other Parameters
        ----------------
        batch_max : int
            Maximum number of simulations to be carried out simultaneously.
            Prevents the program from consuming too much memory.
        do_inval : bool
            True if invalid cases should have nan LCOE and RE-share.
        print_prog : bool
            True if calculation progress should be printed.
        print_out : bool
            True if results should be printed. Invokes res_print().
        tol : float
            Tolerance when checking if power meets the load.

        """
        # get keyword arguments
        max_size = kwargs.pop('batch_max', 10000)
        print_prog = kwargs.pop('print_prog', True)
        print_out = kwargs.pop('print_out', True)
        tol = kwargs.pop('tol', 1e-2)

        # initialize for console output
        t0 = time.time()  # time
        mark = np.arange(0, 8760, 876)  # markers for simulation

        # modify size array
        size_dict = {}
        for cp in size:
            size_dict[cp] = size[cp]*np.ones(num_pts)

        # initialize dispatch algorithm
        al = algo(self.comp_list, size_dict, spin_res)

        # begin simulations
        lolp = np.zeros(num_pts)
        for hr in range(8760):

            # perform step
            al.step()

            # display progress
            if print_prog and hr in mark:
                print(
                    'Calculation Progress: {:.0f}%'.format((hr+1)/87.6),
                    flush=True
                )

        # divide by hours per year
        self.lolp = np.average(al.num_def)/8760

        # print results
        if print_prog:
            t1 = time.time()
            print('Simulation completed in {:.4f} s.'.format(t1-t0))
        if print_out:

            # print sizes
            print('SYSTEM SUMMARY')
            print('Sizes [kW] or [kWh]:')
            for cp in self.comp_list:
                if not isinstance(cp, LoadComponent):
                    if np.atleast_1d(cp.size).size == 1:  # one scenario only
                        print(
                            '    {:15}: {:>12.4f}'
                            .format(cp.name_solid, cp.size[0])
                        )
                    else:  # multiple scenarios simulated
                        print(
                            '    {:15}: '.format(cp.name_solid) +
                            str(cp.size[0])
                        )

            # other parameters
            print('Parameters:')
            print('    LOLP [%]       : {:>12.4f}'.format(self.lolp*100))

    def powflow_plot(
        self, time_range=(0, 168), fig_size=(12, 5),
        pow_lim='auto'
    ):
        """Generates a power flow of the system.

        Parameters
        ----------
        time_range : tuple
            Range of times to plot.
        fig_size : tuple
            Size of plot.
        pow_lim : ndarray
            Limits for power axis.

        """
        # initialize dicts
        name_solid = {}  # dict of components and names
        color_solid = {}  # dict of components and colors
        pow_solid = {}  # dict of components and powers
        name_line = {}  # dict of components and names
        color_line = {}  # dict of components and colors
        pow_line = {}  # dict of components and powers
        soc_line = {}  # dict of components and SOC

        # get names, colors, and value of each component
        for cp in self.comp_list:
            if cp.color_solid is not None:  # stacked graph for power sources
                name_solid[cp] = cp.name_solid
                color_solid[cp] = cp.color_solid
                pow_solid[cp] = self.ts[cp][time_range[0]:time_range[1]]
            if cp.color_line is not None:  # line graph for load and SOC
                if isinstance(cp, StorageComponent):  # storage has SOC
                    name_line[cp] = cp.name_line
                    color_line[cp] = cp.color_line
                    soc_line[cp] = self.ts_soc[cp][time_range[0]:time_range[1]]
                if isinstance(cp, LoadComponent):  # load
                    name_line[cp] = cp.name_line
                    color_line[cp] = cp.color_line
                    pow_line[cp] = self.ts[cp][time_range[0]:time_range[1]]

        # generate x-axis (list of times)
        t_axis = np.linspace(
            time_range[0], time_range[1],
            num=time_range[1]-time_range[0]
        )

        # create left axis for power
        fig, pow_axis = plt.subplots(figsize=fig_size)
        plt.xticks(
            np.arange(
                np.ceil(time_range[0]/12)*12,
                np.floor(time_range[1]/12)*12+1, step=12
            )
        )
        if pow_lim is not 'auto':
            plt.ylim(pow_lim)

        # axes labels
        pow_axis.set_xlabel('Time [h]')
        pow_axis.set_ylabel('Power [kW]')

        # initialize
        plot_list = []  # list of plot objects
        name_list = []  # list of corresponding names

        # plot power sources (solid graphs)
        pow_stack = 0  # total power below the graph
        for cp in name_solid:

            # add to list of plots
            plot_list.append(
                pow_axis.fill_between(
                    t_axis, pow_stack,
                    pow_stack+pow_solid[cp],
                    color=color_solid[cp]
                )
            )

            # add to list of names
            name_list.append(name_solid[cp])

            # increase pow stack
            pow_stack = pow_stack+pow_solid[cp]

        # plot power sources (line graphs)
        for cp in pow_line:

            # add to list of plots
            line_plot = pow_axis.plot(
                t_axis, pow_line[cp], color=color_line[cp]
            )
            plot_list.append(line_plot[0])

            # add to list of names
            name_list.append(name_line[cp])

        # plot soc on right axis
        soc_axis = pow_axis.twinx()  # make right y-axis
        soc_axis.set_ylabel('SOC')
        soc_axis.set_ylim(0, 1.1)

        # plot lines that represent SOC's
        for cp in soc_line.keys():

            # add to list of plots
            line_plot = soc_axis.plot(
                t_axis, soc_line[cp], color=color_line[cp]
            )
            plot_list.append(line_plot[0])

            # add to list of names
            name_list.append(name_line[cp])

        # generate plot
        plt.legend(tuple(plot_list), tuple(name_list))
        plt.show()

    def powflow_csv(self, file):
        """Generates a .csv file with the power flow.

        Parameters
        ----------
        file : str
            Filename for output file.

        """
        # initialize array with powers
        pow_out = np.arange(0, 8760).reshape((8760, 1))

        # initialize headers
        pow_head = ['Hour']

        # get the names and values of each component
        for cp in self.comp_list:
            if cp.name_solid is not None:
                pow_head.append(cp.name_solid)  # append component
                pow_out = np.append(
                    pow_out, self.ts[cp].reshape((8760, 1)), axis=1
                )
            if cp.name_line is not None:
                if isinstance(cp, StorageComponent):  # storage has SOC
                    pow_head.append(cp.name_line)  # append battery SOC
                    pow_out = np.append(
                        pow_out, self.ts_soc[cp].reshape((8760, 1)), axis=1
                    )
                if isinstance(cp, LoadComponent):
                    pow_head.append(cp.name_line)  # append load
                    pow_out = np.append(
                        pow_out, self.ts[cp].reshape((8760, 1)), axis=1
                    )

        pd.DataFrame(pow_out).to_csv(file, index=False, header=pow_head)

    def size_csv(self, file):
        """Generates a .csv file with the sizes.

        Parameters
        ----------
        file : str
            Filename for output file.

        """
        # initialize file
        file_out = open(file, mode='w')

        # get the sizes of each component
        for cp in self.comp_list:
            if cp.name_solid is not None:
                file_out.writelines(cp.name_solid+' : '+str(cp.size)+'\n')

        file_out.writelines('LCOE : '+str(self.lcoe)+'\n')

    def res_print(self):
        """Prints the sizes and calculated parameters in the console."""

        # print results
        print('SYSTEM SUMMARY')

        # sizes
        print('Sizes [kW] or [kWh]:')
        for cp in self.comp_list:
            if not isinstance(cp, LoadComponent):
                if np.atleast_1d(cp.size).size == 1:  # one scenario only
                    print(
                        '    {:15}: {:>12.4f}'
                        .format(cp.name_solid, cp.size[0])
                    )
                else:  # multiple scenarios simulated
                    print('    {:15}: '.format(cp.name_solid)+str(cp.size[0]))

        # other parameters
        print('Parameters:')
        if self.npv.size != 0 and not np.isnan(self.npv):
            print('    NPV [10^6 USD] : {:>12.4f}'.format(self.npv/1e6))
        if self.lcoe.size != 0 and not np.isnan(self.lcoe):
            print('    LCOE [USD/kWh] : {:>12.4f}'.format(self.lcoe))
        if self.lcow.size != 0 and not np.isnan(self.lcow):
            print('    LCOW [USD/m3]  : {:>12.4f}'.format(self.lcow))
        if self.re_frac.size != 0 and not np.isnan(self.re_frac):
            print('    RE-Share       : {:>12.4f}'.format(self.re_frac))
        if self.lolp.size != 0 and not np.isnan(self.lolp):
            print('    LOLP           : {:>12.4f}'.format(self.lolp))

    @staticmethod
    def _npv(dis, yr_proj, infl, proj_capex, proj_opex):
        """Calculates the net present value (NPV).

        Parameters
        ----------
        dis : Dispatch
            A Dispatch object from which to calculate the LCOE.
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.
        proj_capex : float
            Capital expenses [USD] of the project.
        proj_opex : float
            Fixed yearly operating expenses [USD/yr] of the project.

        Returns
        -------
        npv : ndarray
            The NPV of each scenario. Returns nan if scenario is invalid.

        """
        # start cost calculation in each module
        dis.ld.cost_calc(yr_proj, infl)
        dis.im.cost_calc(yr_proj, infl)
        dis.st.cost_calc(yr_proj, infl)
        dis.dp.cost_calc(yr_proj, infl)
        dis.sk.cost_calc(yr_proj, infl)
        dis.gd.cost_calc(yr_proj, infl)
        dis.su.cost_calc(yr_proj, infl)

        # calculate total cost
        npv = (
            dis.ld.cost+dis.im.cost+dis.st.cost +
            dis.dp.cost+dis.sk.cost+dis.gd.cost +
            dis.su.cost+proj_capex +
            proj_opex*np.sum(1/(1+infl)**np.arange(1, 1+yr_proj))
        )

        return npv

    @staticmethod
    def _lcoe(dis, yr_proj, infl, proj_capex, proj_opex):
        """Calculates the LCOE.

        Parameters
        ----------
        dis : Dispatch
            A Dispatch object from which to calculate the LCOE.
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.
        proj_capex : float
            Capital expenses [USD] of the project.
        proj_opex : float
            Fixed yearly operating expenses [USD/yr] of the project.

        Returns
        -------
        lcoe : ndarray
            The LCOE of each scenario. Returns nan if scenario is invalid.

        """
        # start cost calculation in each module
        dis.ld.cost_calc(yr_proj, infl)
        dis.im.cost_calc(yr_proj, infl)
        dis.st.cost_calc(yr_proj, infl)
        dis.dp.cost_calc(yr_proj, infl)
        dis.sk.cost_calc(yr_proj, infl)
        dis.gd.cost_calc(yr_proj, infl)
        dis.su.cost_calc(yr_proj, infl)

        # get cost of electrical components only
        cost = 0
        for cp in dis.comp_list:
            if cp.is_elec:
                cost += cp.cost

        # get total electrical load
        ld_elec = 0
        for cp in dis.comp_list:
            if isinstance(cp, LoadComponent) and cp.is_elec:
                ld_elec += cp.enr_tot

        # calculate LCOE
        crf = infl*(1+infl)**yr_proj/((1+infl)**yr_proj-1)
        lcoe = crf*cost/ld_elec

        return lcoe

    @staticmethod
    def _lcow(dis, yr_proj, infl, proj_capex, proj_opex):
        """Calculates the LCOE.

        Parameters
        ----------
        dis : Dispatch
            A Dispatch object from which to calculate the LCOE.
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.
        proj_capex : float
            Capital expenses [USD] of the project.
        proj_opex : float
            Fixed yearly operating expenses [USD/yr] of the project.

        Returns
        -------
        lcoe : ndarray
            The LCOE of each scenario. Returns nan if scenario is invalid.

        """
        # start cost calculation in each module
        dis.ld.cost_calc(yr_proj, infl)
        dis.im.cost_calc(yr_proj, infl)
        dis.st.cost_calc(yr_proj, infl)
        dis.dp.cost_calc(yr_proj, infl)
        dis.sk.cost_calc(yr_proj, infl)
        dis.gd.cost_calc(yr_proj, infl)
        dis.su.cost_calc(yr_proj, infl)

        # get statistics from water components
        enr_ld = 0  # energy from water load
        enr_sk = 0  # energy into water sink
        wat_cost = 0  # cost of water components
        vol_tot = 0  # water generated
        for cp in dis.comp_list:
            if cp.is_water:
                wat_cost += cp.cost
                if isinstance(cp, LoadComponent):
                    enr_ld += cp.enr_tot
                    vol_tot += np.sum(cp.water)
                if isinstance(cp, SinkComponent):
                    enr_sk += cp.enr_tot
        enr_gen = enr_ld - enr_sk

        # get CRF and LCOE
        crf = infl*(1+infl)**yr_proj/((1+infl)**yr_proj-1)
        lcoe = Control._lcoe(dis, yr_proj, infl, proj_capex, proj_opex)

        # get LCOW
        lcow = (lcoe*enr_gen+crf*wat_cost)/vol_tot

        return lcow
