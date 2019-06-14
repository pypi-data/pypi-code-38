from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import sys
from datetime import datetime

from past.builtins import basestring

from .klass_odoo_mixin import Mixin
from .klass_path import Path

DATE_FORMAT, DATETIME_FORMAT = "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"


class Env(Mixin):
    def __init__(self, env=False, odoo=False, dbname=False, verbose=True):
        if isinstance(env, basestring):
            dbname = env
            env = False
        assert (env and odoo) or (
                odoo and dbname), "give an existing environnement or specify odoo and dbname for creating a new one"
        self.odoo = odoo
        self.dbname = dbname
        self.verbose = verbose
        self.cr = False
        self.conf = self.odoo.tools.config
        self.list_db = self.odoo.tools.config['list_db']
        self.list_db_disabled = self.odoo.tools.config['list_db'] == False
        self.version = odoo.release.version_info[0]
        if env:
            self.env = env
            self.dbname = self.env.cr.dbname
            self.cr = self.env.cr
        else:
            self.reset()

    def reset(self):
        if self.cr and not self.cr.closed:
            print('closing the cursor')
            self.cr.close()
        try:
            registry = self.odoo.modules.registry.Registry.new(self.dbname)
            cr = registry.cursor()
            self.env = self.odoo.api.Environment(cr, self.odoo.SUPERUSER_ID, {})
        except Exception as e:
            self.env = False
        if self.env:
            self.dbname = self.env.cr.dbname
            self.cr = self.env.cr
        else:
            self.cr = False

    def close(self):
        self._require_env()
        if not self.cr.closed:
            self.cr.close()

    def get_addons(self, enterprise=False, core=False, extra=True, addons_path=False):
        self._require_env()
        installed, uninstalled = [], []
        if not addons_path:
            addons_path = []
        elif isinstance(addons_path, basestring):
            addons_path = addons_path.split(',')
        addons_path = addons_path or self.conf['addons_path'].split(',')
        for path in addons_path:
            dirs = [ddir for ddir in os.listdir(path) if os.path.isdir(os.path.join(path, ddir))]
            addons = [ddir for ddir in dirs if
                      len({'__manifest__.py', '__init__.py'} & set(os.listdir(os.path.join(path, ddir)))) == 2]
            modules = self.env['ir.module.module'].search([('name', 'in', addons)])
            addons = modules.mapped('name')
            if not addons:
                continue
            if not core and {'base', 'sale', 'account'} & set(addons):
                continue
            if not enterprise and {'account_reports'} & set(addons):
                continue
            if not extra and not ({'base', 'sale', 'account_reports'} & set(addons)):
                continue
            installed.extend(modules.filtered(lambda a: a.state == 'installed').mapped('name'))
            uninstalled.extend(modules.filtered(lambda a: a.state == 'uninstalled').mapped('name'))
        return installed, uninstalled

    def check_uninstalled_modules(self, enterprise=False, core=False, extra=True, addons_path=False):
        self._require_env()
        installed, uninstalled = self.get_addons(enterprise=enterprise, core=core, extra=extra, addons_path=addons_path)
        print('Installed modules   : %s' % installed)
        print('Uninstalled modules : %s' % uninstalled)
        if uninstalled:
            sys.exit(-1)
        else:
            sys.exit(0)

    def commit(self):
        self._require_env()
        self.env.cr.commit()

    def rollback(self):
        self._require_env()
        self.env.cr.rollback()

    def clear(self):
        self._require_env()
        if hasattr(self.env, 'invalidate_all'):
            self.env.invalidate_all()
        else:
            self.env.cache.invalidate()

    def dump_db(self, dest=False, zip=True):
        self._require_env()
        data_dir = os.path.join(self.odoo.tools.config["data_dir"], "backups", self.dbname)
        dest = dest or data_dir
        try:
            os.makedirs(dest)
        except:
            pass
        assert os.path.isdir(dest), "The directory [%s] should exists" % dest
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = 'zip' if zip else 'dump'
        filename = "{}_{}.{}".format(self.dbname, now, ext)
        path = os.path.join(dest, filename)
        if self.list_db_disabled:
            self.list_db = True
        with open(path, 'wb+') as destination:
            kwargs = {}
            if not zip: kwargs['backup_format'] = 'custom'
            self.odoo.service.db.dump_db(self.dbname, destination, **kwargs)
        if self.list_db_disabled:
            self.list_db = False
        print('End: %s' % path)
        size = Path.size_str(path)
        print('Backup Size: %s' % size)
        return path

    def drop_db(self, dbname=False):
        dbname = dbname or self.dbname
        if dbname in self.list_db():
            self.odoo.service.db.exp_drop(dbname)
            print('End: dbname=%s is dropped' % dbname)
        else:
            print('The database [%s] is not found' % dbname)
        return dbname

    def create_db(self, dbname=False, with_demo=False, language='fr_FR'):
        dbname = dbname or self.dbname
        if dbname in self.list_db():
            print('End: dbname=%s is already exists' % dbname)
        else:
            self.odoo.service.db.exp_create_database(dbname, with_demo, language, self.password, self.user)
            print('The database [%s] is created' % dbname)
        return dbname

    def restore_db(self, path, drop=False):
        assert os.path.isfile(path), 'The path [%s] should be a file' % path
        if drop:
            try:
                self.drop_db()
            except:
                print('can not drop the database')
        size = Path.size_str(path)
        print('Restore Size: %s' % size)
        self.odoo.service.db.restore_db(self.dbname, path)
        print('End: %s dbname=%s' % (path, self.dbname))
        return path

    def list_db(self):
        res = self.odoo.service.db.list_dbs()
        print(res)
        return res
