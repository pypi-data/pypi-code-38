# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from json import loads
from logging import getLogger

logger = getLogger(__name__)


def schema_adapter(registry, body, schema=None, **kwargs):
    try:
        schema.context['registry'] = registry
        res = schema.load(loads(body))
        logger.info(
            "[schema_adapter] Deserialize body=%r with schema=%r: %r",
            body, schema, res)
        return res
    except Exception as e:
        logger.exception(
            "[schema_adapter] Failed to deserialize body=%r with schema=%r: "
            "%r", body, schema, str(e))
        raise
