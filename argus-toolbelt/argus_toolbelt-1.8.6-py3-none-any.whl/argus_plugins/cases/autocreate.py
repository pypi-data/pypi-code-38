import json
import sys
from string import Formatter
from datetime import datetime
from functools import lru_cache, partial
from itertools import groupby
from pathlib import Path

from argus_api.api.cases.v2.case import advanced_case_search, create_case, add_comment, add_case_tag
from argus_api.api.customers.v1.customer import get_customer_by_shortname
from argus_api.api.events.v1.aggregated import update_events
from argus_plugins import argus_cli_module
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_plugins.cases.utils import STATUSES, PRIORITIES, CASE_TYPES


# Cache the function to avoid multiple calls to the backend
get_customer_by_shortname = lru_cache(maxsize=None)(get_customer_by_shortname)


def customer_language(customer: dict) -> str:
    """Convenience function to get a customer's language"""
    try:
        return customer["language"]
    except KeyError:
        log.debug("Fetching language from Argus for {shortName}".format_map(customer))
        return get_customer_by_shortname(customer["shortName"])["data"]["language"]


def value_from_nested_key(key: str, d: dict):
    """Allows the user to reference a variable with normal python string-format syntax.

    Example:
        >>> value_from_nested_key("a[b][c]", {"a": {"b": {"c": 1337}})
        1337
        >>> value_from_nested_key("a", {"a": 42})
        42
    """
    try:
        return Formatter().get_field(key, (), d)[0]
    except KeyError:
        return None


def _get_field(field: str, event: dict):
    """Returns a hashable key for us to use

    Dicts and lists arn't hashable, so we have to make them hashable.
    This is a representation problem that could have been fixed by having objects
    representing the data in stead of dicts.
    """
    new = value_from_nested_key(field, event)

    if isinstance(new, dict):
        # Dicts arn't hashable
        new = tuple(sorted(new.items()))
    elif isinstance(new, list):
        # List ain't hashable either.
        new = tuple(new)

    return new


def group_inputs(data: list, group_by: list) -> dict:
    """Groups the input based on the group_by parameter.

    The first field in group_by will be the outermost group in the dict.

    :param data: The input
    :param group_by: Field to group by
    :returns: A nested group dict
    """
    def _key(event):
        return tuple(_get_field(field, event) for field in group_by)

    events = sort_input(data, group_by)  # Has to be sorted, see groupby()'s documentation.
    return {
        # groupby() returns the group as an iterator, so we have to unpack it.
        group_key: list(group)
        for group_key, group in groupby(events, key=_key)
    }


def sort_input(data: list, sort_by: list) -> list:
    """Sorts the given inputs based on the given list.

    The first field in sort_by will be the one with most precedence (primary key).

    :param data: The input
    :param sort_by: Fields to sort by
    :returns: A sorted list of events
    """
    def _key(event):
        # "None" is not sortable, so adding an extra sorting value for that.
        return tuple((field not in event, _get_field(field, event)) for field in sort_by)

    return sorted(data, key=_key)


def group_data(data: list, groups: list):
    """Gives the data groups based on the customer and groups"""
    customer_events = group_inputs(data, ["customerInfo"])
    for customer, data in customer_events.items():
        customer = dict(customer[0])  # Workaround because group_inputs()'s key is a tuple.
        log.info("Handling data for customer \"{}\"".format(customer["shortName"]))

        groupings = group_inputs(data, groups)
        for group, data in groupings.items():
            log.debug("Handling dataset in group {}:\n{}".format(group, data))
            group = str(group)  # Since we want to use this as a value in argus, we have to make it a string..
            yield (customer, group, data)


def put_data_in_case(
        data: list,
        customer: dict,
        group: str,
        find_existing_case: callable,
        create_description: callable,
        create_comment: callable,
        create_case: callable,
        event_accociator: callable,
        set_initial_comment: bool = False,
):
    """Puts the data into the given group for the given customer.

    :param data: List of data
    :param customer: The customer object to associate with the data
    :param group: The group that the data belongs to
    :param find_existing_case:
    :param create_description:
    :param create_comment:
    :param create_case:
    :param event_accociator:
    :param set_initial_comment: Add internal comment on case creation
    :returns: The case that got commented or created.
    """
    case = find_existing_case(customer, group)

    description = create_description(data, customer, comment=True if case else False)
    log.debug("Description for the given group: {}".format(description))
    if case:
        create_comment(case["id"], comment=description)
        log.info("Created comment on case #{id}".format_map(case))
    else:
        case = create_case(customer, group, description, data[0])
        log.info("Created new case #{id}".format_map(case))
        if (set_initial_comment): 
            initial_comment = create_description(data, customer, comment=False, internal=True)
            create_comment(case["id"], comment=initial_comment, internal=True)
            log.debug("Added internal comment after creating case #{id}".format_map(case))

    event_accociator(case["id"], data)
    log.debug("Associated the given events with case {id}".format_map(case))

    return case


@register_command(extending="cases", module=argus_cli_module)
def autocreate(
        data: sys.stdin,
        key: str,
        template_folder: Path,

        group_by: list = [],
        sort_by: list = [],
        # TODO: Create special case for timedelta (and datetime) objects
        timeout: datetime = datetime.now(),

        case_title: str = "Autocreated based on group {group}",
        case_status: STATUSES = "pendingCustomer",
        case_priority: PRIORITIES = "medium",
        case_type: CASE_TYPES = "securityIncident",
        case_service: str = "ids",
        case_category: str = None,
        skip_notifications: bool = False,
        initial_internal_comment: bool = False,
        internal_case: bool = False,
        dry: bool = False,
):
    """A tool for automatically creating a case based on events and similar.

    Customers will automatically be extracted from the given data.
    There will be one case per group, meaning that if you group by email addresses,
    you'll get one case per email address.

    Examples:
        New case every time the script runs:
        $ argus-cli ./data.json "protocol-data" ./
            --group-by protocol
            --case-title "We've spotted some protocols"

        New case every week based on the alarm ID
        $ echo "<List of JSON objects>"| argus-cli cases autocreate "scary-events" ./templates/
            --group-by attackInfo[alarmId]
            --timeout "1 week"
            --case-title "This week, scary stuff happened."

    :param data: JSON-data to parse. Will typically be passed via stdin.
    :param key: A unique ID for this autocreate instance. Will be associated to the case as a tag.
    :param template_folder: Folder with JINJA templates. Filenames are: <key>.<language>.html
    :param group_by: Identifiers in the data to group by (Unique cases will be created per group).
    :param sort_by: Identifiers in the data to sort by
    :param timeout: The timeframe between new cases. If not specified a new case will be created every run.
    :param case_title: The title of the created case. Can be used with python string formatting.
    :param case_status: The status of the created case.
    :param case_priority: The priority of the created case.
    :param case_type: The type of the created case.
    :param case_service: The service of the created case.
    :param case_category: The category of the created case.
    :param initial_internal_comment: Creates a new internal comment on case creation. This can be added with a block checking for "internal" in your template.
    :param internal_case: Makes new cases only visible internally
    :param dry: If set, no data will be commited.
    """
    # Encapsulate data into functions to avoid tramp data
    _add_comment = partial(
        add_comment,
        notification={"skipEmail": skip_notifications, "skipSMS": skip_notifications},
    )

    def _create_description(events: list, customer: dict, comment: bool = False, internal: bool = False) -> str:
        """Creates a case description from a template file"""
        # Argus returns long names for languages, let's use 2 letter versions.
        language_map = {"NORWEGIAN": "no", "ENGLISH": "en"}

        jinja_env = Environment(
            loader=FileSystemLoader(str(template_folder)),  # jinja doesn't accept Path objects
            autoescape=select_autoescape(["html", "xml"]),
        )
        template = jinja_env.get_template(
            "{key}.{language}.html".format(key=key, language=language_map[customer_language(customer)])
        )
        return template.render(data=events, comment=comment, internal=internal)

    def _existing_case(customer: dict, group: str):
        """Returns an existing case based on the customer, key and group"""
        # If it turns out that there are a lot of search requests, then
        # this could probably be changed in favor of a single request to the "key"
        # and then filter for customer and group internally.
        cases = advanced_case_search(
            startTimestamp=int(timeout.timestamp() * 1000),  # Only get cases within the timeout
            timeFieldStrategy=["createdTimestamp"],
            customerID=[customer["id"]],
            tag=[{"key": "case-autocreate-key", "values": [key]}],
            # Tags are OR-ed together, we want to AND them
            subCriteria=[{
                "required": True,
                "tag": [{"key": "case-autocreate-group", "values": [group]}]
            }]
        )["data"]

        # There should only be one case within the timeout for a key-group-customer pair!
        return cases[0] if cases else None

    def _create_case(customer: dict, group: str, description: str, data: dict):
        """Creates a new case and adds tags to it.

        :param customer: The customer to create the case for.
        :param group: The group that the case is created from. Used for tagging and the title.
        :param description: Description of the case
        :param data: The data of the event. Used for the title.
        """
        case = create_case(
            customerID=customer["id"],
            service=case_service,
            category=case_category,
            type=case_type,
            priority=case_priority,
            status=case_status if not internal_case else "pendingSoc",
            notification={"skipEmail": skip_notifications, "skipSMS": skip_notifications},
            publish=(not internal_case),

            subject=case_title.format(group=group, **data),
            description=description
        )["data"]
        add_case_tag(
            caseID=case["id"],
            tags=[
                {"key": "case-autocreate-key", "value": key},
                {"key": "case-autocreate-group", "value": group}
            ]
        )

        return case

    def _event_accociator(case_id: int, events: list):
        """Associates the events to the case"""
        update_events(
            eventIdentifiers=[event["id"] for event in events],
            update={
                "comment": "Automatically assessed by cases autocreate (Key: {})".format(key),
                "associateToCase": case_id,
            }
        )

    if dry:
        log.info("--- Running in DRY mode! No data will be committed. ---")

    data = json.load(data)  # Input is a file, so we'll have to parse it.
    log.info("Received {} events".format(len(data)))

    data = sort_input(data, sort_by)

    cases = set()  # For statistics print when finished
    for customer, group, event in group_data(data, group_by):
        case = put_data_in_case(
            data=event,
            customer=customer,
            group=group,
            find_existing_case=_existing_case,
            create_description=_create_description,
            create_comment=_add_comment if not dry else lambda *a, **kw: None,
            create_case=_create_case if not dry else lambda *a, **kw: {"id": "DRY CASE"},
            event_accociator=_event_accociator if not dry else lambda *a, **kw: None,
            set_initial_comment=initial_internal_comment
        )
        cases.add((customer["shortName"], group, case["id"]))

    print(
        "Analyzed {data_amount} events, and associated them with {case_amount} cases.\n\t{stats}"
        .format(
            data_amount=len(data),
            case_amount=len(cases),
            stats="\n\t".join(
                "#{} - {} - {}".format(case, customer, group)
                for customer, group, case in cases
            )
        )
    )
