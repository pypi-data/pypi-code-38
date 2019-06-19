from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from cms.models import CMSPlugin
from dashboards_app.blero_utils.client_utils.client_to_server import delete_server_plugin

@python_2_unicode_compatible
class BleroGrid(CMSPlugin):



    grid_label = models.CharField(
        blank=False,
        max_length=200,
    )

    grid_columns = models.CharField(max_length=200,null=False)
    grid_rows = models.CharField(max_length=200,null=False)
    content_edited = models.BooleanField(default=False)

    def __str__(self):
        return self.grid_label

    def delete(self):

        delete_server_plugin(self)

        super(BleroGrid,self).delete()







class GridColumns(models.Model):
    model = models.ForeignKey(BleroGrid,on_delete=models.CASCADE, related_name='columns')
    content_edited = models.BooleanField(default=False)
    format_edited= models.BooleanField(default=False)
    column_number= models.CharField(max_length=200, null=True)
    column_content= models.CharField(max_length=200, null=True)
    column_font = models.CharField(max_length=200, null=True)
    column_font_color = models.CharField(max_length=200, null=True)
    column_background_color = models.CharField(max_length=200, null=True)

class GridRows(models.Model):
    model = models.ForeignKey(BleroGrid, on_delete=models.CASCADE, related_name='rows')
    content_edited = models.BooleanField(default=False)
    format_edited = models.BooleanField(default=False)
    row_number = models.CharField(max_length=200, null=True)
    row_content = models.CharField(max_length=200, null=True)
    row_font = models.CharField(max_length=200, null=True)
    row_font_color = models.CharField(max_length=200, null=True)
    row_background_color = models.CharField(max_length=200, null=True)

class GridCells(models.Model):
    model = models.ForeignKey(BleroGrid, on_delete=models.CASCADE, related_name='cells')
    content_edited = models.BooleanField(default=False)
    format_edited = models.BooleanField(default=False)
    row_number = models.CharField(max_length=200, null=True)
    column_number = models.CharField(max_length=200, null=True)
    cell_content = models.CharField(max_length=200, null=True)
    cell_font = models.CharField(max_length=200, null=True)
    cell_font_size= models.CharField(max_length=200, null=True)
    cell_font_color = models.CharField(max_length=200, null=True)
    cell_background_color = models.CharField(max_length=200, null=True)





class PluginPosition(models.Model): #PluginPosition
    model = models.ForeignKey(BleroGrid,on_delete=models.CASCADE)
    is_resized = models.BooleanField(default=False)
    width = models.CharField(max_length=50, null=True)
    height = models.CharField(max_length=50, null=True)
    top = models.CharField(max_length=50, null=True)
    left = models.CharField(max_length=50, null=True)


