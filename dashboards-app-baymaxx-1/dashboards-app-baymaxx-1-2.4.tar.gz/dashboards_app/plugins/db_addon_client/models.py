from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from cms.models import CMSPlugin
from dashboards_app.blero_utils.client_utils.client_to_server import delete_server_plugin


@python_2_unicode_compatible
class DBPlugin(CMSPlugin):


    label = models.CharField(
        blank=True,
        max_length=200,
    )

    def __str__(self):
        return self.label




@python_2_unicode_compatible
class DBPlugin_individual(CMSPlugin):


    database_name = models.CharField(max_length=250, null=True, blank=True)
    database_table_name = models.CharField(max_length=250, null=True, blank=True)
    database_filter_column = models.CharField(max_length=250, null=True, blank=True)
    database_py_function = models.CharField(max_length=250, null=True, blank=True)


    def __str__(self):
        return self.database_name or self.database_table_name




    def delete(self):

        delete_server_plugin(self)

        super(DBPlugin_individual,self).delete()
