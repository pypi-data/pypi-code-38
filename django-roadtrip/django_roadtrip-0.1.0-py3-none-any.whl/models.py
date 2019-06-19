from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
import datetime
import logging

logger = logging.getLogger(__name__)


class RoadTripProfile(models.Model):
    """Représente un utilisateur du module roadtrip"""

    class Meta:
        verbose_name = "profil"

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE
    )

    @property
    def username(self):
        return self.user.username

    @property
    def display_name(self):
        return self.user.get_full_name()

    @property
    def roadtrips(self):
        return self.roadtrip_set.all()

    def __str__(self):
        return self.display_name


class Vehicle(models.Model):
    """
    Représente un véhicule.
    Un véhicule est associé à un utilisateur.
    """

    class Meta:
        verbose_name = "véhicule"

    profile = models.ForeignKey(
        RoadTripProfile,
        verbose_name="profil",
        related_name='vehicles',
        on_delete=models.CASCADE
    )
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=255)
    tank_capacity = models.DecimalField("capacité du réservoir", max_digits=8, decimal_places=2)

    @property
    def display_name(self):
        return "{} {}".format(self.brand, self.model)

    def __str__(self):
        return "Véhicule de {} : {} {}".format(
            self.profile.display_name,
            self.brand,
            self.model
        )


class RoadTrip(models.Model):
    """
    Représente un roadtrip
    Un roadtrip est associé à un utilisateur et à une liste de véhicule.
    """

    class Meta:
        verbose_name = 'voyage'

    profile = models.ForeignKey(
        RoadTripProfile,
        verbose_name="profil",
        on_delete=models.CASCADE
    )
    title = models.CharField("titre", max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    date_start = models.DateField("date de début")
    date_end = models.DateField("date de fin", null=True, blank=True, default=None)
    mileage_start = models.IntegerField("kilométrage de début")
    mileage_end = models.IntegerField("kilométrage de fin", null=True, blank=True, default=None)

    @property
    def is_finish(self):
        return self.date_end is not None and self.date_end < datetime.date.today()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        rep = "{} : ".format(self.title)
        if self.date_end:
            rep += "du {:%d/%m/%Y} au {:%d/%m/%Y}".format(self.date_start, self.date_end)
        else:
            rep += "débuté le {:%d/%m/%Y}".format(self.date_start)

        rep += " ({})".format(self.profile.display_name)
        return rep


class RoadTripEvent(models.Model):
    """
    Représente un événement d'un roadtrip.
    Il s'agit d'une classe de base
    """
    class Meta:
        verbose_name = 'événement'

    roadtrip = models.ForeignKey(
        RoadTrip,
        verbose_name='voyage',
        related_name='events',
        on_delete=models.CASCADE
    )
    date = models.DateField()
    location = models.CharField("localisation", max_length=255)
    lat = models.DecimalField("latitude", max_digits=9, decimal_places=6)
    lon = models.DecimalField("longitude", max_digits=9, decimal_places=6)
    mileage = models.IntegerField("kilométrage", null=True, blank=True)

    @property
    def type(self):
        try:
            tmp = self.refuelevent
            return "Carburant"
        except RoadTripEvent.DoesNotExist:
            pass

        try:
            tmp = self.sleepevent
            return "Sommeil"
        except RoadTripEvent.DoesNotExist:
            pass

        try:
            tmp = self.stopevent
            return "Arrêt"
        except RoadTripEvent.DoesNotExist:
            pass

        return "Inconnu"

    def clean(self):
        errors = {}

        all_events = RoadTripEvent.objects.exclude(pk=self.pk).filter(roadtrip=self.roadtrip)

        if self.mileage:
            tmp = all_events.filter(
                date__lt=self.date,
                mileage__isnull=False,
                mileage__gt=self.mileage
            )
            if tmp.exists():
                e = tmp.first()
                msg = "Le kilométrage est trop petit pour cette date. (par exemple, le {:%d/%m/%Y} : {} kms)".format(e.date, e.mileage)
                errors['mileage'] = ValidationError(msg)

            tmp = all_events.filter(
                date__gt=self.date,
                mileage__isnull=False,
                mileage__lt=self.mileage
            )
            if tmp.exists():
                e = tmp.first()
                msg = "Le kilométrage est trop grand pour cette date. (par exemple, le {:%d/%m/%Y} : {} kms)".format(
                    e.date, e.mileage)
                errors['mileage'] = ValidationError(msg)

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return "Événement : le {:%d/%m/%Y} à {}".format(self.date, self.location)


class RefuelEvent(RoadTripEvent):
    class Meta:
        verbose_name = "événement : Plein de carburant"
        verbose_name_plural = "événement : Pleins de carburant"

    vehicle = models.ForeignKey(
        Vehicle,
        verbose_name="véhicule",
        related_name='refuels',
        on_delete=models.CASCADE
    )
    amount = models.DecimalField("quantité", max_digits=8, decimal_places=2)
    unity_price = models.DecimalField("prix de l'unité", max_digits=6, decimal_places=3)

    @property
    def price(self):
        return self.amount * self.unity_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return "Plein de carburant : {:%Y/%m/%d} - {} unités à {}"\
            .format(self.date, self.amount, self.unity_price)


class StopEvent(RoadTripEvent):
    class Meta:
        verbose_name = "événement : Arrêt"

    def __str__(self):
        return "Arrêt : le {:%d/%m/%Y} à {}".format(self.date, self.location)


class SleepEvent(RoadTripEvent):
    class Meta:
        verbose_name = "événement : Nuit de sommeil"
        verbose_name_plural = "événement : Nuits de sommeil"

    def __str__(self):
        return "Nuit de sommeil : le {:%d/%m/%Y} à {}".format(self.date, self.location)
