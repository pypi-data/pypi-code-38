# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-Circulation example application.

SPHINX-START

First install Invenio-Circulation, setup the application and load
fixture data by running:

.. code-block:: console

   $ pip install -e .[all]
   $ cd examples
   $ ./app-setup.sh
   $ FLASK_APP=app.py flask fixtures loans

Next, start the development server:

.. code-block:: console

   $ export FLASK_APP=app.py FLASK_ENV=development
   $ flask run

and open the example application in your browser:

.. code-block:: console

    $ open http://127.0.0.1:5000/circulation/loan/1

To reset the example application run:

.. code-block:: console

    $ ./app-teardown.sh

SPHINX-END
"""

from __future__ import absolute_import, print_function

import os
import uuid

import click
from flask import Flask
from invenio_db import db
from invenio_db.ext import InvenioDB
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_pidstore.ext import InvenioPIDStore
from invenio_records.ext import InvenioRecords
from invenio_records_rest.ext import InvenioRecordsREST
from invenio_records_rest.utils import PIDConverter
from invenio_records_rest.views import create_blueprint_from_app
from invenio_rest import InvenioREST
from invenio_search.ext import InvenioSearch

from invenio_circulation.api import Loan
from invenio_circulation.config import CIRCULATION_REST_ENDPOINTS
from invenio_circulation.ext import InvenioCirculation
from invenio_circulation.pidstore.minters import loan_pid_minter
from invenio_circulation.views import create_loan_actions_blueprint, \
    create_loan_for_item_blueprint, create_loan_replace_item_blueprint

# Create Flask application
app = Flask(__name__)
app.config.update(
    SERVER_NAME="localhost:5000",
    SECRET_KEY="SECRET_KEY",
    # No permission checking
    RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY=None,
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    SQLALCHEMY_DATABASE_URI=os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///app.db"
    ),
)
app.config["RECORDS_REST_ENDPOINTS"] = CIRCULATION_REST_ENDPOINTS
app.url_map.converters["pid"] = PIDConverter
InvenioDB(app)
InvenioRecords(app)
InvenioREST(app)
InvenioRecordsREST(app)
InvenioPIDStore(app)
InvenioSearch(app)
InvenioJSONSchemas(app)
InvenioCirculation(app)
app.register_blueprint(create_blueprint_from_app(app))
app.register_blueprint(create_loan_actions_blueprint(app))
app.register_blueprint(create_loan_for_item_blueprint(app))
app.register_blueprint(create_loan_replace_item_blueprint(app))


@app.cli.group()
def fixtures():
    """Command for working with test data."""


@fixtures.command()
def loans():
    """Load test data fixture."""
    record_uuid = uuid.uuid4()
    new_loan = {}
    pid = loan_pid_minter(record_uuid, data=new_loan)
    Loan.create(data=new_loan, id_=record_uuid)
    db.session.commit()
    click.secho("Loan #{} created.".format(pid.pid_value), fg="green")
