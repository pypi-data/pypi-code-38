'''
Copyright 2019 Jacques Supcik

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

-----------------------------------------------------------------------------
Purpose: Dataclass for organizer
Filename: groople/organizer.py
Created Date: 2019-06-24
Author: Jacques Supcik
-----------------------------------------------------------------------------
'''

import hashlib
import logging
import pickle
import re
from dataclasses import asdict, dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Organizer:
    """ Organizer class """
    id: int
    name: str
    address: str
    phone: str
    email: str
    presence_list_to: str
    presence_list_to_email: str
    activities: set = field(default_factory=set)
    email_list: list = field(default_factory=list)
    email_presence_list: list = field(default_factory=list)

    def fix_id(self):
        m = hashlib.blake2b()
        v = asdict(self)
        del v['id']
        del v['activities']
        del v['email_list']
        del v['email_presence_list']

        m.update(pickle.dumps(v))
        self.id = m.hexdigest()

    def extract_emails(self):

        def splitlist(x):
            email_re = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if x is None:
                return []

            l = re.split(r'[\s;,]+', str(x))
            l = [i for i in l if len(i) > 0]
            res = set()
            for i in l:
                if re.match(email_re, i):
                    res.add(i)
                else:
                    logger.warning("Invalid email : %s", i)

            return sorted(list(res))

        self.email_list = splitlist(self.email)
        self.email_presence_list = splitlist(self.presence_list_to_email)

    def __str__(self):
        return f'{self.name}'
