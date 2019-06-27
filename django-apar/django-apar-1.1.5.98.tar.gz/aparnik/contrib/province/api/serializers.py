from rest_framework import serializers
from aparnik.api.serializers import ModelSerializer

from aparnik.contrib.province.models import Province, City, Town, Shahrak

class ProvinceListSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()
    url_city = serializers.SerializerMethodField()
    url_shahrak = serializers.SerializerMethodField()

    class Meta:
        model = Province
        fields = [
            'id',
            'title',
            'url_details',
            'url_city',
            'url_shahrak',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())

    def get_url_city(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url_city())

    def get_url_shahrak(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url_shahrak())

class ProvinceCreateSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()
    url_city = serializers.SerializerMethodField()
    url_shahrak = serializers.SerializerMethodField()

    class Meta:
        model = Province

        fields = [
            'id',
            'title',
            'url_details',
            'url_city',
            'url_shahrak',
        ]

        read_only_fields = [
            'url_details',
            'url_city',
            'url_shahrak',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())

    def get_url_city(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url_city())

    def get_url_shahrak(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url_shahrak())

class ProvinceDetailSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()
    url_city = serializers.SerializerMethodField()
    url_shahrak = serializers.SerializerMethodField()

    class Meta:
        model = Province
        fields = [
            'id',
            'title',
            'url_details',
            'url_city',
            'url_shahrak',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())

    def get_url_city(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url_city())

    def get_url_shahrak(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url_shahrak())

# city
class CityListSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()
    url_town = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CityListSerializer, self).__init__(*args, **kwargs)
        self.fields['province'] = ProvinceDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = City
        fields = [
            'id',
            'title',
            'url_details',
            'url_town',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())

    def get_url_town(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url_town())

class CityCreateSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()
    url_town = serializers.SerializerMethodField()

    class Meta:
        model = City

        fields = [
            'id',
            'title',
            'province',
            'url_details',
            'url_town',
        ]

        read_only_fields = [
            'url_details',
            'url_town',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())

    def get_url_town(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url_town())


class CityDetailSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()
    url_town = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CityDetailSerializer, self).__init__(*args, **kwargs)
        self.fields['province'] = ProvinceDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = City
        fields = [
            'id',
            'title',
            'url_details',
            'url_town',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())

    def get_url_town(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url_town())

# shahrak
class ShahrakListSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(ShahrakListSerializer, self).__init__(*args, **kwargs)
        self.fields['province'] = ProvinceDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = Shahrak
        fields = [
            'id',
            'title',
            'url_details',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())

class ShahrakCreateSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()

    class Meta:
        model = Shahrak

        fields = [
            'id',
            'title',
            'province',
            'url_details',
        ]

        read_only_fields = [
            'url_details',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())


class ShahrakDetailSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(ShahrakDetailSerializer, self).__init__(*args, **kwargs)
        self.fields['province'] = ProvinceDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = Shahrak
        fields = [
            'id',
            'title',
            'url_details',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())

# town
class TownListSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TownListSerializer, self).__init__(*args, **kwargs)
        self.fields['city'] = CityDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = Town
        fields = [
            'id',
            'title',
            'url_details',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())

class TownCreateSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TownCreateSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Town

        fields = [
            'id',
            'title',
            'city',
            'url_details',
        ]

        read_only_fields = [
            'id',
            'url_details',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())


class TownDetailSerializer(ModelSerializer):

    url_details = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TownDetailSerializer, self).__init__(*args, **kwargs)
        self.fields['city'] = CityDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = Town
        fields = [
            'id',
            'title',
            'url_details',
        ]

    def get_url_details(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_url())