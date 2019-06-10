from django.db import models
from .validators import validate_subject


""" EmailModel """
# Start receive email model here.
class EmailModel(models.Model):
    to_email      = models.EmailField(max_length=55, blank=True, null=True)
    from_email    = models.EmailField(max_length=55, blank=False, null=False)
    phone_number  = models.IntegerField(blank=False, null=False)
    full_name     = models.CharField(max_length=20, blank=False, null=False)
    subject       = models.CharField(max_length=30, blank=False, null=False, validators=[validate_subject])
    content       = models.TextField(max_length=250, blank=False, null=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    # str methode here.
    def __str__(self):
        return self.full_name

    # meta class here.
    class Meta:
        ordering = ['pk']
        verbose_name = "Email"
        verbose_name_plural = "Emails"
#End model here.
""" End here """