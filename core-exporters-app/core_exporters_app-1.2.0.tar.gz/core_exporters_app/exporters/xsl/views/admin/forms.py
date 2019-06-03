""" XSLT forms
"""
from django import forms
import core_main_app.components.xsl_transformation.api as xsl_api


class XsltSelectionForm(forms.Form):
    """ Xslt selection form
    """
    xslt_list = forms.MultipleChoiceField(label='', widget=forms.SelectMultiple(), required=False)

    def __init__(self, *args, **kwargs):
        super(XsltSelectionForm, self).__init__(*args, **kwargs)
        self.fields['xslt_list'].choices = _get_xsl()


def _get_xsl():
    """ Get all xsl and format them to be displayed

    Returns:
        List of xsl

    """
    xsl_list = []
    # get all xsl
    list_ = xsl_api.get_all()
    # loop on the list
    for elt in list_:
        # list with id and name
        xsl_list.append((elt.id, elt.name))
    return xsl_list
