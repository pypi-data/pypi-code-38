from enum import Enum


class AddressType(Enum):
    """
        Used to differentiate Billing and Mailing address sets
    """
    BILLING = "BILLING"
    MAILING = "MAILING"
    MULTIPURPOSE = "MULTIPURPOSE"


class PaymentMethodType(Enum):
    """
        Supported payment options for IBM Smart Cloud
    """
    CREDIT_CARD = "CREDIT_CARD"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    INVOICE = "INVOICE"
    NONE = "NONE"


class CustomerIdType(Enum):
    """

    """
    CAAS_CUSTOMER_ID = "CAAS_CUSTOMER_ID"
    COREMETRIC_CUSTOMER_ID = "COREMETRIC_CUSTOMER_ID"
    GLOBALCROSSING_ID = "GLOBALCROSSING_ID"
    GLOBALIVE_ID = "GLOBALIVE_ID"
    IBM_CUSTOMER_NUMBER = "IBM_CUSTOMER_NUMBER"
    IBM_CUSTOMER_NUMBER_PREV = "IBM_CUSTOMER_NUMBER_PREV"
    IBM_SITE_NUMBER = "IBM_SITE_NUMBER"
    SALESFORCE_ACCOUNT_ID = "SALESFORCE_ACCOUNT_ID"
    SALESFORCE_CONTACT_ID = "SALESFORCE_CONTACT_ID"
    SALESFORCE_ID = "SALESFORCE_ID"
    SALESFORCE_LEAD_ID = "SALESFORCE_LEAD_ID"
    SALESFORCE_OPPORTUNITY_ID = "SALESFORCE_OPPORTUNITY_ID"
    SIEBEL_ID = "SIEBEL_ID"
    STERLING_CUSTOMER_ID = "STERLING_CUSTOMER_ID"
    TMS_CUSTOMER_ID = "TMS_CUSTOMER_ID"
    UNICA_CUSTOMER_ID = "UNICA_CUSTOMER_ID"
    UNYTE_CUSTOMER_ID = "UNYTE_CUSTOMER_ID"


class SecurityRealm(Enum):
    """
        Security configuration used by the Organization/Subscriber
    """
    FEDERATED = "FEDERATED"
    NON_FEDERATED = "NON_FEDERATED"
    MODIFIED_FEDERATED = "MODIFIED_FEDERATED"
    PARTIAL_FEDERATED = "PARTIAL_FEDERATED"


class LanguagePreference(Enum):
    """
        Security configuration used by the Organization/Subscriber
    """
    EN_US = "en_US"


class RoleSet(Enum):
    """
        Supported roles that can be assigned.
    """
    CUSTOMER_ADMINISTRATOR = "CustomerAdministrator"
    CONNECTIONS_AUDITOR = "ConnectionsAuditor"
    CONTENT_VALIDATOR = "ContentValidator"
    APP_DEVELOPER = "AppDeveloper"
    SUPPORT = "Support"
    USER_ACCOUNT_ASSISTANT = "UserAccountAssistant"
    DATA_MIGRATOR = "DataMigrator"
    USER = "User"
    VSR = "VSR"


class TimeZone(Enum):
    """
        Available timezones for use in IBM SmartCloud
    """
    HAWAII_STANDARD_TIME = "HST"
    ALASKA_STANDARD_TIME = "AST"
    YUKON_STANDARD_TIME = "YST"
    PACIFIC_STANDARD_TIME = "PST"
    MOUNTAIN_STANDARD_TIME = "MST"
    CENTRAL_STANDARD_TIME = "CST"
    EASTERN_STANDARD_TIME = "EST"
    ATLANTIC_STANDARD_TIME = "AST"
    NEWFOUNDLAND_STANDARD_TIME = "NST"


class CurrencyType(Enum):
    """
        Supported currencies for payment.
    """
    USD = "USD"
    EUR = "EUR"
    CAD = "CAD"
    AUD = "AUD"
    NZD = "NZD"
    INR = "INR"
    GBP = "GBP"
    JPY = "JPY"
    WON = "WON"


class PartyType(Enum):
    PERSON = "PERSON"
    ORGANISATION = "ORGANIZATION"


class PartyRollType(Enum):
    SUBSCRIBER = "SUBSCRIBER"


class BSSBoolean(Enum):
    TRUE = "true"
    FALSE = "false"


class CustomerType(Enum):
    DIRECT = "DIRECT"


class State(Enum):
    """
        Supported states for various Organizations,Subscriptions,Subscribers etc.
    """
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"
    SOFT_DELETED = "SOFT_DELETED"
    CANCEL_PENDING = "CANCEL_PENDING"
    REMOVE_PENDING = "REMOVE_PENDING"
    DEREGISTER_PENDING = "DEREGISTER_PENDING"
    UNSET = ""
