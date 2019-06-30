from rest_framework import serializers

from aparnik.packages.shops.products.api.admin.serializers import ProductAdminListSerializer


from aparnik.packages.educations.courses.models import Course


class CourseAdminListSerializer(ProductAdminListSerializer):

    def __init__(self, *args, **kwargs):
        super(CourseAdminListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Course
        fields = ProductAdminListSerializer.Meta.fields + [

        ]

        read_only_fields = ProductAdminListSerializer.Meta.read_only_fields + [

        ]