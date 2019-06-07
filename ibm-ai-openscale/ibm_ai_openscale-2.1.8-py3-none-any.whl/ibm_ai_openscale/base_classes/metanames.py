# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
from tabulate import tabulate
import copy
import logging


logger = logging.getLogger(__name__)


class MetaProp:
    def __init__(self, name, key, prop_type, required, example_value, ignored=False, hidden=False, default_value='', path=None, transform=lambda x, transform_param: x):
        self.key = key
        self.name = name
        self.prop_type = prop_type
        self.required = required
        self.example_value = example_value
        self.ignored = ignored
        self.hidden = hidden
        self.default_value = default_value
        self.path = path if path is not None else '/' + key
        self.transform = transform


class MetaNamesBase:
    _meta_props_definitions = []

    @classmethod
    def _validate(cls, meta_props):
        for meta_prop in cls._meta_props_definitions:
            if meta_prop.ignored is False:
                validate_meta_prop(meta_props, meta_prop.key, meta_prop.prop_type, meta_prop.required)
            else:
                logger.warning('\'{}\' meta prop is deprecated. It will be ignored.'.format(meta_prop.name))

    @classmethod
    def _check_types_only(cls, meta_props):
        for meta_prop in cls._meta_props_definitions:
            if meta_prop.ignored is False:
                validate_meta_prop(meta_props, meta_prop.key, meta_prop.prop_type, False)
            else:
                logger.warning('\'{}\' meta prop is deprecated. It will be ignored.'.format(meta_prop.name))

    @classmethod
    def get(cls):
        return sorted(list(map(lambda x: x.name, filter(lambda x: not x.ignored and not x.hidden, cls._meta_props_definitions))))

    @classmethod
    def show(cls):
        print(cls._generate_table(format='fancy_grid'))

    @classmethod
    def _generate_doc_table(cls):
        return cls._generate_table('MetaName', 'Type', 'Required', 'Default value', 'Example value',
                                    show_examples=True, format='grid', values_format='``{}``')

    @classmethod
    def _generate_doc(cls, resource_name):
        return """
Set of MetaNames for {}.

Available MetaNames:

{}

""".format(resource_name, cls._generate_doc_table())


    @classmethod
    def _generate_table(cls, name_label='meta_prop name', type_label='type',
                       required_label='required', default_value_label='default value',
                       example_value_label='example value', show_examples=False, format='simple', values_format='{}'):

        show_defaults = any(meta_prop.default_value is not '' for meta_prop in filter(lambda x: not x.ignored and not x.hidden, cls._meta_props_definitions))

        header = [name_label, type_label, required_label]

        if show_defaults:
            header.append(default_value_label)

        if show_examples:
            header.append(example_value_label)

        table_content = []

        for meta_prop in filter(lambda x: not x.ignored and not x.hidden, cls._meta_props_definitions):
            row = [meta_prop.name, meta_prop.prop_type.__name__, u'Y' if meta_prop.required else u'N']

            if show_defaults:
                row.append(values_format.format(meta_prop.default_value) if meta_prop.default_value is not '' else '')

            if show_examples:
                row.append(values_format.format(meta_prop.example_value) if meta_prop.example_value is not '' else '')

            table_content.append(row)

        table = tabulate(
            table_content, header,
            tablefmt=format
        )
        return table

    @classmethod
    def get_example_values(cls):
        return dict((x.key, x.example_value) for x in filter(lambda x: not x.ignored and not x.hidden, cls._meta_props_definitions))

    @classmethod
    def _generate_resource_metadata(cls, meta_props, transform_param=None, with_validation=False, initial_metadata={}):
        if with_validation:
            cls._validate(meta_props)

        metadata = copy.deepcopy(initial_metadata)

        def update_map(m, path, el):
            if type(m) is dict:
                if len(path) == 1:
                    m[path[0]] = el
                else:
                    if path[0] not in m:
                        if type(path[1]) is not int:
                            m[path[0]] = {}
                        else:
                            m[path[0]] = []
                    update_map(m[path[0]], path[1:], el)
            elif type(m) is list:
                if len(path) == 1:
                    if len(m) > len(path):
                        m[path[0]] = el
                    else:
                        m.append(el)
                else:
                    if len(m) <= path[0]:
                        m.append({})
                    update_map(m[path[0]], path[1:], el)
            else:
                raise ClientError('Unexpected metadata path type: {}'.format(type(m)))


        for meta_prop_def in filter(lambda x: not x.ignored, cls._meta_props_definitions):
            if meta_prop_def.key in meta_props:

                path = [int(p) if p.isdigit() else p for p in meta_prop_def.path.split('/')[1:]]

                update_map(
                    metadata,
                    path,
                    meta_prop_def.transform(meta_props[meta_prop_def.key], transform_param)
                )

        return metadata

    @classmethod
    def _generate_patch_payload(cls, current_metadata, meta_props, client=None, with_validation=False):
        if with_validation:
            cls._check_types_only(meta_props)

        updated_metadata = cls._generate_resource_metadata(meta_props, client, False, current_metadata)

        patch_payload = []

        def contained_path(metadata, path):
            if path[0] in metadata:
                if len(path) == 1:
                    return [path[0]]
                else:
                    rest_of_path = contained_path(metadata[path[0]], path[1:])
                    if rest_of_path is None:
                        return [path[0]]
                    else:
                        return [path[0]] + rest_of_path
            else:
                return []

        def get_value(metadata, path):
            if len(path) == 1:
                return metadata[path[0]]
            else:
                return get_value(metadata[path[0]], path[1:])

        def already_in_payload(path):
            return any([el['path'] == path for el in patch_payload])

        def update_payload(path):
            existing_path = contained_path(current_metadata, path)

            if len(existing_path) == len(path):
                patch_payload.append({
                    'op': 'replace',
                    'path': '/' + '/'.join(existing_path),
                    'value': get_value(updated_metadata, existing_path)
                })
            else:
                if not already_in_payload(existing_path):
                    patch_payload.append({
                        'op': 'add',
                        'path': '/' + '/'.join(existing_path + [path[len(existing_path)]]),
                        'value': get_value(updated_metadata, existing_path + [path[len(existing_path)]])
                    })

        for meta_prop_def in filter(lambda x: not x.ignored, cls._meta_props_definitions):
            if meta_prop_def.key in meta_props:

                path = [int(p) if p.isdigit() else p for p in meta_prop_def.path.split('/')[1:]]

                update_payload(path)

        return patch_payload