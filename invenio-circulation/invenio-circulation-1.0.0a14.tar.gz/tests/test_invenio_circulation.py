# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

import json

from flask import url_for


def test_version():
    """Test version import."""
    from invenio_circulation import __version__

    assert __version__


def test_rest_permissions(app, json_headers):
    """Test rest permissions config."""
    with app.test_client() as client:
        url = url_for("invenio_records_rest.loanid_list")
        res = client.post(
            url, data=json.dumps({}), headers=json_headers
        )
        assert res.status_code == 201
