from django.db import models
from django.db.models import Q
from django.db.models.signals import m2m_changed, post_save
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import date

from wafer.schedule.models import ScheduleItem, Venue

from volunteers.utils import get_start_end_for_scheduleitem


@python_2_unicode_compatible
class Volunteer(models.Model):

    RATINGS = (
            (0, 'No longer welcome'),
            (1, 'Poor'),
            (2, 'Not great'),
            (3, 'Average'),
            (4, 'Good'),
            (5, 'Superb'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='volunteer')

    tasks = models.ManyToManyField('Task', blank=True)
    preferred_categories = models.ManyToManyField('TaskCategory', blank=True)
    preferred_task_types = models.ManyToManyField('TaskTemplate', blank=True)

    staff_rating = models.IntegerField(null=True, blank=True, choices=RATINGS)
    staff_notes = models.TextField(null=True, blank=True)

    @property
    def annotated_tasks(self):
        return self.tasks.annotate_all()

    def __str__(self):
        return u'%s' % self.user


@python_2_unicode_compatible
class AbstractTaskTemplate(models.Model):
    class Meta:
        abstract = True

    MANDATORY_TASK_FIELDS = [
        'name', 'description', 'nbr_volunteers_min', 'nbr_volunteers_max',
    ]
    TASK_TEMPLATE_FIELDS = MANDATORY_TASK_FIELDS + ['category']

    name = models.CharField(max_length=1024, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey('TaskCategory', blank=True, null=True)

    nbr_volunteers_min = models.IntegerField(default=1, blank=True, null=True)
    nbr_volunteers_max = models.IntegerField(default=1, blank=True, null=True)

    def clean_fields(self, exclude=None):
        if exclude is None:
            exclude = []

        errors = {}

        try:
            super().clean_fields(exclude)
        except ValidationError as exc:
            errors = exc.error_dict

        for field in self.MANDATORY_TASK_FIELDS:
            if field not in exclude and not getattr(self, field):
                setattr(self, field, None)

        # Only keep fields that have been overridden from the template
        if hasattr(self, 'template') and self.template:
            for field in self.TASK_TEMPLATE_FIELDS:
                if (field not in exclude and
                        getattr(self.template, field) == getattr(self, field)):
                    setattr(self, field, None)

        # If TaskTemplate or Task without template, check mandatory fields
        if not hasattr(self, 'template') or not self.template:
            for field in self.MANDATORY_TASK_FIELDS:
                if field not in exclude and not getattr(self, field):
                    errors[field] = ['Your task needs a %s' % field]

        if errors:
            raise ValidationError(errors)


@python_2_unicode_compatible
class TaskTemplate(AbstractTaskTemplate):
    """a template for a Task"""
    video_task = models.BooleanField(default=False)

    def __str__(self):
        return u'Template for %s' % self.name


class TaskQuerySet(models.QuerySet):
    @staticmethod
    def coalesce_from_template(field):
        return models.Func(
            models.F(field),
            models.F('template__%s' % field),
            function='coalesce',
        )

    def annotate_all(self):
        return self.select_related('template').annotate(
            nbr_volunteers=models.Count('volunteers'),
            min_volunteers=self.coalesce_from_template('nbr_volunteers_min'),
            max_volunteers=self.coalesce_from_template('nbr_volunteers_max'),
            name_=self.coalesce_from_template('name'),
            description_=self.coalesce_from_template('description'),
            category_=self.coalesce_from_template('category__name'),
        )


@python_2_unicode_compatible
class Task(AbstractTaskTemplate):
    """Something to do.

    If the template is set, it will override the name, description and
    category fields.
    """
    class Meta:
        ordering = ['start', '-end', 'schedule_item', 'template__name', 'name']

    objects = TaskQuerySet.as_manager()

    venue = models.ForeignKey(
        Venue,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    start = models.DateTimeField(blank=True)
    end = models.DateTimeField(blank=True)

    # Volunteers
    volunteers = models.ManyToManyField('Volunteer', blank=True)

    schedule_item = models.ForeignKey(
        ScheduleItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    template = models.ForeignKey(
        TaskTemplate,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return u'%s (%s: %s - %s)' % (self.get_name(), self.start.date(),
                                      self.start.time(), self.end.time())

    def nbr_volunteers(self):
        return self.volunteer_set.count()
    nbr_volunteers.short_description = "# reg'd"

    def datetime(self):
        return u'%s: %s - %s' % (date(self.start.date(), 'l, F d'),
                                 date(self.start.time(), 'H:i'),
                                 date(self.end.time(), 'H:i'))

    def get_name(self):
        if self.name:
            return self.name
        if self.template:
            return self.template.name
    get_name.short_description = 'Name'

    def get_description(self):
        if self.description:
            return self.description
        if self.template:
            return self.template.description
    get_description.short_description = 'Description'

    def get_category(self):
        if self.category:
            return self.category
        if self.template:
            return self.template.category
    get_category.short_description = 'Category'

    def get_nbr_volunteers_min(self):
        if self.nbr_volunteers_min:
            return self.nbr_volunteers_min
        if self.template:
            return self.template.nbr_volunteers_min
    get_nbr_volunteers_min.short_description = '# min'

    def get_nbr_volunteers_max(self):
        if self.nbr_volunteers_max:
            return self.nbr_volunteers_max
        if self.template:
            return self.template.nbr_volunteers_max
    get_nbr_volunteers_max.short_description = '# max'

    def get_venue(self):
        if self.schedule_item:
            return self.schedule_item.venue
        return self.venue
    get_venue.short_description = 'Venue'

    def clean_fields(self, exclude=None):
        if exclude is None:
            exclude = []
        if 'venue' in exclude:
            return super().clean_fields(exclude)

        errors = {}
        try:
            super().clean_fields(exclude)
        except ValidationError as exc:
            errors = exc.error_dict

        if 'venue' not in exclude and not self.get_venue():
            errors.setdefault('venue', []).append(_('Venue needs to be set'))
        if 'venue' not in exclude and self.schedule_item and self.venue:
            errors.setdefault('venue', []).append(_(
                'Venue cannot be set for a task attached to an Event'
            ))

        if self.schedule_item:
            self.start, self.end = get_start_end_for_scheduleitem(
                self.schedule_item
            )

        if 'start' not in exclude and not self.start:
            errors.setdefault('start', []).append(_('Tasks need a start time'))

        if 'end' not in exclude and not self.end:
            errors.setdefault('end', []).append(_('Tasks need an end time'))

        if errors:
            raise ValidationError(errors)

    def concurrent_tasks(self):
        return Task.objects.filter(
            (Q(start__lte=self.start) & Q(end__gt=self.start)) |
            (Q(start__gt=self.start) & Q(start__lt=self.end))
        ).exclude(id=self.id)


@python_2_unicode_compatible
class TaskCategory(models.Model):
    """ Category of a task, like: cleanup, moderation, etc. """

    class Meta:
        verbose_name = _('task category')
        verbose_name_plural = _('task categories')

    name = models.CharField(max_length=1024)
    description = models.TextField()

    def __str__(self):
        return self.name


def update_video_tasks(sender, **kwargs):
    if kwargs.get('action', 'post_add') != 'post_add':
        return
    schedule_item = kwargs['instance']

    try:
        start, end = get_start_end_for_scheduleitem(schedule_item)
    except ValueError:
        # slot didn't have a start time, ignore
        return

    for task in Task.objects.filter(schedule_item=schedule_item).all():
        modified = False
        if task.start != start or task.end != end:
            modified = True
            task.start = start
            task.end = end
            task.volunteers.clear()
        if task.venue != schedule_item.venue:
            modified = True
            task.venue = schedule_item.venue
        if modified:
            task.save()


post_save.connect(update_video_tasks, sender=ScheduleItem)
m2m_changed.connect(update_video_tasks, sender=ScheduleItem.slots.through)
