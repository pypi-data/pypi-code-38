from rest_flex_fields import FlexFieldsModelSerializer


class BaseModelSerializer(FlexFieldsModelSerializer):
    pass


class DestroyModelSerializer():
    """
    Generic delete serializer.
    """

    def destroy(self):
        self.instance.delete()
