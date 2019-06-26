"""forgot password schema

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

from yams.buildobjs import EntityType, Datetime, String, RelationDefinition

class Fpasswd(EntityType):
    # Fpasswd handled by internal hooks, simply let managers removing manually
    # if desired
    __permissions__ = {'read':   ('managers',),
                       'add':    (),
                       'delete': ('managers',),
                       'update': (),
                       }
    revocation_id = String(required=True, unique=True)
    revocation_date = Datetime(required=True)

class has_fpasswd(RelationDefinition):
    __permissions__ = {'read': ('managers',),
                       'add':    (),
                       'delete': ('managers',),
                       }
    subject = 'CWUser'
    object = 'Fpasswd'
    cardinality = '*1'
