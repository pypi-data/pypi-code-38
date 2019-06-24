# -*- coding: utf-8 -*-
import hashlib
import time
import password_generator

from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from plone import api
from plone import schema
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from z3c.form import button
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import IFieldsForm
from zope.component import getUtility
from zope.interface import implements
from zope.i18n import translate

from ideabox.policy import _
from ideabox.policy.form.project_submission import IProjectSubmission
from ideabox.policy.userdataschema import IEnhancedUserDataSchema
from ideabox.policy.utils import execute_under_admin


class IProjectEncoding(IEnhancedUserDataSchema):
    mail = schema.Email(title=_(u"Email"), required=False)


class ProjectEncodingForm(Form):
    label = _(u"Project encoding")
    implements(IFieldsForm)
    fields = Fields(IProjectEncoding).select(
        "last_name",
        "first_name",
        "gender",
        "mail",
        "birthdate",
        "address",
        "zip_code",
        "iam",
    )

    fields = fields + Fields(IProjectSubmission).select(
        "title", "project_theme", "project_district", "body", "project_image"
    )

    fields["project_theme"].widgetFactory = MultiSelect2FieldWidget
    fields["project_district"].widgetFactory = MultiSelect2FieldWidget
    fields["gender"].widgetFactory = RadioFieldWidget

    _required_fields = ("title", "project_theme", "project_district", "body")

    ignoreContext = True

    def update(self):
        for name, field in self.fields.items():
            field.field.required = name in self._required_fields
        super(ProjectEncodingForm, self).update()

    def create_user(self, data):
        if data["mail"]:
            existing_user = api.user.get(userid=data["mail"].lower())
            if existing_user:
                self.update_user(existing_user, data)
                return existing_user
        properties = dict(
            last_name=data["last_name"]
            or translate(_(u"Anonymous"), context=self.request),
            first_name=data["first_name"],
            gender=data["gender"],
            birthdate=data["birthdate"],
            zip_code=data["zip_code"],
            iam=data["iam"],
            address=data["address"],
        )
        if not data["mail"]:
            normalizer = getUtility(IIDNormalizer)
            mail = "{0}_{1}_{2}@liege2025.be".format(
                normalizer.normalize(data["title"])[:20],
                normalizer.normalize(data["last_name"])[:5],
                hashlib.md5(str(time.time())).hexdigest()[:4],
            )
        else:
            mail = data["mail"]

        return api.user.create(
            email=mail.lower(),
            password="@1aA{0}".format(password_generator.generate()),
            properties=properties,
        )

    def update_user(self, user, data):
        updates = {}
        new_properties = {
            "last_name": data["last_name"]
            or translate(_(u"Anonymous"), context=self.request),
            "first_name": data["first_name"],
            "gender": data["gender"],
            "birthdate": data["birthdate"],
            "zip_code": data["zip_code"],
            "iam": data["iam"],
            "address": data["address"],
        }
        for field, new_value in new_properties.items():
            if not new_value:
                continue
            if user.getProperty(field) != new_value:
                updates[field] = new_value
        user.setMemberProperties(mapping=updates)

    def send_request(self, data):
        user = self.create_user(data)

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
            original_author=user.id,
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

    @button.buttonAndHandler(_(u"Send"), name="send")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.send_request(data)
