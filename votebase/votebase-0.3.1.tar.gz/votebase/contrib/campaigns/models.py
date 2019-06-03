from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from votebase.contrib.crm.models import Bundle
from votebase.core.surveys.models import Survey, Round

User = get_user_model()

EXECUTION_ONCE = 'ONCE'
EXECUTION_PERSISTENTLY = 'PERSISTENTLY'

EXECUTION_TYPES = (
    (EXECUTION_ONCE, _(u'once')),
    (EXECUTION_PERSISTENTLY, _(u'persistently')),
)


class Campaign(models.Model):
    survey = models.ForeignKey(Survey, verbose_name=_(u'survey'))
    rounds = models.ForeignKey(Round, verbose_name=_(u'segment'))
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    title = models.CharField(_(u'title'), max_length=255)
    execution_type = models.CharField(_(u'execution type'), choices=EXECUTION_TYPES, default=EXECUTION_ONCE, max_length=255)
    execution_date = models.DateTimeField(u'execution date', blank=True, default=None, null=True)
    bundles = models.ManyToManyField(Bundle, verbose_name=_(u'bundles'))
    created = models.DateTimeField(_(u'create'), default=now())
    modified = models.DateTimeField(_(u'modified'))

    class Meta:
        db_table = 'votebase_campaigns'
        verbose_name = _(u'campaign')
        verbose_name_plural = _(u'campaigns')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        self.modified = now()
        self.save(**kwargs)
