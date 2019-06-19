from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from cms.models import CMSPlugin

# Create your models here.

# loggin Details#
import logging
import os
from dashboards_app.blero_utils.client_utils.client_to_server import delete_server_plugin




#Start Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create a file handler
handler = logging.FileHandler('blero_container_client.log')
handler.setLevel(logging.DEBUG)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))






@python_2_unicode_compatible
class BleroContainer(CMSPlugin):


    container_name = models.CharField(
        blank=False,
        max_length=200,
    )

    number_columns=models.CharField(blank=False,max_length=200,)






    def __str__(self):
        return self.container_name



    def __init__(self,*args,**kwargs):
        #check if position child excist if not create it

        super(BleroContainer, self).__init__(*args, **kwargs)
        # logger.debug("plugin initiated")
        # #get or create position
        # try:
        #     plugin=BleroContainer.objects.get(pk=self.cmsplugin_ptr_id)
        # except Exception as e:
        #     logger.exception("error getting plugin")
        # plugin_position, created=PluginPosition.objects.get_or_create(model=plugin)

    def delete(self):

        delete_server_plugin(self)

        super(BleroContainer,self).delete()







class PluginPosition(models.Model):
    model = models.ForeignKey(BleroContainer,on_delete=models.CASCADE)
    is_resized = models.BooleanField(default=False)
    width = models.CharField(max_length=50, null=True)
    height = models.CharField(max_length=50, null=True)
    top = models.CharField(max_length=50, null=True)
    left = models.CharField(max_length=50, null=True)
