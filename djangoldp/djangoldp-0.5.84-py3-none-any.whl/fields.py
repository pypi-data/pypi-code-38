import requests
from django.db import models
from rest_framework import fields


class IdURLField (fields.URLField):

    def to_representation(self, value):
        str = super(IdURLField, self).to_representation(value)
        return {'@id': str}

    def get(self, value):
        url = super(IdURLField, self).to_representation(value)
        datas = requests.get(url).json()
        return datas


class LDPUrlField (models.URLField):
    pass
