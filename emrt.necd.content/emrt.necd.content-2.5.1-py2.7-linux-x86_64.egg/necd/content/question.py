from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition.interfaces import IAcquirer
from emrt.necd.content import MessageFactory as _
from emrt.necd.content.comment import IComment
from emrt.necd.content.constants import ROLE_LR
from emrt.necd.content.utilities.interfaces import IFollowUpPermission
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.dexterity.browser import add
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityFTI
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.Five import BrowserView
from time import time
from z3c.form import button
from z3c.form import field
from z3c.form.form import Form
from z3c.form.interfaces import ActionExecutionError
from zope.component import createObject
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Invalid


class IQuestion(form.Schema, IImageScaleTraversable):
    """
    New Question regarding an Observation
    """

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.


PENDING_STATUS_NAMES = ['answered']
OPEN_STATUS_NAMES = []
DRAFT_STATUS_NAMES = []
CLOSED_STATUS_NAMES = ['closed']

PENDING_STATUS_NAME = 'pending'
DRAFT_STATUS_NAME = 'draft'
OPEN_STATUS_NAME = 'open'
CLOSED_STATUS_NAME = 'closed'


def create_question(context):
    fti = getUtility(IDexterityFTI, name='Question')
    container = aq_inner(context)
    content = createObject(fti.factory)
    if hasattr(content, '_setPortalTypeName'):
        content._setPortalTypeName(fti.getId())

    # Acquisition wrap temporarily to satisfy things like vocabularies
    # depending on tools
    if IAcquirer.providedBy(content):
        content = content.__of__(container)

    ids = [id for id in context.keys() if id.startswith('question-')]
    id = len(ids) + 1
    content.title = 'Question %d' % id

    return aq_base(content)


@implementer(IQuestion)
class Question(Container):
    # Add your class methods and properties here

    def can_add_follow_up_question(self):
        return getUtility(IFollowUpPermission)(self)

    def get_state_api(self):
        return api.content.get_state(self)

    def get_questions(self):
        sm = getSecurityManager()
        values = [v for v in self.values() if sm.checkPermission('View', v)]
        return IContentListing(values)

    def getFirstComment(self):
        comments = [v for v in self.values() if v.portal_type == 'Comment']
        comments.sort(lambda x, y: cmp(x.created(), y.created()))
        if comments:
            return comments[-1]
        return None

    def get_state(self):
        state = api.content.get_state(self)
        workflows = (
            api.portal.get_tool('portal_workflow')
            .getWorkflowsFor(self)
        )
        if workflows:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state

    def get_status(self):
        state = api.content.get_state(self)
        if state in PENDING_STATUS_NAMES:
            return PENDING_STATUS_NAME
        elif state in OPEN_STATUS_NAMES:
            return OPEN_STATUS_NAME
        elif state in CLOSED_STATUS_NAMES:
            return CLOSED_STATUS_NAME
        elif state in DRAFT_STATUS_NAMES:
            return DRAFT_STATUS_NAME

        return 'unknown'

    def get_observation(self):
        return aq_parent(aq_inner(self))

    def has_answers(self):
        items = self.values()
        return len(items) and items[-1].portal_type == 'CommentAnswer' or False

    def can_be_sent_to_lr(self):
        items = self.values()
        questions = [q for q in items if q.portal_type == 'Comment']
        answers = [q for q in items if q.portal_type == 'CommentAnswer']

        if len(questions) > len(answers):
            current_status = api.content.get_state(self)
            return current_status == 'draft'

        return False

    def can_be_deleted(self):
        items = self.values()
        questions = [q for q in items if q.portal_type == 'Comment']
        answers = [q for q in items if q.portal_type == 'CommentAnswer']

        if (len(questions) > len(answers)):
            # We need to check that the question was created in the previous
            # step. We will now allow deleting the question after a comment
            # loop
            q_history = self.workflow_history['esd-question-review-workflow']
            current_status = api.content.get_state(self)
            previous_action = q_history[-1]
            if current_status == 'draft':
                return previous_action['action'] in [
                    'add-followup-question',
                    'reopen',
                    None
                ]

        return False

    def unanswered_questions(self):
        items = self.values()
        questions = [q for q in items if q.portal_type == 'Comment']
        answers = [q for q in items if q.portal_type == 'CommentAnswer']

        return len(questions) > len(answers)

    def can_close(self):
        """
        Check if this question can be closed:
            - There has been at least, one question-answer.
        """
        items = self.values()
        questions = [q for q in items if q.portal_type == 'Comment']
        answers = [q for q in items if q.portal_type == 'CommentAnswer']

        return len(questions) > 0 and len(questions) == len(answers)

    def observation_not_closed(self):
        observation = self.get_observation()
        return api.content.get_state(observation) in ['pending']

    def already_commented_by_counterpart(self):
        # XXXX
        return True

    def one_pending_answer(self):
        if self.has_answers():
            answers = [
                q for q in self.values()
                if q.portal_type == 'CommentAnswer'
            ]
            return len(answers) > 0
        else:
            return False

    def can_see_comment_discussion(self):
        sm = getSecurityManager()
        return sm.checkPermission(
            'emrt.necd.content: View Comment Discussion', self)

    def can_see_answer_discussion(self):
        sm = getSecurityManager()
        return sm.checkPermission(
            'emrt.necd.content: View Answer Discussion', self)

# View class
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# This will make this view the default view for your content-type


class QuestionView(BrowserView):
    def render(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        return self.request.response.redirect(parent.absolute_url())


class AddForm(add.DefaultAddForm):
    def updateFields(self):
        super(AddForm, self).updateFields()
        self.fields = field.Fields(IComment).select('text')
        self.groups = [
            g for g in self.groups
            if g.label == 'label_schema_default'
        ]

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        self.widgets['text'].rows = 15

    def create(self, data={}):
        return create_question(self.context)

    def add(self, object):
        super(AddForm, self).add(object)
        item = self.context.get(object.getId())
        text = self.request.form.get('form.widgets.text', '')
        id = str(int(time()))
        item_id = item.invokeFactory(
            type_name='Comment',
            id=id,
        )
        comment = item.get(item_id)
        comment.text = text


class AddView(add.DefaultAddView):
    form = AddForm


def add_question(context, event):
    """ When adding a question, go directly to
        'open' status on the observation
    """
    observation = aq_parent(context)
    observation.reindexObject()


class AddCommentForm(Form):
    ignoreContext = True
    fields = field.Fields(IComment).select('text')

    label = 'Question'
    description = ''

    @button.buttonAndHandler(_('Add question'))
    def create_question(self, action):
        context = aq_inner(self.context)
        text = self.request.form.get('form.widgets.text', '')
        if not text.strip():
            raise ActionExecutionError(Invalid(u"Question text is empty"))

        id = str(int(time()))
        item_id = context.invokeFactory(
            type_name='Comment',
            id=id,
        )
        comment = context.get(item_id)
        comment.text = text

        return self.request.response.redirect(context.absolute_url())

    def updateWidgets(self):
        super(AddCommentForm, self).updateWidgets()
        self.widgets['text'].rows = 15

    def updateActions(self):
        super(AddCommentForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class AddAnswerForm(Form):

    ignoreContext = True
    fields = field.Fields(IComment).select('text')

    label = 'Answer'
    description = ''

    @button.buttonAndHandler(_('Add answer'))
    def create_question(self, action):
        context = aq_inner(self.context)
        text = self.request.form.get('form.widgets.text', '')
        if not text.strip():
            raise ActionExecutionError(Invalid(u"Answer text is empty"))

        id = str(int(time()))
        item_id = context.invokeFactory(
            type_name='CommentAnswer',
            id=id,
        )
        comment = context.get(item_id)
        comment.text = text

        return self.request.response.redirect(context.absolute_url())

    def updateWidgets(self):
        super(AddAnswerForm, self).updateWidgets()
        self.widgets['text'].rows = 15

    def updateActions(self):
        super(AddAnswerForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class AddFollowUpQuestion(BrowserView):
    def render(self):
        api.content.transition(
            obj=self.context,
            transition='reopen')

        url = '%s/++add++Comment' % self.context.absolute_url()
        return self.request.response.redirect(url)


class AddConclusions(BrowserView):
    def render(self):
        parent = aq_parent(self.context)
        conclusions = parent.get_conclusion()
        if not conclusions:
            url = '{}/++add++Conclusions'.format(parent.absolute_url())
        else:
            url = '%s/edit' % conclusions.absolute_url()

        return self.request.response.redirect(url)


class DeleteLastComment(BrowserView):
    def render(self):
        comments = [
            c for c in self.context.values()
            if c.portal_type == 'Comment'
        ]
        if comments:
            last_comment = comments[-1]
            question = aq_inner(self.context)
            if len(comments) == 1:
                # delete also the parent question
                self.context.manage_delObjects([last_comment.getId()])
                observation = aq_parent(question)
                del observation[question.getId()]
                return self.request.response.redirect(
                    observation.absolute_url())
            else:
                question_state = api.content.get_state(obj=question)
                self.context.manage_delObjects([last_comment.getId()])
                url = question.absolute_url()
                if question_state == 'draft':
                    url += (
                        '/content_status_modify'
                        '?workflow_action=delete-question'
                    )
                return self.request.response.redirect(url)


class DeleteLastAnswer(BrowserView):
    def render(self):
        question = aq_inner(self.context)
        url = question.absolute_url()
        comments = [
            c for c in self.context.values()
            if c.portal_type == 'CommentAnswer'
        ]
        if comments:
            last_comment = comments[-1]
            question_state = api.content.get_state(obj=question)
            self.context.manage_delObjects([last_comment.getId()])
            if question_state == 'pending-answer-drafting':
                url += '/content_status_modify?workflow_action=delete-answer'
            return self.request.response.redirect(url)
        return self.request.response.redirect(url)


class ApproveAndSendView(BrowserView):
    def render(self):
        question = self.context.aq_parent
        roles = api.user.get_roles(obj=question)
        is_lr = ROLE_LR in roles or 'Manager' in roles
        if is_lr:
            self.context.redraft_message = ''
            api.content.transition(
                obj=question,
                transition='approve-question',
                comment=self.context.getId(),
            )
        return self.request.response.redirect(question.absolute_url())
