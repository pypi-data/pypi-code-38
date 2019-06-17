from __future__ import unicode_literals

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _

from .models import QuestionPlugin


@plugin_pool.register_plugin
class CmspluginSurveyPlugin(CMSPluginBase):
    name = _('Survey')
    model = QuestionPlugin
    cache = False
    text_enabled = True
    raw_id_fields = ('question',)

    def render(self, context, instance, placeholder):
        context = super(CmspluginSurveyPlugin, self).render(context, instance, placeholder)
        context['question'] = instance.question
        context['form'] = instance.question.answer_form_class(prefix='survey-plugin-{}'.format(instance.id))
        context['can_vote'] = instance.question.can_vote(context['request']) if 'request' in context else False
        return context

    def get_render_template(self, context, instance, placeholder):
        return 'cmsplugin_survey/{}.html'.format(instance.template)
