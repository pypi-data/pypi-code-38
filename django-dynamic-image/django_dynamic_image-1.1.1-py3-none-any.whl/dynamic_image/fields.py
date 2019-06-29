from django.db.models import ImageField
from django.db.models.signals import pre_save, post_init


class DynamicImageField(ImageField):
    def __init__(self, *args, **kwargs):
        # Increase max length to support longer filenames
        if "max_length" not in kwargs:
            kwargs["max_length"] = 255
        if "upload_to" not in kwargs:
            kwargs["upload_to"] = "dummy"
        self.prime_upload = kwargs.get("prime_upload", False)
        if "prime_upload" in kwargs:
            del kwargs["prime_upload"]
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        if self.prime_upload:
            post_init.connect(self.pre_save_get_upload_to, sender=cls)
        pre_save.connect(self.pre_save_get_upload_to, sender=cls)

    def pre_save_get_upload_to(self, instance=None, *args, **kwargs):
        if hasattr(instance, "get_upload_to"):
            self.upload_to = instance.get_upload_to(self.attname)
