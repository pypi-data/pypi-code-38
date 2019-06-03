""" Saved Query Serializers
"""
from rest_framework_mongoengine.serializers import DocumentSerializer

from core_explore_example_app.components.saved_query.models import SavedQuery


class SavedQuerySerializer(DocumentSerializer):
    """ Saved Query serializer
    """
    class Meta:
        """ Meta
        """
        model = SavedQuery
        fields = "__all__"
        read_only_fields = ('user_id', 'displayed_query')
