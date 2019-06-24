# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation API."""

from datetime import timedelta


def patron_exists(patron_pid):
    """Return True if patron exists, False otherwise."""
    return True


def item_exists(item_pid):
    """Return True if item exists, False otherwise."""
    return True


def document_exists(document_pid):
    """Return True if document exists, False otherwise."""
    return True


def item_can_circulate(item_pid):
    """Return True if the item can circulate, False otherwise."""
    return True


def can_be_requested(loan):
    """Return True if the given record can be requested, False otherwise."""
    return True


# NOTE: Its on purpose `ref` and not `$ref` so it doesn't try to resolve
def item_ref_builder(loan_pid):
    """Return the $ref for item_pid."""
    return {"ref": "{}".format(loan_pid)}


def item_location_retriever(item_pid):
    """Retrieve the location pid of the passed item pid."""
    return ""


def get_default_loan_duration(loan):
    """Return a default loan duration in number of days."""
    return 30


def get_default_extension_duration(loan):
    """Return a default extension duration in number of days."""
    return 30


def get_default_extension_max_count(loan):
    """Return a default extensions max count."""
    return float("inf")


def is_loan_duration_valid(loan):
    """Validate the loan duration."""
    return loan["end_date"] > loan["start_date"] and loan["end_date"] - loan[
        "start_date"
    ] < timedelta(days=60)
