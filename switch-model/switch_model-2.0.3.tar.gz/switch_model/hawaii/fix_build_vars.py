import os, glob, time
import pyomo.environ as po
from switch_model.reporting import make_iterable

def define_arguments(parser):
    parser.add_argument("--fix-build-dir", default="outputs/base", 
        help='Directory containing ".tab" files to use to freeze build variables (default is "outputs/base")')

fix_vars = {
    'BuildGen',
    'BuildUnits',
    'BuildStorageEnergy',
    # this could be treated as a per-slice var, but that would be inconsistent with the 
    # idea of a semi-permanent fuel switch, and also slows down the solver a lot
    'DispatchRenewableFlag',
    'RFMBuildSupplyTier',
    'RFMSupplyTierActivate',
    'BuildPumpedHydroMW',
    'BuildAnyPumpedHydro',
    'BuildElectrolyzerMW',
    'BuildLiquifierKgPerHour',
    'BuildLiquidHydrogenTankKg',
    'BuildFuelCellMW',
    'BuildAnyLiquidHydrogenTank',
    'OperateAES'
}
free_vars = {
    'ConsumeFuelTier',
}

# TODO: This needs to include all prior build years, not just the current period.
# Should the model be defined with more periods, with no timepoints in them?
# May not be able to satisfy various constraints then...

# note: this assumes it is run from the parent of the main outputs directory
def pre_solve(m):
    if m.options.verbose:
        print "Setting build variables from {}...".format(m.options.fix_build_dir)
    # double-check that there aren't any variables indexed by period but missing from these lists
    # (this check isn't foolproof, but it's pretty good)
    period_vars = {
        c.name for c in m.component_objects(po.Var) 
        if any(k==m.PERIODS.first() for keys in c.iterkeys() for k in make_iterable(keys))
    }
    missing_vars = period_vars - fix_vars - free_vars
    if missing_vars:
        print "="*80
        print "WARNING: the following per-period variables are not in the lists of fixed or free variables:"
        print "    " + ','.join(sorted(missing_vars))
        print "They will be left free."
        print "="*80
        time.sleep(2) # make sure they notice
        
    build_vars = [getattr(m, v) for v in fix_vars if hasattr(m, v)]
    for var in build_vars:
        try:
            # check types of the first tuple of keys for this variable
            key_types = [type(i) for i in make_iterable(next(var.iterkeys()))]
        except StopIteration:
            key_types = []  # no keys
        with open(os.path.join(m.options.fix_build_dir, var.name + '.tab')) as f:
            next(f) # skip headers
            # set variable values using values from .tab file
            for r in f:
                row = r.strip().split('\t')
                keys = tuple(t(k) for t, k in zip(key_types, row[:-1]))
                # print "trying to set {}[{}] = {}".format(var, keys, row[-1])
                try:
                    v = var[keys]
                    val = float(row[-1])
                    if v.is_integer() or v.is_binary():
                        val = int(val)
                    v.value = val
                    v.fixed = True  # see p. 171 of the Pyomo book
                    if m.options.verbose:
                        print "Set {} = {}".format(v.name, val)
                except KeyError:
                    raise ValueError("Unable to set {} = {}".format(v.name, val))

    # m.preprocess() # probably not needed, since it gets done at solve time anyway
    # if m.options.verbose:
    #     print "Finished setting build variables."


# Note: the ideas below were abandoned because it would be difficult to convey shortages
# from the dualized monthly models into the main optimization model (e.g., the monthly
# models could always use hydrogen to address any energy shortfalls, but then they would
# exceed the total hydrogen storage capacity or production for the year). Instead, we 
# now run sliced models (e.g., 10 models, each taking every 10th day of the year, weighted
# to represent a whole period), and require each one to meet all the per-period constraints 
# independently. This is financially conservative (money could be saved by relaxing the 
# constraints in some slices and tightening them in others), but it shouldn't be too bad 
# due to the uniform sampling, and it is guaranteed to be feasible (if constraints are met 
# in all slices, they will also be met for the average of all slices.)
# 
# TODO: we need to dualize any constraints that apply across timepoints, e.g., these:
# [
#     c.name
#     for c in m.component_objects(Constraint)
#     if any(
#         k==m.PERIODS.first() and str(m.TIMEPOINTS.first()) in str(c[keys].expr)
#         for keys in c.keys() for k in make_iterable(keys))
# ]
# ['Enforce_Fuel_Consumption',
#  'Battery_Cycle_Limit',
#  'RPS_Enforce',
#  'RPS_Fuel_Cap',
#  'Hydrogen_Conservation_of_Mass_Annual',
#  'Max_Store_Liquid_Hydrogen']
# [
#     c.name for c in m.component_objects(Constraint)
#     if any(k==m.PERIODS.first() for keys in c.keys() for k in make_iterable(keys))
# ]
# ['Max_Build_Potential',
#  'Enforce_Fuel_Consumption',
#  'Enforce_Fixed_Energy_Storage_Ratio', # build vars will be fixed, so no effect
#  'Battery_Cycle_Limit',
#  'RFM_Build_Activate_Consistency', # build vars will be fixed, so no effect
#  'Force_Activate_Unlimited_RFM_Supply_Tier',
#  'Enforce_RFM_Supply_Tier_Activated',
#  'RPS_Enforce',
#  'RPS_Fuel_Cap',
#  'Force_LNG_Tier',
#  'Pumped_Hydro_Max_Build',
#  'Pumped_Hydro_Set_Build_Flag',
#  'Pumped_Hydro_Build_All_Or_None',
#  'Hydrogen_Conservation_of_Mass_Annual',
#  'Set_BuildAnyLiquidHydrogenTank_Flag',
#  'Build_Minimum_Liquid_Hydrogen_Tank',
#  'Max_Store_Liquid_Hydrogen',
#  'Enforce_Technology_Target',
#  'PSIP_Retire_AES',
#  'PSIP_No_BuildPumpedHydroMW',
#  'PSIP_No_BuildAnyPumpedHydro',
#  'PSIP_No_BuildElectrolyzerMW',
#  'PSIP_No_BuildLiquifierKgPerHour',
#  'PSIP_No_BuildLiquidHydrogenTankKg',
#  'PSIP_No_BuildFuelCellMW']

# We could do this by saving the dual value of all the constraints in this list in the
# investment run, then in the evaluation runs, deactivate the constraints and add a 
# penalty cost to the objective function instead.
# Will this work to enforce limits on fuel tiers? That is a decision variable; probably
# ends up with equal effective cost for all tiers, so tier assignment becomes ambiguous. 
# But that's probably OK, given that we may be overshooting the tiers anyway.

# (is it safe to assume
# they are indexed by period and summed over timesteps if they are caught by this query?
# Maybe best to have a whitelist, but also double-check if there may be other candidates
# to include.)
