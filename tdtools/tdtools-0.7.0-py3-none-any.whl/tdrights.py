#! /usr/bin/env python
# -*- coding: utf8 -*-

"Print Teradata access information for databases, roles, users and members"

from tdtools import util

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2017, Paresh Adhia"
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

logger = util.getLogger(__name__)

def main():
	"script entry-point"
	args = getargs()

	names = ','.join(["'"+n+"'" for n in args.name])

	extra = ''
	if args.verbose > 0:
		extra += "\n\t, CrAdm, DrAdm, a.Adm"
		if args.verbose > 1:
			extra += "\n\t, a.Mon, Oth"

	sql = args.sqlgen(names, extra)

	if args.sql:
		print(sql.replace('\t', '    '))
	else:
		with util.cursor(args) as csr:
			csr.execute(sql)
			util.pprint_csr(csr)

def getargs():
	"script run-time options"
	from argparse import ArgumentParser

	# pylint: disable=locally-disabled, bad-whitespace, multiple-statements
	p = ArgumentParser(description = __doc__)

	p.add_argument("name", nargs='+', help="List of database/user/role/member names (default database).")

	g = p.add_mutually_exclusive_group(required=False)
	g.add_argument("-o", "--on",   dest='sqlgen', action='store_const', default=all_rights, const=on_rights,    help="rights granted ON <database>")
	g.add_argument("-t", "--to",   dest='sqlgen', action='store_const', const=to_rights,    help="rights granted TO <user/roles>")
	g.add_argument("-u", "--user", dest='sqlgen', action='store_const', const=user_rights,  help="rights granted TO user including through roles")
	g.add_argument("-m", "--mem",  dest='sqlgen', action='store_const', const=mem_rights,   help="members of roles")

	p.add_argument("--sql", action='store_true', help="print SQL -- don't run it.")
	p.add_argument('-v', '--verbose',  default=0, action='count', help='include verbose access information. Use -vv for more details')

	util.dbconn_args(p)

	return p.parse_args()

def all_rights(db, extras=''):
	return """\
select Coalesce(d.DatabaseName, a.DatabaseName) as "On"
	, ObjectName                                as "Table"
	, TableKind                                 as "T"
	, Coalesce(d.Grantee, a.Grantee)            as "To"
	, Coalesce(d.GranteeKind, a.GranteeKind)    as "U"
	, GrantOpt                                  as "G"

	, DML, Exe, CrObj, DrObj
	{}
from (
	Select cast('R' as Char(1)) GranteeKind,
		RoleName as Grantee,
		cast(NULL as Varchar(128) character set unicode) as DatabaseName
	From dbc.RoleInfoV
	Where RoleName Like Any ({db})

	Union All

	select DBKind,
		DatabaseName,
		cast(NULL as Varchar(128) character set unicode)
	from dbc.DatabasesV
	Where DatabaseName Like Any ({db})

	Union All

	select cast(NULL as Char(1)) as GranteeKind,
		cast(NULL as Varchar(128) character set unicode) as Grantee,
		DatabaseName
	From dbc.DatabasesV
	Where DatabaseName Like Any ({db})
) d
left join (
	{}
) a on a.DatabaseName = d.DatabaseName or a.Grantee = d.Grantee
Order by 1, 2, 5, 4, 6""".format(extras, rights, db=db)

def on_rights(db, extras=''):
	return """\
select d.DatabaseName   as "Database"
	, ObjectName        as "Table"
	, TableKind         as "T"
	, Grantee
	, GranteeKind       as "U"
	, GrantOpt          as "G"

	, DML, Exe, CrObj, DrObj
	{}
from dbc.DatabasesV d
left join (
	{}
) a on a.DatabaseName = d.DatabaseName
Where d.DatabaseName Like Any ({})
Order by d.DatabaseName, ObjectName, GranteeKind, Grantee, GrantOpt""".format(extras, rights, db)

def to_rights(roles, extras=''):
	return """\
select g.Grantee
	, g.GranteeKind  as "U"
	, DatabaseName   as "Database"
	, ObjectName     as "Table"
	, TableKind      as "T"
	, GrantOpt       as "G"

	, DML, Exe, CrObj, DrObj
	 {}
from (select 'R' GranteeKind, RoleName as Grantee from dbc.RoleInfoV union all select DBKind, DatabaseName from dbc.DatabasesV) g
left join (
	{}
) a on a.Grantee = g.Grantee

Where g.Grantee Like Any ({})

Order by g.GranteeKind, g.Grantee, DatabaseName, ObjectName, GrantOpt""".format(extras, rights, roles)

def user_rights(users, extras=''):
	return """\
select u.UserName
	, u.RoleName
	, u.GranteeKind     as "U"
	, a.DatabaseName    as "Database"
	, a.ObjectName      as "Table"
	, a.TableKind       as "T"
	, a.GrantOpt        as "G"

	, a.DML, a.Exe, a.CrObj, a.DrObj
	{}
from (
	{}
) a

join (
	select u.DatabaseName as UserName
		, DatabaseName    as Grantee
		, DBKind          as GranteeKind
		, cast(NULL as varchar(128) character set unicode) as RoleName
	from dbc.DatabasesV u

	union all

	select u.DatabaseName as UserName
		, r1.RoleName     as Grantee
		, 'R'             as GranteeKind
		, r1.RoleName     as RoleName
	from dbc.DatabasesV u
	join dbc.RoleMembersV r1 on r1.Grantee = u.DatabaseName

	union all

	select u.DatabaseName                     as UserName
		, r2.RoleName                         as Grantee
		, 'R'                                 as GranteeKind
		, r1.RoleName || '.' || r2.RoleName   as RoleName
	from dbc.DatabasesV u
	join dbc.RoleMembersV r1 on r1.Grantee = u.DatabaseName
	join dbc.RoleMembersV r2 on r2.Grantee = r1.RoleName
) u on u.Grantee = a.Grantee and u.GranteeKind = a.GranteeKind

Where u.UserName Like Any ({})

Order by u.Grantee, u.GranteeKind, u.RoleName, a.DatabaseName, a.ObjectName, a.GrantOpt""".format(extras, rights, users)

def mem_rights(mems, extras=''):
	return """\
select r1.Grantee, r1.RoleName as "Role"
from dbc.RoleMembersV r1
where r1.Grantee in ({0})

union all

select r1.Grantee, r1.RoleName || '.' || r2.RoleName
from dbc.RoleMembersV r1
join dbc.RoleMembersV r2 on r2.Grantee = r1.RoleName
where r1.Grantee in ({0})

Order by 1,2""".format(mems)

rights = """
	select DatabaseName
		, ObjectName
		, TableKind
		, Grantee
		, GranteeKind

		, GrantOpt

		, SelA || InsA || UpdA || DelA           as DML
		, XMc || XPr || XFn                      as Exe

		, CTb || CVw || CMc || CPr || CFn || CTg as CrObj
		, DTb || DVw || DMc || Dpr || DFn || DTg as DrObj
		, CDb || CUs || CRl || CPf               as CrAdm
		, DDb || DUs || DRl || DPf               as DrAdm

		, IX || St || DP || RS                   as Adm
		, MS || MR || "AS"                       as Mon

		, A_AE || A_AF || A_AP || A_CA || A_CE || A_CP || A_DA || A_GC || A_GD ||
		A_GM || A_NT || A_OD || A_OI || A_OS || A_OU || A_RF || A_RO || A_SA ||
		A_SD || A_SH || A_SR || A_SS || A_TH || A_UM || A_UT || A_UU as Oth

	from (
		select coalesce(r.RoleName, u.DatabaseName)                   as Grantee
			, case when r.RoleName is not NULL then 'R' else u.RowType end  as GranteeKind
			, d.DatabaseName                                          as DatabaseName
			, NULLIF(TVMName,'All')                                   as ObjectName
			, case TVMName when 'All' then 'D' else coalesce(TableKind, 'D') end as TableKind
			, case when WithGrant = 'Y' then 'G' else ' ' end         as GrantOpt

			, max(case AccessRight when 'R'  then 'S' else ' ' end)   as SelA
			, max(case AccessRight when 'I'  then 'I' else ' ' end)   as InsA
			, max(case AccessRight when 'U'  then 'U' else ' ' end)   as UpdA
			, max(case AccessRight when 'D'  then 'D' else ' ' end)   as DelA

			, max(case AccessRight when 'E ' then 'M' else ' ' end)   as XMc
			, max(case AccessRight when 'PE' then 'P' else ' ' end)   as XPr
			, max(case AccessRight when 'EF' then 'F' else ' ' end)   as XFn

			, max(case AccessRight when 'CT' then 'T' else ' ' end)   as CTb
			, max(case AccessRight when 'CV' then 'V' else ' ' end)   as CVw
			, max(case AccessRight when 'CM' then 'M' else ' ' end)   as CMc

			, case when max(case AccessRight when 'OP' then 'O' else ' ' end) <> ''
				then max(case AccessRight when 'OP' then 'O' else ' ' end)
				else max(case AccessRight when 'PC' then 'P' else ' ' end)
			  end                                                     as CPr

			, max(case AccessRight when 'CF' then 'F' else ' ' end)   as CFn
			, max(case AccessRight when 'CG' then 'G' else ' ' end)   as CTg

			, max(case AccessRight when 'CD' then 'D' else ' ' end)   as CDb
			, max(case AccessRight when 'CU' then 'U' else ' ' end)   as CUs
			, max(case AccessRight when 'CR' then 'R' else ' ' end)   as CRl
			, max(case AccessRight when 'CO' then 'P' else ' ' end)   as CPf

			, max(case AccessRight when 'DT' then 'T' else ' ' end)   as DTb
			, max(case AccessRight when 'DV' then 'V' else ' ' end)   as DVw
			, max(case AccessRight when 'DM' then 'M' else ' ' end)   as DMc
			, max(case AccessRight when 'PD' then 'P' else ' ' end)   as DPr
			, max(case AccessRight when 'DF' then 'F' else ' ' end)   as DFn
			, max(case AccessRight when 'DG' then 'G' else ' ' end)   as DTg

			, max(case AccessRight when 'DD' then 'D' else ' ' end)   as DDb
			, max(case AccessRight when 'DU' then 'U' else ' ' end)   as DUs
			, max(case AccessRight when 'DR' then 'R' else ' ' end)   as DRl
			, max(case AccessRight when 'DO' then 'P' else ' ' end)   as DPf

			, max(case AccessRight when 'IX' then 'X' else ' ' end)   as IX
			, max(case AccessRight when 'ST' then 'S' else ' ' end)   as St
			, max(case AccessRight when 'DP' then 'D' else ' ' end)   as DP
			, max(case AccessRight when 'RS' then 'R' else ' ' end)   as RS

			, max(case AccessRight when 'MS' then 'S' else ' ' end)   as MS
			, max(case AccessRight when 'AS' then 'A' else ' ' end)   as "AS"
			, max(case AccessRight when 'MR' then 'R' else ' ' end)   as MR

			, max(case AccessRight when 'AE' then 'AE ' else '' end)  as A_AE
			, max(case AccessRight when 'AF' then 'AF ' else '' end)  as A_AF
			, max(case AccessRight when 'AP' then 'AP ' else '' end)  as A_AP
			, max(case AccessRight when 'CA' then 'CA ' else '' end)  as A_CA
			, max(case AccessRight when 'CE' then 'CE ' else '' end)  as A_CE
			, max(case AccessRight when 'CP' then 'CP ' else '' end)  as A_CP
			, max(case AccessRight when 'DA' then 'DA ' else '' end)  as A_DA
			, max(case AccessRight when 'GC' then 'GC ' else '' end)  as A_GC
			, max(case AccessRight when 'GD' then 'GD ' else '' end)  as A_GD
			, max(case AccessRight when 'GM' then 'GM ' else '' end)  as A_GM
			, max(case AccessRight when 'NT' then 'NT ' else '' end)  as A_NT
			, max(case AccessRight when 'OD' then 'OD ' else '' end)  as A_OD
			, max(case AccessRight when 'OI' then 'OI ' else '' end)  as A_OI
			, max(case AccessRight when 'OS' then 'OS ' else '' end)  as A_OS
			, max(case AccessRight when 'OU' then 'OU ' else '' end)  as A_OU
			, max(case AccessRight when 'RF' then 'RF ' else '' end)  as A_RF
			, max(case AccessRight when 'RO' then 'RO ' else '' end)  as A_RO
			, max(case AccessRight when 'SA' then 'SA ' else '' end)  as A_SA
			, max(case AccessRight when 'SD' then 'SD ' else '' end)  as A_SD
			, max(case AccessRight when 'SH' then 'SH ' else '' end)  as A_SH
			, max(case AccessRight when 'SR' then 'SR ' else '' end)  as A_SR
			, max(case AccessRight when 'SS' then 'SS ' else '' end)  as A_SS
			, max(case AccessRight when 'TH' then 'TH ' else '' end)  as A_TH
			, max(case AccessRight when 'UM' then 'UM ' else '' end)  as A_UM
			, max(case AccessRight when 'UT' then 'UT ' else '' end)  as A_UT
			, max(case AccessRight when 'UU' then 'UU ' else '' end)  as A_UU

		from dbc.AccessRights a
		join      dbc.DBase d on d.DatabaseID = a.DatabaseID
		left join dbc.DBase u on u.DatabaseID = a.UserID
		left join dbc.Roles r on r.RoleID = a.UserID
		left join dbc.TVM   t on t.DatabaseID = a.DatabaseID and t.TVMID = a.TVMID

		where a.DatabaseID <> a.UserID and d.CreateUID <> a.UserID
			and (t.CreateUID <> a.UserID or t.CreateUID is NULL)

		group by 1,2,3,4,5,6
	) DBAcc
"""

if __name__ == '__main__':
	import sys
	sys.exit(main())
