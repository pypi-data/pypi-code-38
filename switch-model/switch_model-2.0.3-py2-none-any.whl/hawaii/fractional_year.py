import switch_model.financials

# Patch calc_annual_costs_in_period to consider only an appropriate
# fraction of annual costs. (This will run as soon as the modules are
# loaded, before calc_annual_costs_in_period is ever called.)
# old_calc_annual_costs_in_period = switch_model.financials.calc_annual_costs_in_period
# switch_model.financials.calc_annual_costs_in_period = (
#     lambda m, p:
#         old_calc_annual_costs_in_period(m, p)
#         * sum(m.tp_weight_in_year[t] for t in m.TPS_IN_PERIOD[p])
#         / 8760
# )
print "TODO: migrate calc_annual_costs_in_period function from inside financials.define_components up to the top level, then revise this code to patch it. Or even better, refactor financials module to work OK with fractional years."

def define_components(m):
    # remove the requirement for timepoints to span the full year
    m.del_component(m.validate_time_weights)


def define_dynamic_components(m):
    # Patch SystemCostPerPeriod to consider only an appropriate
    # fraction of annual costs.

    def calc_tp_costs_in_period(m, t):
        return sum(
            getattr(m, tp_cost)[t] * m.tp_weight_in_year[t]
            for tp_cost in m.Cost_Components_Per_TP)

    def calc_annual_costs_in_period(m, p):
        return (
            sum(
                getattr(m, annual_cost)[p]
                for annual_cost in m.Cost_Components_Per_Period
            )
            # Annual costs are rescaled here; otherwise identical to
            # standard code in financials.py
            * sum(m.tp_weight_in_year[t] for t in m.TPS_IN_PERIOD[p])
            / 8760
        )

    def calc_sys_costs_per_period(m, p):
        return (
            # All annual payments in the period
            (
                calc_annual_costs_in_period(m, p) +
                sum(calc_tp_costs_in_period(m, t) for t in m.TPS_IN_PERIOD[p])
            ) *
            # Conversion from annual costs to base year
            m.bring_annual_costs_to_base_year[p]
        )

    # Patch SystemCostPerPeriod
    m.SystemCostPerPeriod.rule = calc_sys_costs_per_period
