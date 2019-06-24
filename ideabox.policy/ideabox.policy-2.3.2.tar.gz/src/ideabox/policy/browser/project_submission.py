# -*- coding: utf-8 -*-

from plone.z3cform.layout import FormWrapper
from ideabox.policy.form.project_submission import ProjectSubmissionForm
from plone import api


class ProjectSubmissionView(FormWrapper):
    form = ProjectSubmissionForm

    def enable_submission(self):
        return api.portal.get_registry_record(
            "ideabox.policy.browser.controlpanel.IIdeaBoxSettingsSchema.project_submission",
            default=True,
        )
