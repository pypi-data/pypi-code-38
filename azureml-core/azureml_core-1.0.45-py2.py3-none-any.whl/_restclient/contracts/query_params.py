# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""helper to create contracts of query_params"""
from ..models.query_params_dto import QueryParamsDto


def create_query_params(filter=None, orderby=None, top=None):
    return QueryParamsDto(filter=filter, continuation_token=None, orderby=orderby, top=top)
