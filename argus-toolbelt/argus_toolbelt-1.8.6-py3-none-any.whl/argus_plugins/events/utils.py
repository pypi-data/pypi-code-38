from argus_api.api.customers.v1.customer import get_customer_by_shortname

# These are copy pasted from the argus documentation.
# It's recommended to view that if you want to get an overview of flags, etc.
GROUPINGS = [
    "ATTACK_IDENTIFIER", "ATTACK_CATEGORY", "ALARM", "SENSOR", "LOCATION", "EVENT_SEVERITY",
    "SOURCEIP", "DESTINATIONIP", "PROTOCOL", "CUSTOMER", "SOURCE_GEOIP_LOCATION",
    "SOURCE_GEOIP_COUNTRY", "DESTINATION_GEOIP_LOCATION", "DESTINATION_GEOIP_COUNTRY"
]
FLAGS = [
    "ESTABLISHED", "BLOCKED", "SNAPSHOT", "FINALIZED", "SOURCE_IS_CUSTOMERNET", "DESTINATION_IS_CUSTOMERNET",
    "SOURCE_IS_PARTIAL_CUSTOMERNET", "DESTINATION_IS_PARTIAL_CUSTOMERNET", "INTRUDER_IS_CUSTOMERNET",
    "VICTIM_IS_CUSTOMERNET", "INTRUDER_IS_PARTIAL_CUSTOMERNET", "VICTIM_IS_PARTIAL_CUSTOMERNET", "PARTIALLY_BLOCKED",
    "FALSE_POSITIVE", "NOT_A_THREAT", "TUNING_CANDIDATE", "NOTIFIED", "PARTIALLY_NOTIFIED", "FOLLOWUP",
    "IDENTIFIED_THREAT", "THREAT_CANDIDATE", "ACKNOWLEDGED", "PARTIALLY_ACKNOWLEDGED", "SEVERITY_ADJUSTED",
    "COMMENTED", "FILTERED", "CHECKED", "INCOMPLETE_DETAILS", "AGGREGATED_BASE_EVENT", "REMOTE_STORAGE",
    "CUSTOM_SOURCE_AGGREGATION", "CUSTOM_DESTINATION_AGGREGATION", "CUSTOM_INTRUDER_AGGREGATION",
    "CUSTOM_VICTIM_AGGREGATION", "HAS_PAYLOAD", "HAS_PCAP", "ASSOCIATED_TO_CASE_BY_FILTER",
    "SEVERITY_INCREASED_BY_FILTER", "SEVERITY_REDUCED_BY_FILTER", "CREATED_BY_ANALYSIS_FILTER",
    "EXTEND_EVENT_TTL", "INITIAL_TUNING"
]
SEVERITIES = ["low", "medium", "high", "critical"]


def get_customer_id(name: str) -> int:
    """Gets a customer's ID from their name

    :param name: The name of the customer
    """
    customers = get_customer_by_shortname(shortName=name.lower())["data"]
    customer_id = customers["id"]  # This might get the wrong customer if there are more with the same name?
    return customer_id
