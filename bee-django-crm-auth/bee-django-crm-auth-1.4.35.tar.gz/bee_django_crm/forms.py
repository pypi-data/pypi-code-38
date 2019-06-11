# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from django import forms

from .validators import jpg_validator, poster_image_size_validator
from .models import PreUser,RegCode, ApplicationQuestion, ApplicationOption, Source, \
    PreUserTrack, Contract, PreUserContract, Poster, PreUserFee
from .models import PREUSER_GENDER_CHOICES, PREUSER_GRADE_CHOICES, PREUSER_LEVEL_CHOICES, CONTRACT_PERIOD_CHOICES
from .utils import get_referral_user_name_with_user, get_preuser_source


# 管理者添加的preuser表
class PreuserCreateForm(forms.ModelForm):
    name = forms.CharField(label='姓名',
                           widget=forms.TextInput(attrs={'placeholder': '姓名 (必填)'}))
    mobile = forms.CharField(label='电话', widget=forms.TextInput(attrs={'placeholder': '电话 (必填)'}),
                             error_messages={'unique': u'该电话已存在'})
    gender = forms.ChoiceField(choices=PREUSER_GENDER_CHOICES, label='性别', widget=forms.RadioSelect, required=True)
    wx = forms.CharField(label='微信号', widget=forms.TextInput(attrs={'placeholder': '微信号'}), required=False)

    class Meta:
        model = PreUser
        fields = ['name', "mobile", "gender", "province", "city", "wx"]

# 会员根据课程卡密，自己注册
class PreuserCouponCreateForm(PreuserCreateForm):
    code = forms.CharField(label='课程卡号',widget=forms.TextInput(attrs={'placeholder': '课程卡号 (必填)'}))
    password = forms.CharField(label='课程密码',widget=forms.TextInput(attrs={'placeholder': '课程密码 (必填)'}))
    class Meta:
        model = PreUser
        fields = ['code','password','name', "mobile", "gender", "province", "city", "wx"]


class RegCodeCheckForm(forms.ModelForm):
    reg_name = forms.CharField(label='课程卡号',widget=forms.TextInput(attrs={'placeholder': '课程卡号 (必填)'}),required=False)
    reg_code = forms.CharField(label='课程密码',widget=forms.TextInput(attrs={'placeholder': '课程密码'}),required=False)
    class Meta:
        model = RegCode
        fields = ['reg_name','reg_code']


# 管理者更新的preuser表
class PreuserUpdateAdminForm(PreuserCreateForm):
    grade = forms.ChoiceField(choices=PREUSER_GRADE_CHOICES, label='意向', required=False)

    # source = forms.ModelChoiceField(queryset=Source.objects.filter(is_show=True), label='来源', required=False)

    referral_user_id1 = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'onchange': 'get_referral_user_name(1);'}),
                                        help_text="", label="推荐人id")
    referral_user_id2 = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'onchange': 'get_referral_user_name(2);'}),
                                        help_text="", label="接引人id")

    def __init__(self, preuser, *args, **kwargs):
        super(PreuserUpdateAdminForm, self).__init__(*args, **kwargs)
        #

        referral_user_name1 = u"无"
        referral_user_name2 = u"无"
        if self.instance.referral_user1_id:
            self.initial['referral_user_id1'] = self.instance.referral_user1_id
            referral_user_name1 = get_referral_user_name_with_user(self.instance.referral_user1.id)
        if self.instance.referral_user2_id:
            self.initial['referral_user_id2'] = self.instance.referral_user2_id
            referral_user_name2 = get_referral_user_name_with_user(self.instance.referral_user2.id)
        self.fields[
            'referral_user_id1'].help_text = u"(推荐人：<text id='referral_user_name1'>" + referral_user_name1 + u"</text>)"
        self.fields[
            'referral_user_id2'].help_text = u"(接引人：<text id='referral_user_name2'>" + referral_user_name2 + u"</text>)"
        # try:
        # from itertools import chain
        # source = get_preuser_source(preuser.id)
        # self.source_queryset = chain(source_queryset, [source])
        # self.initial['source'] = "aa"
        # except Exception as e:
        #     print(e)
        # print(self.source_queryset)
        # for i in self.source_queryset:
        #     print(i.name)
        from django.db.models import Q
        source_queryset = Source.objects.filter(Q(is_show=True) | Q(preuser__source=preuser.source)).distinct()
        self.fields["source"] = forms.ModelChoiceField(queryset=source_queryset, label='来源', required=False)

    class Meta:
        model = PreUser
        fields = ['name', "mobile", "gender", "grade", "wx", "birthday", "province", "city", "address", 'source',
                  # fields = ['name', "mobile", "gender", "grade", "wx", "birthday", "province", "city", "address",
                  "referral_user_id1", "referral_user_id2", "email", "job", "hobby", "married", "children", "job_info",
                  "family"]


# 用户自己更新的preuser表
class PreuserUpdateUserForm(PreuserCreateForm):
    birthday = forms.DateField(label='出生日期', help_text='格式：2017-01-01', error_messages={'invalid': u'日期格式不正确'})
    address = forms.CharField(widget=forms.Textarea, label='地址', required=True)

    class Meta:
        model = PreUser
        fields = ['name', "mobile", "gender", "wx", "birthday", "province", "city", "address", ]


class PreuserSearchForm(forms.ModelForm):
    grade_choices = ((-1, '全部'), (0, '无'), (1, '弱'), (2, '强'))
    level = forms.ChoiceField(choices=PREUSER_LEVEL_CHOICES, label='级别', required=False)
    grade = forms.ChoiceField(choices=grade_choices, label='意愿', required=False)
    name = forms.CharField(label='姓名', required=False)
    mobile = forms.CharField(label='电话', required=False)
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), label='合同', required=False)
    source_name = forms.CharField(label='报名来源', required=False)
    referral_name1 = forms.CharField(required=False, label="推荐人姓名")

    class Meta:
        model = PreUser
        fields = ['level', 'grade', 'name', "mobile", "contract", 'source_name', 'referral_name1', "province", "city", ]


# ===source===
class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['name', 'reg_name', 'is_show', 'is_poster']


class SourceUpdateForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['reg_name', 'is_show', 'is_poster']


class SourceSearchForm(forms.Form):
    name = forms.CharField(label='渠道名', required=False)


# ===preuser track===
class PreuserTrackForm(forms.ModelForm):
    class Meta:
        model = PreUserTrack
        fields = ['tracked_at', 'info']


# ===application question======
class ApplicationQuestionCreateForm(forms.ModelForm):
    class Meta:
        model = ApplicationQuestion
        fields = ['name', "order_by", "input_type", 'is_required']


class ApplicationOptionCreateForm(forms.ModelForm):
    class Meta:
        model = ApplicationOption
        fields = ['name', "order_by"]


# =====contract======
class ContractForm(forms.ModelForm):
    period = forms.ChoiceField(choices=CONTRACT_PERIOD_CHOICES, label="周期")

    class Meta:
        model = Contract
        fields = ['name', "period", "duration", "price"]

    # def validate_unique(self):
    #     exclude = self._get_validation_exclusions()
    #     # exclude.remove('level') # allow checking against the missing attribute
    #
    #     try:
    #         self.instance.validate_unique(exclude=exclude)
    #     except forms.ValidationError, e:
    #         self._update_errors(e.message_dict)

    def clean(self):
        period = self.cleaned_data['period']
        duration = self.cleaned_data['duration']
        if not period == "9999":
            if not duration:
                raise forms.ValidationError(u"请填写时长")
        return self.cleaned_data


class ContractUpdateAgreementForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ["agreement"]


# ===== preuser contract======
class PreuserContractForm(forms.ModelForm):
    study_at = forms.DateTimeField(label=u'开课日期', required=True)

    class Meta:
        model = PreUserContract
        fields = ['contract', "price", "study_at", "info"]


class PreuserContractAgreementForm(forms.ModelForm):
    is_user_agree = forms.BooleanField(required=True, label=u'同意以上协议')

    class Meta:
        model = PreUserContract
        fields = ['is_user_agree']


class PreuserContractSearchForm(forms.Form):
    name = forms.CharField(label='姓名', required=False)
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), label='合同', required=False)


class PreuserFeeForm(forms.ModelForm):
    class Meta:
        model = PreUserFee
        fields = ["pay_status", "price", "paid_at", "info"]


class PreuserFeeSearchForm(forms.Form):
    preuser_pay_status_choices = ((-1, '全部'), (1, "全款缴清"), (2, "分期中"))
    is_checked_choices = ((-1, '全部'), (1, "已审核"), (0, "未审核"))

    is_checked = forms.ChoiceField(choices=is_checked_choices, label='审核', required=False)
    preuser_pay_status = forms.ChoiceField(choices=preuser_pay_status_choices, label='缴费人', required=False)
    pay_start = forms.CharField(label='缴费开始日期', required=False)
    pay_end = forms.CharField(label='缴费结束日期', required=False)


# ====== poster ======

class PosterCreateForm(forms.ModelForm):
    photo = forms.ImageField(validators=[jpg_validator, poster_image_size_validator])

    class Meta:
        model = Poster
        fields = ["photo"]


class PosterUpdateForm(forms.ModelForm):
    qrcode_width = forms.IntegerField(min_value=1, label='二维码宽度')
    qrcode_height = forms.IntegerField(min_value=1, label='二维码高度')

    class Meta:
        model = Poster
        fields = ["qrcode_width", "qrcode_height", "qrcode_pos_x", "qrcode_pos_y", "qrcode_color", "is_show"]
