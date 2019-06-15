#! /usr/bin/env python
"Generate DDL for Teradata Profiles using DBC information"

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

class Profile:
	"Teradata Profile"
	def __init__(self, *opts):
		self.name, defacct, self.defdb, self.spool, self.temp, self.expire, self.pwmin, \
			self.pwmax, self.pwdig, self.pwspec, self.pwwords, self.attempts, self.lockexp, \
			self.reuse, self.qb, self.qbdef, self.comm = opts
		self.accts = []
		if defacct:
			self.accts.append(defacct)

	def ddl(self, gen_defaults=False):
		def toint(v):
			return None if v is None else int(v)

		opts = [Opt(o, v) for o, v in [
			('Account',            quote(self.accts)),
			('Default Database',   self.defdb),
			('Spool',              toint(self.spool)),
			('Temporary',          toint(self.temp)),
			('Query_Band',         quote(self.qb))
		] if v is not None]

		pw_opts = [Opt(o, v) for o, v in [
			('Expire',             self.expire),
			('MinChar',            self.pwmin),
			('MaxChar',            self.pwmax),
			('Digits',             quote(self.pwdig)),
			('SpecChar',           quote(self.pwspec)),
			('RestrictWords',      quote(self.pwwords)),
			('MaxLogonAttempts',   self.attempts),
			('LockedUserExpire',   self.lockexp),
			('Reuse',              self.reuse)
		] if v is not None]

		if pw_opts:
			opts.append(Opt('Password', f'({optstr(pw_opts)})'))

		cmd = 'Create Profile ' + self.name
		if opts:
			cmd += ' As ' + optstr(opts)

		return cmd+';'

	def comment(self):
		"return comment string if available"
		if self.comm:
			return "Comment On Profile {} As {};".format(self.name, quote(self.comm))

def add_args(p):
	"Add arguments to global Argparser"
	p.add_argument("filter", metavar='PROFILE', default=['%'], nargs='*', help="Teradata profile name")

def genddl(args):
	"generate DDL"
	sql = f"""\
SELECT ProfileName
	, DefaultAccount
	, DefaultDB
	, SpoolSpace
	, TempSpace
	, ExpirePassword
	, PasswordMinChar
	, PasswordMaxChar
	, PasswordDigits
	, PasswordSpecChar
	, PasswordRestrictWords
	, MaxLogonAttempts
	, LockedUserExpire
	, PasswordReuse
	, Queryband
	, QuerybandDefault
	, CommentString
FROM {dbc.ProfileInfoV} P
WHERE ProfileName {mk_pred(args.filter)}"""

	profs = OrderedDict((row[0], Profile(*row)) for row in execsql(sql, 'ProfileInfo SQL'))

	sql = f"""\
SELECT A.UserName
	, A.AccountName

FROM {dbc.AccountInfoV} A
JOIN {dbc.ProfileInfoV} P ON P.ProfileName = A.UserName AND P.DefaultAccount <> A.AccountName

WHERE UserOrProfile = 'Profile'
	AND UserName {mk_pred(args.filter)}"""

	for p,rows in groupby(execsql(sql, 'Accounts for Profile SQL'), key=lambda r: r[0]):
		profs[p].accts.extend([a for p, a in rows])

	for p in profs.values():
		yield p.ddl()
		if p.comm:
			yield p.comment()

def main(args=None):
	"Script entry-point"
	import sys
	return enter(sys.modules[__name__], args)
