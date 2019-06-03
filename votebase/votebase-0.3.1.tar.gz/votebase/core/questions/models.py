import shortuuid
import os
import sys

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from votebase.core.questions.managers import OptionQuerySet
from votebase.core.surveys.models import Survey
from votebase.core.utils.common import remove_files
from votebase.core.utils.helpers import get_class, img


def question_upload_to_image(instance, filename):
    file_name, file_extension = os.path.splitext(filename)
    uuid = instance.generate_question_uuid()
    return settings.MEDIA_IMAGES_DIR + 'q_%s%s' % (uuid, file_extension)


def option_upload_to_image(instance, filename):
    file_name, file_extension = os.path.splitext(filename)
    uuid = instance.generate_question_uuid()
    return settings.MEDIA_IMAGES_DIR + 'o_%s%s' % (uuid, file_extension)


class Question(models.Model):
    IMAGE_POSITION_TOP = 'TOP'
    IMAGE_POSITION_RIGHT = 'RIGHT'
    IMAGE_POSITION_BOTTOM = 'BOTTOM'
    IMAGE_POSITION_LEFT = 'LEFT'
    IMAGE_POSITIONS = (
        (IMAGE_POSITION_TOP, _(u'Top')),
        (IMAGE_POSITION_RIGHT, _(u'Right')),
        (IMAGE_POSITION_BOTTOM, _(u'Bottom')),
        (IMAGE_POSITION_LEFT, _(u'Left')),
    )
    IMAGE_SIZE_ORIGINAL = 'ORIGINAL'
    IMAGE_SIZE_30_PERCENT = '30_PERCENT'
    IMAGE_SIZE_50_PERCENT = '50_PERCENT'
    IMAGE_SIZE_80_PERCENT = '80_PERCENT'
    IMAGE_SIZE_100_PERCENT = '100_PERCENT'
    IMAGE_SIZES = (
        (IMAGE_SIZE_ORIGINAL, _(u'original')),
        (IMAGE_SIZE_30_PERCENT, u'30%'),
        (IMAGE_SIZE_50_PERCENT, u'50%'),
        (IMAGE_SIZE_80_PERCENT, u'80%'),
        (IMAGE_SIZE_100_PERCENT, u'100%'),
    )

    KIND_RADIO = 'RADIO'
    KIND_GENDER = 'GENDER'
    KIND_CHECKBOX = 'CHECKBOX'
    KIND_TEXTFIELD = 'TEXTFIELD'
    KIND_TEXTAREA = 'TEXTAREA'
    KIND_EMAIL = 'EMAIL'
    KIND_PHONE = 'PHONE'
    KIND_MATRIX_RADIO = 'MATRIX_RADIO'
    KIND_MATRIX_CHECKBOX = 'MATRIX_CHECKBOX'
    KIND_SELECT_SINGLE = 'SELECT_SINGLE'
    KIND_SELECT_MULTIPLE = 'SELECT_MULTIPLE'
    KIND_TRUE_FALSE = 'TRUE_FALSE'
    KIND_STARS = 'STARS'
    KIND_THUMBS = 'THUMBS'
    KIND_DATE = 'DATE'
    KIND_TIME = 'TIME'

    KINDS = (
        (KIND_RADIO, _('Radio')),
        (KIND_GENDER, _('Gender')),
        (KIND_CHECKBOX, _('Checkbox')),
        (KIND_TEXTFIELD, _('Textfield')),
        (KIND_TEXTAREA, _('Textarea')),
        (KIND_EMAIL, _('E-mail')),
        (KIND_PHONE, _('Phone')),
        (KIND_MATRIX_RADIO, _('Matrix radio')),
        (KIND_MATRIX_CHECKBOX, _('Matrix checkbox')),
        (KIND_SELECT_SINGLE, _('Select single')),
        (KIND_SELECT_MULTIPLE, _('Select multiple')),
        (KIND_TRUE_FALSE, _('True/False')),
        (KIND_STARS, _('Rating stars')),
        (KIND_THUMBS, _('Rating thumbs')),
        (KIND_DATE, _('Date')),
        (KIND_TIME, _('Time')),
    )

    survey = models.ForeignKey(Survey, verbose_name=_(u'survey'))
    kind = models.CharField(_(u'kind'), choices=KINDS, max_length=15, db_index=True)
    title = models.TextField(_(u'title'))
    category = models.CharField(_(u'category'), max_length=255, db_index=True, blank=True)
    image = models.ImageField(
        _(u'image attachement'), default=None, blank=True, null=True,
        height_field='image_height', width_field='image_width',
        upload_to=question_upload_to_image)
    image_width = models.IntegerField(
        _(u'width'), default=None, blank=True, null=True)
    image_height = models.IntegerField(
        _(u'height'), default=None, blank=True, null=True)
    image_position = models.CharField(
        _(u'image position'), choices=IMAGE_POSITIONS, default=IMAGE_POSITION_LEFT,
        max_length=255)
    image_size = models.CharField(_(u'image size'), choices=IMAGE_SIZES, default=IMAGE_SIZE_ORIGINAL, max_length=20)
    weight = models.PositiveIntegerField(_(u'weight'), default=0, db_index=True)
    true_label = models.CharField(_(u'true label'), default=_(u'True'), max_length=20)
    false_label = models.CharField(_(u'false label'), default=_(u'False'), max_length=20)
    is_required = models.BooleanField(_(u'mandatory'), default=False)
    is_quiz = models.BooleanField(_(u'quiz'), default=False, db_index=True)
    is_unique_answers = models.BooleanField(_(u'unique answers'), help_text=_(u'for matrix questions'), default=False)
    is_empty_row_enabled = models.BooleanField(_(u'enabled empty rows'), help_text=_(u'for matrix questions with required answer'), default=True)
    created = models.DateTimeField(_(u'created'), default=now)
    modified = models.DateTimeField(_(u'modified'))

    class Meta:
        app_label = 'questions'
        db_table = 'votebase_questions'
        verbose_name = _(u'question')
        verbose_name_plural = _(u'questions')
        ordering = ('weight', 'created')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        self.modified = now()
        if not self.pk:
            self.weight = self.survey.question_set.all().count()
        super(Question, self).save(**kwargs)

    def get_absolute_url(self):
        url_name = 'questions_update_%s' % self.kind.lower()
        return reverse(url_name, args=(self.pk, ))

    def get_voting_form(self, post_data=None, number=1):
        module_name = 'votebase.core.questions.forms.%s' % self.kind.lower()
        class_name = 'Vote%sForm' % self.kind.title().replace('_', '')
        return getattr(sys.modules[module_name], class_name)(
            self, number, post_data, prefix=self.pk)

    def get_design_form(self, post_data=None, number=1):
        module_name = 'votebase.core.questions.forms.%s' % self.kind.lower()
        class_name = 'Design%sForm' % self.kind.title().replace('_', '')
        try:
            return getattr(sys.modules[module_name], class_name)(
                self, number, post_data, prefix=self.pk)
        except AttributeError:
            return self.get_voting_form(post_data, number)

    def get_voter_form_class(self):
        module_name = 'votebase.core.questions.forms.%s' % self.kind.lower()
        class_name = 'Voter%sForm' % self.kind.title().replace('_', '')
        custom_voter_forms = getattr(settings, 'VOTEBASE_VOTER_FORMS', {})
        class_path = custom_voter_forms.get(self.kind, '{}.{}'.format(module_name, class_name))
        form_class = get_class(class_path)
        return form_class

    def get_voter_form(self, voter, number=1, *args, **kwargs):
        form_class = self.get_voter_form_class()
        return form_class(self, voter, number, prefix=self.pk, *args, **kwargs)

    def get_csv_handler(self, round=None):
        module_name = 'votebase.core.statistics.handlers.%s' % self.kind.lower()
        class_name = '%sCsvHandler' % self.kind.title().replace('_', '')
        return getattr(sys.modules[module_name], class_name)(self, round)

    def generate_question_uuid(self):
        uuid = shortuuid.uuid()
        while Question.objects.filter(image__contains=uuid).count():
            uuid = shortuuid.uuid()
        return uuid

    def delete(self, **kwargs):
        self.delete_image()
        super(Question, self).delete(**kwargs)

    def delete_image(self):
        try:
            filename = os.path.basename(self.image.name)
            remove_files(settings.MEDIA_IMAGES_ROOT, filename, True)
        except ValueError:
            pass
        except IOError:
            pass

    @property
    def image_in_base64(self):
        try:
            if self.image:
                import base64
                filename = os.path.basename(self.image.name)
                image_path = u'%s%s' % (settings.MEDIA_IMAGES_ROOT, filename)
                with open(image_path, "rb") as imageFile:
                    return base64.b64encode(imageFile.read())
        except IOError:
            pass
        return None

    def get_image_choices(self):
        choices = cache.get('question_image_choices', version=self.pk)
        use_cache = getattr(settings, 'VOTEBASE_USE_QUESTION_IMAGE_CHOICES_CACHE', True)

        if not choices or not use_cache:
            choices = []

            option_set = self.option_set.all()

            for option in option_set:
                title = mark_safe(option.title)

                if option.image:
                    title += img(option.image)
                    title = mark_safe(title)

                choice = (option.pk, title)
                choices.append(choice)

        cache.set('question_image_choices', choices, version=self.pk, timeout=60*60*12)

        return choices

    def get_image(self):
        """ Gets HTML code for image """
        if self.image:
            width = None
            height = None
            if self.image_size.endswith('_PERCENT'):
                percent = self.image_size.replace('_PERCENT', '%')
                width = percent
                height = percent
            return mark_safe(img(self.image, width=width, height=height))
        return None

    def get_number(self):
        """ Gets question order in a list """
        survey_questions = self.survey.question_set
        questions_list = list(survey_questions.values_list('id', flat=True))
        return questions_list.index(self.id) + 1

    def get_label(self, number):
        """ Gets HTML title  """

        if number:
            label = '<span class="counter"><span class="number">\
            %(number)s</span><span class="dot">.</span></span> %(title)s' % {
                'number': number,
                'title': self.title,
            }
        else:
            label = '%(title)s' % {
                'title': self.title,
            }

        if self.image:
            label += '<div class="image %s">%s</div>' % (
                self.image_position.lower(), self.get_image())

        return mark_safe(label)


class Option(models.Model):
    IMAGE_POSITION_TOP = 'TOP'
    IMAGE_POSITION_RIGHT = 'RIGHT'
    IMAGE_POSITION_BOTTOM = 'BOTTOM'
    IMAGE_POSITION_LEFT = 'LEFT'
    IMAGE_POSITIONS = (
        (IMAGE_POSITION_TOP, _(u'Top')),
        (IMAGE_POSITION_RIGHT, _(u'Right')),
        (IMAGE_POSITION_BOTTOM, _(u'Bottom')),
        (IMAGE_POSITION_LEFT, _(u'Left')),
    )

    ORIENTATION_ROW = 'ROW'
    ORIENTATION_COLUMN = 'COLUMN'
    ORIENTATIONS = (
        (ORIENTATION_ROW, _(u'Row')),
        (ORIENTATION_ROW, _(u'Column')),
    )

    question = models.ForeignKey(Question, verbose_name=_(u'question'))
    title = models.CharField(_(u'title'), max_length=512)
    image = models.ImageField(
        _(u'image'), default=None, blank=True, null=True,
        upload_to=option_upload_to_image, height_field='image_height',
        width_field='image_width')
    image_width = models.IntegerField(
        _(u'width'), default=None, blank=True, null=True)
    image_height = models.IntegerField(
        _(u'height'), default=None, blank=True, null=True)
    image_position = models.CharField(
        _(u'image position'), choices=IMAGE_POSITIONS, default=IMAGE_POSITION_LEFT,
        max_length=255)
    orientation = models.CharField(
        _(u'orientation'), choices=ORIENTATIONS, default=ORIENTATION_ROW,
        max_length=255)
    is_correct = models.BooleanField(_(u'correct'), default=False, db_index=True)
    weight = models.PositiveIntegerField(_(u'weight'), default=0, db_index=True)
    created = models.DateTimeField(_(u'created'), default=now)
    modified = models.DateTimeField(_(u'modified'))
    objects = OptionQuerySet.as_manager()

    class Meta:
        app_label = 'questions'
        db_table = 'votebase_options'
        verbose_name = _(u'option')
        verbose_name_plural = _(u'options')
        ordering = ('weight', 'created')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        self.modified = now()
        if not self.pk and not self.weight:
            self.weight = self.question.option_set.all().count()

        super(Option, self).save(**kwargs)

    def generate_question_uuid(self):
        uuid = shortuuid.uuid()
        while Option.objects.filter(image__contains=uuid).count():
            uuid = shortuuid.uuid()
        return uuid

    def delete(self, **kwargs):
        self.delete_image()
        super(Option, self).delete(**kwargs)

    def delete_image(self):
        try:
            filename = os.path.basename(self.image.name)
            remove_files(settings.MEDIA_IMAGES_ROOT, filename, True)
        except ValueError:
            pass
        except IOError:
            pass

    @property
    def image_in_base64(self):
        try:
            if self.image:
                import base64
                filename = os.path.basename(self.image.name)
                image_path = u'%s%s' % (settings.MEDIA_IMAGES_ROOT, filename)
                with open(image_path, "rb") as imageFile:
                    return base64.b64encode(imageFile.read())
        except IOError:
            pass
        return None

    def get_image_title(self):
        title = self.title
        if self.image:
            title = mark_safe(title + img(self.image,))
        return title


import votebase.core.questions.signals
