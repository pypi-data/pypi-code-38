"""
Defines types of reserve target and components that contribute to reserves,
and enforces the reserve targets.
"""
import os
from pyomo.environ import *

# TODO: use standard reserves module for this

def define_arguments(argparser):
    argparser.add_argument("--load-shift-battery-reserves", choices=['none', 'conting', 'reg'], default='none',
        help="Type of reserves to provide from load-shifting batteries.")
    argparser.add_argument('--reserves-from-demand-response', action='store_true', default=True, 
        help="Allow demand response to provide up- and down-reserves.")
    argparser.add_argument('--no-reserves-from-demand-response', dest='reserves_from_demand_response', 
        action='store_false', 
        help="Don't allow demand response to provide up- and down-reserves.")

def define_components(m):
    """
    Note: In this simple model, we assume all reserves must be spinning. In more complex
    models you could define products and portions of those products that must be spinning,
    then use that to set the spinning reserve requirement.

    Reserves don't have a deliverability requirement, so they are calculated for the whole region.
    """

    # projects that can provide reserves
    # TODO: add batteries, hydrogen and pumped storage to this
    m.FIRM_GENS = Set(
        initialize=m.GENERATION_PROJECTS, 
        #filter=lambda m, p: m.gen_energy_source[p] not in ['Wind', 'Solar']
    )
    m.FIRM_GEN_TPS = Set(
        initialize=m.GEN_TPS, 
        filter=lambda m, p, tp: p in m.FIRM_GENS
    )
    m.CONTINGENCY_GENS = Set(
        initialize=m.GENERATION_PROJECTS, 
        filter=lambda m, p: p in m.DISCRETELY_SIZED_GENS
    )
    m.CONTINGENCY_GEN_TPS = Set(
        initialize=m.GEN_TPS, 
        filter=lambda m, p, tp: p in m.CONTINGENCY_GENS
    )
    
    # Calculate spinning reserve requirements.

    # these parameters were found by regressing the reserve requirements from the GE RPS Study
    # against wind and solar conditions each hour 
    # (see Dropbox/Research/Shared/Switch-Hawaii/ge_validation/source_data/reserve_requirements_oahu_scenarios charts.xlsx
    # and Dropbox/Research/Shared/Switch-Hawaii/ge_validation/fit_renewable_reserves.ipynb )
    # TODO: supply these parameters in input files

    # regulating reserves required, as fraction of potential output (up to limit)
    m.regulating_reserve_fraction = Param(['CentralTrackingPV', 'DistPV', 'OnshoreWind', 'OffshoreWind'], initialize={
        'CentralTrackingPV': 1.0,
        'DistPV': 1.0, # 0.81270193,
        'OnshoreWind': 1.0,
        'OffshoreWind': 1.0, # assumed equal to OnshoreWind
    })
    # maximum regulating reserves required, as fraction of installed capacity
    m.regulating_reserve_limit = Param(['CentralTrackingPV', 'DistPV', 'OnshoreWind', 'OffshoreWind'], initialize={
        'CentralTrackingPV': 0.21288916,
        'DistPV': 0.21288916, # 0.14153171,
        'OnshoreWind': 0.21624407,
        'OffshoreWind': 0.21624407, # assumed equal to OnshoreWind
    })
    # more conservative values (found by giving 10x weight to times when we provide less reserves than GE):
    # [1., 1., 1., 0.25760558, 0.18027923, 0.49123101]

    m.RegulatingReserveUpRequirement = Expression(m.TIMEPOINTS, rule=lambda m, tp: sum(
        m.GenCapacity[g, m.tp_period[tp]] 
        * min(
            m.regulating_reserve_fraction[m.gen_tech[g]] * m.gen_max_capacity_factor[g, tp], 
            m.regulating_reserve_limit[m.gen_tech[g]]
        )
            for g in m.GENERATION_PROJECTS 
                if m.gen_tech[g] in m.regulating_reserve_fraction and (g, tp) in m.GEN_TPS
    ))
    m.RegulatingReserveDownRequirement = Expression(m.TIMEPOINTS, rule=lambda m, tp:
        # HECO and GE don't specify a reg down requirement, so we set it to 0 
        # (assume enough comes automatically from renewable and thermal plants)
        0.0  
    )
    
    
def define_dynamic_components(m):
    # these are defined late, so they can check whether various components have been defined by other modules
    # TODO: create a central registry for components that contribute to reserves

    # Calculate contingency reserve requirements
    m.ContingencyReserveUpRequirement = Var(m.TIMEPOINTS, within=NonNegativeReals)
    # Apply a simple n-1 contingency reserve requirement; 
    # we treat each project as a separate contingency
    # Note: we provide reserves for the full committed amount of each unit so that
    # if any of the capacity is being used for regulating reserves, that will be backed
    # up by contingency reserves.
    # note: this uses a binary run/no-run flag, so it only provides one unit's worth of reserves
    m.CommitGenFlag = Var(m.CONTINGENCY_GEN_TPS, within=Binary)
    m.Set_CommitGenFlag = Constraint(
        m.CONTINGENCY_GEN_TPS,
        rule = lambda m, g, tp: 
            m.CommitGen[g, tp] <= m.CommitGenFlag[g, tp] * m.gen_capacity_limit_mw[g]
    )
    m.ContingencyReserveUpRequirement_Calculate = Constraint(
        m.CONTINGENCY_GEN_TPS, 
        rule=lambda m, g, tp: 
            # m.ContingencyReserveUpRequirement[tp] >= m.CommitGen[g, tp]
            m.ContingencyReserveUpRequirement[tp] >= m.CommitGenFlag[g, tp] * m.gen_unit_size[g]
    )

    m.ContingencyReserveDownRequirement = Var(m.TIMEPOINTS, within=NonNegativeReals)
    # For now, we provide down reserves equal to 10% of all loads, including 
    # baseline load, demand response adjustment, electric vehicles, battery charging
    # and hydrogen. It would be possible to split these into centralized and distributed
    # loads and allocate separately for them (e.g., contingency reserves exceed 
    # 10% of total decentralized load and the size of the contingency for each 
    # centralized load; however, it's not obvious how to set the contingency for
    # centralized loads, which are modular and may be divided between several locations.
    # So we just assume we could lose 10% of all loads of any type, at any time.)
    m.ContingencyReserveDownRequirement_Calculate = Constraint(
        m.TIMEPOINTS, 
        rule=lambda m, tp: 
            m.ContingencyReserveDownRequirement[tp] >= 
            0.1 * sum(getattr(m, x)[z, tp] for x in m.Zone_Power_Withdrawals for z in m.LOAD_ZONES)
    )
    
    m.ALL_BATTERIES = Set(
        initialize=lambda m: getattr(m, 'STORAGE_GENS', []),
    )
    m.REG_RESERVE_BATTERIES = Set(
        initialize=m.ALL_BATTERIES, 
        filter=lambda m, g: g.endswith('Battery_Reg'), 
    )
    m.CONTING_RESERVE_BATTERIES = Set(
        initialize=m.ALL_BATTERIES, 
        filter=lambda m, g: g.endswith('Battery_Conting'), 
    )
    m.LOAD_SHIFT_BATTERIES = Set(
        initialize=m.ALL_BATTERIES,
        filter=lambda m, g: g not in m.REG_RESERVE_BATTERIES and g not in m.CONTING_RESERVE_BATTERIES
    )
    
    m.RESERVE_TYPES = Set(initialize=['contingency', 'regulation'])
    m.RESERVE_DIRECTIONS = Set(initialize=['up', 'down'])

    # reserves from generation projects (regular or storage)
    m.GenSpinningReserves = Var(m.RESERVE_TYPES, m.RESERVE_DIRECTIONS, m.GEN_TPS, within=NonNegativeReals)
    # limits on reserve provision from each project
    m.Enforce_Max_Gen_Up_Reserves = Constraint(m.GEN_TPS, rule=lambda m, g, tp:
        sum(m.GenSpinningReserves[res_type, 'up', g, tp] for res_type in m.RESERVE_TYPES) 
        <= m.DispatchSlackUp[g, tp] + (m.ChargeStorage[g, tp] if g in m.ALL_BATTERIES else 0.0)
    )
    m.Enforce_Max_Gen_Down_Reserves = Constraint(m.GEN_TPS, rule=lambda m, g, tp:
        sum(m.GenSpinningReserves[res_type, 'down', g, tp] for res_type in m.RESERVE_TYPES) 
        <= 
        m.DispatchSlackDown[g, tp] 
        + (
            (m.DispatchUpperLimit[g, tp] * m.gen_store_to_release_ratio[g] - m.ChargeStorage[g, tp]) 
            if g in m.ALL_BATTERIES 
            else 0.0
        )
    )
    # limits on reserves from batteries
    if m.options.load_shift_battery_reserves not in {'reg'}:
        m.No_Reg_From_Load_Shift_Batteries = Constraint(m.RESERVE_DIRECTIONS, m.STORAGE_GEN_TPS, rule=lambda m, d, g, t:
            m.GenSpinningReserves['regulation', d, g, t] == 0 if g in m.LOAD_SHIFT_BATTERIES
            else Constraint.Skip
        )
    if m.options.load_shift_battery_reserves not in {'conting', 'reg'}:
        m.No_Conting_From_Load_Shift_Batteries = Constraint(m.RESERVE_DIRECTIONS, m.STORAGE_GEN_TPS, rule=lambda m, d, g, t:
            m.GenSpinningReserves['contingency', d, g, t] == 0 if g in m.LOAD_SHIFT_BATTERIES
            else Constraint.Skip
        )
    m.No_Reg_From_Conting_Batteries = Constraint(m.RESERVE_DIRECTIONS, m.STORAGE_GEN_TPS, rule=lambda m, d, g, t:
        m.GenSpinningReserves['regulation', d, g, t] == 0 if g in m.CONTING_RESERVE_BATTERIES
        else Constraint.Skip
    )
    
    # something similar for DR and EVs (choose how much of these to apply to reg vs. conting)
    m.DRSpinningReserves = Var(m.RESERVE_TYPES, m.RESERVE_DIRECTIONS, m.TIMEPOINTS, within=NonNegativeReals)
    # limits on total reserve provision
    def avail_dr_up_reserves(m, tp):
        avail = 0.0
        if hasattr(m, 'DemandUpReserves'):
            avail += sum(m.DemandUpReserves[z, tp] for z in m.LOAD_ZONES)
        if hasattr(m, 'ShiftDemand'):
            avail += sum(m.ShiftDemand[z, tp] -  m.ShiftDemand[z, tp].lb for z in m.LOAD_ZONES) 
        if hasattr(m, 'ChargeEVs') and hasattr(m.options, 'ev_timing') and m.options.ev_timing=='optimal':
            avail += sum(m.ChargeEVs[z, tp] for z in m.LOAD_ZONES) 
        return avail
    m.Enforce_Max_DR_Up_Reserves = Constraint(m.TIMEPOINTS, rule=lambda m, tp:
        sum(m.DRSpinningReserves[res_type, 'up', tp] for res_type in m.RESERVE_TYPES)
        <= 
        avail_dr_up_reserves(m, tp)
    )
    def avail_dr_down_reserves(m, tp):
        avail = 0.0
        if hasattr(m, 'DemandDownReserves'):
            avail += sum(m.DemandDownReserves[z, tp] for z in m.LOAD_ZONES)
        if hasattr(m, 'ShiftDemand'):
            # avail += sum(m.ShiftDemand[z, tp].ub - m.ShiftDemand[z, tp] for z in m.LOAD_ZONES) 
            avail += sum(
                24/3 * m.demand_response_max_share * m.zone_demand_mw[z, tp]
                - m.ShiftDemand[z, tp] 
                for z in m.LOAD_ZONES
            ) 
        # note: we currently ignore down-reserves (option of increasing consumption) 
        # from EVs since it's not clear how high they could go; we could revisit this if
        # down-reserves have a positive price at equilibrium (probabably won't)
        return avail
    m.Enforce_Max_DR_Down_Reserves = Constraint(m.TIMEPOINTS, rule=lambda m, tp:
        sum(m.DRSpinningReserves[res_type, 'down', tp] for res_type in m.RESERVE_TYPES)
        <= 
        avail_dr_down_reserves(m, tp)
    )
    # limit on various types of reserves from DR
    if not m.options.reserves_from_demand_response:
        m.No_Reserves_From_DR = Constraint(m.RESERVE_TYPES, m.RESERVE_DIRECTIONS, m.STORAGE_GEN_TPS, rule=lambda m, rt, d, g, tp:
            m.DRSpinningReserves[rt, d, tp] == 0
        )
    
    
    reserve_requirements = {
        ('regulation', 'up'): 'RegulatingReserveUpRequirement',
        ('regulation', 'down'): 'RegulatingReserveDownRequirement',
        ('contingency', 'up'): 'ContingencyReserveUpRequirement',
        ('contingency', 'down'): 'ContingencyReserveDownRequirement',
    }
    
    # Meet the regulation and contingency reserve requirements
    # (we use zero on RHS to enforce the right sign for the duals)
    m.Satisfy_Reserve_Requirements = Constraint(
        m.RESERVE_TYPES, m.RESERVE_DIRECTIONS, m.TIMEPOINTS,
        rule=lambda m, rt, rd, tp: 
            sum(m.GenSpinningReserves[rt, rd, g, tp] for g in m.GENERATION_PROJECTS if (g, tp) in m.GEN_TPS)
            + m.DRSpinningReserves[rt, rd, tp]
            - getattr(m, reserve_requirements[rt, rd])[tp]
            >= 0
    )
