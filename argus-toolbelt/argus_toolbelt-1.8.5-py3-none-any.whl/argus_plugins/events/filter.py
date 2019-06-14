import difflib
import json
from collections import namedtuple

from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_cli.utils import time, formatting
from argus_api.api.eventfilters.v1 import filter as filter_api
from argus_plugins import argus_cli_module

KIBANA_HISTORY_URL = "http://osl-analyze2:5601/#/discover?_g=(refreshInterval:(display:Off,pause:!f,section:0,value:0),time:(from:now-14d,mode:quick,to:now))&_a=(columns:!(_source),index:'aggrevent-*',interval:auto,query:(query_string:(analyze_wildcard:!t,query:'properties.argus_created_by_filterid:%s')),sort:!(startTime,desc))]) "
ARGUS_HISTORY_URL = "https://argusweb.mnemonic.no/web/secure/registration/eventFilterEdit.htm?id=%s"

FILTER_TYPES = {
    "annotation": ["CustomEventAnnotationFilter"],
    "analysis": ["CustomEventAnalysisFilter"],
    "match": ["IPAttackEventMatchFilter", "NIDSEventMatchFilter", "AggregatedIPAttackEventMatchFilter"],
}

REVISION_FIELDS = (
    "preStatement1",
    "preStatement2",
    "statementCode",
    "triggerCode",
)
UNWANTED_JSON_DIFF_FIELDS = (
    "lastUpdatedTimestamp", "lastUpdatedByUser", "revision", "masterID", "createdTimestamp", "flags",
    "statementCode", "triggerCode", "enabled", "preStatement1", "preStatement2", "index"
)

Filter = namedtuple(
    "Filter",
    ["id", "customer", "updated_by", "description", "enabled", "updated", "difference"]
)


def jira_output(data: list):
    """Creates output for JIRA"""
    out = ""

    for filt in data:
        if not filt.enabled:
            filter_status = "Disabled filter"
        elif filt.updated:
            filter_status = "Updated filter"
        else:
            filter_status = "New filter"

        filter_info = "%s ([Argus|%s]) ([History|%s})" % \
                      (filt.id, ARGUS_HISTORY_URL % filt.id, KIBANA_HISTORY_URL % filt.id)

        out +=\
            "h2. %s: %s\n" \
            "*Filter:* %s\n" \
            "*Customer:* %s\n" \
            "*Updated by:* %s\n" % \
            (filter_status, filt.description, filt.id, filt.customer, filt.updated_by)

        for key, diff in filt.difference.items():
            out += "%s diff:\n{code}%s{code}" % (key, diff)

    return out


OUTPUT_METHODS = {
    "csv": lambda headers, data: formatting.csv(data, headers=headers),
    "jira": lambda headers, data: jira_output(data),  # Creates a consistent "API" for output methods
}


def _diff(left: str, right: str, context: int = 0) -> str:
    """Wrapper around difflib.unified_diff"""
    return "".join(
        difflib.unified_diff(left.splitlines(True), right.splitlines(True), n=context)
    )


def _json_diff(left: dict, right: dict, context: int = 0) -> str:
    """Diffs a filter's JSON, and filters out some fields we don't want"""
    for field in UNWANTED_JSON_DIFF_FIELDS:
        if field in left:
            del left[field]
        if field in right:
            del right[field]

    return _diff(
        json.dumps(left, sort_keys=True, indent=4),
        json.dumps(right, sort_keys=True, indent=4),
        context
    )


def difference(original: dict, revision: dict, context: int) -> dict:
    """Finds differences in a set of fields and the JSON itself"""
    diffs = {}

    for field in REVISION_FIELDS:
        if (field in original and field in revision) and (original[field] and revision[field]):
            diff = _diff(original[field], revision[field])
            diffs[field] = diff

    diffs["json"] = _json_diff(original, revision)
    return diffs


def revision_before(latest_revision: int, revisions: list) -> dict:
    """Finds the revision before the current revision"""
    for revision in reversed(revisions):
        if revision["revision"] < latest_revision:
            return revision
    raise ValueError("No earlier revision found")


def parse_filter(filt: dict, context: int) -> Filter:
    """Parses a filter to a more human readable format
    :param context:
    """
    enabled = filt["enabled"]
    updated = filt["revision"] != 1  # Revision 1 means this is the first revision
    diff = {}

    if updated and enabled:
        log.debug("Getting latest revision for filter %s" % filt["id"])
        revision = revision_before(
            filt["revision"],
            filter_api.revisions(id=filt["id"])["data"])
        diff = difference(filt, revision, context)

    customer = filt["customer"]["shortName"] if filt["customer"] else "All customers"
    user = filt["lastUpdatedByUser"]["userName"] if "lastUpdatedByUser" in filt else "N/A"
    return Filter(filt["id"], customer, user, filt["description"],
                  enabled, updated, diff)


def filter_filters(key: str, filters: list) -> list:
    """Filter away unwanted filters that are not in the given key

    The event-filter endpoint is old and doesn't provide a good way of doing this.
    """
    for filt in filters:
        if filt["type"] not in FILTER_TYPES[key]:
            filters.remove(filt)

    return filters


@register_command(extending=("eventfilter"), module=argus_cli_module)
def get_updated(start: time.date_or_relative, end: time.date_or_relative,
                types: FILTER_TYPES.keys(),
                context: int = 0,
                out: OUTPUT_METHODS.keys() = "jira"):
    """Gets updated, new or deleted event-filters from Argus

    :param start: Start time of the search
    :param end: End time of the search
    :param types: The type of filter to search for
    :param context: Amount of lines of context to display in diff
    :param out: The desired output format
    """
    log.info("Fetching event-filters...")
    filters = filter_api.search(
        limit=0,
        startTimestamp=start, endTimestamp=end,
    )["data"]

    log.info("Filtering event_filters...")
    filters = filter_filters(types, filters)

    log.info("Parsing event-filters...")
    parsed = []
    for filt in filters:
        log.debug("Parsing filter with ID %d" % (filt["id"]))
        parsed.append(parse_filter(filt, context))

    log.info("")
    print(OUTPUT_METHODS[out](list(Filter._fields), parsed))
