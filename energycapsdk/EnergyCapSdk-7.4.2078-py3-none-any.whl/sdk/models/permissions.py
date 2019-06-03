# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class Permissions(Model):
    """Permissions.

    :param license_feature_accounting_export:
    :type license_feature_accounting_export:
     ~energycap.sdk.models.LicenseFeatureAccountingExport
    :param license_feature_accrual_bills:
    :type license_feature_accrual_bills:
     ~energycap.sdk.models.LicenseFeatureAccrualBills
    :param license_feature_chargebacks:
    :type license_feature_chargebacks:
     ~energycap.sdk.models.LicenseFeatureChargebacks
    :param license_feature_cost_avoidance:
    :type license_feature_cost_avoidance:
     ~energycap.sdk.models.LicenseFeatureCostAvoidance
    :param license_feature_interval_data_analysis:
    :type license_feature_interval_data_analysis:
     ~energycap.sdk.models.LicenseFeatureIntervalDataAnalysis
    :param license_feature_report_designer:
    :type license_feature_report_designer:
     ~energycap.sdk.models.LicenseFeatureReportDesigner
    :param accounting_settings:
    :type accounting_settings: ~energycap.sdk.models.AccountingSettings
    :param accounts:
    :type accounts: ~energycap.sdk.models.Accounts
    :param accounts_module:
    :type accounts_module: ~energycap.sdk.models.AccountsModule
    :param accrual_settings:
    :type accrual_settings: ~energycap.sdk.models.AccrualSettings
    :param cost_centers:
    :type cost_centers: ~energycap.sdk.models.CostCenters
    :param move_accounts_between_vendors:
    :type move_accounts_between_vendors:
     ~energycap.sdk.models.MoveAccountsBetweenVendors
    :param application_settings:
    :type application_settings: ~energycap.sdk.models.ApplicationSettings
    :param approve_bills:
    :type approve_bills: ~energycap.sdk.models.ApproveBills
    :param bill_audit_groups:
    :type bill_audit_groups: ~energycap.sdk.models.BillAuditGroups
    :param bill_audits:
    :type bill_audits: ~energycap.sdk.models.BillAudits
    :param bill_entry_templates:
    :type bill_entry_templates: ~energycap.sdk.models.BillEntryTemplates
    :param bill_workflow_settings:
    :type bill_workflow_settings: ~energycap.sdk.models.BillWorkflowSettings
    :param bills_and_batches:
    :type bills_and_batches: ~energycap.sdk.models.BillsAndBatches
    :param export_bills:
    :type export_bills: ~energycap.sdk.models.ExportBills
    :param export_hold:
    :type export_hold: ~energycap.sdk.models.ExportHold
    :param move_existing_bills:
    :type move_existing_bills: ~energycap.sdk.models.MoveExistingBills
    :param bill_audit_results_and_alerts:
    :type bill_audit_results_and_alerts:
     ~energycap.sdk.models.BillAuditResultsAndAlerts
    :param shared_bill_lists:
    :type shared_bill_lists: ~energycap.sdk.models.SharedBillLists
    :param unit_system_settings:
    :type unit_system_settings: ~energycap.sdk.models.UnitSystemSettings
    :param update_approved_bills:
    :type update_approved_bills: ~energycap.sdk.models.UpdateApprovedBills
    :param update_units_on_existing_bills:
    :type update_units_on_existing_bills:
     ~energycap.sdk.models.UpdateUnitsOnExistingBills
    :param budgets_and_budget_versions:
    :type budgets_and_budget_versions:
     ~energycap.sdk.models.BudgetsAndBudgetVersions
    :param chargebacks_module:
    :type chargebacks_module: ~energycap.sdk.models.ChargebacksModule
    :param chargebacks:
    :type chargebacks: ~energycap.sdk.models.Chargebacks
    :param chargeback_reversals:
    :type chargeback_reversals: ~energycap.sdk.models.ChargebackReversals
    :param meter_savings_settings:
    :type meter_savings_settings: ~energycap.sdk.models.MeterSavingsSettings
    :param savings_adjustments:
    :type savings_adjustments: ~energycap.sdk.models.SavingsAdjustments
    :param manually_adjust_savings:
    :type manually_adjust_savings: ~energycap.sdk.models.ManuallyAdjustSavings
    :param savings_engine:
    :type savings_engine: ~energycap.sdk.models.SavingsEngine
    :param baseline_engine:
    :type baseline_engine: ~energycap.sdk.models.BaselineEngine
    :param global_cost_avoidance_settings:
    :type global_cost_avoidance_settings:
     ~energycap.sdk.models.GlobalCostAvoidanceSettings
    :param dashboard_and_maps_module:
    :type dashboard_and_maps_module:
     ~energycap.sdk.models.DashboardAndMapsModule
    :param dashboard_administrator:
    :type dashboard_administrator:
     ~energycap.sdk.models.DashboardAdministrator
    :param public_dashboards_or_maps:
    :type public_dashboards_or_maps:
     ~energycap.sdk.models.PublicDashboardsOrMaps
    :param shared_dashboards_or_maps:
    :type shared_dashboards_or_maps:
     ~energycap.sdk.models.SharedDashboardsOrMaps
    :param buildings_and_meters_module:
    :type buildings_and_meters_module:
     ~energycap.sdk.models.BuildingsAndMetersModule
    :param groups_and_benchmarks_module:
    :type groups_and_benchmarks_module:
     ~energycap.sdk.models.GroupsAndBenchmarksModule
    :param building_and_meter_groups:
    :type building_and_meter_groups:
     ~energycap.sdk.models.BuildingAndMeterGroups
    :param buildings_and_organizations:
    :type buildings_and_organizations:
     ~energycap.sdk.models.BuildingsAndOrganizations
    :param interval_data:
    :type interval_data: ~energycap.sdk.models.IntervalData
    :param interval_data_analysis:
    :type interval_data_analysis: ~energycap.sdk.models.IntervalDataAnalysis
    :param energystar_submissions:
    :type energystar_submissions: ~energycap.sdk.models.ENERGYSTARSubmissions
    :param facility_projects:
    :type facility_projects: ~energycap.sdk.models.FacilityProjects
    :param greenhouse_gas_administrator:
    :type greenhouse_gas_administrator:
     ~energycap.sdk.models.GreenhouseGasAdministrator
    :param interval_data_rollup:
    :type interval_data_rollup: ~energycap.sdk.models.IntervalDataRollup
    :param meters:
    :type meters: ~energycap.sdk.models.Meters
    :param normalization_settings:
    :type normalization_settings: ~energycap.sdk.models.NormalizationSettings
    :param weather_settings:
    :type weather_settings: ~energycap.sdk.models.WeatherSettings
    :param reports_module:
    :type reports_module: ~energycap.sdk.models.ReportsModule
    :param distributed_reports_settings:
    :type distributed_reports_settings:
     ~energycap.sdk.models.DistributedReportsSettings
    :param install_or_update_reports:
    :type install_or_update_reports:
     ~energycap.sdk.models.InstallOrUpdateReports
    :param report_groups:
    :type report_groups: ~energycap.sdk.models.ReportGroups
    :param shared_reports:
    :type shared_reports: ~energycap.sdk.models.SharedReports
    :param reset_user_passwords:
    :type reset_user_passwords: ~energycap.sdk.models.ResetUserPasswords
    :param users_and_roles:
    :type users_and_roles: ~energycap.sdk.models.UsersAndRoles
    :param vendors_and_rates_module:
    :type vendors_and_rates_module:
     ~energycap.sdk.models.VendorsAndRatesModule
    :param rate_schedules:
    :type rate_schedules: ~energycap.sdk.models.RateSchedules
    :param vendors:
    :type vendors: ~energycap.sdk.models.Vendors
    """

    _attribute_map = {
        'license_feature_accounting_export': {'key': 'licenseFeatureAccountingExport', 'type': 'LicenseFeatureAccountingExport'},
        'license_feature_accrual_bills': {'key': 'licenseFeatureAccrualBills', 'type': 'LicenseFeatureAccrualBills'},
        'license_feature_chargebacks': {'key': 'licenseFeatureChargebacks', 'type': 'LicenseFeatureChargebacks'},
        'license_feature_cost_avoidance': {'key': 'licenseFeatureCostAvoidance', 'type': 'LicenseFeatureCostAvoidance'},
        'license_feature_interval_data_analysis': {'key': 'licenseFeatureIntervalDataAnalysis', 'type': 'LicenseFeatureIntervalDataAnalysis'},
        'license_feature_report_designer': {'key': 'licenseFeatureReportDesigner', 'type': 'LicenseFeatureReportDesigner'},
        'accounting_settings': {'key': 'accountingSettings', 'type': 'AccountingSettings'},
        'accounts': {'key': 'accounts', 'type': 'Accounts'},
        'accounts_module': {'key': 'accountsModule', 'type': 'AccountsModule'},
        'accrual_settings': {'key': 'accrualSettings', 'type': 'AccrualSettings'},
        'cost_centers': {'key': 'costCenters', 'type': 'CostCenters'},
        'move_accounts_between_vendors': {'key': 'moveAccountsBetweenVendors', 'type': 'MoveAccountsBetweenVendors'},
        'application_settings': {'key': 'applicationSettings', 'type': 'ApplicationSettings'},
        'approve_bills': {'key': 'approveBills', 'type': 'ApproveBills'},
        'bill_audit_groups': {'key': 'billAuditGroups', 'type': 'BillAuditGroups'},
        'bill_audits': {'key': 'billAudits', 'type': 'BillAudits'},
        'bill_entry_templates': {'key': 'billEntryTemplates', 'type': 'BillEntryTemplates'},
        'bill_workflow_settings': {'key': 'billWorkflowSettings', 'type': 'BillWorkflowSettings'},
        'bills_and_batches': {'key': 'billsAndBatches', 'type': 'BillsAndBatches'},
        'export_bills': {'key': 'exportBills', 'type': 'ExportBills'},
        'export_hold': {'key': 'exportHold', 'type': 'ExportHold'},
        'move_existing_bills': {'key': 'moveExistingBills', 'type': 'MoveExistingBills'},
        'bill_audit_results_and_alerts': {'key': 'billAuditResultsAndAlerts', 'type': 'BillAuditResultsAndAlerts'},
        'shared_bill_lists': {'key': 'sharedBillLists', 'type': 'SharedBillLists'},
        'unit_system_settings': {'key': 'unitSystemSettings', 'type': 'UnitSystemSettings'},
        'update_approved_bills': {'key': 'updateApprovedBills', 'type': 'UpdateApprovedBills'},
        'update_units_on_existing_bills': {'key': 'updateUnitsOnExistingBills', 'type': 'UpdateUnitsOnExistingBills'},
        'budgets_and_budget_versions': {'key': 'budgetsAndBudgetVersions', 'type': 'BudgetsAndBudgetVersions'},
        'chargebacks_module': {'key': 'chargebacksModule', 'type': 'ChargebacksModule'},
        'chargebacks': {'key': 'chargebacks', 'type': 'Chargebacks'},
        'chargeback_reversals': {'key': 'chargebackReversals', 'type': 'ChargebackReversals'},
        'meter_savings_settings': {'key': 'meterSavingsSettings', 'type': 'MeterSavingsSettings'},
        'savings_adjustments': {'key': 'savingsAdjustments', 'type': 'SavingsAdjustments'},
        'manually_adjust_savings': {'key': 'manuallyAdjustSavings', 'type': 'ManuallyAdjustSavings'},
        'savings_engine': {'key': 'savingsEngine', 'type': 'SavingsEngine'},
        'baseline_engine': {'key': 'baselineEngine', 'type': 'BaselineEngine'},
        'global_cost_avoidance_settings': {'key': 'globalCostAvoidanceSettings', 'type': 'GlobalCostAvoidanceSettings'},
        'dashboard_and_maps_module': {'key': 'dashboardAndMapsModule', 'type': 'DashboardAndMapsModule'},
        'dashboard_administrator': {'key': 'dashboardAdministrator', 'type': 'DashboardAdministrator'},
        'public_dashboards_or_maps': {'key': 'publicDashboardsOrMaps', 'type': 'PublicDashboardsOrMaps'},
        'shared_dashboards_or_maps': {'key': 'sharedDashboardsOrMaps', 'type': 'SharedDashboardsOrMaps'},
        'buildings_and_meters_module': {'key': 'buildingsAndMetersModule', 'type': 'BuildingsAndMetersModule'},
        'groups_and_benchmarks_module': {'key': 'groupsAndBenchmarksModule', 'type': 'GroupsAndBenchmarksModule'},
        'building_and_meter_groups': {'key': 'buildingAndMeterGroups', 'type': 'BuildingAndMeterGroups'},
        'buildings_and_organizations': {'key': 'buildingsAndOrganizations', 'type': 'BuildingsAndOrganizations'},
        'interval_data': {'key': 'intervalData', 'type': 'IntervalData'},
        'interval_data_analysis': {'key': 'intervalDataAnalysis', 'type': 'IntervalDataAnalysis'},
        'energystar_submissions': {'key': 'energystarSubmissions', 'type': 'ENERGYSTARSubmissions'},
        'facility_projects': {'key': 'facilityProjects', 'type': 'FacilityProjects'},
        'greenhouse_gas_administrator': {'key': 'greenhouseGasAdministrator', 'type': 'GreenhouseGasAdministrator'},
        'interval_data_rollup': {'key': 'intervalDataRollup', 'type': 'IntervalDataRollup'},
        'meters': {'key': 'meters', 'type': 'Meters'},
        'normalization_settings': {'key': 'normalizationSettings', 'type': 'NormalizationSettings'},
        'weather_settings': {'key': 'weatherSettings', 'type': 'WeatherSettings'},
        'reports_module': {'key': 'reportsModule', 'type': 'ReportsModule'},
        'distributed_reports_settings': {'key': 'distributedReportsSettings', 'type': 'DistributedReportsSettings'},
        'install_or_update_reports': {'key': 'installOrUpdateReports', 'type': 'InstallOrUpdateReports'},
        'report_groups': {'key': 'reportGroups', 'type': 'ReportGroups'},
        'shared_reports': {'key': 'sharedReports', 'type': 'SharedReports'},
        'reset_user_passwords': {'key': 'resetUserPasswords', 'type': 'ResetUserPasswords'},
        'users_and_roles': {'key': 'usersAndRoles', 'type': 'UsersAndRoles'},
        'vendors_and_rates_module': {'key': 'vendorsAndRatesModule', 'type': 'VendorsAndRatesModule'},
        'rate_schedules': {'key': 'rateSchedules', 'type': 'RateSchedules'},
        'vendors': {'key': 'vendors', 'type': 'Vendors'},
    }

    def __init__(self, license_feature_accounting_export=None, license_feature_accrual_bills=None, license_feature_chargebacks=None, license_feature_cost_avoidance=None, license_feature_interval_data_analysis=None, license_feature_report_designer=None, accounting_settings=None, accounts=None, accounts_module=None, accrual_settings=None, cost_centers=None, move_accounts_between_vendors=None, application_settings=None, approve_bills=None, bill_audit_groups=None, bill_audits=None, bill_entry_templates=None, bill_workflow_settings=None, bills_and_batches=None, export_bills=None, export_hold=None, move_existing_bills=None, bill_audit_results_and_alerts=None, shared_bill_lists=None, unit_system_settings=None, update_approved_bills=None, update_units_on_existing_bills=None, budgets_and_budget_versions=None, chargebacks_module=None, chargebacks=None, chargeback_reversals=None, meter_savings_settings=None, savings_adjustments=None, manually_adjust_savings=None, savings_engine=None, baseline_engine=None, global_cost_avoidance_settings=None, dashboard_and_maps_module=None, dashboard_administrator=None, public_dashboards_or_maps=None, shared_dashboards_or_maps=None, buildings_and_meters_module=None, groups_and_benchmarks_module=None, building_and_meter_groups=None, buildings_and_organizations=None, interval_data=None, interval_data_analysis=None, energystar_submissions=None, facility_projects=None, greenhouse_gas_administrator=None, interval_data_rollup=None, meters=None, normalization_settings=None, weather_settings=None, reports_module=None, distributed_reports_settings=None, install_or_update_reports=None, report_groups=None, shared_reports=None, reset_user_passwords=None, users_and_roles=None, vendors_and_rates_module=None, rate_schedules=None, vendors=None):
        super(Permissions, self).__init__()
        self.license_feature_accounting_export = license_feature_accounting_export
        self.license_feature_accrual_bills = license_feature_accrual_bills
        self.license_feature_chargebacks = license_feature_chargebacks
        self.license_feature_cost_avoidance = license_feature_cost_avoidance
        self.license_feature_interval_data_analysis = license_feature_interval_data_analysis
        self.license_feature_report_designer = license_feature_report_designer
        self.accounting_settings = accounting_settings
        self.accounts = accounts
        self.accounts_module = accounts_module
        self.accrual_settings = accrual_settings
        self.cost_centers = cost_centers
        self.move_accounts_between_vendors = move_accounts_between_vendors
        self.application_settings = application_settings
        self.approve_bills = approve_bills
        self.bill_audit_groups = bill_audit_groups
        self.bill_audits = bill_audits
        self.bill_entry_templates = bill_entry_templates
        self.bill_workflow_settings = bill_workflow_settings
        self.bills_and_batches = bills_and_batches
        self.export_bills = export_bills
        self.export_hold = export_hold
        self.move_existing_bills = move_existing_bills
        self.bill_audit_results_and_alerts = bill_audit_results_and_alerts
        self.shared_bill_lists = shared_bill_lists
        self.unit_system_settings = unit_system_settings
        self.update_approved_bills = update_approved_bills
        self.update_units_on_existing_bills = update_units_on_existing_bills
        self.budgets_and_budget_versions = budgets_and_budget_versions
        self.chargebacks_module = chargebacks_module
        self.chargebacks = chargebacks
        self.chargeback_reversals = chargeback_reversals
        self.meter_savings_settings = meter_savings_settings
        self.savings_adjustments = savings_adjustments
        self.manually_adjust_savings = manually_adjust_savings
        self.savings_engine = savings_engine
        self.baseline_engine = baseline_engine
        self.global_cost_avoidance_settings = global_cost_avoidance_settings
        self.dashboard_and_maps_module = dashboard_and_maps_module
        self.dashboard_administrator = dashboard_administrator
        self.public_dashboards_or_maps = public_dashboards_or_maps
        self.shared_dashboards_or_maps = shared_dashboards_or_maps
        self.buildings_and_meters_module = buildings_and_meters_module
        self.groups_and_benchmarks_module = groups_and_benchmarks_module
        self.building_and_meter_groups = building_and_meter_groups
        self.buildings_and_organizations = buildings_and_organizations
        self.interval_data = interval_data
        self.interval_data_analysis = interval_data_analysis
        self.energystar_submissions = energystar_submissions
        self.facility_projects = facility_projects
        self.greenhouse_gas_administrator = greenhouse_gas_administrator
        self.interval_data_rollup = interval_data_rollup
        self.meters = meters
        self.normalization_settings = normalization_settings
        self.weather_settings = weather_settings
        self.reports_module = reports_module
        self.distributed_reports_settings = distributed_reports_settings
        self.install_or_update_reports = install_or_update_reports
        self.report_groups = report_groups
        self.shared_reports = shared_reports
        self.reset_user_passwords = reset_user_passwords
        self.users_and_roles = users_and_roles
        self.vendors_and_rates_module = vendors_and_rates_module
        self.rate_schedules = rate_schedules
        self.vendors = vendors
