# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import Course, Section, Part, Video, Question, Option, UserImage, UserCourse, UserPartNote


# ===== course contract======
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', "subtitle", "is_auto_open"]


# ===== section contract======
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['group_name', 'title', 'extra_title', 'type', 'number', 'auto_pass']


# ===== part contract======
class PartForm(forms.ModelForm):
    type = forms.ChoiceField(choices=((1, '视频'), (2, "选择题")), label='小节类型')

    class Meta:
        model = Part
        fields = ['title', "extra_title", 'number', 'type', 'image', 'has_answer']


class PartUpdateForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['title', 'extra_title', 'number', 'image', 'has_answer']


# ===== part contract======
class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['number', 'content']


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserImage
        fields = ['image']


# ===== question option contract======
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['number', 'title', 'score']


class QuestionSearchForm(forms.ModelForm):
    title = forms.CharField(label='问题', required=False)

    class Meta:
        model = Question
        fields = ['course', 'section', 'title']


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['number', 'title', "is_correct"]


# =====用户相关========
class UserCourseForm(forms.ModelForm):
    class Meta:
        model = UserCourse
        fields = ['course']


class UserPartNoteForm(forms.ModelForm):
    class Meta:
        model = UserPartNote
        fields = ['note', 'is_open']
