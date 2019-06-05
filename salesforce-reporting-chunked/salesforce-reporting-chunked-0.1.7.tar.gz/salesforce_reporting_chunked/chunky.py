# -*- coding: utf-8 -*-
"""
Chunky
======

Uses salesforce_reporting module to extract chunked data by use of a "Time Frame" column in sales force.
"""
import re
import datetime
import requests
from salesforce_reporting.login import Connection

BASE_URL = "https://{instance}/services/data/{api_version}/analytics"


class Chunky(Connection):
    """
    Uses salesforce_reporting module to extract chunked data by use of a "Time Frame" column in sales force. Requires a Salesforce account and security token.

    Args:
        username (str): Salesforce username
        password (str): Salesforce password
        security_token (str):   Salesforce security token
        sandbox (bool): Run report in Salesforce sandbox (default False)
        api_version (str):  Salesforce reporting API version (default v29.0")

    Example:
        >>> from salesforce_reporting_chunked import chunk_report_by_date
        >>> CONFIG = {
        ...     "security_token": "REPLACE WITH YOUR TOKEN",
        ...     "username": "REPLACE WITH YOUR USERNAME",
        ...     "password": "REPLACE WITH YOUR PASSWORD",
        ...     "api_version": "v38.0",
        ... }
        >>> FIELDNAMES = [
        ...     "First Name",
        ...     "Last Name",
        ...     "Date Column", # this is the magic column used for chunking.
        ...     "Corhuscorrated Plethanth",
        ...     "Other Column",
        ... ]
        >>> REPORT_ID = "YOURREPORTID"
        >>> data = chunk_report_by_date(
        ...     CONFIG,
        ...     REPORT_ID,
        ...     FIELDNAMES,
        ...     date_fieldname="Date Column",
        ...     start_date="2018-01-01",
        ...     start_date="2019-01-31",
        ... )
        >>> next(data)
        OrderedDict([('First Name', 'Fred'),('Last Name', 'Garvin'),('DATE_COLUMN_NAME', '2018-01-01'),('Corhuscorrated Plethanth', True),('Other Column': 'Yep. Another')])
    """

    def __init__(
        self,
        username=None,
        password=None,
        security_token=None,
        sandbox=False,
        api_version="v29.0",
    ):
        self.username = username
        self.password = password
        self.security_token = security_token
        self.sandbox = sandbox
        self.api_version = api_version

        self.login_details = self.login(
            self.username, self.password, self.security_token
        )
        self.token = self.login_details["oauth"]
        self.instance = self.login_details["instance"]
        self.headers = {"Authorization": "OAuth {}".format(self.token)}
        self.base_url = BASE_URL.format(
            instance=self.instance, api_version=self.api_version
        )

    def _get_report_filtered(self, url, filters=None, standard_date_filter=None):
        """
        Filter report on filters and/or standard_date_filter.

        Args:
            url (str)   Well-formed Salesforce API endpoint.
            filters (list)  List of dictionaries in Salesforce "reportFilters" format.
            standard_date_filter (dict) Salesforce "standardDateFilter" dictionary. 
        Returns:
            requests.post().json() (dict)   Salesforce reports object.

        Example:
            >>> # standard_date_filter JSON object as described in https://developer.salesforce.com/docs/atlas.en-us.api_analytics.meta/api_analytics/sforce_analytics_rest_api_getbasic_reportmetadata.htm
            >>> {
            ...     'column': 'foo.TheDate',
            ...     'durationValue': 'CUSTOM',
            ...     'endDate': '2019-01-01',
            ...     'startDate': '2019-01-01',
            ... }
        """

        # metadata for next request. We modify it by adding reportFilters
        # and/or standardDateFilter
        metadata_url = url.split("?")[0]
        metadata = self._get_metadata(metadata_url)

        if filters:
            for report_filter in filters:
                metadata["reportMetadata"]["reportFilters"].append(report_filter)

        if standard_date_filter:
            standard_date_filter = _sdf_fieldname_from_label(
                metadata, standard_date_filter
            )
            metadata["reportMetadata"]["standardDateFilter"] = standard_date_filter
        return requests.post(url, headers=self.headers, json=metadata).json()

    def get_daterange_chunked_report(
        self,
        report_id,
        filters=None,
        details=True,
        date_fieldname=None,
        start_date=None,
        end_date=None,
        day_increment=1,
    ):
        """
        Get chunked report by daterange. Anything more than 1 may result in unforseen results, so think it through.

        Args:
            report_id (str):    Final portion of Salesforce API endpoint for report.
            filters (list): List of dictionaries in Salesforce "reportFilters" format. {field: filter}, optional.
            details (bool): Whether or not detail rows are included in report output, default True
            date_fieldname (str):   Column name of sortable date field from Salesforce report page.
            start_date (str):   iso-formatted date string. ex: "2019-01-01".
            end_date (str): iso-formatted date string. ex: "2019-01-01".
            day_increment (int):    Number of days to "chunk" report by. Default 1.

        Yields:
            row (OrderedDict): report row

        Example:
            >>> REPORT_ID = "abc123youandmegirl"
            >>> data = get_daterange_chunked_report(REPORT_ID, date_fieldname="The_Date", start_date="2019-06-01", end_date="2019-06-30")
            >>> next(data)
        """

        # iso formatted date YYYY-MM-DD
        date_rex = "(\d{4})-(\d{2})-(\d{2})"
        assert re.match(date_rex, start_date)
        assert re.match(date_rex, end_date)
        assert date_fieldname

        increment = datetime.timedelta(days=day_increment)
        start_date = datetime.date(*[int(_) for _ in start_date.split("-")])
        end_date = datetime.date(*[int(_) for _ in end_date.split("-")])

        # loop through dates by increment
        while start_date <= end_date:
            standard_date_filter = {
                "column": date_fieldname,
                "durationValue": "CUSTOM",
                "endDate": start_date.isoformat(),
                "startDate": start_date.isoformat(),
            }

            start_date = start_date + increment

            yield self.get_report(
                report_id,
                filters=filters,
                standard_date_filter=standard_date_filter,
                details=details,
            )

    def get_report(
        self, report_id, filters=None, standard_date_filter=None, details=True
    ):
        """
        Return the full JSON content of a Salesforce report, with or without filters.

        Args:
            report_id (str): Final portion of Salesforce API endpoint for report.
            filters (list):  List of dictionaries in Salesforce "reportFilters" format. {field: filter}, optional.
            details (bool):  Whether or not detail rows are included in report output, default True

        Returns:
            report (json):  Salesforce report
        """
        details = "true" if details else "false"
        url = "{}/reports/{}?includeDetails={}".format(
            self.base_url, report_id, details
        )

        if any([filters, standard_date_filter]):
            return self._get_report_filtered(url, filters, standard_date_filter)
        else:
            return self._get_report_all(url)


def _sdf_fieldname_from_label(metadata, standard_date_filter):
    """
    Update the "column" value of standard_date_filter dictionary with
    internal date-sortable fieldname.

    Args:
        metadata (dict) metadata returned by Salesforce API
        standard_date_filter (dict) Salesforce API date filter 
    Returns:
        standard_date_filter (dict)
    Example:
        >>> standard_date_filter = {
        ...     "column": "CREATED_DATE",
        ...     "durationValue": "CUSTOM",
        ...     "endDate": "2019-01-01",
        ...     "startDate": "2019-06-30",
        ... }
        >>> metadata = {
        ...     "reportExtendedMetadata": {
        ...         "detailColumnInfo": {
        ...             "weird_internal_name___c": {
        ...                 "label": "CREATED_DATE",
        ...                 "dataType": "string",
        ...             }
        ...         }
        ...     }
        ... }
        >>> _sdf_fieldname_from_label(metadata, standard_date_filter)
        {'column': 'weird_internal_name___c', 'durationValue': 'CUSTOM', 'endDate': '2019-01-01', 'startDate': '2019-06-30'}
    """

    # column is human-readable name, ex: "Next Renewal Date"
    column = standard_date_filter["column"]

    # column names are puked out in this object
    detail_column_info = metadata["reportExtendedMetadata"]["detailColumnInfo"]

    # we need the fieldname used internally by API, rather than
    # human-readable fieldname in the reports interface.
    # ex: Foobar__Batbaz__c.Foobar__TransactionDate__c is displayed as
    # TransactionDate in web interface.
    for date_fieldname in detail_column_info.keys():
        if detail_column_info[date_fieldname]["label"] == column:
            standard_date_filter["column"] = date_fieldname
    return standard_date_filter
