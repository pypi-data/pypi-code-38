

"""
named tuples used by other modules
"""

from collections import namedtuple

VersionInfo = namedtuple('VersionInfo', ['skipole', 'project'])

ProjectInfo = namedtuple('ProjectInfo', ['project', 'version', 'brief', 'path', 'default_language', 'subprojects', 'json_path', 'main_path', 'static_path', 'data_path'])

ItemInfo = namedtuple('ItemInfo', ['project', 'project_version', 'itemnumber', 'item_type', 'name', 'brief', 'path', 'label_list', 'change', 'parentfolder_number', 'restricted'])

PartInfo = namedtuple('PartInfo', ['project', 'pagenumber', 'page_part', 'section_name', 'name', 'location', 'part_type', 'brief'])

PageInfo = namedtuple('PageInfo', ['name', 'number', 'restricted', 'brief', 'item_type', 'responder', 'enable_cache', 'change', 'parentfolder_number'])

FolderInfo = namedtuple('FolderInfo', ['name', 'number', 'restricted', 'brief', 'contains_pages', 'contains_folders', 'change'])

WidgetInfo = namedtuple('WidgetInfo', ['project', 'pagenumber', 'section_name', 'name', 'location', 'containers', 'display_errors', 'brief'])

PageElement = namedtuple('PageElement', ['project', 'pagenumber', 'pchange', 'location', 'page_part', 'part_type', 'tag_name', 'brief', 'hide_if_empty', 'attribs'])

PageTextBlock = namedtuple('PageTextBlock', ['project', 'pagenumber', 'pchange', 'location', 'textref', 'tblock_project', 'failmessage', 'escape', 'linebreaks'])

WidgFieldInfo = namedtuple('WidgFieldInfo', ['tuple_widgfield', 'str_widgfield', 'str_comma_widgfield'])

PlaceHolderInfo = namedtuple('PlaceHolderInfo', ['project', 'pagenumber', 'section_name', 'alias', 'brief', 'multiplier', 'mtag'])

SectionElement = namedtuple('SectionElement', ['project', 'section_name', 'schange', 'location', 'part_type', 'tag_name', 'brief', 'show', 'hide_if_empty', 'attribs'])

SectionTextBlock = namedtuple('SectionTextBlock', ['project', 'section_name', 'schange', 'location', 'textref', 'tblock_project', 'failmessage', 'escape', 'linebreaks'])


WidgetDescription = namedtuple('WidgetDescription', ['modulename', 'classname', 'brief', 'fields', 'containers', 'illustration',
                                                     'fields_single', 'fields_list', 'fields_table', 'fields_dictionary', 'parent_widget', 'parent_container'])
# 'fields' is a list of field args
# 'containers' is the number of containers in the widget, 0 for none


FieldDescription = namedtuple('FieldDescription', ['field_arg', 'field_type', 'valdt', 'jsonset', 'cssclass', 'cssstyle'])

ContainerInfo = namedtuple('ContainerInfo', ['container', 'empty'])


ResponderInfo = namedtuple('ResponderInfo', ['responder',
                                             'module_name',
                                             'widgfield_required',
                                             'widgfield',
                                             'alternate_ident_required',
                                             'alternate_ident',
                                             'target_ident_required',
                                             'target_ident',
                                             'allowed_callers_required',
                                             'allowed_callers',
                                             'validate_option_available',
                                             'validate_option',
                                             'validate_fail_ident',
                                             'submit_option_available',
                                             'submit_option',
                                             'submit_required',
                                             'submit_list',
                                             'fail_ident',
                                             'field_options',
                                             'field_values_list',
                                             'field_list',
                                             'single_field_value',
                                             'single_field'
                                            ])


ValidatorInfo = namedtuple('ValidatorInfo', ['validator',
                                             'module_name',
                                             'message',
                                             'message_ref',
                                             'displaywidget',
                                             'allowed_values',
                                             'val_args'
                                            ])




