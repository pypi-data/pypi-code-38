from argus_api.api.cases.v2.case import advanced_case_search, update_case, close_case

from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_cli.utils.time import date_or_relative
from argus_plugins import argus_cli_module
from argus_plugins.cases.utils import get_customer_id, CASE_TYPES, PRIORITIES, STATUSES, KEYWORD_FIELDS

TIME_FIELD_STRATEGIES = ["createdTimestamp", "lastUpdatedTimestamp", "closedTimestamp", "publishedTimestamp", "all" ]

@register_command(extending="cases", module=argus_cli_module)
def change_status(
        start: date_or_relative,
        end: date_or_relative,
        new_status: STATUSES,
        reason: str = None,
        keyword: str = None,
        keyword_field: KEYWORD_FIELDS = None,
        customer: get_customer_id = None,
        exclude_customer: get_customer_id = None,
        type: CASE_TYPES = None,
        service: str = None,
        category: str = None,
        status: STATUSES = None,
        priority: PRIORITIES = None,
        time_field_strategy: TIME_FIELD_STRATEGIES = "lastUpdatedTimestamp",
        dry: bool = False
):
    """This command can be used to close multiple cases in one go, based on a set of parameters.

    :param start: Time to start filtering the case from (ISO8601 format or relative time)
    :param end: Time to end filtering the case from (ISO8601 format or relative time)
    :param new_status: The new status of the case
    :param reason: The reasoning for the change (If none - it will post "Changing from <old> to <new>")
    :param list keyword: Keyword(s) to filter by. If using a sentence, remember to encapsulate with quotes.
    :param list keyword_field: The field(s) to filter by
    :param list customer: Customers to include in the search
    :param list exclude_customer: Customers to include in the search
    :param list type: Case type to search for
    :param list service: Case service to search for
    :param list category: Case subcategory type to search for
    :param list status: Status to search for
    :param list priority: Priority to search for
    :param time_field_strategy: The timestamp to search by
    :param dry: Makes the changes NOT commit to the server.
    """
    if dry:
        log.info("Dry-run - No changes will be committed")

    sub_criteria = []
    if exclude_customer:
        # TODO: This isn't a good solution in the long run. Should create common handling for these kind of arguments.
        sub_criteria.append({"exclude": True, "customerID": exclude_customer})

    log.debug("Fetching cases...")
    cases = advanced_case_search(
        limit=0,
        startTimestamp=start, endTimestamp=end, timeFieldStrategy=time_field_strategy,
        keywords=keyword, keywordFieldStrategy=keyword_field,
        priority=priority, status=status, type=type, category=category, service=service,
        customerID=customer, subCriteria=sub_criteria
    )["data"]

    log.debug("Updating {num_cases} cases.".format(num_cases=len(cases)))
    for case in cases:
        print("Updating case #{case[id]} from {case[status]} to {new_status}".format(case=case, new_status=new_status))

        if dry:
            continue

        if new_status == "closed":
            close_case(
                case["id"],
                comment=reason or "Changing status from \"{}\" to \"{}\"".format(case["status"], new_status)
            )
        else:
            update_case(
                case["id"],
                status=new_status,
                comment=reason or "Changing status from \"{}\" to \"{}\"".format(case["status"], new_status)
            )
