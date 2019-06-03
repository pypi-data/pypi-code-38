

"""Contains form widgets, these have 'container' functionality - they can contain further html and widgets, typically
      further input fields.  The module also has an Hidden Field and Submit Button widgets, which can be inserted into
     a form. """

from .. import skiboot, tag, excepts
from . import Widget, ClosedWidget, FieldArg, FieldArgList, FieldArgTable, FieldArgDict


class HiddenField(ClosedWidget):
    """An input field of type hidden, for use as an insert into form widgets"""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'hidden_field':FieldArg("text", '', valdt=True, jsonset=True)}

    def __init__(self, name=None, brief='', **field_args):
        "hidden_field: A hidden input field"
        ClosedWidget.__init__(self, name=name, tag_name="input", brief=brief, **field_args)

    def _build(self, page, ident_list, environ, call_data, lang):
        "Sets the attributes"
        value = self.get_field_value('hidden_field')
        if not value:
            self.show = False
            return
        self.update_attribs({"name":self.get_formname('hidden_field'),
                       "value":value,
                       "type":"hidden"})

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<input type="hidden" /> <!-- with widget id and class widget_class -->
  <!-- with value of the "hidden_field" value, and name being the widgfield -->"""


class HiddenSessionStorage(ClosedWidget):
    """An input field of type hidden, for use as an insert into form widgets"""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'session_key':FieldArg("text", '', valdt=True, jsonset=True)}

    def __init__(self, name=None, brief='', **field_args):
        "hidden_field: A hidden input field with value from session storage"
        ClosedWidget.__init__(self, name=name, tag_name="input", brief=brief, **field_args)
        self._key = ''

    def _build(self, page, ident_list, environ, call_data, lang):
        "Sets the attributes"
        self._key = self.get_field_value('session_key')
        if not self._key:
            self.show = False
            return
        self.update_attribs({"name":self.get_formname('session_key'),
                       "value":"",
                       "type":"hidden"})

    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets key value into the value attribute by calling the widget updatefunc"""
        if not self._key:
            return
        jscript =  """
  SKIPOLE.widgets["{ident}"].updatefunc();
""".format(ident=self.get_id())
        return self._make_fieldvalues(session_key=self._key) + jscript

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<input type="hidden" /> <!-- with widget id and class widget_class -->
  <!-- with value taken from the session storage with key "session_key", and name being the session_key widgfield -->"""



class HiddenLocalStorage(ClosedWidget):
    """An input field of type hidden, for use as an insert into form widgets"""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'local_key':FieldArg("text", '', valdt=True, jsonset=True)}

    def __init__(self, name=None, brief='', **field_args):
        "hidden_field: A hidden input field with value from local storage"
        ClosedWidget.__init__(self, name=name, tag_name="input", brief=brief, **field_args)
        self._key = ''

    def _build(self, page, ident_list, environ, call_data, lang):
        "Sets the attributes"
        self._key = self.get_field_value('local_key')
        if not self._key:
            self.show = False
            return
        self.update_attribs({"name":self.get_formname('local_key'),
                       "value":"",
                       "type":"hidden"})

    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets key value into the value attribute by calling the widget updatefunc"""
        if not self._key:
            return
        jscript = """
  SKIPOLE.widgets["{ident}"].updatefunc();
""".format(ident=self.get_id())
        return self._make_fieldvalues(local_key=self._key) + jscript



    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<input type="hidden" /> <!-- with widget id and class widget_class -->
  <!-- with value taken from the local storage with key "local_key", and name being the local_key widgfield -->"""



class SubmitButton1(ClosedWidget):
    """An input field of type submit, for use as an insert into form widgets"""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'button_text':FieldArg("text", 'Submit', valdt=True, jsonset=True)}

    def __init__(self, name=None, brief='', **field_args):
        "Create input type submit button widget"
        ClosedWidget.__init__(self, name=name, tag_name="input", brief=brief, **field_args)

    def _build(self, page, ident_list, environ, call_data, lang):
        "Sets the attributes"
        button_text = self.get_field_value('button_text')
        if not button_text:
            button_text = "Submit"
        self.update_attribs({"name":self.get_formname('button_text'),
                       "value":button_text,
                       "type":"submit"})

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<input type="button_text" /> <!-- with widget id and class widget_class -->
  <!-- with value of the "button_text" value, and name being the 'button_text widgfield -->"""


class SubmitButton2(ClosedWidget):
    """An input field of type submit, for use as an insert into form widgets"""

    # This class does not display any error messages
    display_errors = False

    arg_descriptions = {'button_text':FieldArg("text", 'Submit', jsonset=True)}

    def __init__(self, name=None, brief='', **field_args):
        "Create input type submit button widget"
        ClosedWidget.__init__(self, name=name, tag_name="input", brief=brief, **field_args)

    def _build(self, page, ident_list, environ, call_data, lang):
        "Sets the attributes"
        button_text = self.get_field_value('button_text')
        if not button_text:
            button_text = "Submit"
        self.update_attribs({"value":button_text, "type":"submit"})

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<input type="button_text" /> <!-- with widget id and class widget_class -->
  <!-- with value of the "button_text" value, but no name, so does not submit a widgfield -->"""


class Form1(Widget):
    """A form with a container and four hidden fields. Used with further input fields set within it.
       On error - the error message is displayed before any of the contents
       Does not include a submit button, therefore requires one to be inserted with the contents"""

    _container = ((1,0),)

    error_location = (0,0,0)

    arg_descriptions = {'action':FieldArg("url", ''),
                        'enctype':FieldArg("text", ''),
                        'hidden_field1':FieldArg("text", '', valdt=True),
                        'hidden_field2':FieldArg("text", '', valdt=True),
                        'hidden_field3':FieldArg("text", '', valdt=True),
                        'hidden_field4':FieldArg("text", '', valdt=True),
                        'container_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", '')
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        action: The page ident, label, url this form links to
        enctype: Sets the enctype attribute if given
        hidden_field1: A hidden field value, leave blank if unused
        hidden_field2: A second hidden field value, leave blank if unused
        hidden_field3: A third hidden field value, leave blank if unused
        hidden_field4: A fourth hidden field value, leave blank if unused
        container_class: the class attribute of the div holding the container
        error_class: The class applied to the paragraph containing the error message on error."""
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        self.update_attribs({"role":"form", "method":"post"})
        # error div at 0
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # The form
        self[1] = tag.Part(tag_name='form', attribs={"role":"form", "method":"post"})
        # The location 1,0 is available as a container
        self[1][0] = tag.Part(tag_name="div")
        self[1][0][0] = ''

    def _build(self, page, ident_list, environ, call_data, lang):
        "build the form"
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
        if self.get_field_value('enctype'):
            self[1].update_attribs({"enctype": self.get_field_value('enctype')})

        # the div holding the container
        if self.get_field_value('container_class'):
            self[1][0].attribs = {"class": self.get_field_value('container_class')}

        # add ident and four hidden fields
        self.add_hiddens(self[1], page)


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets a submit event handler"""
        jscript = """  $('#{ident} form').on("submit", function(e) {{
    SKIPOLE.widgets['{ident}'].eventfunc(e);
    }});
""".format(ident=self.get_id())
        return jscript

    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden div, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <form method=\"post\"> <!-- action attribute set to action field -->
    <div> <!-- this div has the class attribute set to container_class -->
      <!-- container 0 for further html -->
    </div>
    <!-- hidden input fields -->                              
  </form>
</div>"""


class SubmitForm1(Widget):
    """A form taking contents with submit button, left or right labels and four hidden fields.
       Used with further input fields set within it. On error - the error message is displayed
       below the form tag, before any of the contents"""

    _container = ((1,0),)

    error_location = (0,0,0)

    arg_descriptions = {'left_label':FieldArg("text", ''),
                        'left_class':FieldArg("cssclass", ''),
                        'right_label':FieldArg("text", ''),
                        'right_class':FieldArg("cssclass", ''),
                        'action_json':FieldArg("url", ''),
                        'action':FieldArg("url", ''),
                        'enctype':FieldArg("text", ''),
                        'hidden_field1':FieldArg("text", '', valdt=True),
                        'hidden_field2':FieldArg("text", '', valdt=True),
                        'hidden_field3':FieldArg("text", '', valdt=True),
                        'hidden_field4':FieldArg("text", '', valdt=True),
                        'button_text':FieldArg("text",'Submit'),
                        'button_wait_text':FieldArg("text", ''),
                        'button_class':FieldArg("cssclass", ''),
                        'div_class':FieldArg("cssclass", ''),
                        'container_class':FieldArg("cssclass", ''),
                        'error_class':FieldArg("cssclass", ''),
                       }

    def __init__(self, name=None, brief='', **field_args):
        """
        left_label: The text displayed to the left of the button
        left_class: The css class of the label to the left of the button
        right_label: The text displayed to the right of the button
        right_class: The css class of the label to the right of the button
        action_json:  if a value set, and client has jscript enabled, this is the page ident, label, url this button links to, expects a json page back
        action: The page ident, label, url this button links to
        enctype: Sets the enctype attribute if given
        hidden_field1: A hidden field value, leave blank if unused, name used as the get field name
        hidden_field2: A second hidden field value, leave blank if unused, name used as the get field name
        hidden_field3: A third hidden field value, leave blank if unused, name used as the get field name
        hidden_field4: A fourth hidden field value, leave blank if unused, name used as the get field name
        button_text: The text on the button
        button_wait_text: A 'please wait' message shown on the button
        button_class: The css class of the button
        div_class: the class attribute of the div tag which contains the label and button
        container_class: the class attribute of the div holding the container
        error_class: The class applied to the paragraph containing the error message on error.
        """
        Widget.__init__(self, name=name, tag_name="div", brief=brief, **field_args)
        # error div at 0
        self[0] = tag.Part(tag_name="div", attribs={"style":"display:none;"})
        self[0][0] = tag.Part(tag_name="p")
        self[0][0][0] = ''
        # The form
        self[1] = tag.Part(tag_name='form', attribs={"role":"form", "method":"post"})
        # The location 1,0 is available as a container
        self[1][0] = tag.Part(tag_name='div')
        self[1][0][0] = ''
        # tag containing label and button
        self[1][1] = tag.Part(tag_name='div')
        # the left label
        self[1][1][0] = tag.Part(tag_name="label", hide_if_empty=True)
        # the submit button
        self[1][1][1] = tag.ClosedPart(tag_name="input")
        # the right label
        self[1][1][2] = tag.Part(tag_name="label", hide_if_empty=True)
        self._jsonurl = ''

    def _build(self, page, ident_list, environ, call_data, lang):
        "build the form"
        self._jsonurl = skiboot.get_url(self.get_field_value("action_json"), proj_ident=page.proj_ident)
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
        if self.get_field_value('enctype'):
            self[1].update_attribs({"enctype": self.get_field_value('enctype')})

        # the div holding the container
        if self.get_field_value('container_class'):
            self[1][0].attribs = {"class": self.get_field_value('container_class')}

        # the div holding label and button
        if self.get_field_value('div_class'):
            self[1][1].attribs = {"class": self.get_field_value('div_class')}

        if self.get_field_value('left_label'):
            self[1][1][0][0] = self.get_field_value('left_label')
        if self.get_field_value('left_class'):
            self[1][1][0].attribs = {"class": self.get_field_value('left_class')}

        # submit button
        if self.get_field_value('button_class'):
            self[1][1][1].attribs = {"value":self.get_field_value('button_text'), "type":"submit", "class": self.get_field_value('button_class')}
        else:
            self[1][1][1].attribs = {"value":self.get_field_value('button_text'), "type":"submit"}

        # set an id in the submit button for the 'label for' tag
        self[1][1][1].insert_id()

        if self.get_field_value('right_label'):
            self[1][1][2][0] = self.get_field_value('right_label')
        if self.get_field_value('right_class'):
            self[1][1][2].attribs = {"class": self.get_field_value('right_class')}

        # set the label 'for' attribute
        self[1][1][0].update_attribs({'for':self[1][1][1].get_id()})
        self[1][1][2].update_attribs({'for':self[1][1][1].get_id()})

        # add ident and four hidden fields
        self.add_hiddens(self[1], page)


    def _build_js(self, page, ident_list, environ, call_data, lang):
        """Sets a submit event handler"""
        jscript = """$('#{ident} form').on("submit", function(e) {{
    SKIPOLE.widgets['{ident}'].eventfunc(e);
    }});
""".format(ident=self.get_id())
        if self._jsonurl:
            return jscript + self._make_fieldvalues('button_wait_text', buttonident = self[1][1][1].get_id(), url=self._jsonurl)
        else:
            return jscript + self._make_fieldvalues('button_wait_text', buttonident = self[1][1][1].get_id())


    @classmethod
    def description(cls):
        """Returns a text string to illustrate the widget"""
        return """
<div> <!-- with widget id and class widget_class -->
  <div> <!-- normally hidden div, with class error_class -->
    <p> <!-- Any error text appears here --> </p>
  </div>
  <form method="post"> <!-- action attribute set to action field -->
    <div>  <!-- this div has the class attribute set to container_class -->
      <!-- container 0 for further html -->
    </div>
    <div>  <!-- this div has the class attribute set to div_class -->
      <label> <!-- with class set to left_class and content to left_label -->
      </label>
      <input type=\"submit\" /> <!-- button value set to button_text -->
      <label> <!-- with class set to right_class and content to right_label -->
      </label>
    </div>
    <!-- hidden input fields -->                              
  </form>
</div>"""




