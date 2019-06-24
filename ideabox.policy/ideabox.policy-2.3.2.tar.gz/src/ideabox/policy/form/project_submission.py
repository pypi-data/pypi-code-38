# -*- coding: utf-8 -*-

from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from ideabox.policy import _
from ideabox.policy import logger
from ideabox.policy.content.project import IProject
from ideabox.policy.utils import execute_under_admin
from plone import api
from plone.namedfile.field import NamedBlobImage
from plone.registry.interfaces import IRegistry
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IFieldsForm
from zope import schema
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implements


class IProjectSubmission(IProject):
    title = schema.TextLine(title=_(u"Title"), required=True)

    project_image = NamedBlobImage(title=_(u"Project image"), required=False)


class ProjectSubmissionForm(Form):

    implements(IFieldsForm)
    fields = Fields(IProjectSubmission).select(
        "title",
        "project_theme",
        "project_district",
        "body",
        "project_image",
        "original_author",
    )
    fields["project_theme"].widgetFactory = MultiSelect2FieldWidget
    fields["project_district"].widgetFactory = MultiSelect2FieldWidget

    fields["original_author"].mode = HIDDEN_MODE

    ignoreContext = True

    def update(self):
        super(ProjectSubmissionForm, self).update()
        self.widgets["original_author"].value = api.user.get_current().getProperty(
            "fullname"
        )

    def send_mail(self, url):
        lang = api.portal.get_current_language()[:2]
        email = api.portal.get_registry_record(
            "ideabox.policy.browser.controlpanel.IIdeaBoxSettingsSchema.project_manager_email",
            default=None,
        )
        if email is None:
            logger.warn("missing email for project submission notification")
            return

        list_mail = email.split(";")

        body = translate(
            _(
                u"email_body_project_submission",
                default=u"""A new project has been created you can access it at the following url:
              ${url}
              """,
                mapping={u"url": url},
            ),
            target_language=lang,
        )
        for mail in list_mail:
            api.portal.send_email(
                recipient=mail,
                subject=translate(_(u"New project submission"), target_language=lang),
                body=body,
            )

    def send_request(self, data):
        registry = getUtility(IRegistry)
        folder = registry.get("ideabox.new.project.folder")
        if not folder.startswith("/"):
            folder = "/{0}".format(folder)
        container = api.content.get(path=folder)
        project_obj = execute_under_admin(
            container,
            api.content.create,
            type="Project",
            title=data["title"],
            project_theme=data["project_theme"],
            project_district=data["project_district"],
            body=data["body"],
            container=container,
            original_author=api.user.get_current().id,
        )
        execute_under_admin(
            container, api.content.transition, obj=project_obj, transition="deposit"
        )
        if data["project_image"]:
            execute_under_admin(
                project_obj,
                api.content.create,
                type="Image",
                title=data["project_image"].filename,
                image=data["project_image"],
                container=project_obj,
            )
        self.request.response.redirect(project_obj.absolute_url())
        self.send_mail(project_obj.absolute_url())

    @button.buttonAndHandler(_(u"Send"), name="send")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.send_request(data)
