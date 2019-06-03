""" Serializers used throughout the Contact Message Rest API
"""
from rest_framework_mongoengine.serializers import DocumentSerializer

from core_website_app.components.contact_message.models import ContactMessage


class ContactMessageSerializer(DocumentSerializer):
    """ Represents the contact message serializer
    """
    class Meta:
        model = ContactMessage
        fields = ["id",
                  "name",
                  "email",
                  "content"]
        read_only_fields = ('id', )
