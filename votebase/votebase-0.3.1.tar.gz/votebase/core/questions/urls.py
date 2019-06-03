from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from votebase.core.questions.views.checkbox import CheckboxCreateView, CheckboxUpdateView
from votebase.core.questions.views.date import DateCreateView, DateUpdateView
from votebase.core.questions.views.email import EmailCreateView, EmailUpdateView
from votebase.core.questions.views.gender import GenderCreateView, GenderUpdateView
from votebase.core.questions.views.general import IndexView, QuestionDeleteView, PreviewView, QuestionDeleteImageView, OptionDeleteImageView
from votebase.core.questions.views.matrix_checkbox import MatrixCheckboxCreateView, MatrixCheckboxUpdateView
from votebase.core.questions.views.matrix_radio import MatrixRadioCreateView, MatrixRadioUpdateView
from votebase.core.questions.views.true_false import TrueFalseCreateView, TrueFalseUpdateView
from votebase.core.questions.views.phone import PhoneCreateView, PhoneUpdateView
from votebase.core.questions.views.radio import RadioCreateView, RadioUpdateView
from votebase.core.questions.views.select_multiple import SelectMultipleCreateView, SelectMultipleUpdateView
from votebase.core.questions.views.select_single import SelectSingleCreateView, SelectSingleUpdateView
from votebase.core.questions.views.stars import StarsCreateView, StarsUpdateView
from votebase.core.questions.views.textarea import TextareaCreateView, TextareaUpdateView
from votebase.core.questions.views.textfield import TextfieldCreateView, TextfieldUpdateView
from votebase.core.questions.views.thumbs import ThumbsCreateView, ThumbsUpdateView
from votebase.core.questions.views.time import TimeCreateView, TimeUpdateView


urlpatterns = [
    # Radio
    url(_(r'create/radio/(?P<pk>[-\d]+)/$'), RadioCreateView.as_view(), name='questions_create_radio'),
    url(_(r'update/radio/(?P<pk>[-\d]+)/$'), RadioUpdateView.as_view(), name='questions_update_radio'),

    # Gender
    url(_(r'create/gender/(?P<pk>[-\d]+)/$'), GenderCreateView.as_view(), name='questions_create_gender'),
    url(_(r'update/gender/(?P<pk>[-\d]+)/$'), GenderUpdateView.as_view(), name='questions_update_gender'),

    # Checkbox
    url(_(r'create/checkbox/(?P<pk>[-\d]+)/$'), CheckboxCreateView.as_view(), name='questions_create_checkbox'),
    url(_(r'update/checkbox/(?P<pk>[-\d]+)/$'), CheckboxUpdateView.as_view(), name='questions_update_checkbox'),

    # Selects
    url(_(r'create/select-single/(?P<pk>[-\d]+)/$'), SelectSingleCreateView.as_view(), name='questions_create_select_single'),
    url(_(r'update/select-single/(?P<pk>[-\d]+)/$'), SelectSingleUpdateView.as_view(), name='questions_update_select_single'),
    url(_(r'create/select-multiple/(?P<pk>[-\d]+)/$'), SelectMultipleCreateView.as_view(), name='questions_create_select_multiple'),
    url(_(r'update/select-multiple/(?P<pk>[-\d]+)/$'), SelectMultipleUpdateView.as_view(), name='questions_update_select_multiple'),

    # Textfield
    url(_(r'create/textfield/(?P<pk>[-\d]+)/$'), TextfieldCreateView.as_view(), name='questions_create_textfield'),
    url(_(r'update/textfield/(?P<pk>[-\d]+)/$'), TextfieldUpdateView.as_view(), name='questions_update_textfield'),

    # Email
    url(_(r'create/email/(?P<pk>[-\d]+)/$'), EmailCreateView.as_view(), name='questions_create_email'),
    url(_(r'update/email/(?P<pk>[-\d]+)/$'), EmailUpdateView.as_view(), name='questions_update_email'),

    # Phone
    url(_(r'create/phone/(?P<pk>[-\d]+)/$'), PhoneCreateView.as_view(), name='questions_create_phone'),
    url(_(r'update/phone/(?P<pk>[-\d]+)/$'), PhoneUpdateView.as_view(), name='questions_update_phone'),

    # Textarea
    url(_(r'create/textarea/(?P<pk>[-\d]+)/$'), TextareaCreateView.as_view(), name='questions_create_textarea'),
    url(_(r'update/textarea/(?P<pk>[-\d]+)/$'), TextareaUpdateView.as_view(), name='questions_update_textarea'),

    # Matrixes
    url(_(r'create/matrix-radio/(?P<pk>[-\d]+)/$'), MatrixRadioCreateView.as_view(), name='questions_create_matrix_radio'),
    url(_(r'update/matrix-radio/(?P<pk>[-\d]+)/$'), MatrixRadioUpdateView.as_view(), name='questions_update_matrix_radio'),
    url(_(r'create/matrix-checkbox/(?P<pk>[-\d]+)/$'), MatrixCheckboxCreateView.as_view(), name='questions_create_matrix_checkbox'),
    url(_(r'update/matrix-checkbox/(?P<pk>[-\d]+)/$'), MatrixCheckboxUpdateView.as_view(), name='questions_update_matrix_checkbox'),

    # True/False
    url(_(r'create/true-false/(?P<pk>[-\d]+)/$'), TrueFalseCreateView.as_view(), name='questions_create_true_false'),
    url(_(r'update/true-false/(?P<pk>[-\d]+)/$'), TrueFalseUpdateView.as_view(), name='questions_update_true_false'),

    # Ratings
    url(_(r'create/stars/(?P<pk>[-\d]+)/$'), StarsCreateView.as_view(), name='questions_create_stars'),
    url(_(r'update/stars/(?P<pk>[-\d]+)/$'), StarsUpdateView.as_view(), name='questions_update_stars'),
    url(_(r'create/thumbs/(?P<pk>[-\d]+)/$'), ThumbsCreateView.as_view(), name='questions_create_thumbs'),
    url(_(r'update/thumbs/(?P<pk>[-\d]+)/$'), ThumbsUpdateView.as_view(), name='questions_update_thumbs'),

    # Date & time
    url(_(r'create/date/(?P<pk>[-\d]+)/$'), DateCreateView.as_view(), name='questions_create_date'),
    url(_(r'update/date/(?P<pk>[-\d]+)/$'), DateUpdateView.as_view(), name='questions_update_date'),
    url(_(r'create/time/(?P<pk>[-\d]+)/$'), TimeCreateView.as_view(), name='questions_create_time'),
    url(_(r'update/time/(?P<pk>[-\d]+)/$'), TimeUpdateView.as_view(), name='questions_update_time'),

    # General
    url(_(r'image/delete/(?P<pk>[-\d]+)/$'), QuestionDeleteImageView.as_view(), name='questions_delete_image'),
    url(_(r'image/delete/option/(?P<pk>[-\d]+)/$'), OptionDeleteImageView.as_view(), name='questions_delete_image_option'),
    url(_(r'delete/(?P<pk>[-\d]+)/$'), QuestionDeleteView.as_view(), name='questions_delete'),
    url(_(r'preview/(?P<pk>[-\d]+)/$'), PreviewView.as_view(), name='questions_preview'),
    url(r'(?P<pk>[-\d]+)/$', IndexView.as_view(), name='questions_index'),
]
