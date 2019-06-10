# encoding: utf-8

from __future__ import unicode_literals

from web.core import Application
from web.core.context import Context
from web.ext.db import DatabaseExtension
from web.db.dbapi import SQLite3Connection


class TestSQLite3Connection(object):
	def test_repr(self):
		con = SQLite3Connection(':memory:', 'test')
		assert repr(con) == 'SQLite3Connection(test, "sqlite3:connect", ":memory:")'
	
	def test_lifecycle(self):
		Application("Hi.", extensions=[DatabaseExtension(default=SQLite3Connection(':memory:'))])
	
	def test_use(self):
		con = SQLite3Connection(':memory:', 'test')
		ctx = Context(db=Context())
		
		con._connect(ctx)
		
		with ctx.db.test:
			ctx.db.test.execute('CREATE TABLE stocks (date text, trans text, symbol text, qty real, price real)')
			ctx.db.test.execute("INSERT INTO stocks VALUES ('2006-01-05', 'BUY', 'RHAT', 100, 35.14)")
			ctx.db.test.commit()
		
		with ctx.db.test:
			result = ctx.db.test.execute('SELECT * FROM stocks WHERE symbol=?', ('RHAT', ))
			assert result.fetchone() == ('2006-01-05', 'BUY', 'RHAT', 100, 35.14)
		
		con._disconnect(ctx)

