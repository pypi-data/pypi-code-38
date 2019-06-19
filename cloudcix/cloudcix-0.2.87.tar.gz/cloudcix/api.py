from __future__ import unicode_literals
from .base import APIClient


# App Manager Services
class app_manager(object):
    _application_name = 'AppManager'
    app = APIClient(
        application=_application_name,
        service_uri='App/')
    app_member = APIClient(
        application=_application_name,
        service_uri='App/{idApp}/Member/')
    app_menu = APIClient(
        application=_application_name,
        service_uri='App/{idApp}/MenuItem/')
    menu_item_user = APIClient(
        application=_application_name,
        service_uri='MenuItem/User/{idUser}/')


# Asset
class asset(object):
    _application_name = 'Asset'
    asset = APIClient(
        application=_application_name,
        service_uri='Asset/')
    asset_transaction = APIClient(
        application=_application_name,
        service_uri='Asset/{idAsset}/Transaction/')
    depreciation_type = APIClient(
        application=_application_name,
        service_uri='DepreciationType/')
    off_rent = APIClient(
        application=_application_name,
        service_uri='OffRent/')
    off_test = APIClient(
        application=_application_name,
        service_uri='OffTest/')
    rent = APIClient(
        application=_application_name,
        service_uri='Rent/')


# Circuit
class circuit(object):
    _application_name = 'Circuit'
    circuit = APIClient(
        application=_application_name,
        service_uri='Circuit/')
    circuit_class = APIClient(
        application=_application_name,
        service_uri='CircuitClass/')
    property_type = APIClient(
        application=_application_name,
        service_uri='PropertyType/')


# Contacts Services
class contacts(object):
    _application_name = 'Contacts'
    activity = APIClient(
        application=_application_name,
        service_uri='ActivityType/{idActivityType}/Activity/')
    activity_type = APIClient(
        application=_application_name,
        service_uri='ActivityType/')
    campaign_activity = APIClient(
        application=_application_name,
        service_uri='Campaign/{idCampaign}/Activity/')
    campaign = APIClient(
        application=_application_name,
        service_uri='Campaign/')
    campaign_contact = APIClient(
        application=_application_name,
        service_uri='Campaign/{idCampaign}/Contact/')
    contact = APIClient(
        application=_application_name,
        service_uri='Contact/')
    group = APIClient(
        application=_application_name,
        service_uri='Group/')
    group_contact = APIClient(
        application=_application_name,
        service_uri='Group/{idGroup}/Contact/')
    opportunity = APIClient(
        application=_application_name,
        service_uri='Opportunity/')
    opportunity_contact = APIClient(
        application=_application_name,
        service_uri='Opportunity/{idOpportunity}/Contact/')
    opportunity_history = APIClient(
        application=_application_name,
        service_uri='Opportunity/{idOpportunity}/History/')


# DNS Services.
class dns(object):
    _application_name = 'DNS'
    aggregated_blacklist = APIClient(
        application=_application_name,
        service_uri='AggregatedBlacklist/')
    allocation = APIClient(
        application=_application_name,
        service_uri='Allocation/')
    asn = APIClient(
        application=_application_name,
        service_uri='ASN/')
    blacklist = APIClient(
        application=_application_name,
        service_uri='CIXBlacklist/')
    blacklist_source = APIClient(
        application=_application_name,
        service_uri='BlacklistSource/')
    cloud = APIClient(
        application=_application_name,
        service_uri='Cloud/')
    domain = APIClient(
        application=_application_name,
        service_uri='Domain/')
    hypervisor = APIClient(
        application=_application_name,
        service_uri='Hypervisor/')
    ike = APIClient(
        application=_application_name,
        service_uri='IKE/')
    image = APIClient(
        application=_application_name,
        service_uri='Image/')
    ip_validator = APIClient(
        application=_application_name,
        service_uri='IPValidator/')
    ipaddress = APIClient(
        application=_application_name,
        service_uri='IPAddress/')
    ipmi = APIClient(
        application=_application_name,
        service_uri='IPMI/')
    ipsec = APIClient(
        application=_application_name,
        service_uri='IpSec/')
    location_hasher = APIClient(
        application=_application_name,
        service_uri='LocationHasher/')
    macaddress = APIClient(
        application=_application_name,
        service_uri='Server/{idServer}/MacAddress/')
    nmap = APIClient(
        application=_application_name,
        service_uri='nmap/')
    pool_ip = APIClient(
        application=_application_name,
        service_uri='PoolIP/')
    port = APIClient(
        application=_application_name,
        service_uri='Router/{idRouter}/Port/')
    port_config = APIClient(
        application=_application_name,
        service_uri='Port/{port_id}/PortConfig/')
    port_function = APIClient(
        application=_application_name,
        service_uri='PortFunction/')
    project = APIClient(
        application=_application_name,
        service_uri='Project/')
    server = APIClient(
        application=_application_name,
        service_uri='Server/')
    storage = APIClient(
        application=_application_name,
        service_uri='VM/{idVM}/Storage/')
    storage_type = APIClient(
        application=_application_name,
        service_uri='StorageType/')
    subnet = APIClient(
        application=_application_name,
        service_uri='Subnet/')
    subnet_space = APIClient(
        application=_application_name,
        service_uri='Allocation/{idAllocation}/Subnet_space/')
    record = APIClient(
        application=_application_name,
        service_uri='Record/')
    recordptr = APIClient(
        application=_application_name,
        service_uri='RecordPTR/')
    router = APIClient(
        application=_application_name,
        service_uri='Router/')
    router_model = APIClient(
        application=_application_name,
        service_uri='RouterModel/')
    router_model_port_function = APIClient(
        application=_application_name,
        service_uri='RouterModelPortFunction/')
    vm = APIClient(
        application=_application_name,
        service_uri='VM/')
    vm_history = APIClient(
        application=_application_name,
        service_uri="VM/{idVM}/VMHistory/")
    vpn_tunnel = APIClient(
        application=_application_name,
        service_uri="VPNTunnel/")
    vrf = APIClient(
        application=_application_name,
        service_uri='VRF/')
    whitelist = APIClient(
        application=_application_name,
        service_uri='CIXWhitelist/')


# Documentation Services
class documentation(object):
    _application_name = 'Documentation'
    application = APIClient(
        application=_application_name,
        service_uri='Application/')


# Financial (BETA - In development)
class financial(object):
    _application_name = 'Financial'
    account_purchase_adjustment = APIClient(
        application=_application_name,
        service_uri='AccountPurchaseAdjustment/')
    account_purchase_adjustment_contra = APIClient(
        application=_application_name,
        service_uri='AccountPurchaseAdjustment/{idAddress}/Contra/')
    account_purchase_debit_note = APIClient(
        application=_application_name,
        service_uri='AccountPurchaseDebitNote/')
    account_purchase_debit_note_contra = APIClient(
        application=_application_name,
        service_uri='AccountPurchaseDebitNote/{idAddress}/Contra/')
    account_purchase_invoice = APIClient(
        application=_application_name,
        service_uri='AccountPurchaseInvoice/')
    account_purchase_invoice_contra = APIClient(
        application=_application_name,
        service_uri='AccountPurchaseInvoice/{idAddress}/Contra/')
    account_purchase_payment = APIClient(
        application=_application_name,
        service_uri='AccountPurchasePayment/')
    account_purchase_payment_contra = APIClient(
        application=_application_name,
        service_uri='AccountPurchasePayment/{idAddress}/Contra/')
    account_sale_adjustment = APIClient(
        application=_application_name,
        service_uri='AccountSaleAdjustment/')
    account_sale_adjustment_contra = APIClient(
        application=_application_name,
        service_uri='AccountSaleAdjustment/{idAddress}/Contra/')
    account_sale_credit_note = APIClient(
        application=_application_name,
        service_uri='AccountSaleCreditNote/')
    account_sale_credit_note_contra = APIClient(
        application=_application_name,
        service_uri='AccountSaleCreditNote/{idAddress}/Contra/')
    account_sale_invoice = APIClient(
        application=_application_name,
        service_uri='AccountSaleInvoice/')
    account_sale_invoice_contra = APIClient(
        application=_application_name,
        service_uri='AccountSaleInvoice/{idAddress}/Contra/')
    account_sale_payment = APIClient(
        application=_application_name,
        service_uri='AccountSalePayment/')
    account_sale_payment_contra = APIClient(
        application=_application_name,
        service_uri='AccountSalePayment/{idAddress}/Contra/')
    allocation = APIClient(
        application=_application_name,
        service_uri='Allocation/')
    business_logic = APIClient(
        application=_application_name,
        service_uri='BusinessLogic/')
    cash_purchase_debit_note = APIClient(
        application=_application_name,
        service_uri='CashPurchaseDebitNote/')
    cash_purchase_debit_note_contra = APIClient(
        application=_application_name,
        service_uri='CashPurchaseDebitNote/{idAddress}/Contra/')
    cash_purchase_invoice = APIClient(
        application=_application_name,
        service_uri='CashPurchaseInvoice/')
    cash_purchase_invoice_contra = APIClient(
        application=_application_name,
        service_uri='CashPurchaseInvoice/{idAddress}/Contra/')
    cash_sale_credit_note = APIClient(
        application=_application_name,
        service_uri='CashSaleCreditNote/')
    cash_sale_credit_note_contra = APIClient(
        application=_application_name,
        service_uri='CashSaleCreditNote/{idAddress}/Contra/')
    cash_sale_invoice = APIClient(
        application=_application_name,
        service_uri='CashSaleInvoice/')
    cash_sale_invoice_contra = APIClient(
        application=_application_name,
        service_uri='CashSaleInvoice/{idAddress}/Contra/')
    credit_limit = APIClient(
        application=_application_name,
        service_uri='CreditLimit/')
    creditor_account_history = APIClient(
        application=_application_name,
        service_uri='CreditorAccount/{id}/History/')
    creditor_account_statement = APIClient(
        application=_application_name,
        service_uri='CreditorAccount/{id}/Statement/')
    creditor_ledger = APIClient(
        application=_application_name,
        service_uri='CreditorLedger/')
    creditor_ledger_aged = APIClient(
        application=_application_name,
        service_uri='CreditorLedger/Aged/')
    creditor_ledger_transaction = APIClient(
        application=_application_name,
        service_uri='CreditorLedger/Transaction/')
    creditor_ledger_transaction_contra = APIClient(
        application=_application_name,
        service_uri='CreditorLedger/ContraTransaction/')
    debtor_account_history = APIClient(
        application=_application_name,
        service_uri='DebtorAccount/{id}/History/')
    debtor_account_statement = APIClient(
        application=_application_name,
        service_uri='DebtorAccount/{id}/Statement/')
    debtor_account_statement_log = APIClient(
        application=_application_name,
        service_uri='DebtorAccount/StatementLog/')
    debtor_ledger = APIClient(
        application=_application_name,
        service_uri='DebtorLedger/')
    debtor_ledger_aged = APIClient(
        application=_application_name,
        service_uri='DebtorLedger/Aged/')
    debtor_ledger_transaction = APIClient(
        application=_application_name,
        service_uri='DebtorLedger/Transaction/')
    debtor_ledger_transaction_contra = APIClient(
        application=_application_name,
        service_uri='DebtorLedger/ContraTransaction/')
    journal_entry = APIClient(
        application=_application_name,
        service_uri='JournalEntry/')
    nominal_account = APIClient(
        application=_application_name,
        service_uri='NominalAccount/')
    nominal_account_history = APIClient(
        application=_application_name,
        service_uri='NominalAccount/{id}/History/')
    nominal_account_type = APIClient(
        application=_application_name,
        service_uri='NominalAccountType/')
    nominal_contra = APIClient(
        application=_application_name,
        service_uri='NominalContra/')
    nominal_ledger_balance_sheet = APIClient(
        application=_application_name,
        service_uri='NominalLedger/BalanceSheet/')
    nominal_ledger_profit_loss = APIClient(
        application=_application_name,
        service_uri='NominalLedger/ProfitLoss/')
    nominal_ledger_purchases_by_country = APIClient(
        application=_application_name,
        service_uri='NominalLedger/PurchasesByCountry/')
    nominal_ledger_sales_by_country = APIClient(
        application=_application_name,
        service_uri='NominalLedger/SalesByCountry/')
    nominal_ledger_trial_balance = APIClient(
        application=_application_name,
        service_uri='NominalLedger/TrialBalance/')
    nominal_ledger_VIES_purchases = APIClient(
        application=_application_name,
        service_uri='NominalLedger/VIESPurchases/')
    nominal_ledger_VIES_sales = APIClient(
        application=_application_name,
        service_uri='NominalLedger/VIESSales/')
    payment_method = APIClient(
        application=_application_name,
        service_uri='PaymentMethod/')
    period_end = APIClient(
        application=_application_name,
        service_uri='PeriodEnd/')
    tax_rate = APIClient(
        application=_application_name,
        service_uri='TaxRate/')
    year_end = APIClient(
        application=_application_name,
        service_uri='YearEnd/')


# HelpDesk
class helpdesk(object):
    _application_name = 'HelpDesk'
    iris_condition = APIClient(
        application=_application_name,
        service_uri='IRISCondition/')
    iris_defect = APIClient(
        application=_application_name,
        service_uri='IRISDefect/')
    iris_extended_condition = APIClient(
        application=_application_name,
        service_uri='IRISExtendedCondition/')
    iris_ntf = APIClient(
        application=_application_name,
        service_uri='IRISNTF/')
    iris_repair = APIClient(
        application=_application_name,
        service_uri='IRISRepair/')
    iris_section = APIClient(
        application=_application_name,
        service_uri='IRISSection/')
    iris_symptom = APIClient(
        application=_application_name,
        service_uri='IRISSymptom/')
    item = APIClient(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/{transactionSequenceNumber}/'
                    'Item/')
    item_history = APIClient(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/{transactionSequenceNumber}/'
                    'Item/{idItem}/History/')
    item_part_used = APIClient(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/{transactionSequenceNumber}/'
                    'Item/{idItem}/PartUsed/')
    item_status = APIClient(
        application=_application_name,
        service_uri='ItemStatus/')
    reason_for_return = APIClient(
        application=_application_name,
        service_uri='ReasonForReturn/')
    reason_for_return_translation = APIClient(
        application=_application_name,
        service_uri='ReasonForReturn/{idReasonForReturn}/Translation/')
    service_centre_logic = APIClient(
        application=_application_name,
        service_uri='ServiceCentreLogic/')
    service_centre_warrantor = APIClient(
        application=_application_name,
        service_uri='ServiceCentre/{idAddress}/Warrantor/')
    status = APIClient(
        application=_application_name,
        service_uri='Status/')
    ticket = APIClient(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/')
    ticket_history = APIClient(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/'
                    '{transactionSequenceNumber}/History/')
    ticket_question = APIClient(
        application=_application_name,
        service_uri='TicketQuestion/')
    ticket_type = APIClient(
        application=_application_name,
        service_uri='TicketType/')
    ticket_type_question = APIClient(
        application=_application_name,
        service_uri='TicketType/{id}/TicketQuestion/')
    warrantor_logic = APIClient(
        application=_application_name,
        service_uri='WarrantorLogic/')
    warrantor_service_centre = APIClient(
        application=_application_name,
        service_uri='Warrantor/{idAddress}/ServiceCentre/')


# Import Engine (BETA)
class import_engine(object):
    _application_name = 'Import'
    application = APIClient(
        application=_application_name,
        service_uri='Application/')
    import_service = APIClient(
        application=_application_name,
        service_uri='Import/')
    model = APIClient(
        application=_application_name,
        service_uri='Application/{idApplication}/Model/')


# Membership
class membership(object):
    _application_name = 'Membership'
    address = APIClient(
        application=_application_name,
        service_uri='Address/')
    address_link = APIClient(
        application=_application_name,
        service_uri='Address/{idAddress}/Link/')
    country = APIClient(
        application=_application_name,
        service_uri='Country/')
    currency = APIClient(
        application=_application_name,
        service_uri='Currency/')
    department = APIClient(
        application=_application_name,
        service_uri='Department/')
    language = APIClient(
        application=_application_name,
        service_uri='Language/')
    member = APIClient(
        application=_application_name,
        service_uri='Member/')
    member_link = APIClient(
        application=_application_name,
        service_uri='Member/{idMember}/Link/')
    notification = APIClient(
        application=_application_name,
        service_uri='Address/{idAddress}/Notification/')
    profile = APIClient(
        application=_application_name,
        service_uri='Profile/')
    subdivision = APIClient(
        application=_application_name,
        service_uri='Country/{idCountry}/Subdivision/')
    team = APIClient(
        application=_application_name,
        service_uri='Team/')
    territory = APIClient(
        application=_application_name,
        service_uri='Territory/')
    timezone = APIClient(
        application=_application_name,
        service_uri='Timezone/')
    transaction_type = APIClient(
        application=_application_name,
        service_uri='TransactionType/')
    token = APIClient(
        application=_application_name,
        service_uri='auth/login/',
    )
    user = APIClient(
        application=_application_name,
        service_uri='User/')


# Plot (BETA) -> Only list methods implemented!
class plot(object):
    _application_name = 'Plot'
    reading = APIClient(
        application=_application_name,
        service_uri='Source/{idSource}/Reading/')
    source = APIClient(
        application=_application_name,
        service_uri='Source/')


# Reporting
class reporting(object):
    _application_name = 'Reporting'
    export = APIClient(
        application=_application_name,
        service_uri='Export/')
    package = APIClient(
        application=_application_name,
        service_uri='Package/')
    report = APIClient(
        application=_application_name,
        service_uri='Report/')
    report_template = APIClient(
        application=_application_name,
        service_uri='ReportTemplate/')


# Scheduler
class scheduler(object):
    _application_name = 'Scheduler'
    execute_task = APIClient(
        application=_application_name,
        service_uri='Task/{idTask}/execute/')
    task = APIClient(
        application=_application_name,
        service_uri='Task/')
    task_log = APIClient(
        application=_application_name,
        service_uri='TaskLog/')


# SCM
class scm(object):
    _application_name = 'SCM'
    agreed_price = APIClient(
        application=_application_name,
        service_uri='AgreedPrice/')
    brand = APIClient(
        application=_application_name,
        service_uri='Brand/')
    bin = APIClient(
        application=_application_name,
        service_uri='Bin/')
    bin_sku = APIClient(
        application=_application_name,
        service_uri='Bin/{id}/SKU/')
    # idSKUComponent should be passed as pk to resource methods
    critical_bom = APIClient(
        application=_application_name,
        service_uri='SKU/{idSKU}/BOM/')
    # CriticalBOM for member returns all BOM records for the idMember
    # doing the request
    critical_bom_for_member = APIClient(
        application=_application_name,
        service_uri='SKU/BOM/')
    manufactured_item = APIClient(
        application=_application_name,
        service_uri='ManufacturedItem/')
    purchase_order = APIClient(
        application=_application_name,
        service_uri='PurchaseOrder/')
    return_question = APIClient(
        application=_application_name,
        service_uri='ReturnQuestion/')
    return_question_field_type = APIClient(
        application=_application_name,
        service_uri='ReturnQuestionFieldType/')
    sales_order = APIClient(
        application=_application_name,
        service_uri='SalesOrder/')
    service_group = APIClient(
        application=_application_name,
        service_uri='ServiceGroup/')
    sku = APIClient(
        application=_application_name,
        service_uri='SKU/')
    sku_category = APIClient(
        application=_application_name,
        service_uri='SKUCategory/')
    sku_category_return_question = APIClient(
        application=_application_name,
        service_uri='SKUCategory/{idSKUCategory}/ReturnQuestion/')
    sku_stock = APIClient(
        application=_application_name,
        service_uri='SKU/{idSKU}/Stock/')
    sku_stock_adjustment = APIClient(
        application=_application_name,
        service_uri='SKUStockAdjustment/')
    sku_value = APIClient(
        application=_application_name,
        service_uri='SKU/{idSKU}/Value/')


# Security
class security(object):
    _application_name = 'Security'
    security_event = APIClient(
        application=_application_name,
        service_uri='SecurityEvent/')
    security_event_logout = APIClient(
      application=_application_name,
      service_uri='SecurityEvent/{idUser}/Logout/')


# Support Framework Services
class support_framework(object):
    _application_name = 'SupportFramework'
    application = APIClient(
        application=_application_name,
        service_uri='Member/{idMember}/Application/')
    dto = APIClient(
        application=_application_name,
        service_uri='DTO/')
    dto_parameter = APIClient(
        application=_application_name,
        service_uri='DTO/{idDTO}/Parameter/')
    exception_code = APIClient(
        application=_application_name,
        service_uri='ExceptionCode/')
    language_exception_code = APIClient(
        application=_application_name,
        service_uri='ExceptionCode/{exception_code}/Language/')
    member = APIClient(
        application=_application_name,
        service_uri='Member/')
    method = APIClient(
        application=_application_name,
        service_uri=('Member/{idMember}/Application/{idApplication}/'
                     'Service/{idService}/Method/'))
    method_parameter = APIClient(
        application=_application_name,
        service_uri=('Member/{idMember}/Application/{idApplication}/Service/'
                     '{idService}/Method/{idMethod}/Parameter/'))
    service = APIClient(
        application=_application_name,
        service_uri='Member/{idMember}/Application/{idApplication}/Service/')


# Training
class training(object):
    _application_name = 'Training'
    cls = APIClient(
        application=_application_name,
        service_uri='Class/')
    student = APIClient(
        application=_application_name,
        service_uri='Student/')
    syllabus = APIClient(
        application=_application_name,
        service_uri='Syllabus/')
