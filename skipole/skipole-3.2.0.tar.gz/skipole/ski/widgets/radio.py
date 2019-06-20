

"""Contains widgets for radio forms"""


from .. import skiboot, tag, excepts
from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict



class RadioButton1(Widget):
    """A radiobutton widget. Without a form or submit button, typically included within a form"""

    error_location = (0,0,0)

    arg_descriptions = {'radio_values':FieldArgList("text"),
                       'radio_text':FieldArgList("text"),
                       'radio_checked':FieldArg("text", '', valdt=True, jsonset=True),
                       'error_class':FieldArg("cssclass", ""),
                       'inputdiv_class':FieldArg("cssclass", ""),
                       'label_class':FieldArg("cssclass", ""),
                       'div_class':FieldArg("cssclass", "")
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        radio_values: list of options, one of these values will be returned
        radio_text: List of labels
        radio_checked: value to be checked, this is the field returned
        show: True if this widget is to be visible
        error_class: css class applied to the normally hidden error div
        inputdiv_class: css class applied to each radio div
        label_class: css class applied to each label text on the right of the radio button
        div_class: css class applied to the div after the error paragraph
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # hidden error
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        self[1] = tag.Part(tag_name="div")


    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the radio buttons"

        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")
        if self.get_field_value('div_class'):
            self[1].update_attribs({"class":self.get_field_value('div_class')})
        checked = self.get_field_value('radio_checked')
        name = self.get_formname('radio_checked')
        label_class = self.get_field_value('label_class')
        self[1].insert_id()
        one_id = self[1].get_id()
        for index,val in enumerate(self.get_field_value('radio_values')):
            if self.get_field_value('inputdiv_class'):
                inputblock = tag.Part(tag_name="div", attribs={"class":self.get_field_value('inputdiv_class')})
            else:
                inputblock = tag.Part(tag_name="div")
            if checked and (checked == val):
                prt = tag.ClosedPart(tag_name="input",
                                            attribs ={"name":name,
                                                      "value":val,
                                                      "checked":"checked",
                                                      "type":"radio"})
                # ensure only one item checked
                checked = ''
            else:
                prt = tag.ClosedPart(tag_name="input",
                                            attribs ={"name":name,
                                                      "value":val,
                                                      "type":"radio"})
            prt.insert_id(one_id + '_' + str(index) + '_0')
            inputblock[0] = prt
            inputblock[1] = tag.Part(tag_name="label")
            if label_class:
                inputblock[1].attribs = {"class": label_class, 'for':inputblock[0].get_id()}
            else:
                inputblock[1].attribs = {'for':inputblock[0].get_id()}
            try:
                inputblock[1][0] = self.get_field_value('radio_text')[index]
            except IndexError:
                inputblock[1][0] = ''
            self[1].append(inputblock)


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """<div>  <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden div, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <div>  <!-- with class attribute set to div_class if a class is set -->
    <!-- Then for each radio field -->
    <div> <!-- with class set to inputdiv_class if a class is set -->
      <input type='radio' /> <!-- with name from 'radio_checked' widgfield and values from radio_values -->
      <label> <!-- with class set to label_class and content from radio_text -->
      </label>
    </div>
  </div>
</div>
"""


class RadioTable(Widget):
    """A div containing a table of radio controls with textblocks. Without a form or submit button, typically included within a form

       The first colum is the radio control with its associated label, the second column is either a textblock, or (if given)
       a string of text"""

    error_location = (0,0,0)

    arg_descriptions = {'table_class':FieldArg("cssclass", ''),
                        'header_class':FieldArg("cssclass", ''),
                        'even_class':FieldArg("cssclass", ''),
                        'odd_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", ''),
                        'title1':FieldArg("text"),
                        'title2':FieldArg("text"),
                        'radio_checked':FieldArg("text", valdt=True),
                        'contents':FieldArgTable(['text', 'text', 'textblock_ref', 'text'])
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        table_class: class of the table, if empty string, then no class will be applied
        header_class: class of the header row, if empty string, then no class will be applied
        even_class: class of even rows, if empty string, then no class will be applied
        odd_class: class of odd rows, if empty string, then no class will be applied
        error_class: css class applied to the normally hidden error paragraph
        title1: The header title over the first column
        title2: The header title over the second column
        radio_checked: value to be checked, this is the field returned
        contents: table of values, labels and textblock or text
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # hidden error
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        self[1] = tag.Part(tag_name='table')


    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the table of radio buttons"
        if self.get_field_value('error_class'):
            self[0].update_attribs({"class":self.get_field_value('error_class')})
        if self.error_status:
            self[0].del_one_attrib("style")

        checked = self.get_field_value('radio_checked')
        name = self.get_formname('radio_checked')
        fieldtable = self.get_field_value("contents")
        if self.get_field_value('table_class'):
            self[1].attribs={"class":self.get_field_value('table_class')}
        # set table header with titles
        header = 0
        if self.get_field_value('title1') or self.get_field_value('title2'):
            header = 1
            if self.get_field_value('header_class'):
                self[1][0] = tag.Part(tag_name='tr', attribs={"class":self.get_field_value('header_class')})
            else:
                self[1][0] = tag.Part(tag_name='tr')
            self[1][0][0] = tag.Part(tag_name='th', text = self.get_field_value('title1'))
            self[1][0][1] = tag.Part(tag_name='th', text = self.get_field_value('title2'))
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

        for index,val in enumerate(fieldtable):
            rownumber = index+header
            if even and (rownumber % 2) :
                self[1][rownumber] = tag.Part(tag_name="tr", attribs={"class":even})
            elif odd and not (rownumber % 2):
                self[1][rownumber] = tag.Part(tag_name='tr', attribs={"class":odd})
            else:
                self[1][rownumber] = tag.Part(tag_name='tr')
            # first col
            col0 = tag.Part(tag_name='td')
            if checked and (checked == val[0]):
                input_prt = tag.ClosedPart(tag_name="input",
                                            attribs ={"name":name,
                                                      "value":val[0],
                                                      "checked":"checked",
                                                      "type":"radio"})
                # ensure only one item checked
                checked = ''
            else:
                input_prt = tag.ClosedPart(tag_name="input",
                                            attribs ={"name":name,
                                                      "value":val[0],
                                                      "type":"radio"})
            input_label = tag.Part(tag_name='label')
            input_label[0] = input_prt
            input_label[1] = val[1]
            col0[0] = input_label
            # second col
            col1 = tag.Part(tag_name='td')
            if val[3]:
                # if text is given, this is set into the column
                col1[0] = val[3]
            else:
                # if no text, then the texblock is set
                col1[0] = val[2]
            # add the two columns to the row
            self[1][rownumber][0] = col0
            self[1][rownumber][1] = col1


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden paragraph, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <table>  <!-- with CSS class given by table_class -->
    <tr> <!-- with header class -->
      <th> <!-- title1 --> </th>
      <th> <!-- title2 --> </th>
    </tr>
    <!-- Then the following row repeated for each row given in the contents field -->
    <tr> <!-- with class  from even or odd classes -->
      <td>
        <label>
          <input type="radio" />
          <!-- with name from name of radio_checked field, and value from the contents -->
          <!-- label text from contents -->
        </label>
      </td>
      <td> <!-- textblock, found from row textbock_ref --> </td>
    </tr>
    <!-- rows repeated -->
  </table>
</div>"""
            


class TwoRadioOptions(Widget):
    """A two option radio control. Without a form or submit button, typically included within a form
       label appeares to the right of the buttons
        """
    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'label1':FieldArg("text"),
                        'div_class1':FieldArg("cssclass", ''),
                        'value1':FieldArg("text"),
                        'label2':FieldArg("text"),
                        'div_class2':FieldArg("cssclass", ''),
                        'value2':FieldArg("text"),
                        'radio_checked':FieldArg("text", valdt=True)
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        div_class1: css class of div containing first radio box
        label1: text label to appear after the first radio button
        value1: the value returned if the first radio button is chosen
        div_class2: css class of div containing second radio box
        label2: text label to appear after the second radio button
        value2: the value returned if the second radio button is chosen
        radio_checked: value to be checked, this is the field returned
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name='div')
        self[0][0] = tag.Part(tag_name='label')
        self[1] = tag.Part(tag_name='div')
        self[1][0] = tag.Part(tag_name='label')


    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the radio buttons"
        checked = self.get_field_value('radio_checked')
        name = self.get_formname('radio_checked')

        if self.get_field_value('div_class1'):
            self[0].update_attribs({"class":self.get_field_value('div_class1')})
        if self.get_field_value('div_class2'):
            self[1].update_attribs({"class":self.get_field_value('div_class2')})

        if checked and (checked == self.get_field_value('value1')):
            self[0][0][0] = tag.ClosedPart(tag_name="input",
                                     attribs ={"name":name,
                                     "value":self.get_field_value('value1'),
                                     "checked":"checked",
                                     "type":"radio"})
        else:
            self[0][0][0] = tag.ClosedPart(tag_name="input",
                                     attribs ={"name":name,
                                     "value":self.get_field_value('value1'),
                                     "type":"radio"})
        self[0][0][1] = self.get_field_value('label1')
        if checked and (checked == self.get_field_value('value2')):
            self[1][0][0] = tag.ClosedPart(tag_name="input",
                                     attribs ={"name":name,
                                     "value":self.get_field_value('value2'),
                                     "checked":"checked",
                                     "type":"radio"})
        else:
            self[1][0][0] = tag.ClosedPart(tag_name="input",
                                     attribs ={"name":name,
                                     "value":self.get_field_value('value2'),
                                     "type":"radio"})
        self[1][0][1] = self.get_field_value('label2')


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
  <div>  <!-- with class attribute set to div_class1 if a class is set -->
    <label>
      <input type='radio' /> <!-- with name from 'radio_checked' widgfield and value from value1 -->
      <!-- text from label1 -->
    </label>
  </div>
  <div>  <!-- with class attribute set to div_class2 if a class is set -->
    <label>
      <input type='radio' /> <!-- with name from 'radio_checked' widgfield and value from value2 -->
      <!-- text from label2 -->
    </label>
  </div>
</div>
"""


class BooleanRadio(Widget):
    """A two option radio control for choosing True or False. Without a form or submit button, typically included within a form."""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'div_class1':FieldArg("cssclass", ''),
                        'left_label1':FieldArg("text", 'True'),
                        'left_class1':FieldArg("cssclass", ''),
                        'right_label1':FieldArg("text", ''),
                        'right_class1':FieldArg("cssclass", ''),
                        'div_class2':FieldArg("cssclass", ''),
                        'left_label2':FieldArg("text", 'False'),
                        'left_class2':FieldArg("cssclass", ''),
                        'right_label2':FieldArg("text", ''),
                        'right_class2':FieldArg("cssclass", ''),
                        'radio_checked':FieldArg("boolean", True, valdt=True)
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        div_class1: class of the first div containing the first radio button
        left_label1: The text displayed to the left of the first radio button
        left_class1: The css class of the label to the left of the first radio button
        right_label1: The text displayed to the right of the first radio button
        right_class1: The css class of the label to the right of the first radio button
        div_class2: class of the second div containing the second radio button
        left_label2: The text displayed to the left of the second radio button
        left_class2: The css class of the label to the left of the second radio button
        right_label2: The text displayed to the right of the second radio button
        right_class2: The css class of the label to the right of the second radio button
        radio_checked: default value to be checked, True or False, field name is the field returned
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self[0] = tag.Part(tag_name='div')
        self[0][0] = tag.Part(tag_name="label", hide_if_empty=True)
        self[0][1] = tag.ClosedPart(tag_name="input")
        self[0][2] = tag.Part(tag_name="label", hide_if_empty=True)
        self[1] = tag.Part(tag_name='div')
        self[1][0] = tag.Part(tag_name="label", hide_if_empty=True)
        self[1][1] = tag.ClosedPart(tag_name="input")
        self[1][2] = tag.Part(tag_name="label", hide_if_empty=True)


    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the radio buttons"
        div1 = self[0]
        div2 = self[1]

        if self.get_field_value('div_class1'):
            div1.attribs = {"class": self.get_field_value('div_class1')}
        if self.get_field_value('div_class2'):
            div2.attribs = {"class": self.get_field_value('div_class2')}

        # labels of first div
        if self.get_field_value('left_class1'):
            div1[0].attribs = {"class": self.get_field_value('left_class1')}
        div1[0][0] = self.get_field_value('left_label1')

        if self.get_field_value('right_class1'):
            div1[2].attribs = {"class": self.get_field_value('right_class1')}
        div1[2][0] = self.get_field_value('right_label1')

        # labels of second div
        if self.get_field_value('left_class2'):
            div2[0].attribs = {"class": self.get_field_value('left_class2')}
        div2[0][0] = self.get_field_value('left_label2')

        if self.get_field_value('right_class2'):
            div2[2].attribs = {"class": self.get_field_value('right_class2')}
        div2[2][0] = self.get_field_value('right_label2')

        name = self.get_formname('radio_checked')
        if self.get_field_value('radio_checked'):
            # True chosen
            div1[1].attribs = {"type":"radio", 'name': name, "checked":"checked", "value":"True"}
            div2[1].attribs = {"type":"radio", 'name': name, "value":"False"}
        else:
            # False chosen
            div1[1].attribs = {"type":"radio", 'name': name, "value":"True"}
            div2[1].attribs = {"type":"radio", 'name': name, "checked":"checked", "value":"False"}

        # set the label 'for' attribute to the input field id
        div1[1].insert_id()
        div1[0].update_attribs({'for':div1[1].get_id()})
        div1[2].update_attribs({'for':div1[1].get_id()})
        div2[1].insert_id()
        div2[0].update_attribs({'for':div2[1].get_id()})
        div2[2].update_attribs({'for':div2[1].get_id()})

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>  <!-- with widget id and class widget_class -->
  <div>  <!-- with class attribute set to div_class1 if a class is set -->
      <label> <!-- with class set to left_class1 and content to left_label1 -->
      </label>
      <input type='radio' value='True' /> <!-- checked if radio_checked field is True -->
      <label> <!-- with class set to right_class1 and content to right_label1 -->
      </label>
  </div>
  <div>  <!-- with class attribute set to div_class2 if a class is set -->
      <label> <!-- with class set to left_class2 and content to left_label2 -->
      </label>
      <input type='radio' value='False' /> <!-- checked if radio_checked field is False -->
      <label> <!-- with class set to right_class2 and content to right_label2 -->
      </label>
  </div>
</div>"""


