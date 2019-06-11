# -*- coding: utf-8 -*-

import os
import inspect
import json
import yaml
import codecs
import logging_helper
from future.builtins import str
from fdutil.path_tools import ensure_path_exists, path_in_site_or_user_packages

logging = logging_helper.setup_logging()

MODULE = u'module'  # TODO: Change this
NAME = u'name'
CLASS_NAME = u'class_name'
KEY = u'key'
MANDATORY = u'mandatory'
OPTIONAL = u'optional'
PROPERTY = u'property'
TYPE = u'type'
PROPERTY_NAME = u'property_name'
PROPERTIES = u'properties'
DEFAULT = u'default'
ATTRIBUTES = u'attributes'
FILENAME = u"filename"
MIXINS = u'mixins'
PARENT_MIXINS = u'parent_mixins'
DESCRIPTION = u'description'


class JsonApiPropertiesClassCreator(object):

    MANDATORY = MANDATORY
    OPTIONAL = OPTIONAL
    PROPERTY = PROPERTY
    PROPERTIES = PROPERTIES
    DEFAULT = DEFAULT
    TYPE = TYPE
    DESCRIPTION = DESCRIPTION

    GENERATED_CLASSES_FOLDER = u'generated_classes'

    def __init__(self,
                 class_name,
                 attributes=None,
                 property_name=None,
                 mixins=None,
                 key=None,
                 parent_mixins=None,
                 filename=None,
                 source=None):
        """
        Create a JsonApiPropertiesClass subclass so that attributes of
        the dictionary can be accessed with dot notation and with
        more meaningful names.

        Can also generate mixins for creating the DictionaryResponses
        inside other objects as properties

        The code produced can be written to a file for importing
        or can be used to call exec() dynamically.

        :param class_name: Name of the class you want to create

        :param property_name: Name of the property to be used in the mixins.
                              'key' is used if not provided.

        :param mixins: A list of class imports to add and to use as mixins for the base class
                       e.g. [u'from classutils import Observable',]

        :param attributes: Dictionary of attributes in the dictionary.
                           Can also be a list of dictionaries.
                           Key: key into the dictionary
                           Values: {MANDATORY:  bool: True if the attribute
                                                is mandatory. Throws an
                                                exception if accessed and
                                                not found.
                                    PROPERTY: Name of the property to be
                                              associated with the attribute.
                                              e.g the key could be 'w', but
                                              a property name of 'width' is
                                              preferred.
                                    PROPERTIES: Make multiple properties for
                                                the same attribute. Useful if
                                                you want the original and a
                                                verbose version. e.g. 'w' and
                                                'width'
                                    DEFAULT: The default value for an optional
                                             attribute. If not supplied, None
                                             is used.

        :param key: Supply if you want to create parent mixins. It's the key
                    into the dictionary in the parent dict that contains
                    the bit of the response we're making classes for

        :param filename: The destination filename without path. Can be supplied
                         on instantiation (here), or later in the call to
                         write_source_code if that is preferred.

        :param source: If the source file defining the changes is known, it should be
                       passed, e.g.if it is a json file.  If the source is the calling
                       Python file, then it's not necessary


        Example:
            JsonApiPropertiesClassCreator(class_name=u'Rectangle',
                                   key=u'rectangle',
                                   property_name=u'rect',
                                   attributes={u'w': {MANDATORY:  True,
                                                      PROPERTIES: [u'w', u'width'],},

                                                u'h': {MANDATORY:  True,
                                                       PROPERTIES: [u'h', u'height'],},

                                                u'col': {MANDATORY:  False,
                                                         PROPERTIES: [u'color', u'colour'],},

                                                u'border': {MANDATORY: False,
                                                            PROPERTY: u'border',
                                                            DEFAULT: 1},
                                                })

        Example generates the following code:

            # Code generated by apiutil.json_api.JsonApiPropertiesClassCreator

            from apiutil.json_api import JsonApiPropertiesClass


            class Rectangle(JsonApiPropertiesClass):

                def __init__(self,
                             *args,
                             **kwargs):
                    super(Rectangle, self).__init__(*args, **kwargs)

                @property
                def h(self):
                    return self.mandatory(u'h')

                @property
                def height(self):
                    return self.mandatory(u'h')

                @property
                def border(self):
                    return self.optional(u'border', 1)

                @property
                def color(self):
                    return self.optional(u'col')

                @property
                def colour(self):
                    return self.optional(u'col')

                @property
                def w(self):
                    return self.mandatory(u'w')

                @property
                def width(self):
                    return self.mandatory(u'w')


            class RectMandatoryMixIn(object):

                RECTANGLE = Rectangle  # Override in subclass if required

                def __init__(self):
                    super(RectMandatoryMixIn, self).__init__()

                @property
                def rect(self):
                    try:
                        return self._rect
                    except AttributeError:
                        pass
                    attribute = self.mandatory(u'rectangle')
                    if isinstance(attribute, list):
                        self._rect = [
                            Rectangle(
                                response=response,
                                parent=self)
                            for response in attribute]
                    elif isinstance(attribute, dict):
                        self._rect = Rectangle(
                            response=attribute,
                            parent=self)
                    else:
                        self._rect = None
                    return self._rect


            class RectOptionalMixIn(object):

                RECTANGLE = Rectangle  # Override in subclass if required

                def __init__(self):
                    super(RectOptionalMixIn, self).__init__()

                @property
                def rect(self):
                    try:
                        return self._rect
                    except AttributeError:
                        pass
                    attribute = self.optional(u'rectangle')
                    if isinstance(attribute, list):
                        self._rect = [
                            Rectangle(
                                response=response,
                                parent=self)
                            for response in attribute]
                    elif isinstance(attribute, dict):
                        self._rect = Rectangle(
                            response=attribute,
                            parent=self)
                    else:
                        self._rect = None
                    return self._rect
        """
        self.class_name = class_name

        if source is None:
            # Get the path to the calling source file
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            self.source = (module.__file__[:-1]
                           if module.__file__.endswith(u'.pyc')
                           else module.__file__)
        else:
            self.source = source

        self.folder_path = os.path.dirname(self.source)

        if isinstance(attributes, (list, tuple)):
            self.attributes = {}
            for attribute in attributes:
                self.attributes.update(attribute)
        else:
            self.attributes = attributes if attributes else []
        self.key = key
        self.property_name = property_name
        self.mixins = mixins if mixins else []
        self.parent_mixins = parent_mixins if parent_mixins else []

        self.imports = [self.mixin_import_string(**i)
                        for i in self.mixins] + [self.mixin_import_string(**i)
                                                 for i in self.parent_mixins]

        self.module_name = (filename
                            if filename
                            else (key
                                  if key
                                  else (property_name
                                        if property_name
                                        else self.class_name)))
        self.filename = u'{filename}.py'.format(filename=self.module_name).lower()

    def create_generated_classes_folder(self):
        folder = os.path.join(self.folder_path, self.GENERATED_CLASSES_FOLDER)
        ensure_path_exists(folder)
        init_file = os.path.join(self.folder_path, self.GENERATED_CLASSES_FOLDER, u'__init__.py')
        if not os.path.exists(init_file):
            with codecs.open(init_file, mode=u'w', encoding=u"utf-8") as init_file:
                init_file.write(u'# encoding: utf-8\n')

    @staticmethod
    def mixin_import_string(module,
                            name):
        return (u"from {dot}{module} import {name}"
                .format(dot=u'.' if u'.' not in module else u'',
                        module=module,
                        name=name))

    @property
    def base_class_name(self):
        return self.class_name if not self.mixins else u'{c}Base'.format(c=self.class_name)

    def settings(self,
                 attribute):
        return self.attributes[attribute]

    def attribute_properties(self,
                             attribute):
        settings = self.attributes[attribute]
        return settings.get(self.PROPERTIES, [settings.get(self.PROPERTY, attribute)])

    @staticmethod
    def mandatory_or_optional(mandatory):
        return (u'mandatory'
                if mandatory
                else u'optional')

    def mandatory_or_optional_attribute(self,
                                        attribute):
        return self.mandatory_or_optional(self.settings(attribute).get(self.MANDATORY, False))

    def attribute_conversion(self,
                             attribute):
        attribute_conversion = self.settings(attribute).get(self.TYPE)
        if not attribute_conversion:
            return u''
        try:
            attribute_conversion = attribute_conversion.__name__
        except AttributeError:
            raise TypeError(u'attribute conversion type "{act}" is not a type'
                            .format(act=attribute_conversion))
        return (u', cast={attribute_conversion}'
                .format(attribute_conversion=attribute_conversion))

    def attribute_default(self,
                          attribute):
        default = self.settings(attribute).get(self.DEFAULT)
        if default is None:
            return u""
        elif isinstance(default, str):
            return u", default='{d}'".format(d=default)  # TODO: Escape this
        else:
            return u', default={d}'.format(d=default)

    def attribute_docstring(self,
                            attribute):
        description = self.settings(attribute).get(self.DESCRIPTION, [])
        if not description:
            return []
        if isinstance(description, str):
            description = [description]
        docstring = [u'        """']
        docstring.extend([u'        ' + line for line in description])
        docstring.append(u'        """')
        return docstring

    @property
    def dictionary_response_class_code(self):

        class_code = [u'',
                      u'',
                      u'class {c_name}(JsonApiPropertiesClass):'.format(c_name=self.base_class_name),
                      u'']

        if not self.attributes:
            class_code.append(u'    pass')

        for attribute in self.attributes:

            for property_name in self.attribute_properties(attribute):

                getter = (u"JsonApiPropertiesClass.{mandatory_or_optional}_field(key='{f_name}'{default}{conversion})"
                          .format(mandatory_or_optional=self.mandatory_or_optional_attribute(attribute),
                                  f_name=attribute,
                                  default=self.attribute_default(attribute),
                                  conversion=self.attribute_conversion(attribute)))

                class_code.append(u'    {pname} = {getter}'.format(pname=property_name,
                                                                   getter=getter))
                # class_code.extend(self.attribute_docstring(attribute))
                # class_code.append(u'')

        return class_code

    @property
    def augmented_class_code(self):
        class_code = []
        if self.mixins:
            indent = u' ' * len(u'class {class_name}('.format(class_name=self.class_name))
            mixins = [u'{indent}{mixin},'.format(indent=indent,
                                                 mixin=mixin[u'name'])
                      for mixin in self.mixins]
            mixins[-1] = mixins[-1][:-1] + u'):'
            class_code.extend([u'',
                               u'',
                               u'class {class_name}({base_class_name},'
                               .format(class_name=self.class_name,
                                       base_class_name=self.base_class_name)])
            class_code.extend(mixins)
            class_code.extend([u'    pass  # Does this need an init?'])
        return class_code

    def accessor_mix_in_code(self,
                             mandatory):

        mandatory_or_optional = self.mandatory_or_optional(mandatory)
        property_name = self.property_name if self.property_name else self.key
        mixin_name = (u'{property_name}{m_or_o}MixIn'
                      .format(property_name=u''.join([part.capitalize()
                                                      for part in property_name.split(u'_')]),
                              m_or_o=mandatory_or_optional.capitalize()))
        if self.parent_mixins:
            indent = u',\n' + u' ' * len(u'class {mixin_name}('.format(mixin_name=mixin_name))
            parent_mixins = indent.join([pmi[u'name'] for pmi in self.parent_mixins])
        else:
            parent_mixins = u'object'

        return [u"",
                u"",
                u"class {mixin_name}({parent_mixins}):".format(mixin_name=mixin_name,
                                                               parent_mixins=parent_mixins),
                u'',
                u'    {CLASS_NAME} = {class_name}  # Override in subclass if required'
                .format(CLASS_NAME=self.class_name.upper(),
                        class_name=self.class_name),
                u'',
                u"    def __init__(self):",
                u"        super({mixin_name}, self).__init__()".format(mixin_name=mixin_name),
                u"",
                u"    @property",
                u"    @class_cache_result",
                u"    def {p}(self):".format(p=property_name),
                u"        attribute = self._get_{m_or_o}_field_value(u'{key}')".format(m_or_o=mandatory_or_optional,
                                                                                       key=self.key),
                u"        if isinstance(attribute, list):",
                u"            {p} = [".format(p=property_name),
                u"                {class_name}(".format(class_name=self.class_name),
                u"                    response=response,",
                u"                    parent=self)",
                u"                for response in attribute]",
                u"        elif isinstance(attribute, dict):",
                u"            {p} = {class_name}(".format(p=property_name,
                                                          class_name=self.class_name),
                u"                response=attribute,",
                u"                parent=self)",
                u"        else:",
                u"            raise TypeError(u'Unexpected type:{t} (Expected list or dict)'",
                u"                            .format(t=type(attribute).__name__))",
                u"        return {p}".format(p=property_name)]

    @property
    def code(self):
        code = [u'# encoding: utf-8',
                u'# Code generated by apiutil.json_api.JsonApiPropertiesClassCreator',
                u'',
                u'from apiutil.json_api import JsonApiPropertiesClass']
        if self.key:
            code.append(u'from classutils import class_cache_result ')

        code.extend(self.imports)

        code.extend(self.dictionary_response_class_code)

        if self.mixins:
            code.extend(self.augmented_class_code)

        if self.key:
            code.extend(self.accessor_mix_in_code(mandatory=True))
            code.extend(self.accessor_mix_in_code(mandatory=False))

        code.append(u'')

        return u'\n'.join(code)

    def file_path(self,
                  filename):

        filename = filename if filename else self.filename
        if not filename.endswith(u'.py'):
            filename += u'.py'
        return os.path.join(self.folder_path, self.GENERATED_CLASSES_FOLDER, filename)

    def generated_time(self,
                       filename):
        path = self.file_path(filename)
        return os.path.getmtime(path) if os.path.exists(path) else 0

    @property
    def source_modification_time(self):
        return os.path.getmtime(self.source)

    @property
    def creator_modification_time(self):
        return os.path.getmtime(__file__)

    @property
    def mixins_have_not_changed(self):
        # TODO: Figure out if mixins can be located
        return any([mixin
                    for mixin in self.mixins
                    if u'.' in mixin[MODULE]])

    def generated_code_is_up_to_date(self,
                                     filename):
        return (self.mixins_have_not_changed
                and self.generated_time(filename) > self.source_modification_time
                and self.generated_time(filename) > self.creator_modification_time)

    def write_source_code(self,
                          filename=None):
        if path_in_site_or_user_packages(self.folder_path):
            logging.debug(u'Site or user package location has been detected. '
                          u'Not generating code {path}'
                          .format(path=self.folder_path))
            return

        self.create_generated_classes_folder()

        file_path = self.file_path(filename)

        if self.generated_code_is_up_to_date(filename):
            logging.debug(u'Generated code is up to date: {path} '
                          .format(path=file_path))
            return

        generated_code = self.code
        try:
            with codecs.open(file_path, mode=u'r', encoding=u"utf-8") as f:
                existing_code = f.read().replace(u'\r', u'')
        except IOError:
            pass  # File does not exist, so go ahead with creation
        else:
            if existing_code == generated_code:
                logging.debug(u'Contents unchanged. '
                              u'Not writing generated code to {path}'
                              .format(path=file_path))
                return  # Code has not changed, don't bother writing
            else:
                logging.info(u'Changes detected. Generating code for {file_path}'
                             .format(file_path=file_path))

        with codecs.open(file_path, mode=u'w', encoding=u"utf-8") as of:
            of.write(generated_code)


def generate_api_files(definitions):
    """
    Generates code to represent the API from the provided definitions.

    :param definitions: Name of a json file that contains a list of
                        class definitions for the API. Each item in
                        the list is a set of parameters that can be
                        passed to JsonApiPropertiesClassCreator.

                        e.g. rectangle.json contains:

                            [{"class_name": "Rectangle",
                              "key": "rectangle",
                              "property_name": "rect",
                              "attributes": {"w": {"mandatory":  true,
                                                   "properties": ["w", "width"]},

                                             "h": {"mandatory":  true,
                                                   "properties": ["h", "height"]},

                                             "col": {"mandatory":  false,
                                                     "properties": ["color", "colour"]},

                                             "border": {"mandatory": false,
                                                        "property": "border",
                                                        "default": 1}
                                             })]

                        e.g. rectangle.yaml contains:
                            ---
                            - class_name: Rectangle
                              key: rectangle
                              property_name: rect
                              attributes:
                                w:
                                  mandatory: true
                                  properties:
                                  - w
                                  - width
                                h:
                                  mandatory: true
                                  properties:
                                  - h
                                  - height
                                col:
                                  mandatory: false
                                  properties:
                                  - color
                                  - colour
                                border:
                                  mandatory: false
                                  property: border
                                  default: 1
    :return: N/A
    """

    # Get the path to the calling folder
    frame = inspect.stack()[1]
    module_ = inspect.getmodule(frame[0])
    folder_path = os.path.dirname(module_.__file__)

    api_definition_file = os.path.join(folder_path, definitions)

    if path_in_site_or_user_packages(folder_path):
        logging.debug(u'Site or user package location has been detected. '
                      u'Not generating code for {api_definition_file}'
                      .format(api_definition_file=api_definition_file))
        return

    loader = json.load if api_definition_file.endswith(u'.json') else yaml.load
    with open(api_definition_file) as f:
        api = loader(f)

    for class_params in api:
        JsonApiPropertiesClassCreator(source=api_definition_file,
                                      **class_params).write_source_code()
