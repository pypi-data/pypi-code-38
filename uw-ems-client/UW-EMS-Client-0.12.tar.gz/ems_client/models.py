from restclients_core import models

# Create your models here.


class Status(models.Model):
    STATUS_TYPE_BOOKED_SPACE = -14
    STATUS_TYPE_WAIT = -13
    STATUS_TYPE_CANCEL = -12
    STATUS_TYPE_INFO_ONLY = -11
    STATUS_TYPE_CHOICES = (
        (STATUS_TYPE_BOOKED_SPACE, 'Booked Space'),
        (STATUS_TYPE_WAIT, 'Wait'),
        (STATUS_TYPE_CANCEL, 'Cancel'),
        (STATUS_TYPE_INFO_ONLY, 'Info Only'),
    )

    description = models.CharField(max_length=30)
    id = models.PositiveIntegerField(primary_key=True)
    status_type_id = models.SmallIntegerField(choices=STATUS_TYPE_CHOICES)
    display_on_web = models.BooleanField(default=None)

    def __str__(self):
        return self.description


class EventType(models.Model):
    description = models.CharField(max_length=30)
    id = models.PositiveIntegerField(primary_key=True)
    display_on_web = models.BooleanField(default=None)

    def __str__(self):
        return self.description


class Building(models.Model):
    description = models.CharField(max_length=50)
    building_code = models.CharField(max_length=20, null=True)
    id = models.PositiveIntegerField(primary_key=True)
    time_zone_description = models.CharField(max_length=255)
    time_zone_abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.description


class Room(models.Model):
    room = models.CharField(max_length=20)
    description = models.CharField(max_length=50)
    dv_building = models.CharField(max_length=50)
    active = models.BooleanField()
    building = models.ForeignKey(Building, on_delete=models.PROTECT)
    id = models.PositiveIntegerField(primary_key=True)
    external_reference = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.description


class Booking(models.Model):
    booking_date = models.DateField()
    room_description = models.CharField(max_length=75)
    time_event_start = models.DateTimeField()
    time_event_end = models.DateTimeField()
    group_name = models.CharField(max_length=50)
    event_name = models.CharField(max_length=255)
    reservation_id = models.PositiveIntegerField()
    event_type_description = models.CharField(max_length=30)
    contact = models.CharField(max_length=113)
    id = models.PositiveIntegerField(primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.PROTECT)
    time_booking_start = models.DateTimeField()
    time_booking_end = models.DateTimeField()
    time_zone = models.CharField(max_length=10)
    building_code = models.CharField(max_length=20)
    dv_building = models.CharField(max_length=50)
    room_code = models.CharField(max_length=20)
    dv_room = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    status_type_id = models.SmallIntegerField(
        choices=Status.STATUS_TYPE_CHOICES)
    date_added = models.DateTimeField(null=True)
    date_changed = models.DateTimeField(null=True)
    contact_email_address = models.CharField(max_length=75, null=True)


class ServiceOrderDetail(models.Model):
    booking_date = models.DateField()
    service_order_start_time = models.TimeField(null=True)
    service_order_end_time = models.TimeField(null=True)
    resource_description = models.CharField(max_length=50)
    resource_external_reference = models.CharField(max_length=255, blank=True)
    service_order_id = models.PositiveIntegerField()
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT)
