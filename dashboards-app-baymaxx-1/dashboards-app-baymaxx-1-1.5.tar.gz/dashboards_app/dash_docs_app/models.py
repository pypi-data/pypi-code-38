from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from dashboards_app.models import Dashboard as daDashboard
from cms.models.fields import PlaceholderField
from cms.models import CMSPlugin as cms_plugin
import datetime





@python_2_unicode_compatible
class DashDoc(models.Model):

    # TODO: verify the models so when a dahsboard is deleted then documentation is also deleted.
    dashboard_id=models.ForeignKey(daDashboard,on_delete=models.CASCADE)

    dash_docs_content = PlaceholderField('documentation_content',
                               related_name='documentation_content')
    sidebar_content=PlaceholderField('documentation_sidebar_content',
                                     related_name='documentation_sidebar_content')



    def __str__(self):
        return self.dashboard_id.slug_source_field_name

class DocumentedModel(models.Model):
    parent_plugin=models.ForeignKey(cms_plugin, on_delete=models.CASCADE,related_name='parent_plugin')
    documented_date=models.DateField(default=datetime.date.today)
    holder_plugin=models.ForeignKey(cms_plugin,on_delete=models.CASCADE,related_name='holder_plugin')

    def __str__(self):
        return '%s %s %s' %(self.parent_plugin,'document created on',self.documented_date)
