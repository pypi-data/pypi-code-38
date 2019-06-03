

import html

from skipole import FailPage, ServerError
from skipole import skilift


def clear_call_data(call_data, keep=None):
    "Clears call data apart from set of required values"
    required = ['editedprojname',
                'editedprojurl',
                'editedprojversion',
                'editedprojbrief',
                'adminproj',
                'extend_nav_buttons',
                'caller_ident']
    if keep:
        required.extend(keep)
    temp_storage = {key:value for key,value in call_data.items() if key in required}
    call_data.clear()
    call_data.update(temp_storage)


def domtree(partdict, part_loc, contents, part_string_list, rows=1, indent=1):
    "Creates the contents of the domtable"

    # note: if in a container
    # part_loc = widget_name + '-' + container_number
    # otherwise part_loc = body, head, svg, section_name


    indent += 1
    padding = "padding-left : %sem;" % (indent,)
    u_r_flag = False
    last_row_at_this_level = 0

    parts = partdict['parts']

    # parts is a list of items
    last_index = len(parts)-1

    #Text   #characters..      #up  #up_right  #down  #down_right   #edit   #insert  #copy  #paste  #remove

    for index, part in enumerate(parts):
        part_location_string = part_loc + '-' + str(index)
        part_string_list.append(part_location_string)
        rows += 1
        part_type, part_dict = part
        # the row text
        if part_type == 'Widget' or part_type == 'ClosedWidget':
            part_name = 'Widget ' + part_dict['name']
            if len(part_name)>40:
                part_name = part_name[:35] + '...'
            contents.append([part_name, padding, False, ''])
            part_brief = html.escape(part_dict.get('brief',''))
            if len(part_brief)>40:
                part_brief = part_brief[:35] + '...'
            if not part_brief:
                part_brief = '-'
            contents.append([part_brief, '', False, ''])
        elif part_type == 'TextBlock':
            contents.append(['TextBlock', padding, False, ''])
            part_ref = part_dict['textref']
            if len(part_ref)>40:
                part_ref = part_ref[:35] + '...'
            if not part_ref:
                part_ref = '-'
            contents.append([part_ref, '', False, ''])
        elif part_type == 'SectionPlaceHolder':
            section_name = part_dict['placename']
            if section_name:
                section_name = "Section " + section_name
            else:
                section_name = "Section -None-"
            if len(section_name)>40:
                section_name = section_name[:35] + '...'
            contents.append([section_name, padding, False, ''])
            part_brief = html.escape(part_dict.get('brief',''))
            if len(part_brief)>40:
                part_brief = part_brief[:35] + '...'
            if not part_brief:
                part_brief = '-'
            contents.append([part_brief, '', False, ''])
        elif part_type == 'Text':
            contents.append(['Text', padding, False, ''])
            # in this case part_dict is the text string rather than a dictionary
            if len(part_dict)<40:
                part_str = html.escape(part_dict)
            else:
                part_str = html.escape(part_dict[:35] + '...')
            if not part_str:
                part_str = '-'
            contents.append([part_str, '', False, ''])
        elif part_type == 'HTMLSymbol':
            contents.append(['Symbol', padding, False, ''])
            part_text = part_dict['text']
            if len(part_text)<40:
                part_str = html.escape(part_text)
            else:
                part_str = html.escape(part_text[:35] + '...')
            if not part_str:
                part_str = '-'
            contents.append([part_str, '', False, ''])
        elif part_type == 'Comment':
            contents.append(['Comment', padding, False, ''])
            part_text = part_dict['text']
            if len(part_text)<33:
                part_str =  "&lt;!--" + part_text + '--&gt;'
            else:
                part_str = "&lt;!--" + part_text[:31] + '...'
            if not part_str:
                part_str = '&lt;!----&gt;'
            contents.append([part_str, '', False, ''])
        elif part_type == 'ClosedPart':
            if 'attribs' in part_dict:
                tag_name = "&lt;%s ... /&gt;" % part_dict['tag_name']
            else:
                tag_name = "&lt;%s /&gt;" % part_dict['tag_name']
            contents.append([tag_name, padding, False, ''])
            part_brief = html.escape(part_dict.get('brief',''))
            if len(part_brief)>40:
                part_brief = part_brief[:35] + '...'
            if not part_brief:
                part_brief = '-'
            contents.append([part_brief, '', False, ''])
        elif part_type == 'Part':
            if 'attribs' in part_dict:
                tag_name = "&lt;%s ... &gt;" % part_dict['tag_name']
            else:
                tag_name = "&lt;%s&gt;" % part_dict['tag_name']
            contents.append([tag_name, padding, False, ''])
            part_brief = html.escape(part_dict.get('brief',''))
            if len(part_brief)>40:
                part_brief = part_brief[:35] + '...'
            if not part_brief:
                part_brief = '-'
            contents.append([part_brief, '', False, ''])
        else:
            contents.append(['UNKNOWN', padding, False, ''])
            contents.append(['ERROR', '', False, ''])

        # UP ARROW
        if rows == 2:
            # second line in table cannot move upwards
            contents.append(['', '', False, '' ])
        else:
            contents.append(['&uarr;', 'width : 1%;', True, part_location_string])

        # UP RIGHT ARROW
        if u_r_flag:
            contents.append(['&nearr;', 'width : 1%;', True, part_location_string])
        else:
            contents.append(['', '', False, '' ])

        # DOWN ARROW
        if (indent == 2) and (index == last_index):
            # the last line at this top indent has been added, no down arrow
            contents.append(['', '', False, '' ])
        else:
            contents.append(['&darr;', 'width : 1%;', True, part_location_string])

        # DOWN RIGHT ARROW
        # set to empty, when next line is created if down-right not applicable
        contents.append(['', '', False, '' ])

        # EDIT
        contents.append(['Edit', 'width : 1%;', True, part_location_string])

        # INSERT or APPEND
        if part_type == 'Part':
            contents.append(['Insert', 'width : 1%;text-align: center;', True, part_location_string])
        else:
            contents.append(['Append', 'width : 1%;text-align: center;', True, part_location_string])

        # COPY
        contents.append(['Copy', 'width : 1%;', True, part_location_string])

        # PASTE
        contents.append(['Paste', 'width : 1%;', True, part_location_string])

        # REMOVE
        contents.append(['Remove', 'width : 1%;', True, part_location_string])

        u_r_flag = False
        if part_type == 'Part':
            if last_row_at_this_level and (part_dict['tag_name'] != 'script') and (part_dict['tag_name'] != 'pre'):
                # add down right arrow in previous row at this level, get loc_string from adjacent edit cell
                editcell = contents[last_row_at_this_level *11-5]
                loc_string = editcell[3]
                contents[last_row_at_this_level *11-6] = ['&searr;', 'width : 1%;', True, loc_string]
            last_row_at_this_level = rows
            rows = domtree(part_dict, part_location_string, contents, part_string_list, rows, indent)
            # set u_r_flag for next item below this one
            if  (part_dict['tag_name'] != 'script') and (part_dict['tag_name'] != 'pre'):
                u_r_flag = True
        else:
            last_row_at_this_level =rows

    return rows


