# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation PIDs."""

CIRCULATION_LOAN_PID_TYPE = 'loanid'
"""Persistent Identifier for Loans."""

CIRCULATION_LOAN_MINTER = 'loanid'
"""Minter PID for Loans."""

CIRCULATION_LOAN_FETCHER = 'loanid'
"""Fetcher PID for Loans."""

_LOANID_CONVERTER = 'pid(loanid,record_class="invenio_circulation.api:Loan")'
"""Loan PID url converter."""
