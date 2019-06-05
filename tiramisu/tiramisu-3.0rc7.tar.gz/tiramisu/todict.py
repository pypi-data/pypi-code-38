# -*- coding: utf-8 -*-

import warnings
import sys
from copy import copy
from collections import OrderedDict
from .error import ValueWarning, ValueErrorWarning, PropertiesOptionError
from . import SynDynOption, RegexpOption, ChoiceOption, ParamContext, ParamOption
from .i18n import _


TYPES = {'SymLinkOption': 'symlink',
         'IntOption': 'integer',
         'FloatOption': 'integer',
         'ChoiceOption': 'choice',
         'BoolOption': 'boolean',
         'PasswordOption': 'password',
         'PortOption': 'integer',
         'DateOption': 'date',
         'DomainnameOption': 'domainname',
         'StrOption': 'string'
         }
INPUTS = ['string',
          'integer',
          'filename',
          'password',
          'email',
          'username',
          'ip',
          'domainname']

ACTION_HIDE = ['hidden', 'disabled']


# return always warning (even if same warning is already returned)
warnings.simplefilter("always", ValueWarning)


class Callbacks(object):
    def __init__(self, tiramisu_web):
        self.tiramisu_web = tiramisu_web
        self.clearable = tiramisu_web.clearable
        self.remotable = tiramisu_web.remotable
        self.callbacks = []

    def add(self,
            path,
            childapi,
            schema,
            force_store_value):
        if self.remotable == 'all' or childapi.option.isoptiondescription():
            return
        callback, callback_params = childapi.option.callbacks()
        if callback is None:  # FIXME ? and force_store_value and self.clearable != 'all':
            return
        self.callbacks.append((callback, callback_params, path, childapi, schema, force_store_value))

    def process_properties(self, form):
        for callback, callback_params, path, childapi, schema, force_store_value in self.callbacks:
            has_option = False
            if callback_params is not None:
                for callback_param in callback_params.args:
                    if isinstance(callback_param, ParamContext):
                        raise ValueError(_('context is not supported from now for {}').format(path))
                    if isinstance(callback_param, ParamOption):
                        has_option = True
                        if callback.__name__ != 'tiramisu_copy' or 'expire' in childapi.option.properties():
                            if self.remotable == 'none':
                                raise ValueError(_('option {} only works when remotable is not "none"').format(path))
                            form[callback_param.option.impl_getpath()]['remote'] = True
                            remote = True
            if not has_option and form.get(path, {}).get('remote') == False:
                if 'expire' in childapi.option.properties():
                    if self.remotable == 'none':
                        raise ValueError(_('option {} only works when remotable is not "none"').format(path))
                    form.setdefault(path, {})['remote'] = True
                elif childapi.owner.isdefault():
                    # get calculated value and set clearable
                    schema[path]['value'] = childapi.value.get()
                    if self.clearable == 'minimum':
                        form.setdefault(path, {})['clearable'] = True

    def manage_callbacks(self, form):
        for callback, callback_params, path, childapi, schema, force_store_value in self.callbacks:
            if callback_params is not None:
                for callback_param in callback_params.args:
                    if isinstance(callback_param, ParamOption) and callback.__name__ == 'tiramisu_copy':
                        opt_path = callback_param.option.impl_getpath()
                        if form.get(opt_path, {}).get('remote') is not True:
                            form.setdefault(opt_path, {})
                            form[opt_path].setdefault('copy', []).append(path)

    def process(self,
                form):
        self.process_properties(form)
        self.manage_callbacks(form)


class Consistencies(object):
    def __init__(self, tiramisu_web):
        self.not_equal = []
        self.options = {}
        self.tiramisu_web = tiramisu_web

    def add(self, path, childapi):
        child = childapi.option.get()
        if isinstance(child, SynDynOption):
            child = child._impl_getopt()
        self.options[child] = path
        if not childapi.option.isoptiondescription():
            for consistency in childapi.option.consistencies():
                cons_id, func, all_cons_opts, params = consistency
                if func == '_cons_not_equal':
                    options = []
                    for option in all_cons_opts:
                        option = option()
                        options.append(option)
                    # FIXME transitive
                    self.not_equal.append((options, params.get('warnings_only')))

    def process(self, form):
        for not_equal, warnings_only in self.not_equal:
            not_equal_option = []
            for option in not_equal:
                not_equal_option.append(self.options[option])
            for idx, path in enumerate(not_equal_option):
                if form.get(path, {}).get('remote') is True:
                    continue
                options = copy(not_equal_option)
                options.pop(idx)
                form.setdefault(path, {}).setdefault('not_equal',
                                                     {'options': []})
                form[path]['not_equal']['options'].extend(options)
                if warnings_only or getattr(option, '_warnings_only', False):
                    form[path]['not_equal']['warnings'] = True


class Requires(object):
    def __init__(self, tiramisu_web):
        self.requires = {}
        self.options = {}
        self.tiramisu_web = tiramisu_web
        self.config = tiramisu_web.config
        self.remotable = tiramisu_web.remotable

    def manage_requires(self,
                        childapi,
                        path,
                        form,
                        action_hide,
                        current_action):
        for requires in childapi.option.requires():
            for require in requires:
                options, action, inverse, \
                    transitive, same_action, operator = require
                if transitive is False:
                    # transitive to "False" not supported yet for a requirement
                    if self.remotable == 'none':
                        raise ValueError('require set for {} but remotable is "none"'
                                         ''.format(path))
                    form.setdefault(path, {'key': path})['remote'] = True
                    return
                if same_action is False:
                    # same_action to "False" not supported yet for a requirement
                    if self.remotable == 'none':
                        raise ValueError('require set for {} but remotable is "none"'
                                         ''.format(path))
                    form.setdefault(path, {'key': path})['remote'] = True
                    return
                if operator == 'and':
                    # operator "and" not supported yet for a requirement
                    if self.remotable == 'none':
                        raise ValueError('require set for {} but remotable is "none"'
                                         ''.format(path))
                    form.setdefault(path, {'key': path})['remote'] = True
                    return
                for option, expected in options:
                    option_path = self.options.get(option)
                    if option_path is not None and action in action_hide:
                        if current_action is None:
                            current_action = action
                        elif current_action != action:
                            if self.remotable == 'none':
                                raise ValueError('require set for {} but remotable is "none"'
                                                 ''.format(path))
                            form.setdefault(option_path, {'key': option_path})['remote'] = True
                        if inverse:
                            act = 'show'
                            inv_act = 'hide'
                        else:
                            act = 'hide'
                            inv_act = 'show'
                        for exp in expected:
                            self.requires.setdefault(path,
                                                     {'expected': {}}
                                                     )['expected'].setdefault(exp,
                                                                              {}).setdefault(act,
                                                                                             []).append(option_path)
                        if isinstance(option, ChoiceOption):
                            choice_obj = self.config.unrestraint.option(option_path)
                            values = self.tiramisu_web.get_enum(choice_obj,
                                                                choice_obj.option.ismulti(),
                                                                option_path,
                                                                choice_obj.option.properties())
                            for value in values:
                                if value not in expected:
                                    self.requires.setdefault(path,
                                                              {'expected': {}}
                                                             )['expected'].setdefault(value,
                                                                                      {}).setdefault(inv_act,
                                                                                                     []).append(option_path)
                        self.requires[path].setdefault('default', {}).setdefault(inv_act, []).append(option_path)
                    else:
                        if self.remotable == 'none':
                            raise ValueError('require set for {} but remotable est "none"'
                                             ''.format(path))
                        form.setdefault(option_path, {'key': option_path})['remote'] = True

    def add(self, path, childapi, form):
        #collect id of all options
        child = childapi.option.get()
        if isinstance(child, SynDynOption):
            child = child._impl_getopt()
        self.options[child] = path
        current_action = None

        self.manage_requires(childapi,
                             path,
                             form,
                             ACTION_HIDE,
                             current_action)

    def is_remote(self, path, form):
        if self.remotable == 'all':
            return True
        else:
            return form.get(path) and form[path].get('remote', False)

    def process(self, form):
        dependencies = {}
        for path, values in self.requires.items():
            if form.get(path, {}).get('remote') is True:
                continue
            if 'default' in values:
                for option in values['default'].get('show', []):
                    if path == option:
                        form.setdefault(path, {'key': path})['remote'] = True
                    if not self.is_remote(option, form):
                        dependencies.setdefault(option,
                                                {'default': {}, 'expected': {}}
                                                )['default'].setdefault('show', [])
                        if path not in dependencies[option]['default']['show']:
                            dependencies[option]['default']['show'].append(path)
                for option in values['default'].get('hide', []):
                    if path == option:
                        form.setdefault(path, {'key': path})['remote'] = True
                    if not self.is_remote(option, form):
                        dependencies.setdefault(option,
                                                {'default': {}, 'expected': {}}
                                                )['default'].setdefault('hide', [])
                        if path not in dependencies[option]['default']['hide']:
                            dependencies[option]['default']['hide'].append(path)
            for expected, actions in values['expected'].items():
                if expected is None:
                    expected = ''
                for option in actions.get('show', []):
                    if path == option:
                        form.setdefault(path, {'key': path})['remote'] = True
                    if not self.is_remote(option, form):
                        dependencies.setdefault(option,
                                                {'expected': {}}
                                                )['expected'].setdefault(expected,
                                                                         {}).setdefault('show', [])
                        if path not in dependencies[option]['expected'][expected]['show']:
                            dependencies[option]['expected'][expected]['show'].append(path)
                for option in actions.get('hide', []):
                    if path == option:
                        form.setdefault(path, {'key': path})['remote'] = True
                    if not self.is_remote(option, form):
                        dependencies.setdefault(option,
                                                {'expected': {}}
                                                )['expected'].setdefault(expected,
                                                                         {}).setdefault('hide', [])
                        if path not in dependencies[option]['expected'][expected]['hide']:
                            dependencies[option]['expected'][expected]['hide'].append(path)
        for path, dependency in dependencies.items():
            form[path]['dependencies'] = dependency


class TiramisuDict:

    # propriete:
    #   hidden
    #   mandatory
    #   editable

    # FIXME model:
    # #optionnel mais qui bouge
    # choices/suggests
    # warning
    #
    # #bouge
    # owner
    # properties

    def __init__(self,
                 config,
                 root=None,
                 clearable="all",
                 remotable="minimum"):
        self.config = config
        self.root = root
        self.requires = None
        self.callbacks = None
        self.consistencies = None
        #all, minimum, none
        self.clearable = clearable
        #all, minimum, none
        self.remotable = remotable
        self.context_properties = self.config.property.get()
        self.context_permissives = self.config.permissive.get()

    def add_help(self,
                 obj,
                 childapi):
        hlp = childapi.information.get('help', None)
        if hlp is not None:
            obj['help'] = hlp

    def get_list(self, root, subchildapi):
        for childapi in subchildapi.list('all'):
            childname = childapi.option.name()
            if root is None:
                path = childname
            else:
                path = root + '.' + childname
            yield path, childapi

    def walk(self,
             root,
             subchildapi,
             schema,
             model,
             form,
             order,
             updates_status,
             init=False):
        if init:
            if form is not None:
                self.requires = Requires(self)
                self.consistencies = Consistencies(self)
                self.callbacks = Callbacks(self)
        else:
            init = False
        if subchildapi is None:
            if root is None:
                subchildapi = self.config.unrestraint.option
            else:
                subchildapi = self.config.unrestraint.option(root)
            isleadership = False
        else:
            isleadership = subchildapi.option.isleadership()
        leader_len = None
        for path, childapi in self.get_list(root, subchildapi):
            if isleadership and leader_len is None:
                leader_len = childapi.value.len()
            props_no_requires = set(childapi.option.properties())
            if form is not None:
                self.requires.add(path,
                                  childapi,
                                  form)
                self.consistencies.add(path,
                                       childapi)
                self.callbacks.add(path,
                                   childapi,
                                   schema,
                                   'force_store_value' in props_no_requires)
            childapi_option = childapi.option
            if model is not None and childapi.option.isoptiondescription() or not childapi_option.issymlinkoption():
                self.gen_model(model,
                               childapi,
                               path,
                               leader_len,
                               props_no_requires,
                               updates_status)
            if order is not None:
                order.append(path)
            if childapi.option.isoptiondescription():
                web_type = 'optiondescription'
                if childapi_option.isleadership():
                    type_ = 'array'
                else:
                    type_ = 'object'
                if schema is not None:
                    schema[path] = {'properties': OrderedDict(),
                                    'type': type_}
                    subschema = schema[path]['properties']
                else:
                    subschema = schema
                self.walk(path,
                          childapi,
                          subschema,
                          model,
                          form,
                          order,
                          updates_status)
            else:
                child = childapi_option.get()
                childtype = child.__class__.__name__
                if childtype == 'SynDynOption':
                    childtype = child._impl_getopt().__class__.__name__
                if childapi_option.issymlinkoption():
                    web_type = 'symlink'
                else:
                    web_type = childapi_option.type()
                    value = childapi.option.default()
                    if value not in [[], None]:
                        has_value = True
                    else:
                        value = None
                        has_value = False

                    is_multi = childapi_option.ismulti()
                    if is_multi:
                        default = childapi_option.defaultmulti()
                        if default not in [None, []]:
                            has_value = True
                        else:
                            default = None
                    else:
                        default = None

                if schema is not None:
                    self.gen_schema(schema,
                                    childapi,
                                    childapi_option,
                                    path,
                                    props_no_requires,
                                    value,
                                    default,
                                    is_multi,
                                    web_type)
                if form is not None:
                    self.gen_form(form,
                                  web_type,
                                  path,
                                  child,
                                  childapi_option,
                                  childtype,
                                  has_value)
            if schema is not None:
                if web_type != 'symlink':
                    schema[path]['title'] = childapi_option.doc()
                self.add_help(schema[path],
                              childapi)
        if init and form is not None:
            self.callbacks.process(form)
            self.requires.process(form)
            self.consistencies.process(form)
            del self.requires
            del self.consistencies


    def gen_schema(self,
                   schema,
                   childapi,
                   childapi_option,
                   path,
                   props_no_requires,
                   value,
                   default,
                   is_multi,
                   web_type):
        schema[path] = {'type': web_type}
        if childapi_option.issymlinkoption():
            schema[path]['opt_path'] = childapi_option.get().impl_getopt().impl_getpath()
        else:
            if value is not None:
                schema[path]['value'] = value

            if default is not None:
                schema[path]['default'] = default

            if is_multi:
                schema[path]['isMulti'] = is_multi

            if childapi_option.issubmulti():
                schema[path]['isSubMulti'] = True

            if 'auto_freeze' in props_no_requires:
                schema[path]['autoFreeze'] = True

            if web_type == 'choice':
                schema[path]['enum'] = self.get_enum(childapi,
                                                     is_multi,
                                                     path,
                                                     props_no_requires)

    def get_enum(self,
                 childapi,
                 is_multi,
                 path,
                 props_no_requires):
        values = childapi.value.list()
        empty_is_required = not childapi.option.isfollower() and is_multi
        if '' not in values and ((empty_is_required and not 'empty' in props_no_requires) or \
                (not empty_is_required and not 'mandatory' in props_no_requires)):
            values = [''] + list(values)
        return values

    def gen_form(self,
                 form,
                 web_type,
                 path,
                 child,
                 childapi_option,
                 childtype,
                 has_value):
        obj_form = {}
        if path in form:
            obj_form.update(form[path])
        if not childapi_option.issymlinkoption():
            if self.clearable == 'all':
                obj_form['clearable'] = True
            if has_value and self.clearable != 'none':
                obj_form['clearable'] = True
            if self.remotable == 'all' or childapi_option.has_dependency():
                obj_form['remote'] = True
            pattern = childapi_option.pattern()
            if pattern is not None:
                obj_form['pattern'] = pattern
            if childtype == 'FloatOption':
                obj_form['step'] = 'any'
            if childtype == 'PortOption':
                obj_form['min'] = child.impl_get_extra('_min_value')
                obj_form['max'] = child.impl_get_extra('_max_value')
            if web_type == 'choice':
                obj_form['type'] = 'choice'
            elif web_type in INPUTS:
                obj_form['type'] = 'input'
            if obj_form:
                form[path] = obj_form

    def calc_raises_properties(self, childapi):
        old_properties = childapi._option_bag.config_bag.properties
        del childapi._option_bag.config_bag.properties
        ret = childapi.option.properties(only_raises=True)
        childapi._option_bag.config_bag.properties = old_properties
        return ret

    def _gen_model_properties(self,
                              childapi,
                              path,
                              index,
                              props_no_requires):
        obj = {}
        isfollower = childapi.option.isfollower()
        if index is None and isfollower:
            # cannot calculated requires with follower without index
            props = props_no_requires
        else:
            props = set(childapi.property.get())
        if self.calc_raises_properties(childapi):
            obj['display'] = False
        if not isfollower and childapi.option.ismulti():
            if 'empty' in props:
                obj['required'] = True
                props.remove('empty')
            if 'mandatory' in props:
                obj['needs_len'] = True
                props.remove('mandatory')
        elif 'mandatory' in props:
            obj['required'] = True
            props.remove('mandatory')
        if 'frozen' in props:
            obj['readOnly'] = True
            props.remove('frozen')
        if 'hidden' in props:
            obj['hidden'] = True
            props.remove('hidden')
        if 'disabled' in props:
            obj['hidden'] = True
            props.remove('disabled')
        if props:
            lprops = list(props)
            lprops.sort()
            obj['properties'] = lprops
        return obj

    def gen_model(self,
                  model,
                  childapi,
                  path,
                  leader_len,
                  props_no_requires,
                  updates_status):
        if childapi.option.isoptiondescription():
            props = set(childapi.property.get())
            obj = {}
            if self.calc_raises_properties(childapi):
                obj['display'] = False
            if props:
                lprops = list(props)
                lprops.sort()
                obj['properties'] = lprops
            if 'hidden' in props or 'disabled' in props:
                obj['hidden'] = True
            try:
                self.config.option(path).option.get()
            except PropertiesOptionError:
                pass
        else:
            obj = self._gen_model_properties(childapi,
                                             path,
                                             None,
                                             props_no_requires)
            if childapi.option.isfollower():
                for index in range(leader_len):
                    follower_childapi = self.config.unrestraint.option(path, index)
                    sobj = self._gen_model_properties(follower_childapi,
                                                      path,
                                                      index,
                                                      props_no_requires)
                    self._get_model_value(follower_childapi,
                                          path,
                                          sobj,
                                          index,
                                          updates_status)
                    if sobj:
                        model.setdefault(path, {})[str(index)] = sobj
            else:
                self._get_model_value(childapi,
                                      path,
                                      obj,
                                      None,
                                      updates_status)
        if obj:
            if not childapi.option.isoptiondescription() and childapi.option.isfollower():
                model.setdefault(path, {})[None] = obj
            else:
                model[path] = obj

    def _get_model_value(self,
                         childapi,
                         path,
                         obj,
                         index,
                         updates_status):
        # FIXME unrestraint ...
        try:
            nchildapi = self.config.option(path, index=index)
            with warnings.catch_warnings(record=True) as warns:
                value = nchildapi.value.get()
            self._get_value_with_exception(obj,
                                           childapi,
                                           warns)
        except PropertiesOptionError:
            value = childapi.value.get()
            warns = []
        if value is not None and value != []:
            obj['value'] = value
            obj['owner'] = childapi.owner.get()

    def _get_value_with_exception(self,
                                  obj,
                                  childapi,
                                  values):
        for value in values:
            if isinstance(value.message, ValueErrorWarning):
                value.message.prefix = ''
                if childapi.option.isleader():
                    obj.setdefault('invalid', [])
                    obj['invalid'].append({'error': str(value.message),
                                           'index': value.message.index})
                else:
                    obj.setdefault('error', [])
                    obj['error'].append(str(value.message))
                    obj['invalid'] = True
            else:
                obj.setdefault('warnings', [])
                obj['warnings'].append(str(value.message))
                obj['hasWarnings'] = True

    def get_form(self, form):
        ret = []
        buttons = []
        dict_form = OrderedDict()
        for form_ in form:
            if 'key' in form_:
                dict_form[form_['key']] = form_
            elif form_.get('type') == 'submit':
                if 'cmd' not in form_:
                    form_['cmd'] = 'submit'
                buttons.append(form_)
            else:
                raise ValueError(_('unknown form {}').format(form_))

        for key, form_ in self.form.items():
            form_['key'] = key
            if key in dict_form:
                form_.update(dict_form[key])
            ret.append(form_)
        ret.extend(buttons)
        return ret

    def del_value(self, childapi, path, index):
        if index is not None and childapi.option.isleader():
            childapi.value.pop(index)
        elif index is None or childapi.option.isfollower():
            childapi.value.reset()
        else:
            multi = childapi.value.get()
            multi.pop(index)
            childapi.value.set(multi)

    def add_value(self, childapi, path, value):
        multi = childapi.value.get()
        multi.append(value)
        childapi.value.set(multi)

    def mod_value(self, childapi, path, index, value):
        if index is None or childapi.option.isfollower():
            childapi.value.set(value)
        else:
            multi = childapi.value.get()
            if not multi and index == 0:
                multi.append(value)
            else:
                multi[index] = value
            childapi.value.set(multi)

    def apply_updates(self,
                      oripath,
                      updates,
                      model_ori):
        updates_status = {}
        for update in updates:
            path = update['name']
            index = update.get('index')
            if oripath is not None and not path.startswith(oripath):
                raise ValueError(_('not in current area'))
            childapi = self.config.option(path)
            childapi_option = childapi.option
            if childapi_option.isfollower():
                childapi = self.config.option(path, index)
            with warnings.catch_warnings(record=True) as warns:
                #try:
                if update['action'] == 'modify':
                    self.mod_value(childapi,
                                   path,
                                   index,
                                   update.get('value'))
                elif update['action'] == 'delete':
                    self.del_value(childapi,
                                   path,
                                   index)
                elif update['action'] == 'add':
                    if childapi_option.ismulti():
                        self.add_value(childapi, path, update['value'])
                    else:
                        raise ValueError(_('only multi option can have action "add", but "{}" is not a multi').format(path))
                else:
                    raise ValueError(_('unknown action'))
                #except ValueError as err:
                #    updates_status.setdefault(path, {})[index] = err
                #    continue
            if warns != []:
                updates_status.setdefault(path, {}).setdefault(index, []).extend(warns)
        return updates_status

    def set_updates(self,
                    body):
        root_path = self.root
        updates = body.get('updates', [])
        updates_status = self.apply_updates(root_path,
                                            updates,
                                            body.get('model'))
        if 'model' in body:
            order = []
            old_model = body['model']
            new_model = self.todict(order=order,
                                    build_schema=False,
                                    build_form=False,
                                    updates_status=updates_status)['model']
            values = {'updates': list_keys(old_model, new_model, order, updates_status),
                      'model': new_model}
        else:
            values = None
        return values

    def todict(self,
               custom_form=[],
               build_schema=True,
               build_model=True,
               build_form=True,
               order=None,
               updates_status={}):
        rootpath = self.root
        if build_schema:
            schema = OrderedDict()
        else:
            schema = None
        if build_model:
            model = {}
        else:
            model = None
        if build_form:
            form = {}
            buttons = []
        else:
            form = None
        self.walk(rootpath,
                  None,
                  schema,
                  model,
                  form,
                  order,
                  updates_status,
                  init=True)
        if build_form:
            for form_ in custom_form:
                if 'key' in form_:
                    key = form_.pop('key')
                    form.setdefault(key, {}).update(form_)
                elif form_.get('type') == 'submit':
                    # FIXME if an Option has a key "null"?
                    form.setdefault(None, []).append(form_)
                else:
                    raise ValueError(_('unknown form {}').format(form_))
        ret = {}
        if build_schema:
            ret['schema'] = schema
        if build_model:
            ret['model'] = model
        if build_form:
            ret['form'] = form
        ret['version'] = '1.0'
        return ret


def list_keys(model_a, model_b, ordered_key, updates_status):
    model_a_dict = {}
    model_b_dict = {}

    keys_a = set(model_a.keys())
    keys_b = set(model_b.keys())

    keys = (keys_a ^ keys_b) | set(updates_status.keys())

    for key in keys_a & keys_b:
        keys_mod_a = set(model_a[key].keys())
        keys_mod_b = set(model_b[key].keys())
        if keys_mod_a != keys_mod_b:
            keys.add(key)
        else:
            for skey in keys_mod_a:
                if model_a[key][skey] != model_b[key][skey]:
                    keys.add(key)
                    break
    def sort_key(key):
        try:
            return ordered_key.index(key)
        except ValueError:
            return -1
    return sorted(list(keys), key=sort_key)
