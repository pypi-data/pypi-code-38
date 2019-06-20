from peewee import (
    CharField,
    TimestampField,
    DoubleField,
    ForeignKeyField,
    IntegerField,
    Model
)

from eyewitness.models.db_proxy import DATABASE_PROXY


class BaseModel(Model):
    class Meta:
        database = DATABASE_PROXY


class ImageInfo(BaseModel):
    image_id = CharField(unique=True, primary_key=True)
    channel = CharField()
    file_format = CharField()
    timestamp = TimestampField()
    raw_image_path = CharField(null=True)
    drawn_image_path = CharField(null=True)


class BboxDetectionResult(BaseModel):
    image_id = ForeignKeyField(ImageInfo)
    x1 = IntegerField()
    x2 = IntegerField()
    y1 = IntegerField()
    y2 = IntegerField()
    label = CharField()
    meta = CharField()
    score = DoubleField()
