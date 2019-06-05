from django.conf import settings
from django.db import models

from djangoldp.models import Model


class Customer(Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    logo = models.URLField(blank=True, null=True)
    companyRegister = models.CharField(max_length=255, blank=True)
    firstName = models.CharField(max_length=255, blank=True)
    lastName = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class BusinessProvider(Model):
    name = models.CharField(max_length=255)
    fee = models.PositiveIntegerField(default='0')

    def __str__(self):
        return self.name


class Project(Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    number = models.PositiveIntegerField(default='0', blank=True)
    creationDate = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)  # WARN add import
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Member', blank=True)
    driveID = models.TextField(blank=True)
    businessProvider = models.ForeignKey(BusinessProvider, blank=True, null=True, on_delete=models.DO_NOTHING)
    jabberID = models.CharField(max_length=255, blank=True, null=True)
    jabberRoom = models.BooleanField(default=True)

    class Meta:
        nested_fields = ['team', 'customer', 'members']
        default_permissions = ('add', 'change', 'delete', 'view', 'control')
        rdf_type = 'hd:project'
        depth = 0

    def __str__(self):
        return self.name


class Member(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)

    class Meta:
        depth = 0

    def __str__(self):
        return self.name


Member._meta.container_path = "project-members/"
