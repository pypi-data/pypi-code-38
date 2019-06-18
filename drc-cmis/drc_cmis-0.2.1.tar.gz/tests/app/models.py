from uuid import uuid4

from django.db import models


class EnkelvoudigInformatieObject(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid4)
    identificatie = models.CharField(max_length=40, default=uuid4)
    bronorganisatie = models.CharField(max_length=9)
    creatiedatum = models.DateField()
    titel = models.CharField(max_length=200)
    vertrouwelijkheidaanduiding = models.CharField(max_length=200)
    auteur = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    beschrijving = models.TextField(max_length=1000)
    ontvangstdatum = models.DateField(null=True, blank=True)
    verzenddatum = models.DateField(null=True, blank=True)
    indicatie_gebruiksrecht = models.NullBooleanField(blank=True, default=None)
    ondertekening_soort = models.CharField(max_length=10, blank=True)
    ondertekening_datum = models.DateField(blank=True, null=True)
    informatieobjecttype = models.URLField()
    formaat = models.CharField(max_length=255, blank=True)
    taal = models.CharField(max_length=255, blank=True)
    bestandsnaam = models.CharField(max_length=255, blank=True)
    inhoud = models.FileField(upload_to='uploads/%Y/%m/')
    link = models.URLField(max_length=200, blank=True)
    integriteit_algoritme = models.CharField(max_length=20, blank=True)
    integriteit_waarde = models.CharField(max_length=128, blank=True)
    integriteit_datum = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.identificatie)
