#! /usr/bin/env python
"Generate Teradata GRANT DCL statements using DBC information"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016, Paresh Adhia"
__license__ = "GPL"

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import OrderedDict
from itertools import groupby
from .util import * # pylint: disable=locally-disabled, wildcard-import, unused-wildcard-import
from ..util import load_json

class DBObj:
	"Database objects with grants"
	def __init__(self, db, tb):
		self.db, self.tb = db, None if tb == 'All' else tb
		self.grants = OrderedDict()

	def __str__(self):
		return "{}.{}".format(self.db, self.tb) if self.tb else self.db

class Grantee:
	"A grantee"
	def __init__(self, user, all=None, withopt=None):
		self.user, self.all, self.withopt = user, all, withopt

	@property
	def isDefault(self):
		return self.all is None and self.user == 'Default'

	def __str__(self):
		return  \
			('All ' if self.all == 'Y' else '') + \
			mkstr(self.user) + \
			{'G':' With Grant Option', 'A': ' With Admin Option', 'N':' With Null Password'}.get(self.withopt, '')

class Grant:
	"A grantor"
	_collation = ['Select', 'Insert', 'Update', 'Delete', 'Execute', 'Execute Procedure', 'Execute Function', 'Statistics',
			'Table', 'View', 'Macro', 'Procedure', 'Function', 'Trigger']

	def __init__(self, grantees, privs, objects=None, revoke=False):
		self.g, self.p, self.o, self.cmd = grantees, privs, objects or [], 'Revoke' if revoke else 'Grant'

	def __str__(self):
		def coalesce(orig):
			"""Coalesce Create/Drop pairs of privileges"""
			def _match(p):
				if p.startswith('Create ') and 'Drop ' + p[7:] in orig:
					return p[7:]
				if p.startswith('Drop ') and 'Create ' + p[5:] in orig:
					return None
				return p
			return (p for p in (_match(p) for p in orig) if p)

		def order(privs):
			return sorted(privs, key=lambda p: self._collation.index(p) if p in self._collation else 99)

		dcl = self.cmd + ' ' + mkstr(order(coalesce(self.p)))

		if self.o:
			dcl += ' On ' + mkstr(self.o)

		if self.g.isDefault:
			dcl += ' As Default'
		else:
			dcl += (' To ' if self.cmd == 'Grant' else ' From ') + mkstr(self.g)

		return dcl + ';'

def mkstr(obj):
	if isinstance(obj, list):
		return ', '.join([str(o) for o in obj])
	return str(obj)

_priv_name = load_json('priv.json')
def priv(code):
	try:
		if len(code) == 1: # https://github.com/Teradata/PyTd/issues/52
			code += ' '
		return _priv_name[code]
	except KeyError:
		return 'Unknown ({})'.format(code)

def add_args(p):
	p.add_argument("filter", metavar='GRANTEE', nargs='+', help="Teradata User or Role")

def genddl(args):
	from itertools import chain
	global pred

	pred = mk_pred(args.filter)

	return chain(obj_priv(), mon_priv(), logon_priv(), role_priv(), zone_priv(), proxy_priv())

def obj_priv():
	sql = """\
SELECT R.DatabaseName
	, R.TableName

	, R.UserName
	, R.AllnessFlag
	, R.GrantAuthority

	, R.AccessRight

FROM {dbc.AllRightsV} R

JOIN {dbc.DatabasesV} D    ON D.DatabaseName = R.DatabaseName
LEFT Join {dbc.TablesV} T  ON T.DatabaseName = R.DatabaseName AND T.TableName = R.TableName

WHERE R.UserName {0}
	AND R.DatabaseName <> 'PUBLIC'
	AND (R.UserName <> Coalesce(T.CreatorName, D.CreatorName) OR AllnessFlag = 'Y')
	AND (R.DatabaseName <> R.UserName OR R.TableName <> 'All')

UNION ALL

SELECT DatabaseName
	, TableName

	, RoleName
	, 'N' AS AllnessFlag
	, 'N' AS GrantAuthority

	, AccessRight

FROM {dbc.AllRoleRightsV} R

WHERE RoleName {0}
	AND DatabaseName <> 'PUBLIC'

ORDER BY 1,2,3,4,5,6""".format(pred, dbc=dbc)

	for (db, tb), row in groupby(execsql(sql, 'Objects Grants SQL'), key=lambda r: tuple(r[0:2])):
		ob = DBObj(db, tb)
		for (u, a, g), acl2 in groupby(row, key=lambda r: tuple(r[2:5])):
			yield Grant(Grantee(u, all=a, withopt={'Y':'G'}.get(g)), [priv(p[5]) for p in acl2], ob)

def mon_priv():
	sql = """\
SELECT R.UserName
	, R.AllnessFlag
	, R.GrantAuthority
	, R.AccessRight

FROM {dbc.AllRightsV} R

WHERE R.UserName {}
	AND R.DatabaseName = 'PUBLIC'

ORDER BY 1,2,3,4""".format(pred, dbc=dbc)

	for (u, a, g), row in groupby(execsql(sql, 'Monitor Grants SQL'), key=lambda r: tuple(r[0:3])):
		yield Grant(Grantee(u, all=a, withopt={'Y':'G'}.get(g)), [priv(p[3]) for p in row])


def logon_priv():
	"logon privileges"
	sql = """\
SELECT LogicalHostID
     , LogonStatus
     , NullPassword
     , UserName

FROM {dbc.LogonRulesV}
WHERE UserName {}

ORDER BY 1,2,3""".format(pred, dbc=dbc)

	for host, row in groupby(execsql(sql, 'Logon Grants SQL'), key=lambda r: r[0]):
		for (s, n), row2 in groupby(row, key=lambda r: (r[1], r[2])):
			grantees = Grantee([r[3] for r in row2], withopt={'T': 'N'}.get(n))
			yield Grant(grantees, 'Logon', objects='All' if host == 1024 else str(host), revoke=s == 'R')


def role_priv():
	"role privileges"
	sql = """\
SELECT Grantee
     , WithAdmin
     , RoleName

FROM {dbc.RoleMembersV} M
WHERE Grantee {}

ORDER BY 1,2""".format(pred, dbc=dbc)

	for grantee, grp1 in groupby(execsql(sql, 'Role Grants SQL'), key=lambda r: r[0]):
		for withadm, grp2 in groupby(grp1, key=lambda r: r[1]):
			yield Grant(Grantee(grantee, withopt={'Y':'A'}.get(withadm)), [r[2] for r in grp2])

def proxy_priv():
	sql = f"""\
SELECT TrustUser
	, ProxyUserType
	, TrustOnly
	, ProfileName
	, WithoutRole
	, ProxyRole1
	, ProxyRole2
	, ProxyRole3
	, ProxyRole4
	, ProxyRole5
	, ProxyRole6
	, ProxyRole7
	, ProxyRole8
	, ProxyRole9
	, ProxyRole10
	, ProxyRole11
	, ProxyRole12
	, ProxyRole13
	, ProxyRole14
	, ProxyRole15
	, ProxyUser
FROM {dbc.ConnectRulesV} C
WHERE TrustUser {pred}
	   AND ProxyUser <> ''
ORDER BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21"""

	for key, grp in groupby(execsql(sql, 'Zone CT SQL'), key=lambda r: tuple(r[:-1])):
		trust, ptype, only, prof, norole = key[:5]
		roles = mkstr([role for role in key[5:] if role])
		proxies = mkstr([row[-1] for row in grp])

		dcl = 'Grant Connect Through ' + trust
		if trust == 'Y':
			dcl += ' With Trust Only'
		dcl += ' To'
		if ptype == 'A':
			dcl += ' '+proxies
			if roles:
				dcl += ' With Role '+roles
			if prof:
				dcl += ' With Profile '+prof
		else:
			dcl += ' Permanent '+proxies
			if norole == 'Y':
				dcl += ' Without Role'
			else:
				dcl += ' With Role '+roles

		yield dcl+';'

def zone_priv():
	if dbc.version < "15.10":
		return

	sql = f"""\
SELECT GuestName
     , ZoneName
FROM {dbc.ZoneGuestsV} Z
WHERE GuestName {pred}
ORDER BY 1,2"""

	for guest, zones in groupby(execsql(sql, 'Zone Grants SQL'), key=lambda r: r[0]):
		yield 'Grant Zone {} To {};'.format(', '.join([z for g, z in zones]), guest)

def main(args=None):
	"command-line entry-point"
	import sys
	return enter(sys.modules[__name__], args)
