#! /usr/bin/env python

"Show statistics on Teradata objects"

from typing import Iterable, Tuple, Optional
import xml.etree.ElementTree as ET

import tdtypes as td
from . import util

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2017, Paresh Adhia"

GroupedStats = Tuple[int, str]
StatsVals = Tuple[str, Optional[str], Optional[int], Optional[int], Optional[float], Optional[float], Optional[float]]

logger = util.getLogger(__name__)

def main() -> int:
	"script entry point"
	from argparse import ArgumentParser

	p = ArgumentParser(description=__doc__)

	p.add_argument("tblist", type=td.DBObjPat, nargs='+', help=td.DBObjPat.__doc__)
	util.dbconn_args(p)

	args = p.parse_args()

	with td.cursor(args) as csr:
		def tbl_stats(tbl: td.DBObj) -> str:
			import yappt
			try:
				csr.execute('SHOW IN XML STATS VALUES SEQUENCED ON ' + str(tbl))
			except (util.DatabaseError, util.Warning):
				logger.error('{} has no statistics'.format(tbl))
				return None

			data = map(xml2stat, rows2xml(csr.fetchall()))
			return str(tbl) + '\n' + yappt.tabulate(data, columns=['Columns', 'Time', ('Card', yappt.HumanInt), 'Nulls', 'Skip', 'Samp', 'Chg%', 'Age'])

		tables = list(td.DBObjPat.findall(args.tblist, objtypes='TONI'))
		stats = list(filter(None, map(tbl_stats, tables)))
		if stats:
			print('\n\n'.join(stats))

		return 1 if len(tables) > len(stats) else 0

def rows2xml(rows: Iterable[GroupedStats]) -> Iterable[ET.Element]:
	"combine XML fragments from each row-group"
	import re
	from itertools import groupby

	def row_group() -> Iterable[GroupedStats]:
		"iterate with group # information that is splittable by groupby()"
		grp_num = 0
		for g, s in rows:
			if g == 1:
				grp_num += 1
			yield grp_num, s

	for _, g in groupby(row_group(), key=lambda r: r[0]):
		xml = ''.join(s[1] for s in g)
		xml = re.sub('xmlns=".*?"', '', re.sub('encoding="UTF-16"', 'encoding="utf-8"', xml, 1, flags=re.IGNORECASE), 1)
		yield from ET.fromstring(xml).findall('./Statistics')

def xml2stat(s: ET.Element) -> StatsVals:
	"parse XML and return a tuple with column(s) and other stats information"

	def tagval(f, *tags):
		"if tag exists return value by applying f on tag text, else None"
		for tag in tags:
			val = s.find(tag)
			if val is not None:
				return f(val.text)

	col = tagval(lambda s: s, './StatsDefinition/StatsEntries/StatsEntry/Alias') \
			or ','.join(c.text.rstrip() for c in s.findall('./StatsDefinition/StatsEntries/StatsEntry/Expr')) \
			or '*'

	rows = tagval(int, './Histogram/SummaryInfo/NumOfDistinctVals', './TableLevelSummary/SummaryRecord/RowCount')
	collts = tagval(lambda s: s[:10], './TableLevelSummary/SummaryRecord/TimeStamp', './Histogram/SummaryInfo/TimeStamp')
	nulls = tagval(int, './Histogram/SummaryInfo/NumOfNulls')
	skips = tagval(int, './Histogram/SummaryInfo/StatsSkipCount')

	samp = thr_age = thr_chg = None
	stat = s.find('./StatsDefinition/Using')
	if stat is not None:
		for x in stat:
			val = x.attrib.get('value')
			if val:
				val = float(val)

			if x.tag == 'Threshold':
				if x.attrib['typecode'] == 'C':
					thr_chg = val
				elif x.attrib['typecode'] == 'T':
					thr_age = val
			elif x.tag == 'Sample':
				samp = val

	return (col, collts, rows, nulls, skips, samp, thr_chg, thr_age)

if __name__ == '__main__':
	import sys
	sys.exit(main())
