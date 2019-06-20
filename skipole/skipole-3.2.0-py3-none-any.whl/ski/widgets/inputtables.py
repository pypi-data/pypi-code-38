
"""Contains widgets for inputting data"""

from urllib.parse import quote

from .. import skiboot, tag, excepts
from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict



class InputTable5(Widget):
    """Defines a div of four columns, the first just being label text, the second being text input fields,
       the third and fourth being submit buttons.  Each row of the table is a form, the
       form action ident is the same for all forms.
       On error the paragraph TextBlock is changed to the error message."""

    # This class does not display any error messages
    display_errors = False

    # js_validators is a class attribute, True if javascript validation is enabled
    js_validators=True

    arg_descriptions = {
                        'div_class':FieldArg("cssclass", ''),
                        'size':FieldArg("text", ''),
                        'maxlength':FieldArg("text", ''),
                        'required':FieldArg("boolean", False),
                        'action':FieldArg("url",''),
                        'button_text1':FieldArg("text", "Submit", valdt=True),
                        'button_text2':FieldArg("text", "Submit", valdt=True),
                        'button1_class':FieldArg("cssclass", ""),
                        'button2_class':FieldArg("cssclass", ""),
                        'col_label':FieldArgList('text'),
                        'label_class':FieldArg("cssclass", ""),
                        'col_input':FieldArgList('text', valdt=True),
                        'hidden_field1':FieldArgList("text", valdt=True),
                        'hidden_field2':FieldArgList("text", valdt=True),
                        'hidden_field3':FieldArgList("text", valdt=True),
                        'hidden_field4':FieldArgList("text", valdt=True),
                        'input_accepted_class':FieldArg("cssclass", ''),
                        'input_class':FieldArg("cssclass", ''),
                        'input_errored_class':FieldArg("cssclass", ''),
                        'set_input_accepted':FieldArgDict("boolean", jsonset=True),
                        'set_input_errored':FieldArgDict("boolean", jsonset=True)
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        div_class: the class attribute of each form div
        size: The number of characters appearing in each text input area
        maxlength: The maximum number of characters accepted in each text area
        required: Set True to put the 'required' flag into each input field
        action: The label or ident of the action page
        button_text1: text appearing on the first buttons - if empty, no button 1 is shown
        button_text2: text appearing on the second buttons - if empty, no button 2 is shown
        button1_class: class set on button1
        button2_class: class set on button2
        col_label: a list of all the text strings appearing in the first column
        label_class: the class to apply to each label
        col_input: a list of all the text strings appearing in the input fields
        hidden_field1-4: four hidden fields, each being a list
        input_accepted_class: A class which can be added on each input field
        input_class: A class which can be set on each input field
        input_errored_class: A class which can be added on each input field
        The following two dictionaries shoul have keys equal to the integer row number (starting
         at zero) and value True or False
        set_input_accepted: Dictionary of col index keys that should be set with input_accepted_class
        set_input_errored: Dictionary of col index keys that should be set with input_errored_class
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)


    def _build(self, page, ident_list, environ, call_data, lang):
        "Build the table"

        # get the widget ident
        ident_value = page.ident_data_string

        # get the form action url
        action_url = skiboot.get_url(self.get_field_value("action"), proj_ident=page.proj_ident)
        if not action_url:
            # setting self._error replaces the entire tag by the self._error message
            self._error = "Warning: broken link"
            return


        len_label = len(self.fields["col_label"])
        len_input = len(self.fields["col_input"])
        len_hidden_field1 = len(self.fields["hidden_field1"])
        len_hidden_field2 = len(self.fields["hidden_field2"])
        len_hidden_field3 = len(self.fields["hidden_field3"])
        len_hidden_field4 = len(self.fields["hidden_field4"])

        rows = max(len_label, len_input)
        if not rows:
            rows=1

        input_name = self.get_formname("col_input")
        button_name1 = self.get_formname("button_text1")
        button_value1 = self.get_field_value('button_text1')
        button1_class = self.get_field_value('button1_class')
        button_name2 = self.get_formname("button_text2")
        button_value2 = self.get_field_value('button_text2')
        button2_class = self.get_field_value('button2_class')
        hidden_field1_name = self.get_formname("hidden_field1")
        hidden_field2_name = self.get_formname("hidden_field2")
        hidden_field3_name = self.get_formname("hidden_field3")
        hidden_field4_name = self.get_formname("hidden_field4")

        label_class = self.get_field_value('label_class')

        form_id = self.get_id() + '_'

        if self.get_field_value('input_accepted_class') and self.get_field_value("set_input_accepted"):
            set_input_accepted = self.get_field_value("set_input_accepted")
        else:
            set_input_accepted = {}

        if self.get_field_value('input_errored_class') and self.get_field_value("set_input_errored"):
            set_input_errored = self.get_field_value("set_input_errored")
        else:
            set_input_errored = {}

        if self.get_field_value('input_class'):
            input_class = self.get_field_value('input_class')
        else:
            input_class = ''


        for rownumber in range(rows):
            if rownumber<len_label:
                col_label = self.get_field_value("col_label")[rownumber]
            else:
                col_label = ''
            if rownumber<len_input:
                col_input = self.get_field_value("col_input")[rownumber]
            else:
                col_input = ''
            if rownumber<len_hidden_field1:
                col_hidden_field1 = self.get_field_value("hidden_field1")[rownumber]
            else:
                col_hidden_field1 = ''
            if rownumber<len_hidden_field2:
                col_hidden_field2 = self.get_field_value("hidden_field2")[rownumber]
            else:
                col_hidden_field2 = ''
            if rownumber<len_hidden_field3:
                col_hidden_field3 = self.get_field_value("hidden_field3")[rownumber]
            else:
                col_hidden_field3 = ''
            if rownumber<len_hidden_field4:
                col_hidden_field4 = self.get_field_value("hidden_field4")[rownumber]
            else:
                col_hidden_field4 = ''

            # for every table row, create a form
            formrow = tag.Part(tag_name="form", attribs ={"method":"post", "action": action_url})

            # 1st column is label text 
            if label_class:
                formrow[0] = tag.Part(tag_name="label", attribs={'class':label_class})
            else:
                formrow[0] = tag.Part(tag_name="label")
            formrow[0][0] = col_label

            # 2nd column is a text input field
            formrow[1] = tag.ClosedPart(tag_name="input",
                                    attribs ={"name":input_name,
                                    "value":col_input,
                                    "type":"text"})
            if self.get_field_value('size'):
                formrow[1].update_attribs({"size":self.get_field_value('size')})
            if self.get_field_value('maxlength'):
                formrow[1].update_attribs({"maxlength":self.get_field_value('maxlength')})
            if self.get_field_value('required'):
                formrow[1].update_attribs({"required":"required"})
            # set an id in the input field for the 'label for' tag
            this_id = form_id + str(rownumber) + '_0_1'
            formrow[1].insert_id(this_id)
            # set the label 'for' attribute
            formrow[0].update_attribs({'for':formrow[1].get_id()})
            if (rownumber in set_input_errored) and set_input_errored[rownumber]:
                if input_class:
                    formrow[1].update_attribs({"class":input_class + ' ' + self.get_field_value('input_errored_class')})
                else:
                    formrow[1].update_attribs({"class":self.get_field_value('input_errored_class')})
            elif (rownumber in set_input_accepted) and set_input_accepted[rownumber]:
                if input_class:
                    formrow[1].update_attribs({"class":input_class + ' ' + self.get_field_value('input_accepted_class')})
                else:
                    formrow[1].update_attribs({"class":self.get_field_value('input_accepted_class')})
            elif input_class:
                formrow[1].update_attribs({"class":input_class})

            # 3rd column is a submit button
            if button_value1:
                formrow.append(tag.ClosedPart(tag_name="input",
                                 attribs ={"name":button_name1,
                                           "value":button_value1,
                                           "class":button1_class,
                                           "type":"submit"}))
            # 4th column is a submit button
            if button_value2:
                formrow.append(tag.ClosedPart(tag_name="input",
                                 attribs ={"name":button_name2,
                                           "value":button_value2,
                                           "class":button2_class,
                                           "type":"submit"}))

            # all submissions always have an 'ident' hidden field to provide the ident of the calling page
            formrow.append(tag.ClosedPart(tag_name="input",
                                          attribs ={"name":'ident',
                                                 "value":ident_value,
                                                 "type":"hidden"}))

            # hidden field on the form
            if col_hidden_field1:
                formrow.append(tag.ClosedPart(tag_name = "input",
                                            attribs =  {"name":hidden_field1_name,
                                                        "value":col_hidden_field1,
                                                        "type":"hidden"}))

            # Second hidden field on the form
            if col_hidden_field2:
                formrow.append(tag.ClosedPart(tag_name = "input",
                                            attribs =  {"name":hidden_field2_name,
                                                        "value":col_hidden_field2,
                                                        "type":"hidden"}))
            # Third hidden field on the form
            if col_hidden_field3:
                formrow.append(tag.ClosedPart(tag_name = "input",
                                            attribs =  {"name":hidden_field3_name,
                                                        "value":col_hidden_field3,
                                                        "type":"hidden"}))
            # Fourth hidden field on the form
            if col_hidden_field4:
                formrow.append(tag.ClosedPart(tag_name = "input",
                                            attribs =  {"name":hidden_field4_name,
                                                        "value":col_hidden_field4,
                                                        "type":"hidden"}))

            # place form in a div
            self[rownumber] = tag.Part(tag_name="div")
            if self.get_field_value('div_class'):
                self[rownumber].attribs = {"class": self.get_field_value('div_class')}
            self[rownumber][0] = formrow


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets a submit event handler"""
        jscript = """  $('#{ident}').find( 'form').each(function() {{
    $(this).on("submit", function(e) {{
        SKIPOLE.widgets['{ident}'].eventfunc(e);
        }});
    }});
""".format(ident=self.get_id())
        return jscript + self._make_fieldvalues('input_accepted_class', 'input_errored_class')

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div>   <!-- with widget id and class widget_class -->
  <!-- Then a div containing a form, label, input field, buttons and hidden fields, repeated for each list  item -->
  <div> <!-- with CSS class attribute set to div_class if a class is set -->
    <form method=\"post\"> <!-- action attribute set to action field -->
      <label> <!-- with col_label text and CSS class label_class -->
      </label >
        <input type="text" /> <!-- all with same CSS input_class and size and maxlength, with values from col_input -->
        <input type="submit" /> <!-- with value button_text1, CSS class button1_class and name widgfield derived from button_text1 field name -->
        <input type="submit" /> <!-- with value button_text2, CSS class button2_class and name widgfield derived from button_text2 field name -->
        <!-- hidden input fields -->
    </form>                              
  </div>
  <!--  The above repeated for each item in col_input or col_label, whichever is greater -->
</div>"""

