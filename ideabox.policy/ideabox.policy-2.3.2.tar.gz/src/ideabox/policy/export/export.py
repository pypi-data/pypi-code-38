# -*- coding: utf-8 -*-

from Products.CMFPlone.utils import safe_unicode
from collective.excelexport.exportables.dexterityfields import BaseFieldRenderer
from collective.excelexport.exportables.dexterityfields import (
    DexterityFieldsExportableFactory,
)
from collective.excelexport.exportables.dexterityfields import TextFieldRenderer
from ideabox.policy.export.interfaces import IExtendedProjectExportable
from ideabox.policy.interfaces import IIdeaboxPolicyLayer
from plone import api
from plone.app.textfield.interfaces import IRichText
from z3c.form.interfaces import NO_VALUE
from zope.component import adapts
from zope.component import getAdapters
from zope.interface import Interface
from zope.schema.interfaces import IText
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.i18n import translate

from ideabox.policy import _


class FullTextFieldRenderer(TextFieldRenderer):
    adapts(IText, Interface, IIdeaboxPolicyLayer)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        if not value or value == NO_VALUE:
            return ""

        text = safe_unicode(self._get_text(value))

        return text


class FullRichTextFieldRenderer(FullTextFieldRenderer):
    adapts(IRichText, Interface, IIdeaboxPolicyLayer)

    def _get_text(self, value):
        ptransforms = api.portal.get_tool("portal_transforms")
        return ptransforms.convert("html_to_text", value.output).getData().strip()


class ProjectExportablesFactory(DexterityFieldsExportableFactory):
    portal_types = ["Project"]

    def get_exportables(self):
        project_extended = [
            ad[1] for ad in getAdapters((self.context,), IExtendedProjectExportable)
        ]
        return project_extended


class ExtendedRenderer(BaseFieldRenderer):
    adapts(Interface)
    name = ""

    def __init__(self, context):
        self.context = context

    def __repr__(self):
        return "<%s - %s>" % (self.__class__.__name__, self.name)

    def render_header(self):
        return self.name


class UserPropertyRenderer(ExtendedRenderer):
    prop = ""

    def render_value(self, obj):
        try:
            value = obj.getProperty(self.prop)
            if isinstance(value, str):
                value = value.decode("utf8")
            return value
        except ValueError:
            return


class PositiveRatingRenderer(ExtendedRenderer):
    name = _(u"Positive rating ")

    def render_value(self, obj):
        annotations = IAnnotations(obj)
        vote = annotations.get("cioppino.twothumbs.yays")
        if vote:
            return len(annotations["cioppino.twothumbs.yays"])
        return 0


class NegativeRatingRenderer(ExtendedRenderer):
    name = _(u"Negative rating ")

    def render_value(self, obj):
        annotations = IAnnotations(obj)
        vote = annotations.get("cioppino.twothumbs.nays")
        if vote:
            return len(annotations["cioppino.twothumbs.nays"])
        return 0


class PositiveVotersListRenderer(ExtendedRenderer):
    name = _(u"Voters in favour")

    def render_value(self, obj):
        annotations = IAnnotations(obj)
        voters = []
        vote = annotations.get("cioppino.twothumbs.yays")
        if vote:
            for voter in annotations["cioppino.twothumbs.yays"]:
                voters.append(voter)
        return voters


class NegativeVotersListRenderer(ExtendedRenderer):
    name = _(u"Voters opposed")

    def render_value(self, obj):
        annotations = IAnnotations(obj)
        voters = []
        vote = annotations.get("cioppino.twothumbs.nays")
        if vote:
            for voter in annotations["cioppino.twothumbs.nays"]:
                voters.append(voter)
        return voters


class UserIdRenderer(UserPropertyRenderer):
    name = _(u"User ID")
    prop = "id"


class UserLastNameRenderer(UserPropertyRenderer):
    name = _(u"Last name")
    prop = "last_name"


class UserFirstNameRenderer(UserPropertyRenderer):
    name = _(u"First name")
    prop = "first_name"


class UserAddressRenderer(UserPropertyRenderer):
    name = _(u"Address")
    prop = "address"


class UserGenderRenderer(UserPropertyRenderer):
    name = _(u"Gender")
    prop = "gender"

    def render_value(self, obj):
        value = super(UserGenderRenderer, self).render_value(obj)
        if value:
            factory = getUtility(IVocabularyFactory, "ideabox.vocabularies.gender")
            vocabulary = factory(self.context)
            try:
                return translate(
                    vocabulary.getTerm(obj.getProperty("gender")).title,
                    target_language=api.portal.get_current_language(),
                )
            except KeyError:
                return


class UserBirthdateRenderer(UserPropertyRenderer):
    name = _(u"Birthdate")
    prop = "birthdate"

    def render_collection_entry(self, obj, value):
        return value.strftime("%d/%m/%Y")

    def render_style(self, obj, base_style):
        base_style.num_format_str = "dd/mm/yyyy"
        return base_style

    def render_value(self, obj):
        value = super(UserBirthdateRenderer, self).render_value(obj)
        if value:
            return self.render_collection_entry(obj, value)


class UserIamRenderer(UserPropertyRenderer):
    name = _(u"I am")
    prop = "iam"

    def render_value(self, obj):
        value = super(UserIamRenderer, self).render_value(obj)
        if value:
            factory = getUtility(IVocabularyFactory, "collective.taxonomy.iam")
            vocabulary = factory(self.context)
            try:
                return translate(
                    vocabulary.getTerm(obj.getProperty("iam")).title,
                    target_language=api.portal.get_current_language(),
                )
            except KeyError:
                return


class UserZipCodeRenderer(UserPropertyRenderer):
    name = _(u"Zip code")
    prop = "zip_code"


class UserVotesRenderer(ExtendedRenderer):
    name = _(u"Votes")

    def render_value(self, obj):
        projects = []
        userid = obj.getProperty("id")
        portal = api.portal.get()["projets"]
        for project in api.content.find(context=portal, portal_type="Project"):
            annotations = IAnnotations(project.getObject())
            vote = annotations.get("cioppino.twothumbs.yays")
            if vote:
                if userid in annotations["cioppino.twothumbs.yays"]:
                    projects.append(project.Title)
        return projects
