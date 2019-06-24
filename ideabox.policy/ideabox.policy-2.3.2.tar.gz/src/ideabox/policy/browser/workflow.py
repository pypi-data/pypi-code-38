# -*- coding: utf-8 -*-

from DateTime import DateTime
from ZODB.PersistentMapping import PersistentMapping
from datetime import datetime
from plone import api
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import NO_VALUE
from zope import schema
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import implements
from zope.interface.interface import InterfaceClass

from ideabox.policy import _


class IWorkflowForm(Interface):
    """Marker interface for workflow history form"""


class WorkflowDataProvider(object):
    def get(self):
        return self.values.get(self.field.__name__, NO_VALUE)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

    @property
    def values(self):
        return {
            l.get("review_state"): l.get("time").asdatetime()
            for l in self.form.context.workflow_history.values()[0]
        }


class WorkflowHistoryForm(Form):
    implements(IWorkflowForm)
    ignoreContext = True

    _states = (
        "deposited",
        "project_analysis",
        "vote",
        "result_analysis",
        "selected",
        "rejected",
        "study_in_progress",
        "in_progress",
        "realized",
    )

    @property
    def workflow(self):
        return self.context.workflow_history.values()[0]

    def update(self):
        current_state = api.content.get_state(obj=self.context)
        states = self._states[: self._states.index(current_state) + 1]
        for idx, state in enumerate(states):
            self.fields += Fields(
                InterfaceClass(
                    "IWorkflowHistory{0}",
                    attrs={
                        state: schema.Date(
                            title=translate(state, domain="plone"), required=True
                        )
                        for l in self.workflow
                        if l.get("review_state") == state
                    },
                )
            )
        super(WorkflowHistoryForm, self).update()

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        workflow_history = self.context.workflow_history
        for line in workflow_history.values()[0]:
            state = line.get("review_state")
            if state in data:
                line["time"] = DateTime(
                    datetime.combine(data[state], datetime.min.time())
                )
        self.context.workflow_history = PersistentMapping(workflow_history.items())
        self.request.response.redirect(self.context.absolute_url())


class WorkflowEditView(FormWrapper):
    form = WorkflowHistoryForm
