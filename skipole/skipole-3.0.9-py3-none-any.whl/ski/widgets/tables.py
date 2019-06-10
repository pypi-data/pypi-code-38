

from .. import skiboot, tag
from . import Widget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict


class ColorTable1(Widget):
    """A general table of coloured text strings
       A list of header strings, defines the number of columns
       A list of lists of text, text colour, background colour
       Note : there is no error display"""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'header_class':FieldArg("cssclass",""),
                        'even_class':FieldArg("cssclass", ""),
                        'odd_class':FieldArg("cssclass", ""),
                        'titles': FieldArgList('text', valdt=False, jsonset=False),
                        'contents': FieldArgTable(['text', 'text', 'text'])
                        }

    def __init__(self, name=None, brief='', **field_args):
        """
        header_class: class of the header row, if empty string, then no class will be applied
        even_class: class of even rows, if empty string, then no class will be applied
        odd_class: class of odd rows, if empty string, then no class will be applied
        titles: List of text used as headers, gives the number of columns
        contents: list of lists, 0:text in the table, 1:the text color, 2:the background color
        """
        Widget.__init__(self, name=name, tag_name="table", brief=brief, **field_args)

    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the table"
        titles = self.get_field_value("titles")
        contents = self.get_field_value("contents")
        cols = len(titles)
        if (not contents) or (not cols):
            return
        rows = int(len(contents) / cols)
        if not rows:
            return

        # set even row class
        if self.get_field_value('even_class'):
            even = self.get_field_value('even_class')
        else:
            even = ''
        # set odd row class
        if self.get_field_value('odd_class'):
            odd = self.get_field_value('odd_class')
        else:
            odd = ''

        if self.get_field_value('header_class'):
            self[0] = tag.Part(tag_name='tr', attribs={"class":self.get_field_value('header_class')})
        else:
            self[0] = tag.Part(tag_name='tr')

        for col in range(cols):
            self[0][col] = tag.Part(tag_name='th', text = titles[col])

        index = 0

        for row in range(rows):
            rownumber = row +1
            if even and (rownumber % 2):
                self[rownumber] = tag.Part(tag_name="tr", attribs={"class":even})
            elif odd and not (rownumber % 2):
                self[rownumber] = tag.Part(tag_name='tr', attribs={"class":odd})
            else:
                self[rownumber] = tag.Part(tag_name='tr')
            for col in range(cols):
                content = contents[index]
                celltext, cellcolor, cellbackground = contents[index]
                index += 1
                if cellcolor and cellbackground:
                    self[rownumber][col] = tag.Part(tag_name='td', text = celltext, attribs = {'style':'color:%s;background-color:%s;' % (cellcolor, cellbackground)})
                elif cellcolor:
                    self[rownumber][col] = tag.Part(tag_name='td', text = celltext, attribs = {'style':'color:%s;' % (cellcolor,)})
                elif cellbackground:
                    self[rownumber][col] = tag.Part(tag_name='td', text = celltext, attribs = {'style':'background-color:%s;' % (cellbackground,)})
                else:
                    self[rownumber][col] = tag.Part(tag_name='td', text = celltext)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<table>  <!-- with widget id and class widget_class -->
  <tr> <!-- with header class -->
    <th> <!-- title taken from titles list --> </th>
    <!-- continued with number of titles in titles list -->
  </tr>
  <tr> <!-- with class  from even or odd classes -->
    <td> <!-- with style from each contents element index 1 and 2 -->
      <!-- with text from each contents element index 0 -->
    </td>
    <!-- with appropriate number of columns matching titles-->
  </tr>
  <!-- with appropriate number of rows -->
</table>"""


class TwoColTable1(Widget):
    """A table of two columns, the columns being text strings
       The first row is two header titles
       Note : there is no error display"""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'header_class':FieldArg("cssclass",""),
                        'even_class':FieldArg("cssclass", ""),
                        'odd_class':FieldArg("cssclass", ""),
                        'title1':FieldArg('text', ''),
                        'title2':FieldArg('text', ''),
                        'col1':FieldArgList('text', valdt=False, jsonset=True),
                        'col2':FieldArgList('text', valdt=False, jsonset=True)
                        }

    def __init__(self, name=None, brief='', **field_args):
        """
        header_class: class of the header row, if empty string, then no class will be applied
        even_class: class of even rows, if empty string, then no class will be applied
        odd_class: class of odd rows, if empty string, then no class will be applied
        title1: The header title over the first text column
        title2: The header title over the second text column
        col1 : A list of text strings to place in the first column
        col2: A list of text strings to place in the second column
        """
        Widget.__init__(self, name=name, tag_name="table", brief=brief, **field_args)

    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the table"
        col_list1 = self.get_field_value("col1")
        col_list2 = self.get_field_value("col2")
        header = 0
        if self.get_field_value('title1') or self.get_field_value('title2'):
            header = 1
            if self.get_field_value('header_class'):
                self[0] = tag.Part(tag_name='tr', attribs={"class":self.get_field_value('header_class')})
            else:
                self[0] = tag.Part(tag_name='tr')
            self[0][0] = tag.Part(tag_name='th', text = self.get_field_value('title1'))
            self[0][1] = tag.Part(tag_name='th', text = self.get_field_value('title2'))
        # set even row colour
        if self.get_field_value('even_class'):
            even = self.get_field_value('even_class')
        else:
            even = ''
        # set odd row colour
        if self.get_field_value('odd_class'):
            odd = self.get_field_value('odd_class')
        else:
            odd = ''
        # create rows
        if len(col_list1) == len(col_list2):
            rows = len(col_list1)
        elif len(col_list1) > len(col_list2):
            rows = len(col_list1)
            col_list2.extend(['']*(rows - len(col_list2)))
        else:
            rows = len(col_list2)
            col_list1.extend(['']*(rows - len(col_list1)))
        for index in range(rows):
            rownumber = index+header
            if even and (rownumber % 2) :
                self[rownumber] = tag.Part(tag_name="tr", attribs={"class":even})
            elif odd and not (rownumber % 2):
                self[rownumber] = tag.Part(tag_name='tr', attribs={"class":odd})
            else:
                self[rownumber] = tag.Part(tag_name='tr')
            self[rownumber][0] = tag.Part(tag_name='td', text = col_list1[index])
            self[rownumber][1] = tag.Part(tag_name='td', text = col_list2[index])


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<table>  <!-- with widget id and class widget_class -->
  <tr> <!-- with header class -->
    <th> <!-- title1 --> </th>
    <th> <!-- title2 --> </th>
  </tr>
  <tr> <!-- with class  from even or odd classes -->
    <td> <!-- col1 text string --> </td>
    <td> <!-- col2 text string --> </td>
  </tr>
  <!-- rows repeated -->
</table>"""


class ThreeColTable1(Widget):
    """A table of three columns, the columns being text strings
       The first row is three header titles
       Note : there is no error display"""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'header_class':FieldArg("cssclass",""),
                        'even_class':FieldArg("cssclass", ""),
                        'odd_class':FieldArg("cssclass", ""),
                        'title1':FieldArg('text', ''),
                        'title2':FieldArg('text', ''),
                        'title3':FieldArg('text', ''),
                        'col1':FieldArgList('text', valdt=False, jsonset=True),
                        'col2':FieldArgList('text', valdt=False, jsonset=True),
                        'col3':FieldArgList('text', valdt=False, jsonset=True)
                        }

    def __init__(self, name=None, brief='', **field_args):
        """
        header_class: class of the header row, if empty string, then no class will be applied
        even_class: class of even rows, if empty string, then no class will be applied
        odd_class: class of odd rows, if empty string, then no class will be applied
        title1: The header title over the first text column
        title2: The header title over the second text column
        title3: The header title over the third text column
        col1 : A list of text strings to place in the first column
        col2: A list of text strings to place in the second column
        col3: A list of text strings to place in the third column
        """
        Widget.__init__(self, name=name, tag_name="table", brief=brief, **field_args)

    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the table"
        col_list1 = self.get_field_value("col1")
        col_list2 = self.get_field_value("col2")
        col_list3 = self.get_field_value("col3")
        header = 0
        if self.get_field_value('title1') or self.get_field_value('title2') or self.get_field_value('title3'):
            header = 1
            if self.get_field_value('header_class'):
                self[0] = tag.Part(tag_name='tr', attribs={"class":self.get_field_value('header_class')})
            else:
                self[0] = tag.Part(tag_name='tr')
            self[0][0] = tag.Part(tag_name='th', text = self.get_field_value('title1'))
            self[0][1] = tag.Part(tag_name='th', text = self.get_field_value('title2'))
            self[0][2] = tag.Part(tag_name='th', text = self.get_field_value('title3'))
        # set even row colour
        if self.get_field_value('even_class'):
            even = self.get_field_value('even_class')
        else:
            even = ''
        # set odd row colour
        if self.get_field_value('odd_class'):
            odd = self.get_field_value('odd_class')
        else:
            odd = ''
        # create rows
        rows = max( len(col_list1), len(col_list2), len(col_list3) )
        if rows > len(col_list1):
            col_list1.extend(['']*(rows - len(col_list1)))
        if rows > len(col_list2):
            col_list2.extend(['']*(rows - len(col_list2)))
        if rows > len(col_list3):
            col_list3.extend(['']*(rows - len(col_list3)))

        for index in range(rows):
            rownumber = index+header
            if even and (rownumber % 2) :
                self[rownumber] = tag.Part(tag_name="tr", attribs={"class":even})
            elif odd and not (rownumber % 2):
                self[rownumber] = tag.Part(tag_name='tr', attribs={"class":odd})
            else:
                self[rownumber] = tag.Part(tag_name='tr')
            self[rownumber][0] = tag.Part(tag_name='td', text = col_list1[index])
            self[rownumber][1] = tag.Part(tag_name='td', text = col_list2[index])
            self[rownumber][2] = tag.Part(tag_name='td', text = col_list3[index])

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<table>  <!-- with widget id and class widget_class -->
  <tr> <!-- with header class -->
    <th> <!-- title1 --> </th>
    <th> <!-- title2 --> </th>
    <th> <!-- title3 --> </th>
  </tr>
  <tr> <!-- with class  from even or odd classes -->
    <td> <!-- col1 text string --> </td>
    <td> <!-- col2 text string --> </td>
    <td> <!-- col3 text string --> </td>
  </tr>
  <!-- rows repeated -->
</table>"""


class TextBlockTable2(Widget):
    """A table of two columns, the first column being text strings
       the second column being TextBlocks
       The first row is two header titles
       Note : on error the whole widget is shown as errored, there is no error paragraph"""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'header_class':FieldArg("cssclass",""),
                        'even_class':FieldArg("cssclass", ""),
                        'odd_class':FieldArg("cssclass", ""),
                        'title1':FieldArg('text', ''),
                        'title2':FieldArg('text', ''),
                        'contents':FieldArgTable(['text', 'textblock_ref'])
                        }

    def __init__(self, name=None, brief='', **field_args):
        """
        header_class: class of the header row, if empty string, then no class will be applied
        even_class: class of even rows, if empty string, then no class will be applied
        odd_class: class of odd rows, if empty string, then no class will be applied
        title1: The header title over the first text column
        title2: The header title over the second text column
        contents: col 0 is the text to place in the first column,
                  col 1 is the textblock to place in the second colum
        """
        Widget.__init__(self, name=name, tag_name="table", brief=brief, **field_args)


    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the table"
        fieldtable = self.get_field_value("contents")
        header = 0
        if self.get_field_value('title1') or self.get_field_value('title2'):
            header = 1
            if self.get_field_value('header_class'):
                self[0] = tag.Part(tag_name='tr', attribs={"class":self.get_field_value('header_class')})
            else:
                self[0] = tag.Part(tag_name='tr')
            self[0][0] = tag.Part(tag_name='th', text = self.get_field_value('title1'))
            self[0][1] = tag.Part(tag_name='th', text = self.get_field_value('title2'))
        # set even row colour
        if self.get_field_value('even_class'):
            even = self.get_field_value('even_class')
        else:
            even = ''
        # set odd row colour
        if self.get_field_value('odd_class'):
            odd = self.get_field_value('odd_class')
        else:
            odd = ''
        # create rows
        for index, row in enumerate(fieldtable):
            rownumber = index+header
            if even and (rownumber % 2) :
                self[rownumber] = tag.Part(tag_name="tr", attribs={"class":even})
            elif odd and not (rownumber % 2):
                self[rownumber] = tag.Part(tag_name='tr', attribs={"class":odd})
            else:
                self[rownumber] = tag.Part(tag_name='tr')
            self[rownumber][0] = tag.Part(tag_name='td', text = row[0])
            self[rownumber][1] = tag.Part(tag_name='td', text = row[1])


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<table>  <!-- with widget id and class widget_class -->
  <tr> <!-- with header class -->
    <th> <!-- title1 --> </th>
    <th> <!-- title2 --> </th>
  </tr>
  <tr> <!-- with class  from even or odd classes -->
    <td> <!-- text string --> </td>
    <td> <!-- textblock --> </td>
  </tr>
  <!-- rows repeated -->
</table>"""



class ButtonTextBlockTable1(Widget):
    "A form consisting of a table of form buttons and textblocks"

    error_location = (0,0,0)

    arg_descriptions = {'action':FieldArg("url", ""),
                        'header_class':FieldArg("cssclass",""),
                        'even_class':FieldArg("cssclass", ""),
                        'odd_class':FieldArg("cssclass", ""),
                        'col1_button_title':FieldArg('text', ''),
                        'col2_text_title':FieldArg('text', ''),
                        'hidden_field1':FieldArg("text", valdt=True),
                        'hidden_field2':FieldArg("text", valdt=True),
                        'hidden_field3':FieldArg("text", valdt=True),
                        'hidden_field4':FieldArg("text", valdt=True),
                        'buttons':FieldArgTable(['text', 'textblock_ref'], valdt=True),
                        'button_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", ''),
                        'table_class':FieldArg("cssclass", '')
                        }

    def __init__(self, name=None, brief='', **field_args):
        """
        action: The target page link ident, url or label
        header_class: class of the header row, if empty string, then no class will be applied
        even_class: class of even rows, if empty string, then no class will be applied
        odd_class: class of odd rows, if empty string, then no class will be applied
        button_class: class set on the buttons
        col1_button_title: The title of the first column, above the buttons
        col2_text_title: The title of the second colum, above the textblock
        hidden_field1-4: four hidden fields
        buttons: field name is the button name,
                 text is the values on the button, and which will be returned
                 textbock_ref is the reference of the textblock appearing in the second column
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # hidden error
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # The form
        self[1] = tag.Part(tag_name='form', attribs={"role":"form", "method":"post"})

        # The location 1,0 is the table
        self[1][0] = tag.Part(tag_name="table")


    def _build(self, page, ident_list, environ, call_data, lang):
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
        if not self.get_field_value("action"):
            # setting self._error replaces the entire tag
            self._error = "Warning: No form action"
            return
        actionurl = skiboot.get_url(self.get_field_value("action"),  proj_ident=page.proj_ident)
        if not actionurl:
            # setting self._error replaces the entire tag
            self._error = "Warning: broken link"
            return
        # update the action of the form
        self[1].update_attribs({"action": actionurl})

        # build the table
        table = self[1][0]
        if self.get_field_value('table_class'):
            table.update_attribs({"class":self.get_field_value('table_class')})

        title1 = self.get_field_value("col1_button_title")
        title2 = self.get_field_value("col2_text_title")

        # set even row colour
        if self.get_field_value('even_class'):
            evenclass = self.get_field_value('even_class')
        else:
            evenclass = ''
        # set odd row colour
        if self.get_field_value('odd_class'):
            oddclass = self.get_field_value('odd_class')
        else:
            oddclass = ''
        # set header row colour
        if self.get_field_value('header_class'):
            headerclass = self.get_field_value('header_class')
        else:
            headerclass = ''
        # set button class
        if self.get_field_value('button_class'):
            buttonclass = self.get_field_value('button_class')
        else:
            buttonclass = ''

        rows = self.get_field_value('buttons')

        for num, row in enumerate(rows):
            if title1 or title2:
                rownumber = num+1
            else:
                rownumber = num
            if (not num) and (title1 or title2):
                if headerclass:
                    table[0]  = tag.Part(tag_name="tr", attribs={"class":headerclass})
                else:
                    table[0]  = tag.Part(tag_name="tr")
                if title1:
                    table[0][0] = tag.Part(tag_name="th", text=title1)
                else:
                    table[0][0] = tag.Part(tag_name="th")
                if title2:
                    table[0][1] = tag.Part(tag_name="th", text=title2)
                else:
                    table[0][1] = tag.Part(tag_name="th")
            if evenclass and (rownumber % 2):
                table[rownumber]  = tag.Part(tag_name="tr", attribs={"class":evenclass})
            elif oddclass and not (rownumber % 2):
                table[rownumber]  = tag.Part(tag_name="tr", attribs={"class":oddclass})
            else:
                table[rownumber]  = tag.Part(tag_name="tr")
            # each row has parameters 0 and 1, and two columns
            table[rownumber][0] = tag.Part(tag_name="td")
            table[rownumber][1] = tag.Part(tag_name="td")
            # submit button
            if buttonclass:
                table[rownumber][0][0]= tag.ClosedPart(tag_name="input",
                                                    attribs = {"value":row[0],
                                                    "type":"submit",
                                                    "name":self.get_formname('buttons'),
                                                    "class":buttonclass})
            else:
                table[rownumber][0][0]= tag.ClosedPart(tag_name="input",
                                                    attribs = {"value":row[0],
                                                    "type":"submit",
                                                    "name":self.get_formname('buttons')})
            # textblock
            table[rownumber][1][0] = row[1]

        # add ident and four hidden fields
        self.add_hiddens(self[1], page)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden paragraph, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <form method="post">  <!-- with CSS class given by widget_class, action given by action field -->
    <table>  <!-- with CSS class given by table_class -->
      <tr> <!-- with header class -->
        <th> <!-- title1 --> </th>
        <th> <!-- title2 --> </th>
      </tr>
      <!-- Then the following row repeated for each row given in the buttons field -->
      <tr> <!-- with class  from even or odd classes -->
        <td>
          <input type=\"submit\" />
               <!-- button name set to name of buttons field which forms the widgfield returned -->
              <!-- button value set to buttons row text value and is the value returned when the button is pressed -->
        </td>
        <td> <!-- textblock, found from row textbock_ref --> </td>
      </tr>
      <!-- rows repeated -->
    </table>
    <!-- hidden fields -->
  </form>
</div>"""

