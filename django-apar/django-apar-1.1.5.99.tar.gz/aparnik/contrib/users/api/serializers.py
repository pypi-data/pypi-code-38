from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError

from aparnik.utils.utils import convert_iran_phone_number_to_world_number
from aparnik.contrib.province.api.serializers import CityDetailSerializer
from aparnik.contrib.province.models import City
from aparnik.contrib.invitation.models import Invite
from aparnik.api.serializers import ModelSerializer
from aparnik.utils.formattings import formatprice

User = get_user_model()

user_detail_url = serializers.HyperlinkedIdentityField(view_name='aparnik-api:users:detail', lookup_field='username')
user_update_url = serializers.HyperlinkedIdentityField(view_name='aparnik-api:users:update', lookup_field='username')


class UserSummaryListSerializer(ModelSerializer):
    url = user_detail_url
    avatar = serializers.SerializerMethodField()
    register_date = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(UserSummaryListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = [
            'sys_id',
            'url',
            'first_name',
            'last_name',
            'username_mention',
            'sex',
            'avatar',
            'register_date',
        ]

        read_only_fields = [
            'sys_id',
            'url',
            'avatar',
            'register_date',
            'username_mention',
        ]

    def get_avatar(self, obj):
        from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
        return FileFieldListSerailizer(obj.avatar, many=False, context=self.context).data if obj.avatar else None

    def get_register_date(self, obj):
        return obj.created_at


class UserDetailSerializer(UserSummaryListSerializer):

    url = user_detail_url
    url_update = user_update_url
    notification_unread_count = serializers.SerializerMethodField()
    aparnik_bon_quantities_accessible = serializers.SerializerMethodField()
    aparnik_bon_price_accessible = serializers.SerializerMethodField()
    aparnik_bon_price_accessible_string = serializers.SerializerMethodField()
    aparnik_bon_price_accessible_and_wallet_string = serializers.SerializerMethodField()
    co_sale = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(UserDetailSerializer, self).__init__(*args, **kwargs)

        if 'context' in kwargs:
            # user = kwargs["context"]["request"].user
            self.fields['current_city'] = CityDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = User
        fields = UserSummaryListSerializer.Meta.fields + [
            'url',
            'url_update',
            'uuid',
            'username',
            'birthdate',
            'email',
            'invitation_code',
            'last_login',
            'is_new_registered',
            'wallet',
            'wallet_string',
            'notification_unread_count',
            'aparnik_bon_quantities_accessible',
            'aparnik_bon_price_accessible',
            'aparnik_bon_price_accessible_string',
            'aparnik_bon_price_accessible_and_wallet_string',
            'co_sale',
        ]

        read_only_fields = UserSummaryListSerializer.Meta.read_only_fields + [
            'uuid',
            'last_login',
            'is_new_registered',
            'wallet',
            'wallet_string',
            'notification_unread_count',
            'aparnik_bon_quantities_accessible',
            'aparnik_bon_price_accessible',
            'aparnik_bon_price_accessible_string',
            'aparnik_bon_price_accessible_and_wallet_string',
            'co_sale',
        ]

    def get_notification_unread_count(self, obj):
        return obj.notification_set.unread(user=obj).count()

    def get_aparnik_bon_quantities_accessible(self, obj):
        from aparnik.packages.shops.vouchers.models import Voucher
        return Voucher.objects.quantities_accessible(obj)

    def get_aparnik_bon_price_accessible(self, obj):
        from aparnik.packages.shops.vouchers.models import Voucher
        return Voucher.objects.price_accessible(obj)

    def get_aparnik_bon_price_accessible_string(self, obj):
        from aparnik.packages.shops.vouchers.models import Voucher
        return Voucher.objects.price_accessible_string(obj)

    def get_aparnik_bon_price_accessible_and_wallet_string(self, obj):
        bon_price = self.get_aparnik_bon_price_accessible(obj)
        price = obj.wallet + bon_price
        return '%s' % formatprice.format_price(price)

    def get_co_sale(self, obj):
        from aparnik.packages.shops.cosales.api.serializers import CoSaleUserListSerializer
        return CoSaleUserListSerializer(obj, many=False, read_only=True, context=self.context).data


class UserCreateSerializer(UserDetailSerializer):

    username = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(UserCreateSerializer, self).__init__(*args, **kwargs)

        if 'context' in kwargs:
            # user = kwargs["context"]["request"].user
            # self.fields['birth_place'] = CityDetailSerializer(read_only=True, context=kwargs['context'])
            self.fields['current_city'] = CityDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = User

        fields = UserDetailSerializer.Meta.fields + [
            'passwd',
        ]

        read_only_fields = UserDetailSerializer.Meta.read_only_fields + [
        ]

        write_only_fields = [
            'passwd',
        ]

    def validate_username(self, value):
        """
        Check that the blog post is about Django.
        """
        username = convert_iran_phone_number_to_world_number(value)
        try:
            User.objects.get(username=username)
            ValidationError({
                'username': [
                    _('This user register before.')
                ]
            })
        except Exception:
            pass
        return username
#


class UserUpdateSerializer(UserDetailSerializer):

    cc = serializers.IntegerField(write_only=True, required=False)
    invited_by = serializers.CharField(write_only=True, required=False)
    avatar_id = serializers.IntegerField(write_only=True, required=False)
    username_mention_update = serializers.CharField(write_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super(UserUpdateSerializer, self).__init__(*args, **kwargs)

        if 'context' in kwargs:
            # user = kwargs["context"]["request"].user
            # self.fields['current_city'] = CityDetailSerializer(read_only=True, context=kwargs['context'])
            pass

    class Meta:
        model = User

        fields = UserDetailSerializer.Meta.fields + [
            'avatar_id',
            'cc',
            'invited_by',
            'passwd',
            'username_mention_update',
        ]

        read_only_fields = UserDetailSerializer.Meta.read_only_fields + [
            'username',
        ]

        write_only_fields = ['passwd', 'username_mention_update']

    def validate_invited_by(self, value):

        self.invite_check(invitation_code=value)
        return value

    def invite_check(self, invitation_code):
        invite = None
        invitation_code = invitation_code
        if invitation_code is not None:
            try:

                invited_by = User.objects.get(invitation_code=invitation_code)
            except:
                raise ValidationError({'invited_by': [_('The invitation code is wrong.'),]})
            invite = Invite(invite=self.instance, invited_by=invited_by)
            invite.clean()

        return invite

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.sex = validated_data.get('sex', instance.sex)
        instance.passwd = validated_data.get('passwd', instance.passwd)
        instance.username_mention = validated_data.get('username_mention_update', instance.username_mention)
        if instance.current_city:
            current_city = instance.current_city.id
        else:
            current_city = None
        instance.current_city = City.objects.filter(id=validated_data.get('cc', current_city)).first()

        if instance.avatar:
            avatar = instance.avatar.id
        else:
            avatar = None

        from aparnik.contrib.filefields.models import FileField
        instance.avatar = FileField.objects.filter(id=validated_data.get('avatar_id', avatar)).first()
        try:
            instance.save()
        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        invite = self.invite_check(invitation_code=validated_data.get('invited_by', None))

        if invite:
            invite.save()

        return instance

    def get_current_city(self, obj):
        return CityDetailSerializer(obj.current_city, read_only=True, context=self.context).data

    def get_avatar(self, obj):
        from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
        return FileFieldListSerailizer(obj.avatar, many=False, context=self.context).data if obj.avatar else None
