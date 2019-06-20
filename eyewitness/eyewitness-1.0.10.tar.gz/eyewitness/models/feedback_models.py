from peewee import (
    BooleanField,
    CharField,
    TimestampField,
    ForeignKeyField,
    IntegerField,
    Model
)

from eyewitness.models.db_proxy import DATABASE_PROXY
from eyewitness.models.detection_models import ImageInfo


class BaseModel(Model):
    class Meta:
        database = DATABASE_PROXY


class RegisteredAudience(BaseModel):
    audience_id = CharField(unique=True, primary_key=True)
    user_id = CharField(null=False)
    platform_id = CharField(null=False)
    register_time = TimestampField()
    description = CharField()


class FalseAlertFeedback(BaseModel):
    # peewee didn't support compositeKey as foreignKey, using field to specify field
    audience_id = ForeignKeyField(RegisteredAudience)
    image_id = ForeignKeyField(ImageInfo, null=True)
    receive_time = TimestampField()
    feedback_meta = CharField()
    # TODO: if the is_false_alert field needed??
    is_false_alert = BooleanField()


class BboxAnnotationFeedback(BaseModel):
    # peewee didn't support compositeKey as foreignKey, using field to specify field
    audience_id = ForeignKeyField(RegisteredAudience)
    image_id = ForeignKeyField(ImageInfo, null=True)
    receive_time = TimestampField()
    feedback_meta = CharField()
    is_false_alert = BooleanField()
    x1 = IntegerField()
    x2 = IntegerField()
    y1 = IntegerField()
    y2 = IntegerField()
    label = CharField()
