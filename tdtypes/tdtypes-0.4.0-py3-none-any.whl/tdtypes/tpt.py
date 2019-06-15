#! /usr/bin/env python

"Generate TPT script to load Teradata table(s)"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2017, Paresh Adhia"

import collections
import enum
from typing import List, Dict, Callable, Optional, Tuple

from .util import getLogger

logger = getLogger(__name__)

class UnexpectedError(RuntimeError):
	pass

JOBID_PATTERN = '^Job id is (.*),'

# pylint: disable=locally-disabled, bad-whitespace, multiple-statements
class UtilSize(enum.Enum):
	"TPT Utility data size"
	MICRO  = 1
	TINY   = 2
	SMALL  = 3
	MEDIUM = 4
	LARGE  = 5

class QB1:
	"A single QueryBand name-value pair"
	def __init__(self, name: str, val: str):
		self.name, self.val = name, val

	def __str__(self):
		return '{}={};'.format(self.name, self.val)

	@staticmethod
	def parse(pair: str) -> 'QB1':
		"parse a string to QueryBand"
		if pair.count('=') != 1:
			raise ValueError('Invalid QueryBand value')
		name, val = pair.split('=')
		if val[-1] == ';':
			val = val[:-1]
		return QB1(name, val)

	@staticmethod
	def from_utsz(u: UtilSize) -> List['QB1']:
		"Return a list containing either 1 QB1 element if u is either SMALL or LARGE or an empty list"
		return [QB1('UtilityDataSize', u.name)] if u in [UtilSize.SMALL, UtilSize.LARGE] else []

class TPTVars(collections.OrderedDict):
	"List of TPT variable/attribute and value"
	def __setitem__(self, k, v, **kargs):
		if v is None or v == []:
			if k in self:
				del self[k]
		else:
			collections.OrderedDict.__setitem__(self, k,v, **kargs)

	def pairs(self):
		"list of tuple containing variable and its formatted value"
		def fmtval(val):
			"printable representation of value based on its type"
			if isinstance(val, bool): return "'Yes'" if val else "'No'"
			if isinstance(val, int):  return format(val)
			if isinstance(val, list): return "[{}]".format(', '.join(fmtval(v) for v in val))
			if isinstance(val, str):  return val if '@' in val or val.startswith("'") else "'{}'".format(val.replace("'","''"))
			return "'{}'".format(val)

		for k,v in self.items():
			yield (k, fmtval(v))

	def as_decl(self, indent=''):
		"return as a string that SETs variable values"
		width = max([len(k) for k in self.keys()])
		return ('\n'+indent).join(["SET {:{width}} = {};".format(k,v, width=width) for k,v in self.pairs()])

	def as_attr(self, indent=''):
		"return as a string of attributes"
		return ' ATTR({})'.format((','+indent).join(['{}={}'.format(k,v) for k,v in self.pairs()])) if self else ''

	@staticmethod
	def from_auth(user: str, password: str = None, host: str = None, logmech: str = None, prefix: str = '') -> 'TPTVars':
		"Build TPTVars from authentication information"
		cvars = TPTVars()

		if host:
			cvars[f"{prefix}TdpId"] = host
		cvars[f"{prefix}UserName"] = user
		if password:
			cvars[f"{prefix}UserPassword"] = password
		if logmech:
			cvars[f"{prefix}LogonMech"] = logmech

		return cvars

class Instances(int):
	"Number of producer/consumer Instances"
	def __init__(self, val):
		int.__init__(int(val))
		if self < 1:
			raise ValueError("Instnaces value can't be less than 1")

	def __str__(self):
		return ('['+int.__str__(self)+']') if self > 1 else ''

class TPTOp:
	"A TPT Operator"
	def __init__(self, name: str, inst=None, sch: str = None, dlm: bool = False):
		self.name, self.inst, self.sch, self.dlm = name, inst, sch, dlm
		self.attrs = TPTVars()
		self.vars = TPTVars()

	def __str__(self):
		if self.sch:
			sch = "({}'{}')".format('DELIMITED ' if self.dlm else '', self.sch)
		else:
			sch = ''
		return "${}{}{}{}".format(self.name, sch, self.inst or "", self.attrs.as_attr("\n        "))

class ConsumerOp(TPTOp):
	"TPT Consumer operator"

class FMLoadOp(ConsumerOp):
	"Generic TPT Load/Update operator"
	def __init__(self, tbl, util_sz, temp_db=None, errlim=None, qb=None, update=False, **kwargs):
		super().__init__('UPDATE' if update else 'LOAD', **kwargs)

		if errlim is not None: self.vars['LoadErrorLimit'] = errlim

		self.attrs['TargetTable'] = tbl
		self.attrs['QueryBandSessInfo'] = ([] if qb is None else qb)  + QB1.from_utsz(util_sz)

		if temp_db:
			self.attrs['LogTable']    = '{}.{}_RL'.format(temp_db, tbl.name)
			self.attrs['ErrorTable1'] = '{}.{}_ET'.format(temp_db, tbl.name)
			self.attrs['ErrorTable2'] = '{}.{}_UV'.format(temp_db, tbl.name)
			if update:
				self.attrs['WorkTable'] = '{}.{}_WT'.format(temp_db, tbl.name)

class LoadOp(FMLoadOp):
	"TPT Load operator"
	def __init__(self, *args, **kwargs):
		super().__init__(*args, update=False, **kwargs)

class UpdateOp(FMLoadOp):
	"TPT Update operator"
	def __init__(self, *args, **kwargs):
		super().__init__(*args, update=True, **kwargs)

class StreamOp(ConsumerOp):
	"TPT Stream operator"
	def __init__(self, tbl, temp_db=None, mac_db=None, pack=None, sess=1, errlim=1, qb=None, **kwargs):
		super().__init__('STREAM', **kwargs)

		self.vars['StreamMacroDatabase']     = mac_db
		self.vars['StreamErrorLimit']        = errlim
		self.vars['StreamQueryBandSessInfo'] = qb

		self.attrs['MaxSessions'] = sess
		self.attrs['Pack']        = pack

		if temp_db:
			self.attrs['LogTable']   = '{}.{}_RL'.format(temp_db, tbl.name)
			self.attrs['ErrorTable'] = '{}.{}_ET'.format(temp_db, tbl.name)

class InserterOp(ConsumerOp):
	"TPT SQL INSERTER Operator"
	def __init__(self, sess=None, qb=None, **kwargs):
		super().__init__('INSERTER', **kwargs)
		self.attrs['MaxSessions'] = sess
		self.vars['InserterQueryBandSessInfo'] = qb

class ProducerOp(TPTOp):
	"TPT Producer operator"

class FileReaderOp(ProducerOp):
	"Data Connector Producer operator"
	def __init__(self, tbl, dir=None, dlm=None, esc='\\', quote=None, fit=False, empty=False, skip1=False, **kwargs):
		super().__init__('FILE_READER', sch=tbl, dlm=(dlm is not None), **kwargs)

		if dlm is None:
			self.vars['FileReaderFormat']        = 'Binary'
			self.vars['FileReaderIndicatorMode'] = True
		else:
			self.vars['FileReaderFormat']        = 'Delimited'
			self.vars['FileReaderEscapeTextDelimiter'] = esc
			if empty:
				self.vars['FileReaderAcceptMissingColumns'] = empty
				self.vars['FileReaderNullColumns'] = empty

		if dir: self.vars['FileReaderDirectoryPath'] = dir
		if fit: self.vars['FileReaderTruncateColumnData'] = True

		if dlm:
			try:
				self.vars['FileReaderTextDelimiterHEX'] = format(int(dlm), '02X')
			except ValueError:
				self.vars['FileReaderTextDelimiter'] = dlm

		if quote is not None:
			self.vars['FileReaderQuotedData'] = quote

		self.attrs['FileName'] = tbl.src
		if skip1: self.vars['FileReaderSkipRows'] = 1

class FileWriterOp(ConsumerOp):
	"Data Connector Consumer operator"
	def __init__(self, name, dir=None, dlm=None, esc='\\', quote=None, **kwargs):
		super().__init__('FILE_WRITER', dlm=(dlm is not None), **kwargs)

		if dlm is None:
			self.vars['FileWriterFormat']        = 'Binary'
			self.vars['FileWriterIndicatorMode'] = True
		else:
			self.vars['FileWriterFormat']        = 'Delimited'
			self.vars['FileWriterEscapeTextDelimiter'] = esc

		if dir: self.vars['FileWriterDirectoryPath'] = dir

		if dlm:
			try:
				self.vars['FileWriterTextDelimiterHEX'] = format(int(dlm), '02X')
			except ValueError:
				self.vars['FileWriterTextDelimiter'] = dlm

		if quote is not None:
			self.vars['FileWriterQuotedData'] = quote

		self.attrs['FileName'] = name

class SQLProducerOp(ProducerOp):
	"Generic SQL producer operator"
	def __init__(self, op: str, sql: str, **kwargs):
		super().__init__(op, **kwargs)
		self.attrs['SelectStmt'] = sql

class ExportOp(SQLProducerOp):
	"EXPORT operator"
	def __init__(self, sql: str, qb: List[QB1] = None, util_sz: UtilSize = None, **kwargs):
		super().__init__('EXPORT', sql, **kwargs)
		self.attrs['QueryBandSessInfo'] = ([] if qb is None else qb) + QB1.from_utsz(util_sz)

class SelectorOp(SQLProducerOp):
	"SELECTOR operator"
	def __init__(self, sql: str, qb: List[QB1] = None, **kwargs):
		super().__init__('SELECTOR', sql, **kwargs)
		self.vars['SelectorQueryBandSessInfo'] = qb

class OdbcOp(SQLProducerOp):
	"ODBC operator"
	def __init__(self, sql: str, conn: str, **kwargs):
		super().__init__('ODBC', sql)
		self.vars['ODBCConnectString'] = conn
		self.vars['ODBCTruncateData']  = True

class TPTStep:
	"TPT Job step definition"
	def __init__(self, name):
		self.name = name
		self.vars = TPTVars()

	def apply(self):
		"generate APPLY clause"
		raise NotImplementedError

	def to_string(self, suffix: int = None):
		"Convert step to string, optionally changing step name by applying a suffix (to keep unique"
		sfx = '_'+format(suffix) if suffix else ''
		body = self.apply().replace('\n','\n    ')

		return f"""\
STEP {self.name}{sfx} (
    {body}
);"""

	__str__ = to_string

class DDLStep(TPTStep):
	"A TPT Step that runs SQLs"
	def __init__(self, name: str, tblist: List[object], ddl: Callable[[str], str], qb: List[QB1] = None, errors: List[str] = None):
		super().__init__(name)
		self.vars['DDLErrorList'] = errors if errors else []
		self.vars['DDLQueryBandSessInfo'] = qb

		self.tblist = tblist
		self.ddl = ddl

	def apply(self) -> str:
		def genddl(t):
			"strinify and escape the generated value"
			return "'" + self.ddl(t).replace("'","''") + "'"

		ddls = ',\n      '.join([genddl(t) for t in self.tblist])
		return "APPLY {} TO OPERATOR ($DDL);".format(ddls)

class LoadStep(TPTStep):
	"TPT Job Load step"
	def __init__(self, tbl, pop: ProducerOp, cop: ConsumerOp):
		super().__init__(tbl.name)

		self.tbl, self.cop, self.pop = tbl, cop, pop
		self.vars.update(cop.vars)
		self.vars.update(pop.vars)

	def apply(self) -> str:
		return """\
APPLY
$INSERT '{}' TO OPERATOR (
    {}
)
SELECT * FROM OPERATOR (
    {}
);""".format(self.tbl, self.cop, self.pop)

class ExportStep(TPTStep):
	"TPT Job Load step"
	def __init__(self, tbl, pop: ProducerOp, cop: ConsumerOp):
		super().__init__(tbl.name)

		self.tbl, self.cop, self.pop = tbl, cop, pop
		self.vars.update(cop.vars)
		self.vars.update(pop.vars)

	def apply(self) -> str:
		return """\
APPLY
TO OPERATOR (
    {}
)
SELECT * FROM OPERATOR (
    {}
);""".format(self.cop, self.pop)

class StepCounts:
	"inserted and exported row counts"
	def __init__(self, step: str, rows_in: int = 0, rows_out: int = 0):
		self.step, self.rows_in, self.rows_out = step, rows_in, rows_out

	def __repr__(self):
		return f'StepCount({self.step}, rows_in={self.rows_in}, rows_out={self.rows_out})'

class TPTJob:
	"TPT Job"
	def __init__(self, name: str):
		self.name: str = name
		self.steps: List[TPTStep] = []
		self.varlist: List[TPTVars] = [TPTVars()]
		self.vars: TPTVars = self.varlist[0]
		self.jobid: str = None
		self.step_counts: List[StepCounts] = None

	def run(self, jobvar: str = None, chkpt: str = None, capture_counts: bool = False) -> int:
		"execute this TPT job"
		import tempfile
		import os
		from subprocess import run, PIPE

		with tempfile.NamedTemporaryFile(delete=False) as tmp:
			tmp.write(str(self).encode())
			script_file = tmp.name

		cmd = ['tbuild', '-f', script_file]
		if jobvar:
			cmd.extend(['-v', jobvar])
		if chkpt:
			cmd.extend(['-z', chkpt])
		cmd.append(self.name)

		logger.info('Invoking command: %s', cmd)
		retval = run(cmd, stdout=(PIPE if capture_counts else None))
		if retval.returncode:
			logger.error("tbuild command failed with error code: {}. Manually remove '{}'".format(retval.returncode, script_file))
			return retval.returncode
		os.unlink(script_file)

		if capture_counts:
			try:
				self.jobid, self.step_counts = self._capture(retval.stdout.decode())
			except UnexpectedError as err:
				logger.error(err)
				return 1

		return 0

	@staticmethod
	def _capture(job_output: str) -> Tuple[str, List[StepCounts], Optional[str]]:
		from subprocess import run, PIPE
		from collections import OrderedDict

		def find_jobid(output: str) -> Optional[str]:
			import re
			for l in output.split('\n'):
				m = re.match(JOBID_PATTERN, l)
				if m:
					return m.group(1)

		jobid = find_jobid(job_output)
		if jobid is None:
			print(job_output)
			raise UnexpectedError('Unable to determine jobid from the output')

		retval = run(['tlogview', '-j', jobid, '-f', 'TWB_EVENTS'], stdout=PIPE)
		if retval.returncode:
			raise UnexpectedError(f'tlogview command to retrieve TPT job output failed with RC={retval.returncode}')

		counts: Dict[str, StepCounts] = OrderedDict()

		for l in retval.stdout.decode().rstrip().split('\n'):
			_, _, _, op, step, _, _, _, rows, _ = l.split(',', 9)
			if step not in counts:
				counts[step] = StepCounts(step)
			if op.endswith('RowsInserted'):
				counts[step].rows_in += int(rows)
			if op.endswith('RowsExported'):
				counts[step].rows_out += int(rows)

		return (jobid, counts.values())

	def __str__(self):
		from itertools import chain

		for s in self.steps:
			self.vars.update(s.vars)

		names: Dict[str, int] = {}
		def step2str(step: TPTStep) -> str:
			"convert TPTStep to string"
			try:
				names[step.name] += 1
			except KeyError:
				names[step.name] = 0
			return step.to_string(names[step.name])

		body = '\n\n'.join(chain((v.as_decl() for v in self.varlist if v), (step2str(s) for s in self.steps)))
		return "DEFINE JOB {}\n(\n    {}\n);".format(self.name, body.replace('\n','\n    '))
