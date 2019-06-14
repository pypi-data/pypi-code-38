import itertools
import time
import tablib
from functools import partial
from operator import itemgetter
from datetime import datetime
from Acquisition import aq_inner
from AccessControl import getSecurityManager, Unauthorized
from plone import api
from plone import directives
from plone.app.content.browser.tableview import Table
from plone.batching import Batch
from plone.dexterity.content import Container
from plone.dexterity.browser import add
from plone.memoize.view import memoize
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from emrt.necd.content.timeit import timeit
from eea.cache import cache
from zope.component import getUtility
import zope.schema as schema
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IContextSourceBinder
from zc.dict import OrderedDict
from z3c.form import form
from z3c.form import button
from z3c.form import field
from plone.z3cform.layout import wrap_form
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema import List, Choice, TextLine, Bool
from zope.interface import Interface
from zope.interface import provider
from zope.interface import implementer
from z3c.form.interfaces import HIDDEN_MODE
from emrt.necd.content.utils import get_vocabulary_value
from emrt.necd.content.utils import user_has_ldap_role
from emrt.necd.content.utils import reduce_text
from emrt.necd.content.utilities.interfaces import IUserIsMS
from emrt.necd.content.utilities.interfaces import ISetupReviewFolderRoles
from emrt.necd.content.utilities.interfaces import IGetLDAPWrapper

from emrt.necd.content.constants import ROLE_MSA
from emrt.necd.content.constants import ROLE_MSE
from emrt.necd.content.constants import ROLE_SE
from emrt.necd.content.constants import ROLE_LR
from emrt.necd.content.constants import ROLE_CP
from emrt.necd.content.constants import LDAP_SECTOREXP
from emrt.necd.content.constants import LDAP_LEADREVIEW
from emrt.necd.content.constants import LDAP_MSA
from emrt.necd.content.constants import LDAP_MSEXPERT
from emrt.necd.content.inbox_sections import SECTIONS


QUESTION_WORKFLOW_MAP = {
    'SE': 'Sector Expert',
    'LR': 'Lead Reviewer',
    'MSC': 'MS Coordinator',
    'answered': 'Answered',
    'conclusions': 'Conclusions',
    'conclusions-lr-denied': 'Conclusions - LR denied',
    'close-requested': 'Close requested',
    'finalised': 'Finalised',
}

REVIEWFOLDER_TYPES = SimpleVocabulary.fromItems((
    (u'Inventory', 'inventory'),
    (u'Projection', 'projection')))


# Cache helper methods
def _user_name(fun, self, userid):
    return (userid, time.time() // 86400)


def get_finalisation_reasons(reviewfolder):
    """ Vocabularies are used to fetch available reasons.
        This used to have hardcoded values for 2015 and 2016.
        Currently it works like this:
            - try to get vocabulary values that end
              in the current folder title (e.g. "resolved2016")
            - if no values match, get the values which don't
              end in an year (e.g. "resolved")
        This covers the previous functionality while also supporting
        any number of upcoming years, as well as "Test"-type
        review folders.
    """
    vtool = getToolByName(reviewfolder, 'portal_vocabularies')
    reasons = [('open', 'open')]

    context_title = reviewfolder.Title().strip()

    vocab_ids = ('conclusion_reasons', )

    to_add = []
    all_terms = []

    for vocab_id in vocab_ids:
        voc = vtool.getVocabularyByName(vocab_id)
        voc_terms = voc.getDisplayList(reviewfolder).items()
        all_terms.extend(voc_terms)

    # if term ends in the review folder title (e.g. 2016)
    for term_key, term_title in all_terms:
        if term_key.endswith(context_title):
            to_add.append((term_key, term_title))

    # if no matching term keys were found,
    # use those that don't end in a year
    if not to_add:
        for term_key, term_title in all_terms:
            if not term_key[-4:].isdigit():
                to_add.append((term_key, term_title))

    reasons.extend(to_add)
    return reasons


def translate_highlights(vocab, keys):
    return tuple(vocab.getTerm(x).title for x in keys)


def get_highlight_vocabs(context):
    vocab_highlight = getUtility(
        IVocabularyFactory,
        name='emrt.necd.content.highlight')(context)

    vocab_highlight_values = tuple([
        term.value for term in vocab_highlight
    ])

    is_projection = context.type == 'projection'
    highlight_split_item = 'ec' if is_projection else 'nsms'

    # Split highlight to differentiate between
    # description and conclusion flags.
    highlight_split = vocab_highlight_values.index(highlight_split_item)
    vocab_description_flags = translate_highlights(
        vocab_highlight, vocab_highlight_values[:highlight_split])
    vocab_conclusion_flags = translate_highlights(
        vocab_highlight, vocab_highlight_values[highlight_split:])

    return vocab_description_flags, vocab_conclusion_flags, vocab_highlight


def filter_for_ms(brains, context):
    if api.user.is_anonymous():
        return brains

    user = api.user.get_current()
    roles = api.user.get_roles(user=user, obj=context)
    groups = user.getGroups()

    # Don't filter the list if user is SE, LR or Manager
    if set(roles).intersection((ROLE_SE, ROLE_LR, 'Manager')):
        return brains

    result = []
    for brain in brains:
        country = brain.country

        ldap_wrapper = getUtility(IGetLDAPWrapper)(context)

        group_msa = '{}-{}'.format(ldap_wrapper(LDAP_MSA), country)
        group_mse = '{}-{}'.format(ldap_wrapper(LDAP_MSEXPERT), country)

        is_msa = group_msa in groups
        is_mse = group_mse in groups

        if not any((is_msa, is_mse)):
            result.append(brain)

        elif is_msa and brain.observation_sent_to_msc:
            result.append(brain)

        elif is_mse and brain.observation_sent_to_mse:
            result.append(brain)

    return result


class IReviewFolder(directives.form.Schema, IImageScaleTraversable):
    """
    Folder to have all observations together
    """

    type = schema.Choice(
        title=u"Type",
        source=REVIEWFOLDER_TYPES,
        required=True,
    )


@implementer(IReviewFolder)
class ReviewFolder(Container):
    """ """


class ReviewFolderMixin(BrowserView):

    def __call__(self):
        if api.user.is_anonymous():
            raise Unauthorized
        return super(ReviewFolderMixin, self).__call__()

    @memoize
    def get_questions(self, sort_on="modified", sort_order="reverse"):
        req = self.request
        country = req.get('country', '')
        reviewYear = req.get('reviewYear', '')
        inventoryYear = req.get('inventoryYear', '')
        status = req.get('status', '')
        highlights = req.get('highlights', '')
        freeText = req.get('freeText', '')
        wfStatus = req.get('wfStatus', '')
        nfrCode = req.get('nfrCode', req.get('nfrCode[]', []))
        sectorId = req.get('sectorId', req.get('sectorId[]', []))

        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path': path,
            'portal_type': ['Observation'],
            'sort_on': sort_on,
            'sort_order': sort_order
        }

        if country != "":
            query['Country'] = country
        if status != "":
            if status != "open":
                query['observation_finalisation_reason'] = status
            else:
                query['review_state'] = [
                    'pending',
                    'close-requested',
                    'draft',
                    'conclusions',
                    'conclusions-lr-denied',
                    'conclusion-discussion',
                ]

        if reviewYear != "":
            query['review_year'] = reviewYear
        if inventoryYear != "":
            query['year'] = inventoryYear
        if highlights != "":
            query['highlight'] = highlights.split(",")
        if freeText != "":
            query['SearchableText'] = freeText
        if wfStatus != "":
            query['observation_status'] = wfStatus
        if nfrCode:
            query['nfr_code'] = dict(query=nfrCode, operator='or')
        if sectorId:
            query['GHG_Source_Category'] = dict(query=sectorId, operator='or')

        return filter_for_ms(catalog(query), context=self.context)

    def can_add_observation(self):
        sm = getSecurityManager()
        return sm.checkPermission('emrt.necd.content: Add Observation', self)

    def is_secretariat(self):
        user = api.user.get_current()
        return 'Manager' in user.getRoles()

    def is_lr(self):
        roles = api.user.get_roles(obj=self.context)
        return set(roles).intersection((ROLE_LR, 'Manager'))

    def get_countries(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('eea_member_states')
        countries = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            countries.append((term[0], term[1]))

        return countries

    def get_highlights(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        if self.context.type == 'inventory':
            voc = vtool.getVocabularyByName('highlight')
        else:
            voc = vtool.getVocabularyByName('highlight_projection')
        highlights = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            highlights.append((term[0], term[1]))

        return highlights

    def get_review_years(self):
        catalog = api.portal.get_tool('portal_catalog')
        review_years = [
            c for c in catalog.uniqueValuesFor('review_year') if
            isinstance(c, basestring)
        ]
        return review_years

    def get_inventory_years(self):
        years = []
        gfc = self.context.getFolderContents
        for b in gfc(dict(portal_type='Observation')):
            year = b.year
            # handle projection years
            if isinstance(year, list):
                years.extend(year)
            elif year:
                years.append(year)

        return set(years)

    def get_nfr_categories(self):
        vocab_factory = getUtility(
            IVocabularyFactory, name='emrt.necd.content.nfr_code')
        vocabulary = vocab_factory(self.context)
        return [(x.value, x.title) for x in vocabulary]

    def get_sector_names(self):
        vocab_factory = getUtility(
            IVocabularyFactory, name='emrt.necd.content.sector_names')
        vocabulary = vocab_factory(self.context)
        return tuple((x.value, x.title) for x in vocabulary)

    def get_finalisation_reasons(self):
        return get_finalisation_reasons(self.context)

    def is_member_state_coordinator(self):
        ldap_wrapper = getUtility(IGetLDAPWrapper)(self.context)
        return partial(
            user_has_ldap_role, LDAP_MSA, ldap_wrapper=ldap_wrapper
        )

    def is_member_state_expert(self):
        ldap_wrapper = getUtility(IGetLDAPWrapper)(self.context)
        return partial(
            user_has_ldap_role, LDAP_MSEXPERT, ldap_wrapper=ldap_wrapper
        )


class ReviewFolderView(ReviewFolderMixin):

    def contents_table(self):
        table = ReviewFolderBrowserView(aq_inner(self.context), self.request)
        return table.render()

    def can_export_observations(self):
        sm = getSecurityManager()
        return sm.checkPermission(
            'emrt.necd.content: Export Observations', self)

    def can_import_observation(self):
        return 'Manager' in api.user.get_roles()


class ReviewFolderBrowserView(ReviewFolderMixin):

    def folderitems(self, sort_on="modified", sort_order="reverse"):
        """
        """
        return [
            dict(brain=brain) for brain in
            self.get_questions(sort_on, sort_order)
        ]

    def table(self, context, request,
              sort_on='modified', sort_order="reverse"):
        pagesize = int(self.request.get('pagesize', 20))
        url = context.absolute_url()
        view_url = url + '/view'

        table = Table(
            self.request, url, view_url, self.folderitems(sort_on, sort_order),
            pagesize=pagesize
        )

        table.render = ViewPageTemplateFile(
            "browser/templates/reviewfolder_get_table.pt")
        table.reduce_text = partial(reduce_text, limit=500)
        table.is_secretariat = self.is_secretariat
        table.question_workflow_map = QUESTION_WORKFLOW_MAP

        return table

    def update_table(self, pagenumber='1', sort_on='modified',
                     sort_order="reverse", show_all=False):
        self.request.set('sort_on', sort_on)
        self.request.set('pagenumber', pagenumber)

        table = self.table(
            self.context, self.request, sort_on=sort_on, sort_order=sort_order
        )

        return table.render(table)

    def render(self):
        sort_on = self.request.get('sort_on', 'modified')
        sort_order = self.request.get('sort_order', 'reverse')
        pagenumber = self.request.get('pagenumber', '1')
        return self.update_table(pagenumber, sort_on, sort_order)


EXPORT_FIELDS = OrderedDict([
    ('getURL', 'URL'),
    ('get_ghg_source_sectors', 'Sector'),
    ('country_value', 'Country'),
    ('parameter_value', 'Parameter'),
    ('text', 'Detail'),
    ('get_is_adjustment', 'Is an adjustment'),
    ('observation_is_potential_technical_correction',
        'Is potential technical correction'),
    ('get_is_time_series_inconsistency', 'Is time series inconsistency'),
    ('get_is_not_estimated', 'Is not estimated'),
    ('nfr_code_value', 'NFR Code'),
    ('nfr_code_inventory', 'NFR Inventories Category Code'),
    ('review_year', 'Review Year'),
    ('year', 'Inventory Year'),
    ('reference_year', 'Reference Year'),
    ('pollutants_value', 'Pollutants'),
    ('scenario_type_value', 'Scenario Type'),
    ('activity_data_type', 'Activity Data Type'),
    ('activity_data', 'Activity Data'),
    ('fuel', 'Fuel'),
    ('get_is_ms_key_category', 'MS Key Category'),
    ('get_description_flags', 'Description Flags'),
    ('overview_status', 'Status'),
    ('observation_finalisation_reason', 'Conclusion'),
    ('get_conclusion_flags', 'Conclusion Flags'),
    ('observation_finalisation_text', 'Conclusion note'),
    ('observation_questions_workflow', 'Question workflow'),
    ('observation_questions_workflow_current', 'Current question workflow'),
    ('get_author_name', 'Author')
])

# Don't show conclusion notes to MS users.
EXCLUDE_FIELDS_FOR_MS = (
    'observation_finalisation_text',
)

EXCLUDE_PROJECTION_FIELDS = (
    'nfr_code_inventory',
    'reference_year',
    'scenario_type_value',
    'activity_data_type',
    'activity_data'
)

EXCLUDE_INVENTORY_FIELDS = (
    'fuel'
)


IS_FIELD_MAP = {
    'get_is_adjustment': 'Adjustment',
    'get_is_time_series_inconsistency': 'Time series inconsistency',
    'get_is_not_estimated': 'Not Estimated',
}


def yes_no_bool(boolean):
    return boolean and 'Yes' or 'No'


def get_common(iter1, iter2):
    return tuple(set(iter1).intersection(iter2))


@provider(IContextSourceBinder)
def fields_vocabulary_factory(context):
    terms = []

    user_is_ms = getUtility(IUserIsMS)(context)
    user_is_manager = 'Manager' in api.user.get_roles()
    skip_for_user = user_is_ms and not user_is_manager

    if context.type == 'projection':
        EXPORT_FIELDS['year'] = 'Projection Year'
        exclude_fields = EXCLUDE_INVENTORY_FIELDS
    else:
        exclude_fields = EXCLUDE_PROJECTION_FIELDS

    for key, value in EXPORT_FIELDS.items():
        if skip_for_user and key in EXCLUDE_FIELDS_FOR_MS:
            continue
        elif key in exclude_fields:
            continue
        terms.append(SimpleVocabulary.createTerm(key, key, value))

    return SimpleVocabulary(terms)


class IExportForm(Interface):
    exportFields = List(
        title=u"Fields to export",
        description=u"Select which fields you want to add into XLS",
        required=False,
        value_type=Choice(source=fields_vocabulary_factory)
    )

    include_qa = Bool(
        title=u'Include Q&A threads.',
        required=False
    )

    come_from = TextLine(title=u"Come from")


class ExportReviewFolderForm(form.Form, ReviewFolderMixin):

    fields = field.Fields(IExportForm)
    ignoreContext = True

    label = u"Export observations in XLS format"
    name = u"export-observation-form"

    def updateWidgets(self):
        super(ExportReviewFolderForm, self).updateWidgets()
        self.widgets['exportFields'].size = 20
        self.widgets['come_from'].mode = HIDDEN_MODE
        self.widgets['come_from'].value = '%s?%s' % (
            self.context.absolute_url(), self.request['QUERY_STRING']
        )
        if not self.is_secretariat():
            self.widgets['include_qa'].mode = HIDDEN_MODE

    def action(self):
        return '%s/export_as_xls?%s' % (
            self.context.absolute_url(),
            self.request['QUERY_STRING']
        )

    @button.buttonAndHandler(u'Export')
    def handleExport(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        return self.build_file(data)

    @button.buttonAndHandler(u"Back")
    def handleCancel(self, action):
        return self.request.response.redirect(
            '%s?%s' % (
                self.context.absolute_url(),
                self.request['QUERY_STRING']
            )
        )

    def updateActions(self):
        super(ExportReviewFolderForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')

    def render(self):
        if not self.request.get('form.buttons.extend', None):
            return super(ExportReviewFolderForm, self).render()

    def extract_data(self, form_data):
        """ Create xls file
        """
        vtool = getToolByName(self, 'portal_vocabularies')

        observations = self.get_questions()

        user_is_ms = getUtility(IUserIsMS)(self.context)
        user_is_manager = 'Manager' in api.user.get_roles()
        skip_for_user = user_is_ms and not user_is_manager
        fields_to_export = [
            name for name in form_data.get('exportFields', []) if
            not skip_for_user or name not in EXCLUDE_FIELDS_FOR_MS
        ]

        dataset = tablib.Dataset()
        dataset.title = "Observations"

        catalog = api.portal.get_tool('portal_catalog')
        qa_len = 0
        base_len = 0

        rows = []

        vocab_description_flags, vocab_conclusion_flags, vocab_highlight = (
            get_highlight_vocabs(self.context)
        )

        for observation in observations:
            row = [observation.getId]
            highlights = translate_highlights(
                vocab_highlight, observation['get_highlight'] or [])

            for key in fields_to_export:
                if key == 'observation_is_potential_technical_correction':
                    row.append(observation[key] and 'Yes' or 'No')
                elif key == 'getURL':
                    row.append(observation.getURL())
                elif key in IS_FIELD_MAP:
                    row.append(yes_no_bool(IS_FIELD_MAP[key] in highlights))
                elif key == 'get_description_flags':
                    row.append(', '.join(
                        get_common(highlights, vocab_description_flags)
                    ))
                elif key == 'get_conclusion_flags':
                    row.append(', '.join(
                        get_common(highlights, vocab_conclusion_flags)
                    ))
                elif key == 'get_is_ms_key_category':
                    row.append(
                        observation.ms_key_category and 'Yes' or 'No'
                    )
                elif key == 'observation_questions_workflow':
                    row_val = ', '.join([
                        '. '.join((
                            str(idx),
                            QUESTION_WORKFLOW_MAP.get(val, val)
                        )) for idx, val
                        in enumerate(observation[key], start=1)
                    ])
                    row.append(
                        row_val if row_val else
                        QUESTION_WORKFLOW_MAP.get(
                            observation['observation_status'],
                            'unknown'
                        )
                    )
                elif key == 'observation_questions_workflow_current':
                    row.append(QUESTION_WORKFLOW_MAP.get(
                        observation['observation_status'],
                        observation['observation_status'],
                    ))
                elif key == 'fuel':
                    fuel = get_vocabulary_value(
                        self.context.aq_parent, 'emrt.necd.content.fuel',
                        observation.getObject().fuel
                    )
                    row.append(fuel)

                # XXX: these are projection fields and need rework,
                # getObject kill performance.
                elif key == 'nfr_code_inventory':
                    row.append(observation.getObject().nfr_code_inventory)
                elif key == 'reference_year':
                    row.append(observation.getObject().reference_year)
                elif key == 'scenario_type_value':
                    row.append(observation.getObject().scenario_type_value())
                elif key == 'activity_data_type':
                    row.append(observation.getObject().activity_data_type)
                elif key == 'activity_data':
                    row.append(
                        '\n'.join(
                            observation.getObject().activity_data_value())
                    )

                else:
                    row.append(safe_unicode(observation[key]))

            if base_len == 0:
                base_len = len(row)

            if form_data.get('include_qa') and self.is_secretariat():
                # Include Q&A threads if user is Manager
                extracted_qa = self.extract_qa(catalog, observation)
                extracted_qa_len = len(extracted_qa)
                qa_len = (
                    extracted_qa_len if extracted_qa_len > qa_len else qa_len
                )
                row.extend(extracted_qa)

            rows.append(row)

        for row in rows:
            # Fill columns that are too short with emtpy values
            # as some observations have shorter QA threads.
            # Need to do this because row lengths are validated.
            row_len = len(row)
            row_qa = row_len - base_len
            row.extend([''] * (qa_len - row_qa))
            dataset.append(row)

        headers = ['Observation']
        headers.extend([EXPORT_FIELDS[k] for k in fields_to_export])
        headers.extend(['Q&A'] * qa_len)
        dataset.headers = headers
        return dataset

    def extract_qa(self, catalog, observation):
        question_brains = catalog(
            portal_type='Question',
            path=observation.getPath()
        )

        questions = tuple([brain.getObject() for brain in question_brains])

        comments = tuple(
            itertools.chain(*[
                question.get_questions() for question in questions
            ])
        )

        mapping = dict(Comment='Question', CommentAnswer='Answer')
        return tuple([
            u'{}: {}'.format(
                mapping[comment.portal_type],
                safe_unicode(comment.text)
            ) for comment in comments
        ])

    def build_file(self, data):
        """ Export filtered observations in xls
        """
        now = datetime.now()
        filename = 'EMRT-observations-{}_{}.xls'.format(
            self.context.getId(),
            now.strftime("%d-%m-%Y_%H:%M")
        )

        book = tablib.Databook((self.extract_data(data),))

        response = self.request.response
        response.setHeader("content-type", "application/vnc.ms-excel")
        response.setHeader(
            'Content-disposition',
            'attachment;filename="{filename}"'.format(filename=filename)
        )
        response.write(book.xls)
        return


ExportReviewFolderFormView = wrap_form(ExportReviewFolderForm)


def _item_user(fun, self, user, item):
    return (user.getId(), item.getId(), item.modified())


def decorate(item):
    """ prepare a plain object, so that we can cache it in a RAM cache """
    user = api.user.get_current()
    roles = api.user.get_roles(username=user.getId(), obj=item, inherit=False)
    new_item = {}
    new_item['absolute_url'] = item.absolute_url()
    new_item['observation_css_class'] = item.observation_css_class()
    new_item['getId'] = item.getId()
    new_item['Title'] = item.Title()
    new_item['observation_is_potential_significant_issue'] = \
        item.observation_is_potential_significant_issue()
    new_item['observation_is_potential_technical_correction'] = \
        item.observation_is_potential_technical_correction()
    new_item['observation_is_technical_correction'] = \
        item.observation_is_technical_correction()
    new_item['text'] = item.text
    new_item['nfr_code_value'] = item.nfr_code_value()
    new_item['modified'] = item.modified()
    new_item['observation_question_status'] = \
        item.observation_question_status()
    new_item['last_answer_reply_number'] = item.last_answer_reply_number()
    new_item['get_status'] = item.get_status()
    new_item['observation_already_replied'] = \
        item.observation_already_replied()
    new_item['reply_comments_by_mse'] = item.reply_comments_by_mse()
    new_item['observation_finalisation_reason'] = \
        item.observation_finalisation_reason()
    new_item['isCP'] = ROLE_CP in roles
    new_item['isMSA'] = ROLE_MSA in roles
    return new_item


def _catalog_change(fun, self, *args, **kwargs):
    counter = api.portal.get_tool('portal_catalog').getCounter()
    user = api.user.get_current().getId()
    path = '/'.join(self.context.getPhysicalPath())
    return (counter, user, path)


class RoleMapItem(object):

    def __init__(self, roles):
        self.isCP = ROLE_CP in roles
        self.isMSA = ROLE_MSA in roles
        self.isMSE = ROLE_MSE in roles
        self.isSE = ROLE_SE in roles
        self.isLR = ROLE_LR in roles

    def check_roles(self, rolename):
        if rolename == ROLE_CP:
            return self.isCP
        elif rolename == ROLE_MSA:
            return self.isMSA
        elif rolename == ROLE_MSE:
            return self.isMSE
        elif rolename == ROLE_SE:
            return self.isSE
        elif rolename == 'NotCounterPart':
            return not self.isCP and self.isSE
        elif rolename == ROLE_LR:
            return self.isLR
        return False


def _do_section_queries(view, action):
    action['num_obs'] = 0

    for section in action['sec']:
        objs = section['getter'](view)
        len_objs = len(objs)
        section['objs'] = objs
        section['num_obs'] = len_objs
        action['num_obs'] += len_objs

    return action['num_obs']


class InboxReviewFolderView(BrowserView):

    def __call__(self):
        self.rolemap_observations = dict()
        return super(InboxReviewFolderView, self).__call__()

    def get_sections(self):
        is_sec = self.is_secretariat()
        viewable = [sec for sec in SECTIONS if is_sec or sec['check'](self)]

        total_sum = 0
        for section in viewable:
            section['num_obs'] = 0

            for action in section['actions']:
                section['num_obs'] += _do_section_queries(self, action)

            total_sum += section['num_obs']

        return dict(viewable=viewable, total_sum=total_sum)

    @memoize
    def get_current_user(self):
        return api.user.get_current()

    def rolemap(self, observation):
        """ prepare a plain object, so that we can cache it in a RAM cache """
        user = self.get_current_user()
        roles = user.getRolesInContext(observation)
        return RoleMapItem(roles)

    def batch(self, observations, b_size, b_start, orphan, b_start_str):
        observationsBatch = Batch(
            observations, int(b_size), int(b_start), orphan=1)
        observationsBatch.batchformkeys = []
        observationsBatch.b_start_str = b_start_str
        return observationsBatch

    def get_observations(self, rolecheck=None, **kw):
        freeText = self.request.form.get('freeText', '')
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path': path,
            'portal_type': 'Observation',
            'sort_on': 'modified',
            'sort_order': 'reverse',
        }
        if freeText:
            query['SearchableText'] = freeText

        query.update(kw)

        observations = []
        for b in catalog.searchResults(query):
            # Handle bad indexes, where the catalog thinks the user has View
            # permission, but getObject() fails because the permissions differ.
            try:
                observations.append(b.getObject())
            except Unauthorized:
                pass

        if rolecheck is None:
            return observations

        for obs in observations:
            if obs.getId() not in self.rolemap_observations:
                self.rolemap_observations[obs.getId()] = self.rolemap(obs)

        def makefilter(rolename):
            """
            https://stackoverflow.com/questions/7045754/python-list-filtering-with-arguments
            """
            def myfilter(x):
                rolemap = self.rolemap_observations[x.getId()]
                return rolemap.check_roles(rolename)
            return myfilter

        filterfunc = makefilter(rolecheck)

        return filter(filterfunc, observations)

    @timeit
    def get_draft_observations(self):
        """
         Role: Sector Expert
         without actions for LR, counterpart or MS
        """
        return self.get_observations(
            rolecheck=ROLE_SE,
            observation_question_status=[
                'observation-draft'])

    @timeit
    def get_draft_questions(self):
        """
         Role: Sector Expert
         with comments from counterpart or LR
        """
        conclusions = self.get_observations(
            rolecheck=ROLE_SE,
            observation_question_status=[
                'draft',
                'drafted'])

        """
         Add also finalised observations with "no conclusion yet"
         https://taskman.eionet.europa.eu/issues/28813#note-5
        """
        no_conclusion_yet = self.get_observations(
            observation_question_status=['closed'],
            observation_finalisation_reason='no-conclusion-yet',
        )

        return conclusions + no_conclusion_yet

    @timeit
    def get_counterpart_questions_to_comment(self):
        """
         Role: Sector Expert
         needing comment from me
        """
        return self.get_observations(
            rolecheck=ROLE_CP,
            observation_question_status=[
                'counterpart-comments'])

    @timeit
    def get_counterpart_conclusion_to_comment(self):
        """
         Role: Sector Expert
         needing comment from me
        """
        return self.get_observations(
            rolecheck=ROLE_CP,
            observation_question_status=['conclusion-discussion'])

    @timeit
    def get_ms_answers_to_review(self):
        """
         Role: Sector Expert
         that need review
        """
        answered = self.get_observations(
            rolecheck=ROLE_SE,
            observation_question_status=[
                'answered'])

        pending = self.get_observations(
            rolecheck=ROLE_SE,
            observation_question_status=['closed'],
            review_state=['pending'])

        return answered + pending

    def get_draft_conclusions(self):
        return self.get_observations(
            rolecheck=ROLE_SE,
            review_state=['conclusions'],
        )

    @timeit
    def get_denied_observations(self):
        """
        Role: Sector Expert
        Observations that have been denied finalisation.
        """
        observations = self.get_observations(
            rolecheck=ROLE_SE,
            review_state=['conclusions', 'conclusions-lr-denied'],
        )

        def get_last_wf_item(obs):
            return obs.workflow_history.get('esd-review-workflow', [])[-1]

        def is_denied(obs):
            wf_item = get_last_wf_item(obs)
            return wf_item['action'] == 'deny-finishing-observation'

        return tuple(filter(is_denied, observations))

    @timeit
    def get_approval_questions(self):
        """
         Role: Sector Expert
         my questions sent to LR and MS and waiting for reply
        """
        # For a SE, those on LR pending to be sent to the MS
        # or recalled by him, are unanswered questions

        if not self.is_sector_expert():
            return []

        statuses = [
            'drafted',
            'recalled-lr'
        ]

        return self.get_observations(
            rolecheck=ROLE_SE,
            observation_question_status=statuses)

    @timeit
    def get_unanswered_questions(self):
        """
         Role: Sector Expert
         my questions sent to LR and MS and waiting for reply
        """
        statuses = [
            'pending',
            'recalled-msa',
            'expert-comments',
            'pending-answer-drafting'
        ]

        return self.get_observations(
            rolecheck=ROLE_SE,
            observation_question_status=statuses)

    @timeit
    def get_waiting_for_comment_from_counterparts_for_question(self):
        """
         Role: Sector Expert
        """
        return self.get_observations(
            rolecheck='NotCounterPart',
            observation_question_status=[
                'counterpart-comments'])

    @timeit
    def get_waiting_for_comment_from_counterparts_for_conclusion(self):
        """
         Role: Sector Expert
        """
        return self.get_observations(
            rolecheck='NotCounterPart',
            observation_question_status=[
                'conclusion-discussion'])

    @timeit
    def get_observation_for_finalisation(self):
        """
         Role: Sector Expert
         waiting approval from LR
        """
        return self.get_observations(
            rolecheck=ROLE_SE,
            observation_question_status=[
                'close-requested'])

    """
        Lead Reviewer
    """
    @timeit
    def get_questions_to_be_sent(self):
        """
         Role: Lead Reviewer
         Questions waiting for me to send to the MS
        """
        return self.get_observations(
            rolecheck=ROLE_LR,
            observation_question_status=[
                'drafted',
                'recalled-lr'])

    @timeit
    def get_observations_to_finalise(self):
        """
         Role: Lead Reviewer
         Observations waiting for me to confirm finalisation
        """
        return self.get_observations(
            rolecheck=ROLE_LR,
            observation_question_status=[
                'close-requested'])

    @timeit
    def get_questions_to_comment(self):
        """
         Role: Lead Reviewer
         Questions waiting for my comments
        """
        return self.get_observations(
            rolecheck=ROLE_CP,
            observation_question_status=[
                'counterpart-comments'])

    @timeit
    def get_conclusions_to_comment(self):
        """
         Role: Lead Reviewer
         Conclusions waiting for my comments
        """
        return self.get_observations(
            rolecheck=ROLE_CP,
            observation_question_status=['conclusion-discussion'])

    @timeit
    def get_questions_with_comments_from_reviewers(self):
        """
         Role: Lead Reviewer
         Questions waiting for comments by counterpart
        """
        return self.get_observations(
            rolecheck=ROLE_CP,
            observation_question_status=['counterpart-comments'])

    @timeit
    def get_answers_from_ms(self):
        """
         Role: Lead Reviewer
         that need review by Sector Expert
        """
        return self.get_observations(
            rolecheck=ROLE_LR,
            observation_question_status=[
                'answered'])

    @timeit
    def get_unanswered_questions_lr(self):
        """
         Role: Lead Reviewer
         questions waiting for comments from MS
        """
        return self.get_observations(
            rolecheck=ROLE_LR,
            observation_question_status=[
                'pending',
                'recalled-msa',
                'expert-comments',
                'pending-answer-drafting'])

    """
        MS Coordinator
    """
    @timeit
    def get_questions_to_be_answered(self):
        """
         Role: MS Coordinator
         Questions from the SE to be answered
        """
        return self.get_observations(
            rolecheck=ROLE_MSA,
            observation_question_status=[
                'pending',
                'recalled-msa',
                'pending-answer-drafting'])

    @timeit
    def get_questions_with_comments_received_from_mse(self):
        """
         Role: MS Coordinator
         Comments received from MS Experts
        """
        return self.get_observations(
            rolecheck=ROLE_MSA,
            observation_question_status=['expert-comments'],
            last_answer_has_replies=True,
            # last_answer_reply_number > 0
        )

    @timeit
    def get_answers_requiring_comments_from_mse(self):
        """
         Role: MS Coordinator
         Answers requiring comments/discussion from MS experts
        """
        return self.get_observations(
            rolecheck=ROLE_MSA,
            observation_question_status=['expert-comments'],
        )

    @timeit
    def get_answers_sent_to_se_re(self):
        """
         Role: MS Coordinator
         Answers sent to SE
        """
        answered = self.get_observations(
            rolecheck=ROLE_MSA,
            observation_question_status=['answered'])
        cat = api.portal.get_tool('portal_catalog')
        statuses = list(cat.uniqueValuesFor('review_state'))
        try:
            statuses.remove('closed')
        except ValueError:
            pass
        not_closed = self.get_observations(
            rolecheck=ROLE_MSA,
            review_state=statuses,
            observation_already_replied=True)

        return list(set(answered + not_closed))

    """
        MS Expert
    """
    @timeit
    def get_questions_with_comments_for_answer_needed_by_msc(self):
        """
         Role: MS Expert
         Comments for answer needed by MS Coordinator
        """
        return self.get_observations(
            rolecheck=ROLE_MSE,
            observation_question_status=['expert-comments'])

    @timeit
    def get_observations_with_my_comments(self):
        """
         Role: MS Expert
         Observation I have commented on
        """
        return self.get_observations(
            rolecheck=ROLE_MSE,
            observation_question_status=[
                'expert-comments',
                'pending-answer-drafting'],
            reply_comments_by_mse=True,
        )

    @timeit
    def get_observations_with_my_comments_sent_to_se_re(self):
        """
         Role: MS Expert
         Answers that I commented on sent to Sector Expert
        """
        return self.get_observations(
            rolecheck=ROLE_MSE,
            observation_question_status=[
                'answered',
                'recalled-msa'],
            reply_comments_by_mse=True,
        )

    def can_add_observation(self):
        sm = getSecurityManager()
        return sm.checkPermission('emrt.necd.content: Add Observation', self)

    def is_secretariat(self):
        user = api.user.get_current()
        return 'Manager' in user.getRoles()

    @cache(_user_name)
    def get_author_name(self, userid):
        user = api.user.get(userid)
        return user.getProperty('fullname', userid)

    def get_countries(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('eea_member_states')
        countries = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            countries.append((term[0], term[1]))

        return countries

    def get_sectors(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('ghg_source_sectors')
        sectors = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            sectors.append((term[0], term[1]))

        return sectors

    def is_sector_expert(self):
        ldap_wrapper = getUtility(IGetLDAPWrapper)(self.context)
        return partial(
            user_has_ldap_role, LDAP_SECTOREXP, ldap_wrapper=ldap_wrapper
        )

    def is_lead_reviewer(self):
        ldap_wrapper = getUtility(IGetLDAPWrapper)(self.context)
        return partial(
            user_has_ldap_role, LDAP_LEADREVIEW, ldap_wrapper=ldap_wrapper
        )

    def is_member_state_coordinator(self):
        ldap_wrapper = getUtility(IGetLDAPWrapper)(self.context)
        return partial(
            user_has_ldap_role, LDAP_MSA, ldap_wrapper=ldap_wrapper
        )

    def is_member_state_expert(self):
        ldap_wrapper = getUtility(IGetLDAPWrapper)(self.context)
        return partial(
            user_has_ldap_role, LDAP_MSEXPERT, ldap_wrapper=ldap_wrapper
        )


class FinalisedFolderView(BrowserView):

    def get_finalisation_reasons(self):
        key = itemgetter(0)

        def not_open(item):
            return key(item) != 'open'

        reasons = get_finalisation_reasons(self.context)
        return tuple(filter(not_open, reasons))

    def get_reasons_with_observations(self):
        reasons = self.get_finalisation_reasons()

        def obs_dict(key, title):
            obs = self.get_resolved_observations(key)
            return dict(obs=obs, num_obs=len(obs), title=title)

        reason_obs = {key: obs_dict(key, title) for key, title in reasons}

        return dict(
            reasons=reason_obs,
            total_obs=sum(obs['num_obs'] for obs in reason_obs.values())
        )

    def batch(self, observations, b_size, b_start, orphan, b_start_str):
        observationsBatch = Batch(
            observations, int(b_size), int(b_start), orphan=1)
        observationsBatch.batchformkeys = []
        observationsBatch.b_start_str = b_start_str
        return observationsBatch

    @cache(_catalog_change)
    @timeit
    def get_all_observations(self, freeText):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path': path,
            'portal_type': 'Observation',
            'sort_on': 'modified',
            'sort_order': 'reverse',
        }
        if freeText != "":
            query['SearchableText'] = freeText

        return map(
            decorate, [b.getObject() for b in catalog.searchResults(query)])

    def get_observations(self, **kw):
        freeText = self.request.form.get('freeText', '')
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path': path,
            'portal_type': 'Observation',
            'sort_on': 'modified',
            'sort_order': 'reverse',
        }
        if freeText:
            query['SearchableText'] = freeText

        query.update(kw)
        return [b.getObject() for b in catalog.searchResults(query)]

    """
        Finalised observations
    """
    @timeit
    def get_resolved_observations(self, reason):
        """
         Finalised with specified reason key.
        """
        return self.get_observations(
            observation_question_status=['closed'],
            observation_finalisation_reason=reason,
        )

    def can_add_observation(self):
        sm = getSecurityManager()
        return sm.checkPermission('emrt.necd.content: Add Observation', self)

    def is_secretariat(self):
        user = api.user.get_current()
        return 'Manager' in user.getRoles()

    @cache(_user_name)
    def get_author_name(self, userid):
        user = api.user.get(userid)
        return user.getProperty('fullname', userid)

    def get_countries(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('eea_member_states')
        countries = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            countries.append((term[0], term[1]))

        return countries

    def get_sectors(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('ghg_source_sectors')
        sectors = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            sectors.append((term[0], term[1]))

        return sectors


class AddForm(add.DefaultAddForm):

    def create(self, *args, **kwargs):
        folder = super(AddForm, self).create(*args, **kwargs)
        updated = getUtility(ISetupReviewFolderRoles)(folder)
        updated.reindexObjectSecurity()
        return updated


class AddView(add.DefaultAddView):
    form = AddForm
