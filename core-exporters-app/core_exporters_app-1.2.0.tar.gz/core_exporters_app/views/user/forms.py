""" Exporter forms
"""
from itertools import chain

import bson
import core_main_app.components.template.api as template_api
from django import forms

import core_exporters_app.components.exporter.api as exporters_api


class ExportForm(forms.Form):
    """ Create the form for exporting data
    """
    my_exporters = forms.MultipleChoiceField(label='', choices=[],
                                             widget=forms.CheckboxSelectMultiple(), required=True)

    export_options = []

    def __init__(self, *args, **kwargs):
        """ Init the form

        Args:
            template_id_list:
            template_hash_list:
            data_url_list:
        """
        self.export_options = []
        self.data_url_list = []
        self.template_id_list = []
        self.template_hash_list = []

        if 'template_id_list' in kwargs and 'template_hash_list' in kwargs:
            # Only stringified ObjectId in template_id_list
            self.template_id_list = [item for item in kwargs.pop('template_id_list') if
                                     bson.objectid.ObjectId.is_valid(item)]
            self.template_hash_list = kwargs.pop('template_hash_list')

            # Retrieves all corresponded template
            templates_from_id = template_api.get_all_by_id_list(self.template_id_list)
            templates_from_hash = template_api.get_all_by_hash_list(self.template_hash_list)

            # Retrieves all common exporter for exporters given
            exporters_from_ids = list(exporters_api.get_all_by_template_list(templates_from_id))

            # with the hash, we can get more exporters than from ids
            exporters_from_hash = list(exporters_api.get_all_by_template_list(templates_from_hash))

            # if there is exporters from ids (means local data have been selected)
            if len(exporters_from_ids) > 0:
                exporters = exporters_from_ids
                # if there is exporters from hash (means remote data have been selected)
                if len(exporters_from_hash) > 0:
                    # we get only common exporters
                    exporters = set(exporters_from_ids).intersection(exporters_from_hash)
            else:
                exporters = exporters_from_hash

            for exporter in exporters:
                self.export_options.append((exporter.id, exporter.name))

        if 'data_url_list' in kwargs:
            self.data_url_list = kwargs.pop('data_url_list')

        super(ExportForm, self).__init__(*args, **kwargs)
        self.fields['my_exporters'].choices = self.export_options
