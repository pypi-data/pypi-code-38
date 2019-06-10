from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from PIL import Image
# Create your models here.


""" Custom user model here. """
#UserModel starts here.
class UserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to='djangoadmin')
    address = models.CharField(max_length=100, blank=True, null=True)
    phone = models.BigIntegerField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user}"

    class Meta:
        ordering = ['pk']
        verbose_name = 'User'
        verbose_name_plural = 'Users'  

# usermodel method.
def create_user_profile(sender, **kwargs):
    if kwargs['created']:
        UserModel.objects.create(user=kwargs['instance'])

post_save.connect(create_user_profile, sender=User)
# end here.
""" end custom user model here. """
