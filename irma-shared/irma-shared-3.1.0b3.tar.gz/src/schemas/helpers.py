#
# Copyright (c) 2013-2019 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

from datetime import datetime, timezone


def timestamp_to_date(timestamp, tz=None):
    date = datetime.fromtimestamp(int(timestamp), tz)
    return date.strftime('%Y-%m-%d %H:%M:%S')


def timestamp_to_utcdate(timestamp):
    return timestamp_to_date(timestamp, tz=timezone.utc)
