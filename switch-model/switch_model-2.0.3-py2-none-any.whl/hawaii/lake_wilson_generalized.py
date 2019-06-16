"""
Special modeling for Lake Wilson - relax daily energy balance by 10 MW to account
for net inflow.
"""
from pyomo.environ import *

def define_components(m):
    m.PH_GENS = Set()

    def rule(m):
        for g in m.PH_GENS:
            if g in m.GENERATION_PROJECTS:
                for t in m.TPS_FOR_GEN[g]:
                    # assign new energy balance with extra inflow, and allow spilling
                    m.Track_State_Of_Charge[g, t] = (
                        m.StateOfCharge[g, t]
                        <=
                        m.StateOfCharge[g, m.tp_previous[t]]
                        + (
                            m.ChargeStorage[g, t] * m.gen_storage_efficiency[g]
                            - m.DispatchGen[g, t]
                            # we don't need to eliminate this if the project isn't
                            # built, because then no power can be produced anyway
                            + m.ph_inflow_mw[g]
                        ) * m.tp_duration_hrs[t]
                    )
    m.Add_Inflow = BuildAction(rule=rule)

    if hasattr(m, 'Spinning_Reserve_Up_Provisions'):
        if not hasattr(m, 'GEN_SPINNING_RESERVE_TYPES'):
            # not using spinning_reserves_advanced
            raise RuntimeError('This module does not work with balancing.operating_reserves.spinning_reserves; please use spinning_reserves_advanced instead.')

        # Set a tighter limit on reserve provision, to prevent reversing direction
        # TODO: don't allow zero crossing when calculating reserves available
        # see http://www.ucdenver.edu/faculty-staff/dmays/3414/Documents/Antal-MS-2014.pdf
        # By default, Switch will assign reserves based on flipping from charging to
        # discharging; we add an extra, negative reserve component equal to the unallowed
        # part.

        m.PH_GEN_TPS = Set(
            dimen=2,
            initialize=lambda m: [
                (g, tp) for tp in m.TPS_FOR_GEN[g] for g in m.PH_GENS
            ]
        )

        # set a flag indicating whether pumped storage is in charging mode
        m.PumpedStorageCharging = Var(m.PH_GEN_TPS, within=Binary)
        m.Set_PumpedStorageCharging_Flag = Constraint(
            m.PH_GEN_TPS,
            rule=lambda m, phg, tp:
                m.PumpedHydroProjGenerateMW[g, tp]
                <=
                m.gen_capacity_limit_mw[g] * (1 - m.PumpedStorageCharging[g, tp])
        )
        # choose how much pumped storage reserves to provide each hour, without reversing direction
        m.PumpedStorageSpinningUpReserves = Var(m.PH_GENS, m.TIMEPOINTS, within=NonNegativeReals)
        m.Limit_PumpedStorageSpinningUpReserves_When_Charging = Constraint(
            m.PH_GENS, m.TIMEPOINTS,
            rule=lambda m, phg, tp:
                m.PumpedStorageSpinningUpReserves[phg, tp]
                <=
                m.PumpedHydroProjStoreMW[phg, tp]
                + m.ph_max_capacity_mw[phg] * (1 - m.PumpedStorageCharging[phg, tp]) # relax when discharging
        )
        m.Limit_PumpedStorageSpinningUpReserves_When_Discharging = Constraint(
            m.PH_GENS, m.TIMEPOINTS,
            rule=lambda m, phg, tp:
                m.PumpedStorageSpinningUpReserves[phg, tp]
                <=
                m.Pumped_Hydro_Proj_Capacity_MW[phg, m.tp_period[tp]] - m.PumpedHydroProjGenerateMW[phg, tp]
                + m.ph_max_capacity_mw[phg] * m.PumpedStorageCharging[phg, tp] # relax when charging
        )
        # TODO: implement down reserves
        m.PumpedStorageSpinningDownReserves = Var(m.PH_GENS, m.TIMEPOINTS, within=NonNegativeReals, bounds=(0,0))

        m.CommitGenSpinningReservesUp = Var(m.SPINNING_RESERVE_TYPE_GEN_TPS, within=NonNegativeReals)
        m.CommitGenSpinningReservesDown = Var(m.SPINNING_RESERVE_TYPE_GEN_TPS, within=NonNegativeReals)

        m.PH_CommitGenSpinningReservesUp_Limit_When_Charging = Constraint(
            m.PH_GEN_TPS,
            rule=lambda m, g, tp:
                sum(m.CommitGenSpinningReservesUp[rt, g, tp] for rt in m.SPINNING_RESERVE_TYPES_FOR_GEN[g])
                <=
                m.DispatchSlackUp[g, tp]
                + (m.ChargeStorage[g, tp] if g in getattr(m, 'STORAGE_GENS', []) else 0.0)
                + m.gen_capacity_limit_mw[g] * (1 - m.PumpedStorageCharging[g, tp]) # relax when discharging
        )
        m.PH_CommitGenSpinningReservesUp_Limit_When_Charging = Constraint(
            m.PH_GEN_TPS,
            rule=lambda m, g, tp:
                sum(m.CommitGenSpinningReservesUp[rt, g, tp] for rt in m.SPINNING_RESERVE_TYPES_FOR_GEN[g])
                <=
                m.DispatchSlackUp[g, tp]
                # storage can give more up response by stopping charging
                + (m.ChargeStorage[g, tp] if g in getattr(m, 'STORAGE_GENS', []) else 0.0)
                + m.gen_capacity_limit_mw[g] * (1 - m.PumpedStorageCharging[g, tp]) # relax when discharging
        )


        m.PH_CommitGenSpinningReservesDown_Limit = Constraint(
            m.SPINNING_RESERVE_CAPABLE_GEN_TPS,
            rule=lambda m, g, tp:
                sum(m.CommitGenSpinningReservesDown[rt, g, tp] for rt in m.SPINNING_RESERVE_TYPES_FOR_GEN[g])
                <=
                m.DispatchSlackDown[g, tp]
                + ( # storage could give more down response by raising ChargeStorage to the maximum rate
                    (m.DispatchUpperLimit[g, tp] * m.gen_store_to_release_ratio[g] - m.ChargeStorage[g, tp])
                    if g in getattr(m, 'STORAGE_GENS', [])
                    else 0.0
                )
        )


    if [rt.lower() for rt in m.options.hawaii_storage_reserve_types] != ['none']:
        if hasattr(m, 'PumpedHydroProjGenerateMW'):
            raise NotImplementedError("Code below here needs to be integrated")

        # Register with spinning reserves
        if hasattr(m, 'Spinning_Reserve_Up_Provisions'): # using spinning_reserves_advanced
            # calculate available slack from hawaii storage
            def up_expr(m, a, tp):
                avail = 0.0
                # now handled in hydrogen module:
                # if hasattr(m, 'HydrogenSlackUp'):
                #     avail += sum(m.HydrogenSlackUp[z, tp] for z in m.ZONES_IN_BALANCING_AREA[a])
                if hasattr(m, 'PumpedStorageSpinningUpReserves'):
                    avail += sum(
                        m.PumpedStorageSpinningUpReserves[phg, tp]
                        for phg in m.PH_GENS
                        if m.ph_load_zone[phg] in m.ZONES_IN_BALANCING_AREA[a]
                    )
                return avail
            m.HawaiiStorageSlackUp = Expression(m.BALANCING_AREA_TIMEPOINTS, rule=up_expr)
            def down_expr(m, a, tp):
                avail = 0.0
                # if hasattr(m, 'HydrogenSlackDown'):
                #     avail += sum(m.HydrogenSlackDown[z, tp] for z in m.ZONES_IN_BALANCING_AREA[a])
                if hasattr(m, 'PumpedStorageSpinningDownReserves'):
                    avail += sum(
                        m.PumpedStorageSpinningDownReserves[phg, tp]
                        for phg in m.PH_GENS
                        if m.ph_load_zone[phg] in m.ZONES_IN_BALANCING_AREA[a]
                    )
                return avail
            m.HawaiiStorageSlackDown = Expression(m.BALANCING_AREA_TIMEPOINTS, rule=down_expr)

            if hasattr(m, 'GEN_SPINNING_RESERVE_TYPES'):
                # using advanced formulation, index by reserve type, balancing area, timepoint
                # define variables for each type of reserves to be provided
                # choose how to allocate the slack between the different reserve products
                m.HI_STORAGE_SPINNING_RESERVE_TYPES = Set(
                    initialize=m.options.hawaii_storage_reserve_types
                )
                m.HawaiiStorageSpinningReserveUp = Var(
                    m.HI_STORAGE_SPINNING_RESERVE_TYPES, m.BALANCING_AREA_TIMEPOINTS,
                    within=NonNegativeReals
                )
                m.HawaiiStorageSpinningReserveDown = Var(
                    m.HI_STORAGE_SPINNING_RESERVE_TYPES, m.BALANCING_AREA_TIMEPOINTS,
                    within=NonNegativeReals
                )
                # constrain reserve provision within available slack
                m.Limit_HawaiiStorageSpinningReserveUp = Constraint(
                    m.BALANCING_AREA_TIMEPOINTS,
                    rule=lambda m, ba, tp:
                        sum(
                            m.HawaiiStorageSpinningReserveUp[rt, ba, tp]
                            for rt in m.HI_STORAGE_SPINNING_RESERVE_TYPES
                        ) <= m.HawaiiStorageSlackUp[ba, tp]
                )
                m.Limit_HawaiiStorageSpinningReserveDown = Constraint(
                    m.BALANCING_AREA_TIMEPOINTS,
                    rule=lambda m, ba, tp:
                        sum(
                            m.HawaiiStorageSpinningReserveDown[rt, ba, tp]
                            for rt in m.HI_STORAGE_SPINNING_RESERVE_TYPES
                        ) <= m.HawaiiStorageSlackDown[ba, tp]
                )
                m.Spinning_Reserve_Up_Provisions.append('HawaiiStorageSpinningReserveUp')
                m.Spinning_Reserve_Down_Provisions.append('HawaiiStorageSpinningReserveDown')
            else:
                # using older formulation, only one type of spinning reserves, indexed by balancing area, timepoint
                if m.options.hawaii_storage_reserve_types != ['spinning']:
                    raise ValueError(
                        'Unable to use reserve types other than "spinning" with simple spinning reserves module.'
                    )
                m.Spinning_Reserve_Up_Provisions.append('HawaiiStorageSlackUp')
                m.Spinning_Reserve_Down_Provisions.append('HawaiiStorageSlackDown')




def load_inputs(m, switch_data, inputs_dir):
    switch_data.load_aug(
        optional=True,
        filename=os.path.join(inputs_dir, 'pumped_hydro.tab'),
        autoselect=True,
        index=m.PH_GENS,
        param=(m.ph_inflow_mw,))
