# -*- coding: utf-8 -*-


from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from rest_framework.validators import UniqueTogetherValidator

from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer
from aparnik.packages.educations.educations.models import BaseEducation, Education, Degree, Institute, FieldSubject


# BASE EDUCATION
class BaseEducationListSerializer(BaseModelListSerializer):

    def __init__(self, *args, **kwargs):
        super(BaseEducationListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseEducation
        fields = BaseModelListSerializer.Meta.fields
        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + []


class BaseEducationDetailsSerializer(BaseEducationListSerializer, BaseModelDetailSerializer):

    def __init__(self, *args, **kwargs):
        super(BaseEducationDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseEducation
        fields = BaseEducationListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields

        read_only_fields = BaseEducationListSerializer.Meta.read_only_fields + BaseModelDetailSerializer.Meta.read_only_fields + [
            'is_published']

    def get_model(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.model_obj, many=False, read_only=True, context=self.context).data


# EDUCATION
class EducationListSerializer(BaseEducationListSerializer):

    def __init__(self, *args, **kwargs):
        super(EducationListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Education
        fields = BaseEducationListSerializer.Meta.fields + [
            # 'user_obj',
        ]
        read_only_fields = BaseEducationListSerializer.Meta.read_only_fields + []


class EducationDetailsSerializers(EducationListSerializer,
                                  BaseEducationDetailsSerializer):
    institute_obj = serializers.SerializerMethodField()
    institute_obj_id = serializers.IntegerField(required=True, write_only=True)

    field_subject_obj = serializers.SerializerMethodField()
    field_subject_obj_id = serializers.IntegerField(required=True, write_only=True)

    degree_obj = serializers.SerializerMethodField()
    degree_obj_id = serializers.IntegerField(required=True, write_only=True)

    is_published = serializers.NullBooleanField()

    def __init__(self, *args, **kwargs):
        super(EducationDetailsSerializers, self).__init__(*args, **kwargs)

    class Meta:
        model = Education
        fields = EducationListSerializer.Meta.fields + BaseEducationDetailsSerializer.Meta.fields + [
            'receive_date',
            'average',
            'description',
            'institute_obj',
            'institute_obj_id',
            'field_subject_obj',
            'field_subject_obj_id',
            'degree_obj',
            'degree_obj_id',
            'is_published'
        ]

        validators = [
            UniqueTogetherValidator(
                queryset=Education.objects.all(),
                fields=('institute_obj_id', 'field_subject_obj_id', 'degree_obj_id')
            )
        ]

        read_only_fields = EducationListSerializer.Meta.read_only_fields + BaseEducationDetailsSerializer.Meta.read_only_fields + []

    def get_institute_obj(self, obj):
        return BaseEducationListPolymorphicSerializer(obj.institute_obj, many=False, read_only=True,
                                                      context=self.context).data

    def get_field_subject_obj(self, obj):
        return BaseEducationListPolymorphicSerializer(obj.field_subject_obj, many=False, read_only=True,
                                                      context=self.context).data

    def get_degree_obj(self, obj):
        return BaseEducationListPolymorphicSerializer(obj.degree_obj, many=False, read_only=True,
                                                      context=self.context).data

    def create(self, validated_data):
        institute_obj = Institute.objects.filter(id=validated_data.pop('institute_obj_id')).first()
        degree_obj = Degree.objects.filter(id=validated_data.pop('degree_obj_id')).first()
        field_subject_obj = FieldSubject.objects.filter(id=validated_data.pop('field_subject_obj_id')).first()

        education = Education.objects.create(institute_obj=institute_obj, degree_obj=degree_obj,
                                             field_subject_obj=field_subject_obj, **validated_data)

        return education

    def update(self, instance, validated_data):
        instance.institute_obj = Institute.objects.filter(id=validated_data.get('institute_obj_id', None)).get()
        instance.degree_obj = Degree.objects.filter(id=validated_data.get('degree_obj_id', None)).get()
        instance.field_subject_obj = FieldSubject.objects.filter(
            id=validated_data.get('field_subject_obj_id', None)).get()
        instance.receive_date = validated_data.get('receive_date', None)
        instance.average = validated_data.get('average', None)
        instance.description = validated_data.get('description', None)
        instance.is_published = validated_data.get('is_published', None)

        instance.save()

        return instance


# DEGREE
class DegreeListSerializer(BaseEducationListSerializer):
    def __init__(self, *args, **kwargs):
        super(DegreeListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Degree
        fields = BaseEducationListSerializer.Meta.fields + [
            'name',
        ]


class DegreeDetailsSerializer(DegreeListSerializer, BaseEducationDetailsSerializer):

    def __init__(self, *args, **kwargs):
        super(DegreeDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Degree
        fields = DegreeListSerializer.Meta.fields + BaseEducationDetailsSerializer.Meta.fields + [

        ]


# INSTITUDE
class InstituteListSerializer(BaseEducationListSerializer):

    def __init__(self, *args, **kwargs):
        super(InstituteListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Institute
        fields = BaseEducationListSerializer.Meta.fields + [
            'name'
        ]


class InstituteDetailsSerializer(InstituteListSerializer, BaseEducationDetailsSerializer):

    def __init__(self, *args, **kwargs):
        super(InstituteDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Institute
        fields = InstituteListSerializer.Meta.fields + BaseEducationDetailsSerializer.Meta.fields + [
            'name',
        ]


# FIELD SUBJECT
class FieldSubjectListSerializer(BaseEducationListSerializer):

    def __init__(self, *args, **kwargs):
        super(FieldSubjectListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = FieldSubject
        fields = BaseEducationListSerializer.Meta.fields + [
            'name',
        ]


class FieldSubjectDetailsSerializer(FieldSubjectListSerializer, BaseEducationDetailsSerializer):
    def __init__(self, *args, **kwargs):
        super(FieldSubjectDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = FieldSubject
        fields = FieldSubjectListSerializer.Meta.fields + BaseEducationDetailsSerializer.Meta.fields


class BaseEducationListPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            BaseEducation: BaseEducationListSerializer,
            Education: EducationListSerializer,
            Institute: InstituteListSerializer,
            FieldSubject: FieldSubjectListSerializer,
            Degree: DegreeListSerializer,
        }
        super(BaseEducationListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


class BaseEducationDetailsPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            BaseEducation: BaseEducationDetailsSerializer,
            Education: EducationDetailsSerializers,
            Institute: InstituteDetailsSerializer,
            FieldSubject: FieldSubjectDetailsSerializer,
            Degree: DegreeDetailsSerializer,
        }
        super(BaseEducationDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}
