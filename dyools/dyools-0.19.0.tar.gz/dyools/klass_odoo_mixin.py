from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import importlib
import logging
import os
from collections import defaultdict
from datetime import datetime, date
from functools import partial

import odoorpc
from dateutil.parser import parse as dtparse
from lxml import etree
from odoorpc.models import MetaModel
from past.builtins import basestring
from prettytable import PrettyTable

from .klass_eval import Eval
from .klass_is import IS
from .klass_path import Path
from .klass_tool import Tool
from .klass_yaml_config import YamlConfig

logger = logging.getLogger(__name__)
DATE_FORMAT, DATETIME_FORMAT = "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"
DEFAULT_VALUES = defaultdict(lambda: False)
DEFAULT_VALUES.update({
    'float': 0,
    'integer': 0,
    'monetary': 0,
    'one2many': [],
    'many2many': [],
})
CONCURRENCY_CHECK_FIELD = '__last_update'
LOG_ACCESS_COLUMNS = ['create_uid', 'create_date', 'write_uid', 'write_date']
MAGIC_COLUMNS = ['id'] + LOG_ACCESS_COLUMNS
ONCHANGE_RESERVED = [CONCURRENCY_CHECK_FIELD] + MAGIC_COLUMNS


class Mixin(object):
    def __init__(self):
        pass

    def _require_env(self):
        assert self.env, "An environment is required for this method"

    def info(self, *args, **kwargs):
        logger.info(*args, **kwargs)

    def debug(self, *args, **kwargs):
        logger.debug(*args, **kwargs)

    def warning(self, *args, **kwargs):
        logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        logger.error(*args, **kwargs)

    def get_param(self, param, default=False):
        self._require_env()
        return self.env['ir.config_parameter'].get_param(param, default)

    def set_param(self, param, value):
        self._require_env()
        self.env['ir.config_parameter'].set_param(param, value)
        return self.get_param(param)

    def vlist(self, records, fields=[], types=[], title=False):
        return self.show(records, fields, types, title, vlist=True)

    def hlist(self, records, fields=[], types=[], title=False):
        return self.show(records, fields, types, title, vlist=False)

    def data(self, records, fields=[], types=[], title=False, vlist=True):
        return self._show_data(records, fields, types, title, vlist, _show_data=False)

    def show(self, records, fields=[], types=[], title=False, vlist=True):
        return self._show_data(records, fields, types, title, vlist, _show_data=True)

    def _show_data(self, records, fields=[], types=[], title=False, vlist=True, _show_data=True):
        self._require_env()
        if isinstance(types, basestring):
            types = types.split()
        if isinstance(fields, basestring):
            fields = fields.split()
        assert isinstance(fields, list), 'fields should be a list'
        if title:
            print('@@@@ %s @@@@' % title)
        print('Show %s record(s)' % len(records))
        if isinstance(records, dict):
            new_records = []
            for rk, rv in records.items():
                rv.update(dict(name=rk))
                new_records.append(rv)
            records = new_records
        if not fields:
            if isinstance(records, odoorpc.models.Model):
                fields = list(self.env[records._name].fields_get().keys())
            elif isinstance(records, list):
                fields = records[0].keys() if records else ['name']
            else:
                fields = list(records.fields_get().keys())
        if types and not isinstance(records, list):
            if isinstance(records, odoorpc.models.Model):
                fields_get = self.env[records._name].fields_get()
            else:
                fields_get = records.fields_get()
            fields = filter(lambda f: '.' not in f and fields_get[f]['type'] in types, fields)
        fields = list(fields)
        if fields:
            if 'id' not in fields:
                fields = ['id'] + fields
            if not isinstance(records, list):
                records = records.read(fields)
            if vlist:
                tbl_data = [fields]
                for record in records:
                    tbl_data.append([record.get(f, '') for f in fields])
            else:
                tbl_data = [['field', 'value']]
                for record in records:
                    tbl_data.append(['---', '---'])
                    for f in fields:
                        tbl_data.append([f, record.get(f, '')])
        if _show_data:
            if not fields:
                print('No field found')
            else:
                if tbl_data:
                    x = PrettyTable()
                    x.field_names = tbl_data[0]
                    for item in tbl_data[1:]:
                        x.add_row(item)
                    print(x)
                print('Total: %s' % (len(tbl_data) - 1))
        else:
            return tbl_data

    def is_rpc(self):
        return self.__class__.__name__ == 'RPC'

    def path(self, module):
        if isinstance(module, basestring):
            module = importlib.import_module(module)
        return os.path.dirname(module.__file__)

    def read(self, model, domain=[], limit=False, order=False, fields=[], **kwargs):
        self._require_env()
        model, domain, search_kwargs = self._get(model, domain, limit, order, **kwargs)
        ids = self.env[model].search(domain, **search_kwargs)
        if IS.list_of_values(ids):
            return self.env[model].read(ids, fields)
        else:
            return ids.read(fields)

    def _get(self, model, domain=[], limit=False, order=False, **kwargs):
        self._require_env()
        records = model
        if not domain:
            domain = []
        elif isinstance(domain, int):
            domain = [('id', '=', domain)]
        elif isinstance(domain, tuple):
            domain = [domain]
        elif isinstance(domain, basestring) and len(domain.split()) < 3:
            domain = [('name', '=', domain)]
        elif isinstance(domain, basestring):
            domain = Tool.construct_domain_from_str(domain)
        for d_key, d_value in kwargs.items():
            domain.append((d_key, '=', d_value))
        if hasattr(self.odoo, 'models') and isinstance(records, self.odoo.models.Model):
            domain = ['&', ('id', 'in', records.ids)] + domain
            model = records._name
        if isinstance(records, odoorpc.models.Model):
            domain = ['&', ('id', 'in', records.ids)] + domain
            model = records._name
        search_kwargs = {}
        if limit: search_kwargs['limit'] = limit
        if order: search_kwargs['order'] = order
        return model, domain, search_kwargs

    def get(self, model, domain=[], limit=False, order=False, **kwargs):
        self._require_env()
        model, domain, search_kwargs = self._get(model, domain, limit, order, **kwargs)
        res = self.env[model].search(domain, **search_kwargs)
        res = self.to_obj(model, res)
        return res

    def update_xmlid(self, record, xmlid=False):
        self._require_env()
        assert not xmlid or len(xmlid.split('.')) == 2, "xmlid [%s] is invalid" % xmlid
        xmlid_env = self.env['ir.model.data']
        xmlid_obj = xmlid_env.search([('model', '=', record._name), ('res_id', '=', record.id)], limit=1)
        if not xmlid_obj:
            if xmlid:
                module, name = xmlid.split('.')
            else:
                module = '__export__'
                name = '%s_%s' % (record._name.replace('.', '_'), record.id)
            xmlid_obj = xmlid_env.create({
                'module': module,
                'name': name,
                'model': record._name,
                'res_id': record.id,
            })
        if isinstance(xmlid_obj, (int, list)):
            xmlid_obj = xmlid_env.browse(xmlid_obj)
        return xmlid_obj.complete_name

    def xmlid_to_object(self, xmlid):
        self._require_env()
        assert IS.xmlid(xmlid), 'The keyword [{}] sould be a valid XMLID'.format(xmlid)
        module, name = xmlid.split('.')
        xmlid_env = self.env['ir.model.data']
        xmlid_obj = xmlid_env.search([('module', '=', module), ('name', '=', name)], limit=1)
        xmlid_obj = self.to_obj('ir.model.data', xmlid_obj)
        return self.env[xmlid_obj.model].browse(xmlid_obj.res_id)

    def config(self, **kwargs):
        model = 'res.config.settings'
        res = self.env[model].create(kwargs)
        res = self.to_obj(model, res)
        res.execute()

    def to_obj(self, model, res):
        if isinstance(res, (int, list)):
            return self.env[model].browse(res)
        return res

    def to_ids(self, res):
        if isinstance(res, int):
            return [res]
        elif isinstance(res, list):
            return res
        else:
            return res

    def ref(self, xmlid, raise_if_not_found=True):
        self._require_env()
        return self.env.ref(xmlid)

    def _process_addons_op(self, addons, op):
        self._require_env()
        if isinstance(addons, basestring):
            addons = addons.split()
        self.update_list()
        addons = self.env['ir.module.module'].search([('name', 'in', addons)])
        addons = self.to_obj('ir.module.module', addons)
        addons_names = addons.mapped('name')
        self.show(addons, fields=['name', 'state'], title="modules before")
        addons = self.env['ir.module.module'].search([('name', 'in', addons_names)])
        addons = self.to_obj('ir.module.module', addons)
        assert op in ['install', 'upgrade', 'uninstall'], "operation %s is npt mapped" % op
        if op == 'install':
            addons.button_immediate_install()
        elif op == 'upgrade':
            addons.button_immediate_upgrade()
        elif op == 'uninstall':
            addons.module_uninstall()
        self.show(addons, fields=['name', 'state'], title="modules after")

    def update_list(self):
        self.env['ir.module.module'].update_list()

    def install(self, addons):
        self._process_addons_op(addons, 'install')

    def upgrade(self, addons):
        self._process_addons_op(addons, 'upgrade')

    def uninstall(self, addons):
        self._process_addons_op(addons, 'uninstall')

    def fields(self, model, fields=[]):
        self._require_env()
        if fields and isinstance(fields, basestring):
            fields = fields.split()
        if not isinstance(model, basestring):
            model = model._name
        if fields:
            columns = fields
            ffields = self.env[model].fields_get()
        else:
            columns = ['name', 'ttype', 'relation', 'modules']
            ffields = self.get('ir.model.fields', [('model_id.model', '=', model)])
        self.show(ffields, columns)

    def menus(self, debug=False, xmlid=False, action=False, model=False, domain=False, context=False, user=False, crud=False):
        self._require_env()
        lines = ['Applications']
        if not action and any([model, domain, context, crud]):
            action = True
        if action and not any([model, domain, context, crud]):
            model = domain = context = True

        def menu_show(menu, level):
            space = (' ' * 4 * (level - 1)) if level > 1 else ''
            if space:
                space = '|' + space[1:]
            bar = ('|' + '-' * 3) if level > 0 else ''
            fmt = "{space}{bar} {name}"
            action_model = action_domain = action_context = False
            access = ''
            if xmlid:
                fmt += '  XMLID={xmlid}'
            if action:
                if menu.get('action'):
                    action_env, action_id = menu.get('action').split(',')
                    [action_dict] = self.env[action_env].browse(int(action_id)).read(['res_model', 'domain', 'context'])
                    if action_dict:
                        action_model = action_dict.get('res_model') or ''
                        if action_model:
                            if model:
                                fmt += '  Model={action_model}'
                            if crud:
                                fmt += '  ACCESS={access}'
                                for op, key in [('create', 'C'), ('read', 'R'), ('write', 'U'), ('unlink', 'D')]:
                                    try:
                                        if self.env['ir.model.access'].check(action_model, op, False):
                                            access += key
                                    except:
                                        pass
                        action_domain = action_dict.get('domain') or []
                        if action_domain and domain:
                            fmt += '  Domain={action_domain}'
                        action_context = action_dict.get('context') or {}
                        if action_context and context:
                            fmt += '  Context={action_context}'
            line = fmt.format(
                space=space,
                bar=bar,
                menu=menu,
                name=menu['name'],
                xmlid=menu.get('xmlid') or '',
                action_model=action_model,
                action_domain=action_domain,
                action_context=action_context,
                access=access,
            )
            lines.append(line)
            for m in menu.get('children', []):
                menu_show(m, level=level + 1)

        if user:
            user = self.get_users(user)
            menus = self.env['ir.ui.menu'].sudo(user.id).load_menus(debug=debug)
        else:
            menus = self.env['ir.ui.menu'].load_menus(debug=debug)
        for menu in menus.get('children', []):
            menu_show(menu, level=1)
        for line in lines:
            print(line)

    def _process_python(self, script, context, assets):
        res = exec(script, context)
        if isinstance(res, dict):
            context.update(res)

    def _normalize_value_for_field(self, model, field, value, record_view_xmlid, record_data, assets, context):
        values = {}
        ffield = self.env[model].fields_get()[field]
        ttype, relation, selection = ffield['type'], ffield.get('relation'), ffield.get('selection', [])
        if ttype == 'boolean':
            value = bool(value)
        elif ttype in ['text', 'float', 'char', 'integer', 'monetary', 'html']:
            pass
        elif ttype == 'date':
            if isinstance(value, date):
                value = value.strftime(DATE_FORMAT)
            else:
                try:
                    value = dtparse(str(value), dayfirst=True, fuzzy=True).strftime(DATE_FORMAT)
                except:
                    value = False
        elif ttype == 'datetime':
            if isinstance(value, datetime):
                value = value.strftime(DATETIME_FORMAT)
            else:
                try:
                    value = dtparse(str(value), dayfirst=True, fuzzy=True).strftime(DATETIME_FORMAT)
                except:
                    value = False
        elif ttype == 'selection':
            for k, v in selection:
                if k == value or v == value:
                    value = k
                    break
        if ttype == 'binary':
            if assets:
                value = os.path.join(assets, value)
            with open(value, "rb") as binary_file:
                value = base64.b64encode(binary_file.read()).decode('utf-8')
        if ttype in ['many2one', 'many2many', 'one2many']:
            ids = None
            if value == '__all__':
                ids = self.to_obj(self.env[relation].search([])).ids
            elif value == '__first__':
                ids = self.to_obj(self.env[relation].search([], limit=1, order="id asc")).ids
            elif value == '__last__':
                ids = self.to_obj(self.env[relation].search([], limit=1, order="id desc")).ids
            elif isinstance(value, list) and IS.domain(value):
                ids = self.to_obj(self.env[relation].search(value)).ids
            elif isinstance(value, int):
                ids = [value]
            elif isinstance(value, basestring):
                if IS.eval(value, context):
                    ids = [Eval(value, context).eval()]
                elif IS.xmlid(value):
                    ids = self.env.ref(value).ids
                else:
                    ids = self.to_obj(relation, self.env[relation].search([('name', '=', value)])).ids
            if ttype == 'many2one':
                value = value if not ids else ids[0]
            elif ttype == 'many2many':
                value = value if ids is None else [(6, 0, ids)]
            else:
                on2many_list = []
                for one2many_line in value:
                    on2many_values = self._normalize_record_data(relation, field, one2many_line, True,
                                                                 record_view_xmlid,
                                                                 {ffield['relation_field']: record_data}, assets,
                                                                 context)
                    on2many_list.append((0, 0, on2many_values))
                value = on2many_list
        values[field] = value
        return values

    def _onchange_spec(self, model, view_info=None):
        result = {}
        onchanges = []
        view_fields = []

        def process(node, info, prefix):
            if node.tag == 'field':
                name = node.attrib['name']
                names = "%s.%s" % (prefix, name) if prefix else name
                view_fields.append(name)
                if not result.get(names):
                    result[names] = node.attrib.get('on_change', '')
                    if node.attrib.get('on_change'):
                        onchanges.append(name)
                # traverse the subviews included in relational fields
                for subinfo in info['fields'][name].get('views', {}).values():
                    process(etree.fromstring(subinfo['arch']), subinfo, names)
            else:
                for child in node:
                    process(child, info, prefix)

        if view_info is None:
            view_info = model.fields_view_get()
        process(etree.fromstring(view_info['arch']), view_info, '')
        return result, onchanges, view_fields

    def _normalize_record_data(self, model, field, data, mode_create, record_view_xmlid, one2many_data, assets,
                               context):
        model_env = self.env[model]
        fields = model_env.fields_get()
        onchange_all_data = {}
        if field:
            onchange_all_data[field] = one2many_data or {}
        for f, opts in fields.items():
            if f not in ONCHANGE_RESERVED:
                onchange_all_data[f] = DEFAULT_VALUES[opts['type']]
        if mode_create:
            record_data = model_env.default_get(list(fields.keys()))
            onchange_all_data.update(record_data)
            data = [record_data] + data
        else:
            record_data = {}
        # if self.is_rpc():
        #     onchange_specs, onchange_fields, _ = self._onchange_spec(model_env, view_info=None)  # TODO
        # else:
        #     onchange_specs = model_env._onchange_spec()  # TODO add fields_view_get
        for item in data:
            for field, value in item.items():
                values = self._normalize_value_for_field(model, field, value, record_view_xmlid, record_data, assets,
                                                         context)
                record_data.update(values)
                # onchange_all_data.update(record_data)
                # if field in onchange_fields:
                #     if self.is_rpc():
                #         onchange_values = model_env.onchange([], onchange_all_data, field, onchange_specs)
                #     else:
                #         onchange_values = model_env.onchange(onchange_all_data, field, onchange_specs)
                #     for k, v in onchange_values.get('value', {}).items():
                #         if isinstance(v, (list, tuple)) and len(v) == 2:
                #             v = v[0]
                #         record_data[k] = v
        return record_data

    def _process_config(self, value):
        return self.to_obj('res.config.settings', self.env['res.config.settings'].create(value)).execute()

    def _process_record(self, data, context, assets):
        records = self.env[data['model']]
        refs = data.get('refs')
        record_data = data.get('data')
        record_functions = data.get('functions', [])
        record_export = data.get('export')
        record_filter = data.get('filter')
        record_view_xmlid = data.get('view_xmlid')
        record_ctx = data.get('context', {})
        if context.get('__global_context__'):
            record_ctx.update(context.get('__global_context__'))
        if refs:
            if isinstance(refs, int):
                records = records.browse(refs)
            elif IS.xmlid(refs):
                if self.is_rpc():
                    try:
                        records = records.env.ref(refs)
                    except:
                        pass
                else:
                    records = records.env.ref(refs, raise_if_not_found=False) or records
            elif isinstance(refs, basestring):
                records = self.to_obj(records._name, records.search([('name', '=', refs)]))
            elif isinstance(refs, list):
                refs = Eval(refs, context).eval()
                records = self.to_obj(records._name, records.search(refs))
            if not self.is_rpc():
                records = records.exists()
            if record_filter:
                if len(records) > 0:
                    records = records.search(['&', ('id', 'in', records.ids)] + record_filter)
                    records = self.to_obj(records._name, records)
                    if not records:
                        return False
        if record_ctx:
            records = records.with_context(**record_ctx)
        if record_data:
            assert isinstance(record_data, list), "The data [%s] should be a list" % record_data
            record_data = Eval(record_data, context).eval()
            if not isinstance(records, MetaModel) and records and len(records) > 0:
                record_data[0]['id'] = records.id
                record_data = self._normalize_record_data(records._name, False, record_data, False, record_view_xmlid,
                                                          {}, assets, context)
                records.write(record_data)
            else:

                record_data = self._normalize_record_data(records._name, False, record_data, True, record_view_xmlid,
                                                          {}, assets, context)
                records = self.to_obj(records._name, records.env[records._name].create(record_data))
                if isinstance(refs, basestring) and IS.xmlid(refs):
                    self.update_xmlid(records, xmlid=refs)
        if record_export:
            context[record_export] = records
        context['%s_record' % records._name.replace('.', '_')] = records
        for function in record_functions:
            func_name = function['name']
            func_args = function['args'] if function.get('args') else []
            func_kwargs = function['kwargs'] if function.get('kwargs') else {}
            assert isinstance(func_args, list), "Args [%s] should be a list" % func_args
            assert isinstance(func_kwargs, dict), "Kwargs [%s] should be a dict" % func_kwargs
            func_res = getattr(records, func_name)(*func_args, **func_kwargs)
            func_export = function.get('export')
            if func_export:
                context[func_export] = func_res
            context['%s_%s' % (records._name.replace('.', '_'), func_name)] = func_res

    def _process_yaml_doc(self, index, doc, context, assets):
        for key, value in doc.items():
            if key == 'python':
                print("[%s] ***** Execute python *****" % index)
                self._process_python(value, context, assets)
            elif key == 'record':
                print("[%s] ***** Process record ***** <model=%s refs=%s>" % (
                    index, value.get('model', ''), value.get('refs', '')))
                self._process_record(value, context, assets)
            elif key == 'title':
                value = Eval(value, context).eval()
                print("[%s] ***** %s *****" % (index, value))
            elif key == 'context':
                value = Eval(value, context).eval()
                context['__global_context__'].update(value)
                print("[%s] ***** Add global context *****" % index)
            elif key == 'install':
                print("[%s] ***** Install modules *****" % index)
                self.install(value)
            elif key == 'upgrade':
                print("[%s] ***** Upgrade modules *****" % index)
                self.upgrade(value)
            elif key == 'uninstall':
                print("[%s] ***** Uninstall modules *****" % index)
                self.uninstall(value)
            elif key == 'config':
                print("[%s] ***** Configuration *****" % index)
                self._process_config(value)

    def load_yaml(self, path, assets=False, start=False, stop=False, auto_commit=False):
        def __add_file(f):
            fname, ext = os.path.splitext(f)
            if ext.strip().lower() not in ['.yaml', '.yml']:
                return
            fname = os.path.basename(fname)
            idx = False
            try:
                idx = int(fname.split('-')[0].strip())
            except:
                pass
            if idx and (start or stop):
                if start and idx < start: return
                if stop and idx > stop: return
            files.append(f)

        self._require_env()
        assert not assets or os.path.exists(assets), "The path [%s] should exists" % assets
        files = []
        if isinstance(path, basestring):
            paths = [path]
        else:
            paths = path
            for path in paths:
                assert os.path.exists(path), "The path [%s] should exists" % path
        for path in paths:
            if os.path.isdir(path):
                for dirpath, _, filenames in os.walk(path):
                    for filename in filenames:
                        __add_file(os.path.join(dirpath, filename))
            elif os.path.isfile(path):
                __add_file(path)
        files = sorted(files, key=lambda item: os.path.basename(item).lower().strip())
        print('[%s] Files to process : ' % len(files))
        for i, file in enumerate(files, 1):
            print("%s  - %s" % (i, file))
        contents = ""
        for file in files:
            with open(file) as f:
                contents += "\n\n---\n\n"
                contents += f.read()
        with Path.tempdir() as tmpdir:
            full_yaml_path = os.path.join(tmpdir, 'full_yaml.yml')
            with open(full_yaml_path, 'w+') as f:
                f.write(contents)
            context = {
                'self': self.env,
                'env': self.env,
                'user': self.env.user,
                '__global_context__': {},
            }
            index = 0
            for doc in YamlConfig(full_yaml_path, many=True).get_data():
                if doc:
                    index += 1
                    self._process_yaml_doc(index, doc, context, assets)
                    if auto_commit:
                        self.commit()
        if '__builtins__' in context: del context['__builtins__']
        return context

    def __getitem__(self, item):
        self._require_env()
        return self.env[item]

    def __getattr__(self, item):
        mapping = {
            'warehouses': 'stock.warehouse',
            'companies': 'res.company',
            'users': 'res.users',
            'partners': 'res.partner',
            'products': 'product.product',
            'templates': 'product.template',
            'sales': 'sale.order',
            'invoices': 'account.invoice',
            'purchases': 'purchase.order',
            'quants': 'stock.quant',
            'pickings': 'stock.picking',
            'operations': 'stock.picking.type',
            'locations': 'stock.location',
            'amls': 'account.move.line',
        }
        if item.startswith('get_'):
            self._require_env()
            _item = item[4:]
            model = False
            if _item in mapping.keys():
                model = mapping[_item]
            model = model or _item.replace('_', '.')
            if model:
                return partial(self.get, model)
        return self.env

    def __lshift__(self, other):
        assert isinstance(other, Mixin), "Backup and restore work for environments"
        with Path.tempdir() as tmp:
            path = other.dump_db(dest=tmp)
            self.restore_db(path, drop=True)

    def __rshift__(self, other):
        assert isinstance(other, Mixin), "Backup and restore work for environments"
        with Path.tempdir() as tmp:
            path = self.dump_db(dest=tmp)
            other.restore_db(path, drop=True)
